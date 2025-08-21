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

    def place_item(self, item, position):
        try:
            item.position = position
            item.placed_bin = self.id
            self.items[item.pallet_id] = item
        except Exception as e:
            raise ValueError(f"Error placing item {item.pallet_id} in bin {self.id}: {e}")
        
    def find_available_spots(self, item_to_place):
        """
        Find available y-coordinates in the bin where the item can be placed.
        Returns a list of y-coordinates where the item can be placed.

        :param item_to_place: The item to be placed in the bin.
        :return: List of available y-coordinates.
        """
        if (item_to_place.placed_dimensions[0] > self.width or
            item_to_place.placed_dimensions[2] > self.depth):
            return []

        item_height = utils.get_adjusted_height(item_to_place.placed_dimensions[1], self.min_adjust_length)
        if item_height > self.height:
            return []
            
        available_y_coords = []

        sorted_items = sorted(self.items.values(), key=lambda item: item.position[1])

        # check if the item can be placed at the bottom of the bin
        if not sorted_items:
            if item_height <= self.height:
                available_y_coords.append(0)
            return available_y_coords
        else:
            first_item = sorted_items[0]
            if item_height <= first_item.position[1]:
                available_y_coords.append(0)

        # check gaps between items
        for i in range(len(sorted_items) - 1):
            current_item = sorted_items[i]
            next_item = sorted_items[i+1]
            
            current_item_top = current_item.position[1] + utils.get_adjusted_height(current_item.placed_dimensions[1], self.min_adjust_length)
            gap = next_item.position[1] - current_item_top
            
            if item_height <= gap:
                available_y_coords.append(current_item_top)

        # 3. check if the item can be placed at the top of the bin
        last_item = sorted_items[-1]
        last_item_top = last_item.position[1] + utils.get_adjusted_height(last_item.placed_dimensions[1], self.min_adjust_length)
        top_gap = self.height - last_item_top
        if item_height <= top_gap:
            available_y_coords.append(last_item_top)
            
        return available_y_coords

    def _intersects(self, item1, pos1, item2, pos2):
        """
        Check if two items intersect based on their positions and dimensions.
        Returns True if they intersect, False otherwise.
        """
        dim1 = item1.placed_dimensions
        dim2 = item2.placed_dimensions

        adjusted_h1 = utils.get_adjusted_height(dim1[1], self.min_adjust_length)
        adjusted_h2 = utils.get_adjusted_height(dim2[1], self.min_adjust_length)

        y_overlap = (pos1[1] < pos2[1] + adjusted_h2) and (pos1[1] + adjusted_h1 > pos2[1])

        return y_overlap

    def check_for_collision(self, new_item, new_position):
        """
        Check if the new item at the specified position will collide with any existing items in the bin.
        Returns True if a collision is detected, False otherwise.
        """
        for existing_item in self.items.values():
            if self._intersects(new_item, new_position, existing_item, existing_item.position):
                return True 
        return False 