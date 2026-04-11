import copy
import io
import os
import random
import shutil
import time

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
        self.copy_originals_into_directories(self.depth)
        self.create_escalated_icons(self.depth)
        tile_indexer.index_tiles()

    def get_directory(self, level):
        folder_name = f'assets/tiles_{self.set_num}/level_{level}'
        if not os.path.exists(folder_name):
            os.mkdir(path=folder_name)

        return folder_name

    def get_num_of_copies(self, level):
        return 9 * (8 - level)

    def get_num_of_set_icons(self, level):
        with open('tile_index.json', 'r') as file:
            tile_index = json.load(file)
        return tile_index[str(self.set_num)][level - 1]

    def icons_sampled_for_level(self, level):
        num_of_copies_to_make = self.get_num_of_copies(level)
        num_of_set_icons = self.get_num_of_set_icons(level - 1)
        return random.sample(range(num_of_set_icons+1), num_of_copies_to_make)

    def copy_originals_into_directories(self, level):
        icon_numbers_to_copy = self.icons_sampled_for_level(level)
        new_level_directory = self.get_directory(level)
        new_icon_num = 0
        for icon_number in icon_numbers_to_copy:
            new_icon_path = f'{new_level_directory}/icon{new_icon_num}.png'
            if not os.path.exists(new_icon_path):
                shutil.copy(f'assets/tiles_{self.set_num}/icon{icon_number}.png', new_icon_path)
                print(f'{new_icon_path} saved')
            new_icon_num += 1

    def create_escalated_icons(self, level):
        num_of_original_icons = self.get_num_of_copies(level)
        level_dir = self.get_directory(level)
        original_icon_num = 0
        alternate_prompt = None
        while original_icon_num < num_of_original_icons:
            original_icon_path = f'{level_dir}/icon{original_icon_num}.png'
            escalated_icon_path = f'{level_dir}/icon{original_icon_num+54}.png'
            if os.path.exists(escalated_icon_path):
                print(f'{escalated_icon_path} already exists')
                original_icon_num += 1
                # Image.open(original_icon_path).show()
                # Image.open(escalated_icon_path).show()
                # input('hold')
                continue

            escalated_icon = self.generate_escalated_icon(original_icon_path, alternate_prompt=alternate_prompt)
            alternate_prompt = None
            old = Image.open(original_icon_path)
            old_width, old_height = old.size
            old.show()
            img_bytes = Image.open(io.BytesIO(escalated_icon.read()))
            img_bytes.thumbnail((old_width, old_height))
            img_bytes.show()

            response = input('If youd like to try again with a new prompt, enter "change", otherwise press enter: ')
            if response == 'change':
                alternate_prompt = input('enter your new prompt: ')
                continue

            img_bytes.save(escalated_icon_path)
            print(f'escalated icon {escalated_icon_path} saved')
            original_icon_num += 1
            #input('Press Enter to goto next')

    def generate_escalated_icon(self, original_icon_path, alternate_prompt=None):
        input_image = open(original_icon_path, 'rb')
        if alternate_prompt is None:
            prompt = "take this image and alter at least 8 distinct features of it, such as it's color, position, shape, overall form or even the entire art style. at least 8 changes."
        else:
            prompt = alternate_prompt
        input_dict = {
            'images' : [input_image],
            'prompt' : prompt,
            'aspect_ratio' : '1:1'
        }
        print('connecting to Replicate...', end="")
        output = replicate.run(
            "prunaai/p-image-edit",
            input=input_dict
        )
        print(' done')
        print(output.url)

        return output














test = IconEscalator(1, 2)



