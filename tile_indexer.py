import json
import os

def tile_indexer():
    tile_index = {}
    try:
        with os.scandir('assets') as dir:
            for entry in dir:
                if 'tiles_' in entry.name:
                    set_num = int(entry.name.strip('tiles_'))
                    with os.scandir(f'assets/tiles_{set_num}') as tile_dir:
                        for count, file in enumerate(tile_dir):
                            tile_num = count
                        tile_index[set_num] = tile_num
    except FileNotFoundError:
        exit(1)
    return tile_index, set_num

def index_tiles():
    title_index, set_num = tile_indexer()
    with open('tile_index.json', 'w') as file:
        json.dump(title_index, file, indent=4)
    print(f'... indexing complete, latest {max(set(title_index.keys()))}')

def get_tile_index() -> dict:
    with open('tile_index.json', 'r') as file:
        return json.load(fp=file)
