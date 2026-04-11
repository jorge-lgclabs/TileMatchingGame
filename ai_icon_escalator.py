import copy
import os

from PIL import Image
import numpy as np
import tile_indexer
import json
import replicate
from dotenv import load_dotenv
import requests
from requests import HTTPError

load_dotenv()  # Loads variables from .env into the environment


class IconEscalator:
    def __init__(self, set_num, depth=2):
        self.set_num = set_num
        self.depth = max(2, min(depth, 7))
        self.create_directories()


    def create_directories(self):
        x = 2
        while x <= self.depth:
            folder_name = f'assets/tiles_{self.set_num}/level_{x}'
            if not os.path.exists(folder_name):
                os.mkdir(path=folder_name)
            x += 1

    def get_num_of_copies(self, level):
        return 9 * (8 - level)

    def copy_originals_into_directories(self, level):
        pass














test = IconEscalator(1, 2)

