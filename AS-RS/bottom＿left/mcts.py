import numpy as np
from heapq import heappush, heappop, heapify
import random
import math
import copy

class Item:
    def __init__(self, width, height, depth, weight, rotation, fragile, id=None):
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight  
        self.rotation = rotation    # 1 if item is allowed to rotate, 0 otherwise
        self.fragile = fragile  # 1 if item is fragile, 0 otherwise
        self.position = None  # (x, y, z) coordinates when placed
        self.id = id
        self.placed_dimensions = None  # Store final dimensions after rotation

class Container:
    def __init__(self, width, height, depth, buffer):
        self.width = width
        self.height = height
        self.depth = depth
        self.items = []
        self.buffer = buffer  # Buffer spaces between items
        self.space = np.zeros((width, height, depth), dtype=bool)  # Track occupied space
        self.extreme_points = [(0, 0, 0)]  # Start with bottom-left-back corner

    def get_state_snapshot(self):
        """為了 MCTS，建立一個輕量級的狀態快照"""
        snapshot = {
            'items': [item.id for item in self.items],
            'space': self.space.copy(),
            'extreme_points': self.extreme_points.copy()
        }
        return snapshot
    
    def load_state_snapshot(self, snapshot):
        """從快照恢復狀態，注意：這不會恢復 item 物件本身"""
        # 為了簡化，我們只恢復 MCTS 決策所需的核心狀態
        self.space = snapshot['space'].copy()
        self.extreme_points = snapshot['extreme_points'].copy()
        # 實際 items 列表的恢復較複雜，在 MCTS 中我們主要關心空間

    def can_place(self, x, y, z, width, height, depth):
        # Check container boundaries with given dimensions
        if (x + width + self.buffer > self.width or
            y + height> self.height or
            z + depth + self.buffer > self.depth):
            return False
        return not np.any(self.space[x:x+width, y:y+height, z:z+depth])

    def place_item(self, item, x, y, z, width, height, depth):
        # Mark space as occupied
        self.space[x:x+width+self.buffer, y:y+height, z:z+depth+self.buffer] = True
        item.position = (x, y, z)
        item.placed_dimensions = (width, height, depth)  # Store final dimensions
        self.items.append(item)
        # Update extreme points
        
        self.update_extreme_points(item, x, y, z, width, height, depth)

    def update_extreme_points(self, item, x, y, z, width, height, depth):
        """
        更新極端點列表。
        1. 移除被新放置物品佔據或遮蔽的所有現有極端點。
        2. 加入由新物品產生的三個新極端點。
        3. 去除重複點並重新整理成一個堆。
        """
        # 步驟 1: 找出並移除所有被新物品遮蔽的點
        # 我們定義新物品佔據的體積（不包含緩衝區，因為極端點本身不應落在緩衝區內）
        item_x_end = x + width
        item_y_end = y + height
        item_z_end = z + depth

        survivors = []
        for point in self.extreme_points:
            px, py, pz = point
            # 如果一個點位於新物品的體積之內，它就被遮蔽了
            if (px >= x and px < item_x_end and
                py >= y and py < item_y_end and
                pz >= z and pz < item_z_end):
                continue  # 這個點被遮蔽了，捨棄
            survivors.append(point)
        
        # 步驟 2: 加入由新物品產生的新極端點
        new_points = [
            (x + width, y, z),          # 右側面產生的點
            (x, y, z + depth),          # 前側面產生的點
        ]
        if not item.fragile:
            new_points.append((x, y + height, z))  # 頂面產生的點

        # 步驟 3: 將倖存的點和新產生的點合併
        # 我們只加入在貨櫃範圍內的點
        for p in new_points:
            if p[0] < self.width and p[1] < self.height and p[2] < self.depth:
                survivors.append(p)

        # 步驟 4: 去除重複的點並重新堆化 (heapify)
        # 使用 set 來快速去除重複項
        self.extreme_points = list(set(survivors))
        heapify(self.extreme_points)

# def bottom_left_3d_bin_packing(container, items):
#     """
#     Bottom-Left heuristic for online 3D bin packing using extreme points.
#     Supports item rotation for items with rotation=1, trying all 6 orientations.
#     Places items at the lowest, leftmost, backmost feasible extreme point.
#     """
#     for item in items:
#         placed = False
#         # Define possible orientations
#         w, h, d = item.width, item.height, item.depth
#         orientations = set([
#             (w, h, d), (d, h, w),
#             ])  # Default orientation. Check the item without rotation first
#         if item.rotation == 1:      
#             orientations = set([
#                 (w, h, d), (d, h, w), 
#                 (h, w, d), (h, d, w),
#                 (w, d, h), (d, w, h),
#             ])
        
#         # Create a temporary copy of extreme points to reuse if needed
#         temp_points = container.extreme_points.copy()
        
