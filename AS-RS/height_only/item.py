class Item:
    """
    Represents an item to be placed in a bin.
    Attributes:
        width: Width of the item.
        height: Height of the item.
        depth: Depth of the item.   
        rotation: 1 if item is allowed to rotate, 0 otherwise.
        weight: Weight of the item.
        id: Unique identifier for the item. Here it is used to identify the pallet in the system, not item ID.
        empty: True if it is an empty pallet.
        position: Item's placed position. (x, y, z) coordinates when placed.
        placed_bin: ID of the bin where the item is placed.
        placed_dimensions: Store final dimensions after rotation.
    """
    def __init__(self, width, height, depth, rotation, weight, id, empty):
        self.width = width
        self.height = height
        self.depth = depth
        self.rotation = rotation    # 1 if item is allowed to rotate, 0 otherwise
        self.empty = empty  # True if it is an empty pallet.
        self.weight = weight
        self.id = id    # Item ID
        self.position = None  # Item's placed position. (x, y, z) coordinates when placed
        self.placed_bin = None  # ID of the bin where the item is placed
        self.placed_dimensions = (width, height, depth)  # Store final dimensions after rotation

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

