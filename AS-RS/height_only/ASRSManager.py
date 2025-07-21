import yaml
from bin import Bin
from item import Item
from algorithms.first_fit import first_fit
from algorithms.best_fit import best_fit
from visualization import visualization

class ASRSManager:
    """
    ASRSManager handles the operations of the Automated Storage and Retrieval System (ASRS).
    It manages the placement of items online and the reorganization of items offline.
    config_path: Path to the configuration file containing bin dimensions and priorities (.yaml file).
    The configuration file should have the following structure:
    
    .. code-block:: yaml

        # bin limitations
        bin_dimensions:
          width: 100
          height: 100
          depth: 100
          min_adjust_length: 5

        # online operation phase bin usage priority.
        # This is a list of integers representing bin IDs in the order they should be tried.
        online_priority: [10, 9, 11, 8, 12, 7, 13, 6, 14, 5, 15, 4, 16, 3, 17, 2, 18, 1, 19]

        # offline operation phase bin usage priority.
        # This is a list of integers representing bin IDs in the order they should be tried.
        offline_priority: [19, 1, 18, 2, 17, 3, 16, 4, 15, 5, 14, 6, 13, 7, 12, 8, 11, 9, 10]
    """
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        self.online_priority = config['online_priority']
        self.offline_priority = config['offline_priority']
        b_dims = config['bin_dimensions']
        self.bin_dimensions = (b_dims['width'], b_dims['height'], b_dims['depth'], b_dims['min_adjust_length'])
        
        num_all_bins = len(self.online_priority)

        self.bins = {}
        for i in range(1, num_all_bins + 1):
            self.bins[i] = Bin(id=i, width=b_dims['width'], height=b_dims['height'], depth=b_dims['depth'], min_adjust_length=b_dims['min_adjust_length'])

    def place_item_online(self, item: Item):
        """
        Online operation to place an item into the ASRS system.
        :param item: Item object to be placed.
        :return: Boolean indicating whether the item was successfully placed.
        """
        bin_id = first_fit(all_bins=self.bins, 
                           item_to_place=item, 
                           bin_dimensions=self.bin_dimensions, 
                           online_priority=self.online_priority)

        if bin_id is not None:
            return True
        else:
            return False

    def reorganize_offline(self):
        """
        Offline operation to reorganize items in the ASRS system.
        This method collects all items from the bins, clears the bins,
        and then applies the Best Fit algorithm to reorganize them.
        :return: Boolean indicating whether the reorganization was successful.
        """

        items_to_reorganize = []
        for bin_obj in self.bins.values():
            if bin_obj.items:
                items_to_reorganize.extend(bin_obj.items)
        
        if not items_to_reorganize:
            return False

        # 2. reset all bins
        for bin_obj in self.bins.values():
            bin_obj.reset()
    
        # 3. do the Best Fit algorithm
        unplaced_items = best_fit(items=items_to_reorganize, 
                                   all_bins=self.bins, 
                                   bin_dimensions=self.bin_dimensions, 
                                   offline_priority=self.offline_priority)

        if unplaced_items:
            return True
        else:
            return False
    
    def retrieve_item(self, item_id:int):
        """
        Retrieve an item from the ASRS system.
        :param item_id: ID of the item to be retrieved.
        :return: Item object if found, None otherwise.
        """
        for bin_obj in self.bins.values():
            for item in bin_obj.items:
                if item.id == item_id:
                    return item
        return None
    
    def visualize_bins(self, bin_id:int, save_path=None):
        """
        Visualize the current state of the bins in the ASRS system.
        This method prints the IDs of items in each bin.
        """
        visualization.plot_bin(self.bins, bin_id, save_path=save_path)