#         # Try each orientation
#         for width, height, depth in orientations:
#             while container.extreme_points:
#                 x, y, z = heappop(container.extreme_points)
#                 if container.can_place(item, x, y, z, width, height, depth):
#                     container.place_item(item, x, y, z, width, height, depth)
#                     placed = True
#                     break
#             if placed:
#                 break
        
#         if not placed:
#             print(f"Cannot place item with original dimensions ({item.width}, {item.height}, {item.depth})")
#             # raise ValueError("No feasible placement found for item.")

class MonteCarloNode:
    def __init__(self, parent, container_state, unplaced_items, action_item=None):
        self.parent = parent
        self.container_state = container_state # 儲存貨櫃狀態快照
        self.unplaced_items = unplaced_items # 尚未放置的物品 set
        self.action_item = action_item # 導致這個節點的動作 (放置了哪個 item)

        self.children = []
        self.visits = 0
        self.total_value = 0.0 # 來自模擬的總分數

    def is_fully_expanded(self):
        """檢查是否所有可能的動作（放置物品）都已經有對應的子節點"""
        return len(self.children) == len(self.unplaced_items)

    def select_best_child(self, exploration_weight=1.41):
        """使用 UCB1 公式選擇最佳子節點"""
        best_score = -1
        best_child = None
        for child in self.children:
            if child.visits == 0:
                # 優先選擇未訪問過的節點
                return child
            
            exploit_score = child.total_value / child.visits
            explore_score = math.sqrt(math.log(self.visits) / child.visits)
            ucb_score = exploit_score + exploration_weight * explore_score
            
            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child
        return best_child

def find_best_placement_for_item(container, item):
    """一個輔助函式，為單一物品找到最佳放置點"""
    # 這裡使用你之前的邏輯：找到第一個可行的極端點
    temp_container = copy.deepcopy(container) # 在副本上操作
    
    # 產生方向
    orientations = [(item.width, item.height, item.depth)]
    if item.rotation == 1:
        w, h, d = item.width, item.height, item.depth
        orientations = list(set([(w,h,d), (d,h,w), (w,d,h), (h,w,d), (h,d,w), (d,w,h)]))

    # 遍歷所有極端點和方向
    # 為了穩定性，我們不 heappop，而是遍歷排序後的副本
    sorted_points = sorted(temp_container.extreme_points)
    for y, z, x in sorted_points:
        for w, h, d in orientations:
            if temp_container.can_place(x, y, z, w, h, d):
                return {'x': x, 'y': y, 'z': z, 'w': w, 'h': h, 'd': d}
    return None # 放不下了

def run_mcts(initial_container, items_to_place, n_simulations, exploration_weight=1.41):
    """執行 MCTS 來決定下一步要放哪個物品"""
    
    root = MonteCarloNode(None, initial_container.get_state_snapshot(), set(items_to_place))
    
    for _ in range(n_simulations):
        node = root
        
        # 1. Selection
        while node.is_fully_expanded() and node.children:
            node = node.select_best_child(exploration_weight)
            
        # 2. Expansion
        if not node.is_fully_expanded():
            unexpanded_items = node.unplaced_items - {c.action_item for c in node.children}
            item_to_place = random.choice(list(unexpanded_items))
            
            # 建立一個臨時的貨櫃來模擬放置
            temp_container = Container(initial_container.width, initial_container.height, initial_container.depth, initial_container.buffer)
            temp_container.load_state_snapshot(node.container_state)
            
            placement = find_best_placement_for_item(temp_container, item_to_place)
            
            if placement:
                temp_container.place_item(item_to_place, placement['x'], placement['y'], placement['z'],
                                          placement['w'], placement['h'], placement['d'])
                
                new_unplaced = node.unplaced_items - {item_to_place}
                child_node = MonteCarloNode(node, temp_container.get_state_snapshot(), new_unplaced, action_item=item_to_place)
                node.children.append(child_node)
                node = child_node # 模擬從新節點開始
        
        # 3. Simulation (Rollout)
        sim_container = Container(initial_container.width, initial_container.height, initial_container.depth, initial_container.buffer)
        sim_container.load_state_snapshot(node.container_state)
        
        items_for_simulation = list(node.unplaced_items)
        random.shuffle(items_for_simulation) # 隨機順序是蒙地卡羅的精髓
        
        placed_volume = 0
        for item in items_for_simulation:
            placement = find_best_placement_for_item(sim_container, item)
            if placement:
                sim_container.place_item(item, placement['x'], placement['y'], placement['z'],
                                         placement['w'], placement['h'], placement['d'])
                placed_volume += placement['w'] * placement['h'] * placement['d']
        
        # 評分：成功放置的體積 / 總體積
        total_possible_volume = sum(i.width * i.height * i.depth for i in items_to_place)
        score = placed_volume / total_possible_volume if total_possible_volume > 0 else 0

        # 4. Backpropagation
        while node is not None:
            node.visits += 1
            node.total_value += score
            node = node.parent

    # 決策：選擇訪問次數最多的子節點的動作
    if not root.children:
        return None # 如果根節點無法擴展，代表一個都放不了
    
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.action_item


