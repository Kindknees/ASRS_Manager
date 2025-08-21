import yaml
from bin import Bin
from item import Item
from algorithms.first_fit import first_fit
from algorithms.best_fit import best_fit
from visualization import visualize_bin
import utils
from pydantic import validate_call
from typing import Optional

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

        online_priority: [4, 6, 3, 7, 2, 8, 1, 9]
        offline_priority: [1, 9, 2, 8, 3, 7, 4, 6]
        bins_for_pallets: [5]
        num_pallets: 40
        entrance_position: [0, 100, 0, 5]

        bin_config:
        width: 50
        height: 230
        depth: 50
        min_adjust_length: 5
        weight_limit: 17
    """
    @validate_call
    def __init__(self, online_priority: list=None, 
                offline_priority: list=None, 
                bin_dimensions: tuple=None, 
                weight_limit: float=None, 
                bins_for_pallets: list=None, 
                num_pallets: int=None, 
                entrance_position: tuple=None,  # entrance position (x, y, z, bin_id)
                config_path=None):
        
        # if config path is given
        if config_path:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            self.online_priority = [str(i) for i in config['online_priority']]
            self.offline_priority = [str(i) for i in config['offline_priority']]
            bin_config = config['bin_config']
            self.bin_dimensions = (bin_config['width'], bin_config['height'], bin_config['depth'], bin_config['min_adjust_length'])
            self.bins_for_pallets = [str(i) for i in config['bins_for_pallets']]
            self.num_pallets = config['num_pallets']
            self.entrance_position = config['entrance_position']

            try:
                self.weight_limit = bin_config['weight_limit']
            except:
                # print ("no weight limit is set")
                self.weight_limit = None
        # if config path is not given, then read the data form all parameters
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
            self.bins[f"{i}"] = Bin(id=i,
                               width=self.bin_dimensions[0], 
                               height=self.bin_dimensions[1], 
                               depth=self.bin_dimensions[2], 
                               min_adjust_length=self.bin_dimensions[3], 
                               weight_limit=self.weight_limit
                               )
        
        self._initialize_empty_pallets()

    @validate_call
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
                    pallet_id=f"{i}",
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

    @validate_call
    def place_item_online(self, item_to_place: Item) -> dict:
        """
        Online operation to place an item into the ASRS system.

        :param item: Item object to be placed.
        :return: A dictionary containing the result of the placement execution.
        """
        # check if the item has a unique cargo ID
        retrieve_result = None
        try:
            placed_cargo_id = item_to_place.cargo_id
            if placed_cargo_id:
                retrieve_result = self.retrieve_item(cargo_id=placed_cargo_id)
        except:
            pass

        if retrieve_result:
            raise ValueError(f"Item with cargo ID {placed_cargo_id} already exists in the system. Please use a unique cargo ID.")

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

        # placement_plan = self.plan_online_placement(item_to_place=item_to_place)
        for key, value in first_fit_plan.items():
            if value is None:
                raise ValueError(f"Placement plan for item {item_to_place.pallet_id} is incomplete. Please check the item dimensions and bin configurations. Missing key: {key} with value: {value}")

        if first_fit_plan:
            first_fit_plan['item_object'] = item_to_place
            execute_result = self.execute_online_placement_plan(first_fit_plan, item_to_place)
            if execute_result["success"]:
                # item_to_place.placed_bin = first_fit_plan['target_bin']
                # item_to_place.position = first_fit_plan['target_position']
                return execute_result
        raise ValueError("Failed to place item for an unknown reason.")
    
    @validate_call
    def execute_online_placement_plan(self, plan: dict, item_to_place: Item) -> dict:
        """
        Execute the placement plan for an item in the ASRS system.

        :param plan: A dictionary containing the placement plan.
        :param item_to_place: Item object to be placed.
        :return: A dictionary containing the result of the placement execution.
        """
        pallet_id = plan['pallet_id']
        original_pallet_placed_bin = plan['original_pallet_placed_bin']
        original_pallet_position = plan['original_pallet_position']
        target_bin = plan['target_bin']
        target_position = plan['target_position']

        pallet = self.bins[original_pallet_placed_bin].items[pallet_id]
        if not pallet or not pallet.empty:
            raise ValueError(f"No valid pallet found for item placement.")

        del self.bins[original_pallet_placed_bin].items[pallet_id]

        pallet.width = item_to_place.placed_dimensions[0]
        pallet.height = item_to_place.placed_dimensions[1]
        pallet.depth = item_to_place.placed_dimensions[2]
        pallet.weight = item_to_place.weight
        pallet.empty = False
        pallet.placed_dimensions = item_to_place.placed_dimensions
        pallet.position = target_position
        pallet.placed_bin = target_bin
        pallet.cargo_id = item_to_place.cargo_id

        self.bins[target_bin].place_item(pallet, target_position)

        return_dict = {
            "success": True,
            "original_pallet_placed_bin": original_pallet_placed_bin,
            "original_pallet_position": original_pallet_position,
            "target_bin": target_bin,
            "target_position": target_position,
            "item": pallet.to_dict(),
            "pallet_id": pallet_id
        }

        return return_dict

    def reorganize_offline(self) -> dict:
        """
        Offline operation to reorganize items in the ASRS system.
        This method collects all items from the bins, clears the bins,
        and then applies the Best Fit algorithm to reorganize them.

        :return: A dictionary containing the result of the reorganization.
        """

        items_to_reorganize = []
        for bin_obj in self.bins.values():
            if bin_obj.items:
                for item in bin_obj.items.values():
                    if not item.empty:
                        items_to_reorganize.append(item)
        
        # if not items_to_reorganize:
        #     return False

        # reset all bins
        all_bins_id = set(self.online_priority + self.offline_priority)    # get all bins that are used for cargo in the system
        for bin_id in all_bins_id:
            self.bins[bin_id].reset()

        unplaced_items = best_fit(items=items_to_reorganize, 
                                   all_bins=self.bins, 
                                   bin_dimensions=self.bin_dimensions, 
                                   offline_priority=self.offline_priority)

        if unplaced_items:
            print (unplaced_items)
            raise ValueError(f"Reorganization failed. The following items could not be placed: {[item.pallet_id for item in unplaced_items]}. Please check the bin configurations and available space.")
        else:
            result_dict = {}
            for bin in self.bins.values():
                for item in bin.items.values():
                    result_dict[f"{item.pallet_id}"] = {
                        'new_position': item.position,
                        'new_bin': item.placed_bin,
                    }
            return result_dict
    
    @validate_call
    def retrieve_item(self, pallet_id: Optional[str]=None, cargo_id: Optional[str]=None) -> dict:
        """
        Retrieve an item from the ASRS system. You can specify the pallet ID or cargo ID to retrieve the item. However, you can only send one of them.

        :param pallet_id: Pallet ID of the item to be retrieved.
        :param cargo_id: Cargo ID of the item to be retrieved.
        :return: A dictionary containing the item details if found, None otherwise.
        """
        if not pallet_id and not cargo_id:
            raise ValueError("Either pallet_id or cargo_id must be provided to retrieve an item.")
        if pallet_id and cargo_id:
            raise ValueError("Only one of pallet_id or cargo_id can be provided to retrieve an item.")

        for bin_obj in self.bins.values():
            for item in bin_obj.items.values():
                if item.pallet_id == pallet_id and pallet_id:
                    return item.to_dict()
                if item.cargo_id == cargo_id and cargo_id:
                    return item.to_dict()
        raise ValueError(f"Item with {'cargo_id' if cargo_id else 'pallet_id'} {cargo_id or pallet_id} not found in any bin.")

    def get_all_items(self) -> list[Item]:
        """
        Get all items in the ASRS system.

        :return: A list of Item objects representing all items in the system.
        """
        all_items = {}
        for bin_obj in self.bins.values():
            for item in bin_obj.items.values():
                if (not item.empty):
                    all_items[f"{item.pallet_id}"] = item.to_dict()
        return all_items
    
    @validate_call
    def visualize_bins(self, bin_id:str, save_path=None):
        """
        Visualize the current state of one bin in the ASRS system.
        This method prints the IDs of items in each bin.
        """
        visualize_bin.plot_bin(self.bins, bin_id, save_path=save_path)

    @validate_call
    def remove_item(self, pallet_id: Optional[str]=None, cargo_id: Optional[str]=None) -> dict:
        """
        Iterate all the bins to find the item and remove the item from the ASRS system.

        :param item_id: ID of the item to be removed.
        :return: A dictionary containing the success status and the moved pallet item if applicable: {'success': bool, 'item': Item}. You can see the empty pallet's final status through the `item` key.
        """
        if not pallet_id and not cargo_id:
            raise ValueError("Either pallet_id or cargo_id must be provided to remove an item.")
        if (pallet_id is not None) and (cargo_id is not None):
            raise ValueError("Only one of pallet_id or cargo_id can be provided to remove an item.")

        item_to_remove = None
        original_bin_obj = None
        original_pallet_id = None

        for bin_obj in self.bins.values():
            found = False
            if pallet_id and pallet_id in bin_obj.items:
                item_to_remove = bin_obj.items[pallet_id]
                original_pallet_id = pallet_id
                original_bin_obj = bin_obj
                found = True
            elif cargo_id:
                for item in bin_obj.items.values():
                    if item.cargo_id == cargo_id:
                        item_to_remove = item
                        original_pallet_id = item.pallet_id
                        original_bin_obj = bin_obj
                        found = True
                        break
            if found:
                break

        if item_to_remove is None:
            raise ValueError(f"Item with {'cargo_id' if cargo_id else 'pallet_id'} {cargo_id or pallet_id} not found in any bin.")
        
        item_to_remove.reset(self.bin_dimensions[3])

        # move the empty pallet to the closest bin designated for pallets
        min_distance = float('inf')
        closest_bin = None
        best_position = float('inf')
        for bin_id in self.bins_for_pallets:
            bin_obj = self.bins[bin_id]
            available_spots = bin_obj.find_available_spots(item_to_place=item_to_remove)
            # print (f"Available spots in bin {bin_id}: {available_spots}")
            for position in available_spots:
                distance = abs(position - self.entrance_position[1]) + abs(int(bin_id) - int(self.entrance_position[3])) * self.bin_dimensions[0]
                if distance < min_distance:
                    min_distance = distance
                    closest_bin = bin_obj
                    best_position = position

        if closest_bin is None or best_position == float('inf'):
            raise ValueError("Something went wrong! No suitable bin found for the empty pallet.")
        
        item_to_remove.position = (0, best_position, 0)
        item_to_remove.placed_bin = closest_bin.id
        closest_bin.place_item(item_to_remove, (0, best_position, 0))
        del original_bin_obj.items[original_pallet_id]
        return_dict = {
            'success': True,
            'item': item_to_remove.to_dict()
        }
        return return_dict
    
    @validate_call
    def get_closest_pallet(self, entrance_position=(0, 0, 0)) -> dict:
        """
        Get the closest empty pallet to the entrance of the ASRS system.
        This method returns the ID of the closest empty pallet to the entrance.

        :return: a dictionary containing the item details representing the closest empty pallet to the entrance.
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
        if closest_pallet is None:
            raise ValueError("No empty pallet found in the ASRS system.")
        return closest_pallet.to_dict()
    
    @validate_call
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
    
    @validate_call
    def batch_place_items(self, items: list[Item]) -> dict:
        """
        Place a batch of items in the ASRS system. These items' all information (including placed bin, position, etc.) should be provided in advanced.
        This method is for resuming the system if any accident happens.

        :param items: A list of Item objects to be placed.
        :return: A dictionary containing the placement results for each item.
        """
        results = {}
        for item in items:
            placed_bin = item.placed_bin
            if placed_bin not in self.bins :
                raise ValueError (f"Bin {placed_bin} not found for item {item.pallet_id}. Please check the bin configurations.")
            if placed_bin is None:
                raise ValueError (f"Item {item.pallet_id} does not have a placed bin. Please check the item configurations.")
            
            target_bin = self.bins[placed_bin]
            if target_bin.check_for_collision(item, item.position):
                raise ValueError(f"Item {item.pallet_id} at position {item.position} collides with existing items in bin {placed_bin}. Please check the item configurations.")
            
            self.bins[placed_bin].place_item(item, item.position)
            results[item.pallet_id] = {
                'placed_bin': placed_bin if placed_bin else None,
                'position': item.position,
                'placed_dimensions': item.placed_dimensions
            }
        return results
    
    @validate_call
    def exp_reorganize_offline(self) -> dict:
        """
        This is an experiment method to verify the effectiveness of the reorganization process.
        Offline operation to reorganize items in the ASRS system.
        This method collects all items from the bins, clears the bins,
        and then applies the Best Fit algorithm (exp_best_fit, ascending height priority) to reorganize them.

        :return: A dictionary containing the result of the reorganization.
        """
        from experiment.exp_best_fit import exp_best_fit
        items_to_reorganize = []
        for bin_obj in self.bins.values():
            if bin_obj.items:
                for item in bin_obj.items.values():
                    if not item.empty:
                        items_to_reorganize.append(item)
        
        # if not items_to_reorganize:
        #     return False

        # reset all bins
        all_bins_id = set(self.online_priority + self.offline_priority)    # get all bins that are used for cargo in the system
        for bin_id in all_bins_id:
            self.bins[bin_id].reset()

        unplaced_items = exp_best_fit(items=items_to_reorganize, 
                                   all_bins=self.bins, 
                                   bin_dimensions=self.bin_dimensions, 
                                   offline_priority=self.offline_priority)

        if unplaced_items:
            print (unplaced_items)
            raise ValueError(f"Reorganization failed. The following items could not be placed: {[item.pallet_id for item in unplaced_items]}. Please check the bin configurations and available space.")
        else:
            result_dict = {}
            for bin in self.bins.values():
                for item in bin.items.values():
                    result_dict[f"{item.pallet_id}"] = {
                        'new_position': item.position,
                        'new_bin': item.placed_bin,
                    }
            return result_dict
        