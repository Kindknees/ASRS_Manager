import pandas as pd
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Tuple, Dict, Any

from ASRSManager import ASRSManager
from item import Item

app = FastAPI(
    title="ASRS Management API",
    description="API for managing an Automated Storage and Retrieval System.",
)

try:
    manager = ASRSManager(config_path='./config.yaml')
except FileNotFoundError:
    raise RuntimeError("Configuration file 'config.yaml' not found. API cannot start.")
except Exception as e:
    raise RuntimeError(f"Failed to initialize ASRSManager: {e}")

class ItemInput(BaseModel):
    width: float
    height: float
    depth: float
    weight: float
    can_rotate: bool = Field(default=False, description="Whether the item can be rotated. True if it can be rotated, False otherwise.")
    empty: bool = Field(default=False, description="Whether the item is an empty pallet.")
    cargo_id: Optional[str] = Field(None, description="Optional cargo ID for the item.")

class PlacementResponse(BaseModel):
    success: bool
    original_pallet_placed_bin: str
    original_pallet_position: Tuple[float, float, float]
    target_bin: str
    target_position: Tuple[float, float, float]
    pallet_id: str
    item: Dict[str, Any]

class ItemModel(BaseModel):
    pallet_id: Optional[str] = None
    cargo_id: Optional[str] = None
    width: float
    height: float
    depth: float
    weight: Optional[float]
    rotation: Optional[bool]
    empty: bool
    position: Optional[Tuple[float, float, float]]
    placed_bin: Optional[int]
    placed_dimensions: Optional[Tuple[float, float, float]]

class RemoveItemResponse(BaseModel):
    success: bool
    item: ItemModel

class BatchPlacementInput(BaseModel):
    pallet_id: str = Field(..., description="Unique identifier of the pallet.")
    cargo_id: str = Field(None, description="Optional cargo ID for the item.")
    width: float
    height: float
    depth: float
    weight: float
    can_rotate: bool = Field(default=False, description="Whether the item can be rotated. True if it can be rotated, False otherwise.")
    empty: bool = Field(default=False, description="Whether the item is an empty pallet.")
    position: Tuple[float, float, float] = Field(..., description="The position of the item in the bin.")
    placed_bin: str = Field(..., description="The ID of the bin where the item is placed.")
    placed_dimensions: Tuple[float, float, float] = Field(..., description="The dimensions of the item after placement. (width, height, depth)")

class BatchPlacementInfo(BaseModel):
    placed_bin: str
    position: Tuple[float, float, float]
    placed_dimensions: Tuple[float, float, float]

class BatchPlacementResponse(RootModel):
    root: Dict[str, BatchPlacementInfo]

class NewPlacementInfo(BaseModel):
    new_bin: str = Field(..., description="The new bin ID where the item is placed after reorganization.")
    new_position: Tuple[float, float, float] = Field(..., description="The new position (x, y, z) of the item.")

class ReorganizationResponse(BaseModel):
    status: str = Field(..., example="success")
    new_placements: Dict[str, NewPlacementInfo] = Field(..., description="A dictionary mapping each pallet ID to its new placement information.")

@app.post("/items", response_model=PlacementResponse, status_code=201, summary="Place a new single item (Online Operation)")
def place_new_cargo(item_input: ItemInput):
    """
    接收一個新貨物的資訊，使用線上 First-Fit 演算法將其存入儲位。
    """
    try:
        item_to_place = Item(
            width=item_input.width, height=item_input.height, depth=item_input.depth,
            rotation=item_input.can_rotate, weight=item_input.weight, cargo_id=item_input.cargo_id, empty=False
        )
        placement_plan = manager.place_item_online(item_to_place)
        if placement_plan:
            return placement_plan
        raise HTTPException(status_code=500, detail="Failed to place item for an unknown reason.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/items", response_model=Dict[str, ItemModel], summary="Get all items in the system")
def get_all_items():
    """
    獲取倉儲系統中所有已存入 (非空棧板) 貨物的列表。
    """
    try:
        results = manager.get_all_items()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {str(e)}")


@app.get("/items/{item_id}", response_model=ItemModel, summary="Retrieve a specific item")
def retrieve_item(pallet_id: Optional[str] = None, cargo_id: Optional[str] = None) -> dict:
    """
    根據貨物 ID 查詢特定貨物的詳細資訊。
    """
    try:
        result_dict = manager.retrieve_item(pallet_id=pallet_id, cargo_id=cargo_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Item not found.")
        
    return result_dict

@app.delete("/items/{item_id}", response_model=RemoveItemResponse, summary="Remove a specific item")
def remove_item(pallet_id: Optional[str]=None, cargo_id: Optional[str]=None):
    """
    根據貨物 ID 將其從系統中移除。被取出的貨物會變回空棧板並放回棧板區。
    """
    try:
        result = manager.remove_item(pallet_id=pallet_id, cargo_id=cargo_id)
    except Exception as e:
       raise HTTPException(status_code=500, detail=f"Failed to remove item: {str(e)}")
    if not result['success']:
        raise HTTPException(status_code=404, detail=result.get('message', f"Failed to remove item {pallet_id or cargo_id}."))
    return result

@app.post("/reorganize", response_model=ReorganizationResponse, summary="Perform offline reorganization")
def reorganization():
    """
    觸發離線整理操作。此操作會使用 Best-Fit 演算法重新排列所有貨物，以最佳化空間使用率。
    """
    try:
        reorg_result = manager.reorganize_offline()
        return {
            "status": "success",
            "new_placements": reorg_result
        }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/batch-place", response_model=BatchPlacementResponse, summary="Batch place items")
def batch_place_items(batch_items: List[BatchPlacementInput]):
    """
    批量放置貨物。接收一組貨物資訊，並將它們放入指定的儲位。此功能用於系統突然發生事故（如斷電、故障等）後，重新使系統回到正常狀態。
    """
    try:
        items = []
        
        for i in batch_items:
            item = Item(
                width=i.width, height=i.height, depth=i.depth,
                rotation=i.can_rotate, weight=i.weight, pallet_id=i.pallet_id,
                cargo_id=i.cargo_id, empty=i.empty
            )
            item.position = i.position
            item.placed_bin = i.placed_bin
            item.placed_dimensions = i.placed_dimensions
            items.append(item)

        results = manager.batch_place_items(items)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", summary="API Root")
def read_root():
    return {"message": "Welcome to the ASRS Management API. Go to /docs for interactive documentation."}