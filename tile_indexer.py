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
    return tile_index

with open('tile_index.json', 'w') as file:
    json.dump(tile_indexer(), file, indent=4)
