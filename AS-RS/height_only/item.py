class Item:
    def __init__(self, width, height, depth, rotation, weight, id):
        self.width = width
        self.height = height
        self.depth = depth
        self.rotation = rotation    # 1 if item is allowed to rotate, 0 otherwise
        self.position = None  # (x, y, z) coordinates when placed
        self.placed_bin = None  # ID of the bin where the item is placed
        self.weight = weight
        self.id = id    # Item ID
        self.placed_dimensions = None  # Store final dimensions after rotation
