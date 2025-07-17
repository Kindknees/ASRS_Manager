class Item:
    def __init__(self, width, height, depth, rotation, weight, id):
        self.width = width
        self.height = height
        self.depth = depth
        self.rotation = rotation    # 1 if item is allowed to rotate, 0 otherwise
        self.position = None  # (x, y, z) coordinates when placed
        self.placed_bin = None
        self.weight = weight
        self.id = id
        self.placed_dimensions = None  # Store final dimensions after rotation
