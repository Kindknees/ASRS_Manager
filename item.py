from pydantic import BaseModel
from typing import Optional, Tuple

class Item(BaseModel):
    """
    Represents an item to be placed in a bin.
    Attributes:
        pallet_id: Unique identifier for the pallet.
        cargo_id: Optional cargo ID for the item.
        width: Width of the item.
        height: Height of the item.
        depth: Depth of the item.   
        rotation: 1 if item is allowed to rotate, 0 otherwise.
        weight: Weight of the item.
        empty: True if it is an empty pallet.
        position: Item's placed position. (x, y, z) coordinates when placed.
        placed_bin: ID of the bin where the item is placed.
        placed_dimensions: Store final dimensions after rotation.
    """
    pallet_id: Optional[str] = None
    width: float
    height: float
    depth: float
    weight: Optional[float]
    rotation: bool = False
    empty: bool

    cargo_id: Optional[str] = None
    position: Optional[Tuple[float, float, float]] = None
    placed_bin: Optional[str] = None
    placed_dimensions: Optional[Tuple[float, float, float]] = None

    def reset(self, min_adjust_length):
        """
        Reset the item to be an empty pallet.
        """
        self.width = 0
        self.height = min_adjust_length
        self.depth = 0
        self.rotation = False
        self.empty = True
        self.weight = None
        self.position = None
        self.placed_bin = None
        self.placed_dimensions = (self.width, self.height, self.depth)
        self.cargo_id = None

    def to_dict(self):
        """Converts the item object to a dictionary for JSON serialization."""
        return {
            "pallet_id": self.pallet_id,
            "cargo_id": self.cargo_id,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "weight": self.weight,
            "rotation": self.rotation,
            "empty": self.empty,
            "position": self.position,
            "placed_bin": self.placed_bin,
            "placed_dimensions": self.placed_dimensions
        }