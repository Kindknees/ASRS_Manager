class Bin:
    def __init__(self, width, height, depth, min_adjust_length):
        self.width = width
        self.height = height
        self.depth = depth
        self.min_adjust_length = min_adjust_length  # 櫃子每次進行調整時的單位長度
        self.items = []

    def get_current_height(self):
        if not self.items:
            return 0
        return max(item.position[1] + item.placed_dimensions[1] for item in self.items)

    def can_place(self, item, position):
        """
        檢查物品是否可以在指定位置放置，而不與其他已放置物品重疊或超出邊界。
        """
        # 檢查邊界
        if (position[0] + item.placed_dimensions[0] > self.width or
            position[1] + item.placed_dimensions[1] > self.height or
            position[2] + item.placed_dimensions[2] > self.depth):
            return False

        # 檢查與已放置物品的重疊
        for placed_item in self.items:
            if self._intersects(item, position, placed_item):
                return False
        return True

    def _intersects(self, item1, pos1, item2):
        """
        檢查兩個物品是否重疊。
        """
        # item2 已經有 position 屬性
        pos2 = item2.position
        dim2 = item2.placed_dimensions

        # item1 的維度
        dim1 = item1.placed_dimensions

        # 檢查 x, y, z 軸上是否有間隔
        x_overlap = (pos1[0] < pos2[0] + dim2[0]) and (pos1[0] + dim1[0] > pos2[0])
        y_overlap = (pos1[1] < pos2[1] + dim2[1]) and (pos1[1] + dim1[1] > pos2[1])
        z_overlap = (pos1[2] < pos2[2] + dim2[2]) and (pos1[2] + dim1[2] > pos2[2])

        return x_overlap and y_overlap and z_overlap

    def place_item(self, item, position):
        """
        將物品放置在指定位置。
        """
        item.position = position
        self.items.append(item)

    def get_possible_positions(self, item):
        """
        為新物品生成可能的放置點。
        """
        if not self.items:
            return [(0, 0, 0)]
        
        top_item = max(self.items, key=lambda i: i.position[1] + i.placed_dimensions[1])
    
        # 新的放置點在該物品的正上方
        pos_height = top_item.position[1] + top_item.placed_dimensions[1]
        
        return [(0, pos_height, 0)]