import json
import os

def tile_indexer():
    set_folders_and_subfolders = get_folders_and_sub_folders()
    current_index = get_tile_index()
    print(set_folders_and_subfolders)
    print(current_index)

    for set_num, subfolder_nums in set_folders_and_subfolders:
        if str(set_num) in current_index.keys():
            current_set_index = current_index[str(set_num)]
            number_of_subfolders = len(subfolder_nums)
            if number_of_subfolders == len(current_set_index) - 1:
                print(f'tile set {set_num} and all its subfolders are already indexed')
                continue
            else:
                for index, level in enumerate(subfolder_nums):
                    if index + 1 >= len(current_set_index):
                        current_set_index.append(get_number_of_icons(set_num, level))
                        print(f'tile set {set_num}/level {level} added to index')
        else:
            current_index[str(set_num)] = []
            current_set_index = current_index[str(set_num)]
            current_set_index.append(get_number_of_icons(set_num, 1))
            print(f'new tile set {set_num} added to index')
            for level in subfolder_nums:
                current_set_index.append(get_number_of_icons(set_num, level))
                print(f'tile set {set_num}/level {level} added to index')

    return current_index

def get_number_of_icons(set_num, level):
    folder_to_index = f'assets/tiles_{set_num}'
    if level > 1:
        folder_to_index += f'/level_{level}'

    count = 0
    with os.scandir(folder_to_index) as dir:
        for entry in dir:
            if 'icon' in entry.name:
                count += 1

    return count


def get_folders_and_sub_folders():
    set_folder_and_subfolders = []
    try:
        with os.scandir('assets') as dir:
            for entry in dir:
                if 'tiles_' in entry.name:
                    set_num = int(entry.name.strip('tiles_'))
                    set_folder_and_subfolders.append((set_num, []))
            set_folder_and_subfolders.sort(key=lambda x: x[0])

        for set_num, subfolder_nums in set_folder_and_subfolders:
            with os.scandir(f'assets/tiles_{set_num}') as tile_dir:
                for entry in tile_dir:
                    if 'level_' in entry.name:
                        level_num = int(entry.name.strip('level_'))
                        subfolder_nums.append(level_num)

    except FileNotFoundError:
        exit(1)
    return set_folder_and_subfolders

def index_tiles():
    title_index = tile_indexer()
    with open('tile_index.json', 'w') as file:
        json.dump(title_index, file, indent=4)
    print(f'... indexing complete')

def get_tile_index() -> dict:
    with open('tile_index.json', 'r') as file:
        return json.load(fp=file)

index_tiles()