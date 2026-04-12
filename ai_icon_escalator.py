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
        if 2 > depth > 7:
            print('enter a number between 2 and 7')
            exit(1)
        self.set_num = set_num
        self.new_level = depth

        # how many icons are in the previous level
        self.num_of_icons_in_prev_level = self.get_how_many_icons_in_prev_level(self.new_level)

        # how many icons from the previous level will be copied into the new level
        # and then have an 'escalated' version created of them
        self.num_to_copy_from_prev_level = self.get_how_many_copies(self.new_level)

        # the list of which randomly selected icons from the previous level will be copied into the new level
        self.icons_from_prev_level_to_copy = random.sample(range(self.num_of_icons_in_prev_level), self.num_to_copy_from_prev_level)

        # get the path to (and in the process create) the directory for the new level
        self.new_level_directory = self.get_directory(self.new_level)

        print(f'Creating level {self.new_level} for tile set {self.set_num}',
              f'\nWill be copying {self.num_to_copy_from_prev_level} tiles from the {self.num_of_icons_in_prev_level} present in level {self.new_level - 1}',
              f'\nThe specific tiles to be copied are: {self.icons_from_prev_level_to_copy}')
        input('Press enter to continue')

        self.copy_originals_into_directories(self.new_level)
        print(f'Copying originals from level {self.new_level - 1} into new level folder complete')
        self.create_escalated_icons(self.new_level)
        tile_indexer.index_tiles()

    def get_directory(self, level):
        folder_name = f'assets/tiles_{self.set_num}/level_{level}'
        if not os.path.exists(folder_name):
            os.mkdir(path=folder_name)

        return folder_name

    def get_how_many_copies(self, level):
        return 9 * (8 - level)

    def get_how_many_icons_in_prev_level(self, level):
        with open('tile_index.json', 'r') as file:
            tile_index = json.load(file)

        return tile_index[str(self.set_num)][level - 2]

    def copy_originals_into_directories(self, level):
        previous_level_directory = f'assets/tiles_{self.set_num}'
        if level > 2:
            previous_level_directory += f'/level_{level-1}'

        print(f'Copying {self.num_to_copy_from_prev_level} icons from {previous_level_directory} to {self.new_level_directory}')
        new_icon_num = 0
        for icon_number in self.icons_from_prev_level_to_copy:
            new_icon_path = f'{self.new_level_directory}/icon{new_icon_num}.png'
            if not os.path.exists(new_icon_path):
                shutil.copy(f'{previous_level_directory}/icon{icon_number}.png', new_icon_path)
                print(f'{new_icon_path} saved')
            else:
                print(f'{new_icon_path} already exists, skipping...')
            new_icon_num += 1

    def create_escalated_icons(self, level):
        old_icon_num = 0
        alternate_prompt = None
        while old_icon_num < self.num_to_copy_from_prev_level:
            old_icon_path = f'{self.new_level_directory}/icon{old_icon_num}.png'
            escalated_icon_path = f'{self.new_level_directory}/icon{old_icon_num+self.num_to_copy_from_prev_level}.png'
            if os.path.exists(escalated_icon_path):
                print(f'{escalated_icon_path} already exists')
                old_icon_num += 1
                # Image.open(original_icon_path).show()
                # Image.open(escalated_icon_path).show()
                # input('hold')
                continue

            escalated_icon = self.generate_escalated_icon(old_icon_path, alternate_prompt=alternate_prompt)
            alternate_prompt = None
            old = Image.open(old_icon_path)
            old_width, old_height = old.size
            old.show()
            img_bytes = Image.open(io.BytesIO(escalated_icon.read()))
            img_bytes.thumbnail((old_width, old_height))
            img_bytes.show()

            response = input('If youd like to try again with a new prompt, enter "change", otherwise press enter: ')
            if response == 'change':
                alternate_prompt = input('enter your new prompt: ')
                old.close()
                img_bytes.close()
                continue

            img_bytes.save(escalated_icon_path)
            print(f'escalated icon {escalated_icon_path} saved')
            img_bytes.close()
            old.close()
            old_icon_num += 1

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














test = IconEscalator(1, 3)



