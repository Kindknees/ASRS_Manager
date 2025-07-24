import yaml
from bin import Bin
from item import Item
from algorithms.first_fit import first_fit
from algorithms.best_fit import best_fit
from visualization import visualize_bin
import utils

class ASRSManager:
    """
    ASRSManager handles the operations of the Automated Storage and Retrieval System (ASRS).
    It manages the placement of items online and the reorganization of items offline.

    :param config_path: Path to the configuration file containing bin dimensions and priorities (.yaml file).
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
    def __init__(self, online_priority=None, offline_priority=None, bin_dimensions=None, weight_limit=None, config_path=None):
        if config_path:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            self.online_priority = config['online_priority']
            self.offline_priority = config['offline_priority']
            bin_config = config['bin_config']
            self.bin_dimensions = (bin_config['width'], bin_config['height'], bin_config['depth'], bin_config['min_adjust_length'])

            try:
                weight_limit = bin_config['weight_limit']
                self.weight_limit = weight_limit
            except:
                print ("no weight limit is set")
        else:
            self.online_priority = online_priority
            self.offline_priority = offline_priority
            self.bin_dimensions = bin_dimensions
            self.weight_limit = weight_limit if weight_limit is not None else None
            if not self.online_priority or not self.offline_priority or not self.bin_dimensions:
                raise ValueError("If config_path is not provided, online_priority, offline_priority, and bin_dimensions must be specified.")

        try:
            weight_limit = bin_config['weight_limit']
        except:
            print ("no weight limit is set")

        self.bins = {}
        for i in range(1, len(self.online_priority) + 1):
            self.bins[i] = Bin(id=i,
                               width=self.bin_dimensions[0], 
                               height=self.bin_dimensions[1], 
                               depth=self.bin_dimensions[2], 
                               min_adjust_length=self.bin_dimensions[3], 
                               weight_limit=self.weight_limit
                               )

    def place_item_online(self, item: Item) -> bool:
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

    def reorganize_offline(self) -> bool:
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
            print (unplaced_items)
            return False
        else:
            return True
    
    def retrieve_item(self, item_id:str) -> Item:
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
    
    def visualize_bins(self, bin_id:str, save_path=None):
        """
        Visualize the current state of one bin in the ASRS system.
        This method prints the IDs of items in each bin.
        """
        visualize_bin.plot_bin(self.bins, bin_id, save_path=save_path)

    def remove_item(self, item_id:str) -> tuple[bool, list]:
        """
        Remove an item from the ASRS system. Besides removing the item, it also moves down the items above it in the bin.

        :param item_id: ID of the item to be removed.
        :return: Boolean indicating whether the item was successfully removed, moved_items: a list containing item objects that were moved down.
        """
        for bin_obj in self.bins.values():
            item_to_remove_index = -1
            for i, item in enumerate(bin_obj.items):
                if item.id == item_id:
                    item_to_remove_index = i
                    break
            
            if item_to_remove_index != -1:
                removed_item = bin_obj.items[item_to_remove_index]
                
                adjusted_height_to_remove = utils.get_adjusted_height(
                    removed_item.placed_dimensions[1], 
                    bin_obj.min_adjust_length
                )

                bin_obj.items.pop(item_to_remove_index)
                
                # move down the items above item_to_move
                moved_items = []
                for i in range(item_to_remove_index, len(bin_obj.items)):
                    later_item = bin_obj.items[i]
                    x, y, z = later_item.position
                    later_item.position = (x, y - adjusted_height_to_remove, z)
                    moved_items.append(later_item)
                    
                return True, moved_items

        return False, None