def pack_items_with_mcts(container, all_items, lookahead_k, n_simulations):
    """
    使用 MCTS 進行裝箱的主控函式。
    - lookahead_k: 可預見的貨物數量 (1-3)
    - n_simulations: 每次決策要執行的模擬次數
    """
    item_queue = list(all_items)
    
    while item_queue:
        # 決定 lookahead 緩衝區
        buffer_size = min(lookahead_k, len(item_queue))
        lookahead_buffer = item_queue[:buffer_size]
        
        # print(f"\n--- Deciding for buffer: {[item.id for item in lookahead_buffer]} ---")
        
        # 使用 MCTS 決定下一步要放哪個物品
        best_item_to_place = run_mcts(container, lookahead_buffer, n_simulations)
        
        if best_item_to_place is None:
            # print(f"MCTS decided no item in the buffer can be placed. Stopping.")
            # 可能是真的滿了，也可能是 find_best_placement_for_item 找不到位置
            # 可以加入一個機制，跳過這個物品，嘗試下一個
            item_to_move = item_queue.pop(0)
            # item_queue.append(item_to_move)
            print(f"Skipping item {item_to_move.id} for now, will retry later.")
            continue

        # print(f"MCTS Choice: Place item {best_item_to_place.id}")
        
        # 執行最佳動作
        placement = find_best_placement_for_item(container, best_item_to_place)
        if placement:
            container.place_item(best_item_to_place, placement['x'], placement['y'], placement['z'],
                                 placement['w'], placement['h'], placement['d'])
            
            # 從隊列中移除已放置的物品
            # 要注意比對 id，因為物件可能不同
            item_to_remove = next(i for i in item_queue if i.id == best_item_to_place.id)
            item_queue.remove(item_to_remove)
            
            print(f"Placed {best_item_to_place.id} at {best_item_to_place.position} with dims {best_item_to_place.placed_dimensions}")
        else:
            # 理論上 MCTS 找到的解應該是可行的，但以防萬一
            print(f"Error: MCTS chose {best_item_to_place.id}, but placement failed in final step. Skipping.")
            item_to_remove = next(i for i in item_queue if i.id == best_item_to_place.id)
            item_queue.remove(item_to_remove)

if __name__ == "__main__":
    # 定義貨櫃和貨物
    container = Container(width=10, height=10, depth=10, buffer=1)
    items = [
        Item(width=2, height=2, depth=2, weight=1, rotation=1, fragile=0, id=1),
        Item(width=3, height=3, depth=3, weight=2, rotation=1, fragile=0, id=2),
        Item(width=4, height=4, depth=4, weight=3, rotation=1, fragile=0, id=3),
        Item(width=5, height=5, depth=5, weight=4, rotation=1, fragile=0, id=4),
        Item(width=2, height=3, depth=1, weight=1, rotation=1, fragile=0, id=5),
        Item(width=1, height=2, depth=3, weight=1, rotation=1, fragile=0, id=6),
        Item(width=3, height=2, depth=1, weight=2, rotation=1, fragile=0, id=7),
        Item(width=2, height=1, depth=3, weight=1, rotation=1, fragile=0, id=8),
        Item(width=1, height=1, depth=1, weight=1, rotation=1, fragile=0, id=9),
        Item(width=2, height=2, depth=3, weight=1, rotation=1, fragile=0, id=10),
        Item(width=3, height=1, depth=2, weight=2, rotation=1, fragile=0, id=11),
        Item(width=4, height=2, depth=1, weight=3, rotation=1, fragile=0, id=12),
        Item(width=5, height=3, depth=2, weight=4, rotation=1, fragile=0, id=13),
        Item(width=2, height=4, depth=3, weight=1, rotation=1, fragile=0, id=14),
    ]
    
    # --- 參數設定 ---
    # 可預見的貨物數量 (1, 2, or 3)
    LOOKAHEAD_K = 4
    
    # 每次決策的模擬次數。越高，決策品質越好，但越慢。
    # 500-1000 是一個不錯的起點
    N_SIMULATIONS = 500

    # 執行裝箱
    if LOOKAHEAD_K:
        pack_items_with_mcts(container, items, lookahead_k=LOOKAHEAD_K, n_simulations=N_SIMULATIONS)
    
    # 輸出結果
    print("\n--- Final Placement Result ---")
    for i, item in enumerate(container.items):
        print(f"Item {item.id} placed at position {item.position} with dimensions "
              f"{item.placed_dimensions}")
    
    total_volume = container.width * container.height * container.depth
    used_volume = sum(item.placed_dimensions[0] * item.placed_dimensions[1] * item.placed_dimensions[2]
                      for item in container.items)
    utilization = used_volume / total_volume
    print(f"\nSpace utilization: {utilization:.2%}")