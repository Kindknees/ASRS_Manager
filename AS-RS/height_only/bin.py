import utils

class Bin:
    def __init__(self, width, height, depth, min_adjust_length, id, weight_limit=None):
        self.width = width
        self.height = height
        self.depth = depth
        self.weight_limit = weight_limit
        self.min_adjust_length = min_adjust_length
        self.id = id
        self.items = {}

    def reset(self):
        self.items = {}

    def get_current_height(self):
        if not self.items:
            return 0
        return max(item.position[1] + utils.get_adjusted_height(item.placed_dimensions[1], self.min_adjust_length) for item in self.items.values())

    def can_place(self, item):
        bin_dimensions = (self.width, self.height, self.depth, self.min_adjust_length)
        item_dimension = utils.get_optimal_dimension(item, bin_dimensions)
        item.placed_dimensions = item_dimension
        adjusted_item_height = utils.get_adjusted_height(item.placed_dimensions[1], self.min_adjust_length)

        # check if the item fits within the bin dimensions at the given position
        if (item.width > self.width or
            adjusted_item_height > self.height or
            item.depth > self.depth):
            return False
        
        remaining_height = self.height - self.get_current_height() - adjusted_item_height
        if remaining_height < 0:
            return False
        return True

    # def _intersects(self, item1, pos1, item2):  # not used
    #     """
    #     check whether two items are overlapped
    #     """
    #     pos2 = item2.position
    #     dim2 = item2.placed_dimensions
    #     dim1 = item1.placed_dimensions

    #     adjusted_dim1_h = utils.get_adjusted_height(dim1[1], self.min_adjust_length)
    #     adjusted_dim2_h = utils.get_adjusted_height(dim2[1], self.min_adjust_length)

    #     x_overlap = (pos1[0] < pos2[0] + dim2[0]) and (pos1[0] + dim1[0] > pos2[0])
    #     y_overlap = (pos1[1] < pos2[1] + adjusted_dim2_h) and (pos1[1] + adjusted_dim1_h > pos2[1])
    #     z_overlap = (pos1[2] < pos2[2] + dim2[2]) and (pos1[2] + dim1[2] > pos2[2])

    #     return x_overlap and y_overlap and z_overlap

    def place_item(self, item, position):
        try:
            item.position = position
            item.placed_bin = self.id
            self.items[item.id] = item
        except Exception as e:
            raise ValueError(f"Error placing item {item.id} in bin {self.id}: {e}")