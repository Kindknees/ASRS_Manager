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
    You can either provide a configuration file or specify the parameters directly.

    :param online_priority: A list of bin IDs representing the order in which to try placing items online.
    :param offline_priority: A list of bin IDs representing the order in which to try placing items when reorganizing items offline.
    :param bin_dimensions: A tuple representing the dimensions of the bins (width, height, depth, min_adjust_length).
    :param weight_limit: Weight limit for the bins.
    :param bins_for_pallets: A list of bin IDs designated for empty pallets. In optimal, these bins should be as close to the entrance as possible.
    :param num_pallets: Number of empty pallets to be initialized in the ASRS system.
    :param entrance_position: A tuple representing the entrance position of the ASRS system (x, y, z, bin_id).
    :param config_path: Optional path to a configuration

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
    def __init__(self, online_priority: list=None, 
                offline_priority: list=None, 
                bin_dimensions: tuple=None, 
                weight_limit: float=None, 
                bins_for_pallets: list=None, 
                num_pallets: int=None, 
                entrance_position: tuple=(0, 0, 0, 5),  # entrance position (x, y, z, bin_id)
                config_path=None):
        
        if config_path:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            self.online_priority = config['online_priority']
            self.offline_priority = config['offline_priority']
            bin_config = config['bin_config']
            self.bin_dimensions = (bin_config['width'], bin_config['height'], bin_config['depth'], bin_config['min_adjust_length'])
            self.bins_for_pallets = config['bins_for_pallets']
            self.num_pallets = config['num_pallets']
            self.entrance_position = config['entrance_position']

            try:
                self.weight_limit = bin_config['weight_limit']
            except:
                # print ("no weight limit is set")
                self.weight_limit = None
        else:
            self.online_priority = online_priority
            self.offline_priority = offline_priority
            self.bin_dimensions = bin_dimensions
            self.bins_for_pallets = bins_for_pallets
            self.num_pallets = num_pallets
            self.entrance_position = entrance_position
            self.weight_limit = weight_limit if weight_limit is not None else None
            if not self.online_priority or not self.offline_priority or not self.bin_dimensions or not self.bins_for_pallets or not self.num_pallets or not self.entrance_position:
                raise ValueError("If config_path is not provided, online_priority, offline_priority, bin_dimensions, bins_for_pallets, num_pallets and entrance_position must be specified.")

            try:
                self.weight_limit = weight_limit
            except:
                # print ("no weight limit is set")
                self.weight_limit = None

        # initialize bins
        self.bins = {}
        all_bins = set(self.online_priority + self.bins_for_pallets + self.offline_priority)
        for i in all_bins:
            self.bins[i] = Bin(id=i,
                               width=self.bin_dimensions[0], 
                               height=self.bin_dimensions[1], 
                               depth=self.bin_dimensions[2], 
                               min_adjust_length=self.bin_dimensions[3], 
                               weight_limit=self.weight_limit
                               )
        
        self._initialize_empty_pallets()

    def _initialize_empty_pallets(self):
        """ Initialize empty pallets in the ASRS system.
        This method creates empty pallets and places them in the bins designated for pallets.
        """
        bins_for_pallets = self.bins_for_pallets
        num_pallets = self.num_pallets

        # place the empty pallets into bins for empty pallets

        for i in range (1, num_pallets + 1, 1):    
            item = Item(
                    width=self.bin_dimensions[0]/2,
                    height=self.bin_dimensions[3],  # set as min_adjust_length
                    depth=self.bin_dimensions[2]/2,
                    rotation=False,
                    weight=None,
                    id=i,
                    empty=True
                    )
            item.placed_dimensions = (self.bin_dimensions[0]/2, self.bin_dimensions[3], self.bin_dimensions[2]/2)  # Set as min_adjust_length. This is for bin.can_place(item) to work correctly.
            for bin_id in bins_for_pallets:
                bin = self.bins[bin_id]
                if bin.can_place(item):
                    item.position = (0, bin.get_current_height(), 0)
                    item.placed_bin = bin_id
                    bin.place_item(item, item.position)
                    break
            
            if item.placed_bin is None:
                raise ValueError(f"Failed to place empty pallet {i} in any bin. Please check the bin configurations and available space.")

    def place_item_online(self, item_to_place: Item) -> bool:
        """
        Online operation to place an item into the ASRS system.

        :param item: Item object to be placed.
        :return: Boolean indicating whether the item was successfully placed.
        """
        placement_plan = self.plan_online_placement(item_to_place=item_to_place)
        for key, value in placement_plan.items():
            if value is None:
                # raise ValueError(f"Placement plan for item {item_to_place.id} is incomplete. Please check the item dimensions and bin configurations.")
                raise ValueError(f"Placement plan for item {item_to_place.id} is incomplete. Please check the item dimensions and bin configurations. Missing key: {key} with value: {value}")
            
        if placement_plan:
            placement_plan['item_object'] = item_to_place
            if self.execute_online_placement_plan(placement_plan, item_to_place):
                return placement_plan
        return None

    def plan_online_placement(self, item_to_place: Item) -> dict:
        """
        Plan the placement of an item in the ASRS system.
        This method returns a dictionary containing the plan.

        :param item: Item object to be placed.
        :return: A dictionary containing the placement plan: pallet_placed_bin, pallet_position, target_bin, target_position.
        If no suitable bin is found, it returns None.
        """
        best_pallet = None
        item_dimension = utils.get_optimal_dimension(item_to_place, self.bin_dimensions)


        item_to_place.placed_dimensions = item_dimension

        best_pallet = self.get_closest_pallet(self.entrance_position)
        if best_pallet is None:
            raise ValueError("No empty pallet found for item placement.")
        first_fit_plan = first_fit(item_to_place=item_to_place,
                                   all_bins=self.bins, 
                                   online_priority=self.online_priority, 
                                   bin_dimensions=self.bin_dimensions, 
                                   best_pallet=utils.ItemDictToItem(best_pallet))
        return first_fit_plan
    
    def execute_online_placement_plan(self, plan: dict, item_to_place: Item) -> bool:
        """
        Execute the placement plan for an item in the ASRS system.

        :param plan: A dictionary containing the placement plan.
        :return: Boolean indicating whether the placement was successful.
        """
        pallet_id = plan['pallet_id']
        original_pallet_placed_bin = plan['original_pallet_placed_bin']
        original_pallet_position = plan['original_pallet_position']
        target_bin = plan['target_bin']
        target_position = plan['target_position']

        pallet = self.bins[original_pallet_placed_bin].items[pallet_id]
        if not pallet or not pallet.empty:
            print(f"No valid pallet found for item placement.")
            return False

        del self.bins[original_pallet_placed_bin].items[pallet_id]

        pallet.width = item_to_place.placed_dimensions[0]
        pallet.height = item_to_place.placed_dimensions[1]
        pallet.depth = item_to_place.placed_dimensions[2]
        pallet.empty = False
        pallet.placed_dimensions = item_to_place.placed_dimensions
        pallet.position = target_position
        pallet.placed_bin = target_bin

        self.bins[target_bin].place_item(pallet, target_position)

        return True

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
                items_to_reorganize.extend(bin_obj.items.values())
        
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
            raise ValueError(f"Reorganization failed. The following items could not be placed: {[item.id for item in unplaced_items]}. Please check the bin configurations and available space.")
        else:
            result_dict = {}
            for bin in self.bins.values():
                for item in bin.items.values():
                    result_dict[f"{item.id}"] = {
                        'new_position': item.position,
                    }
            return result_dict
    
    def retrieve_item(self, item_id:str) -> Item:
        """
        Retrieve an item from the ASRS system.

        :param item_id: ID of the item to be retrieved.
        :return: Item object if found, None otherwise.
        """
        for bin_obj in self.bins.values():
            for item in bin_obj.items.values():
                if item.id == item_id:
                    return item.to_dict()
        return None

    def get_all_items(self) -> list[Item]:
        """
        Get all items in the ASRS system.

        :return: A list of Item objects representing all items in the system.
        """
        all_items = {}
        for bin_obj in self.bins.values():
            for item in bin_obj.items:
                if (not item.empty):
                    all_items[f"{item.id}"] = item.to_dict()
        return all_items
    
    def visualize_bins(self, bin_id:str, save_path=None):
        """
        Visualize the current state of one bin in the ASRS system.
        This method prints the IDs of items in each bin.
        """
        visualize_bin.plot_bin(self.bins, bin_id, save_path=save_path)

    def remove_item(self, item_id:str) -> tuple[bool, list]:
        """
        Iterate all the bins to find the item and remove the item from the ASRS system.

        :param item_id: ID of the item to be removed.
        :return: A dictionary containing the success status and the moved pallet item if applicable: {'success': bool, 'pallet': Item}. You can see the empty pallet's final status through the `pallet` key.
        """
        item = None
        flag = False
        for bin_obj in self.bins.values():
            if item_id in bin_obj.items:
                # check if the empty pallet can be placed in the bin designated for pallets
                for bin_id_for_pallet in self.bins_for_pallets: 
                    item = bin_obj.items[item_id]
                    item.reset(self.bin_dimensions[3])  # reset the item to be an empty pallet
                    if self.bins[bin_id_for_pallet].can_place(item):
                        self.bins[bin_id_for_pallet].place_item(item, (0, self.bins[bin_id_for_pallet].get_current_height(), 0))
                        bin_obj.items.pop(item_id)
                        flag = True # the item is successfully removed and the empty pallet is placed
                        break
                if flag:
                    break

        if flag is False:
            raise ValueError(f"Item {item_id} not found in any bin, or no suitable bin found for empty pallet.")
                        
        return_dict = {
            'success': True if flag else False,
            'pallet': item.to_dict() if item else None
        }
        return return_dict
    
    def get_closest_pallet(self, entrance_position=(0, 0, 0)) -> Item:
        """
        Get the closest empty pallet to the entrance of the ASRS system.
        This method returns the ID of the closest empty pallet to the entrance.

        :return: an item object representing the closest empty pallet to the entrance.
        """
        closest_pallet = None
        min_distance = float('inf')

        for bin_id in self.bins_for_pallets:
            if self.bins[bin_id].items:  # Check if the bin is not empty
                for item in self.bins[bin_id].items.values():
                    if item.empty:
                        distance = self._calculate_distance_to_entrance(item, entrance_position)
                        if distance < min_distance:
                            min_distance = distance
                            closest_pallet = item

        return closest_pallet.to_dict() if closest_pallet else None
    
    def _calculate_distance_to_entrance(self, item: Item, entrance_position=(0, 0, 0, 1)):
        """
        A util function for calculating the Manhattan distance between an item and the entrance.

        :param item: The item to calculate the distance for.
        :param entrance_position: The entrance position as a tuple (x, y, z, bin_id).
        :return: Manhattan distance between the item and the entrance.
        """
        item_position = item.position
        return self.bin_dimensions[0] * abs(int(item.placed_bin) - int(entrance_position[3])) + \
               abs(item_position[1] - entrance_position[1])