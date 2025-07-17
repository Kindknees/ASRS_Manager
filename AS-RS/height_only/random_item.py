import random
import csv

def generate_random_item(num_items, min_width, max_width, min_height, max_height, min_depth, max_depth, min_weight, max_weight, can_rotate=1):
    items_data = []

    # CSV header
    items_data.append(['width', 'height', 'depth', 'weight', 'can_rotate', 'id'])

    for i in range(1, num_items + 1):
        width = random.randint(min_width, max_width)
        height = random.randint(min_height, max_height)
        depth = random.randint(min_depth, max_depth)
        weight = random.randint(min_weight, max_weight)
        if can_rotate == 1:
            rotation = 1
        elif can_rotate == 0:
            rotation = 0
        else:
            rotation = random.randint(0, 1)
        id = str(i)
        items_data.append([width, height, depth, weight, rotation, id])

    csv_file_name = 'items.csv'
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(items_data)

    print(f"successfully generate {num_items} items to '{csv_file_name}'。")

if __name__ == "__main__":
    config = {
        "num_items":1000,
        "min_width":30, 
        "max_width":60, 
        "min_height":20, 
        "max_height":50, 
        "min_depth":30, 
        "max_depth":60,
        "min_weight":1,
        "max_weight":20,
        "can_rotate":0
    }
    generate_random_item(**config)