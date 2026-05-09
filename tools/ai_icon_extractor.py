import copy
import os
from time import sleep

from PIL import Image
import numpy as np
import tile_indexer
import json
import replicate
from dotenv import load_dotenv
import requests
from requests import HTTPError

load_dotenv()  # Loads variables from .env into the environment

class IconSheet:
    def __init__(self, image_path, max_size):
        self.image = open(image_path, 'rb')
        self.max_size = max_size
        self.pil_image = Image.open(image_path).convert('RGBA')
        self.image_array = self.get_image_array()
        self.file_urls = self.load_masks_urls()
        self.error_urls = []
        self.file_list = self.get_masks_files()
        self.padding = 15

    def extract_icons(self):
        save_folder = self.create_next_folder()
        icon_number = 0
        for file in self.file_list:
            cropped = self.mask_crop(file)
            if not cropped:
                continue
            print(f'saving {save_folder}/icon{icon_number}.png... ', end="")
            cropped.save(fp=f'{save_folder}/icon{icon_number}.png')
            print('done')
            icon_number += 1
            # if 'mask_17' in file:
            #     input('check 17')
        tile_indexer.index_tiles()

    def create_next_folder(self):
        tile_index = tile_indexer.get_tile_index()
        next_folder_num = max(int(num) for num in tile_index.keys()) + 1
        folder_name = f'assets/tiles_{next_folder_num}'
        if not os.path.exists(folder_name):
            os.mkdir(path=folder_name)
        return folder_name

    def mask_crop(self, mask_file):
        mask = Image.open(mask_file)
        mask_array = np.array(mask)
        max_x, min_x, max_y, min_y = self.get_crop_coords(mask_array)
        if max_x - min_x > self.max_size:
            print(f'icon rejected for being {max_x - min_x}px')
        return self.apply_mask(mask_array, max_x, min_x, max_y, min_y)

    def apply_mask(self, mask_array, max_x, min_x, max_y, min_y):
        cropped_mask_array = mask_array[min_y:max_y, min_x:max_x]
        if len(cropped_mask_array) > self.max_size:
            return False
        # old_cropped = self.image_array[min_y:max_y, min_x:max_x, :] for comparison purposes during testing
        cropped_image_array = self.image_array[min_y:max_y, min_x:max_x, :].copy()
        # old_crop = Image.fromarray(old_cropped)
        for line_index, line in enumerate(cropped_mask_array):
            for pixel_index, pixel in enumerate(line):
                if pixel == 0:
                    cropped_image_array[line_index][pixel_index] = np.full(4, 255, dtype=np.uint8)

        cropped_and_masked = Image.fromarray(cropped_image_array)
        # old_crop.show()
        # cropped_and_masked.show()
        return cropped_and_masked

    def get_crop_coords(self, mask_array):
        min_x = len(mask_array[0])
        min_y = len(mask_array)
        max_x = 0
        max_y = 0
        for line_num, line in enumerate(mask_array):
            for pixel_num, pixel in enumerate(line):
                if pixel > 0:
                    if pixel_num < min_x:
                        min_x = pixel_num
                    if pixel_num > max_x:
                        max_x = pixel_num
                    if line_num < min_y:
                        min_y = line_num
                    if line_num > max_y:
                        max_y = line_num
                    #print(pixel_num, line_num, pixel)
        min_y -= self.padding
        min_x -= self.padding
        max_y += self.padding
        max_x += self.padding

        max_x, min_x, max_y, min_y = self.get_crop_square(max_x, min_x, max_y, min_y, mask_array)

        return max_x, min_x, max_y, min_y

    def get_crop_square(self, max_x, min_x, max_y, min_y, mask_array):
        if (max_x - min_x) > (max_y - min_y):
            longest_side = (max_x - min_x)
            difference = longest_side - (max_y - min_y)
            short = difference // 2
            long = difference - short
            max_y += short
            min_y -= long
        else:
            longest_side = (max_y - min_y)
            difference = longest_side - (max_x - min_x)
            short = difference // 2
            long = difference - short
            max_x += short
            min_x -= long

        if min_x < 0:
            max_x += (min_x * -1)
            min_x = 0
        if max_x >= len(mask_array[0]):
            min_x -= (max_x - (len(mask_array[0]))) + 1
            max_x = len(mask_array[0]) - 1
        if min_y < 0:
            max_y += (min_y * -1)
            min_y = 0
        if max_y >= len(mask_array):
            min_y -= (max_y - (len(mask_array))) + 1
            max_y = len(mask_array) - 1

        return max_x, min_x, max_y, min_y

    def get_image_array(self):
        return np.array(self.pil_image)

    def generate_masks(self):
        print('getting mask output from sam-2 API...')
        output = replicate.run("meta/sam-2:fe97b453a6455861e3bac769b441ca1f1086110da7466dbb65cf1eecfd60dc83",
            input={
            "image": self.image,
            "points_per_side": 32,
            "pred_iou_thresh": 0.88,
            "stability_score_thresh": 0.95,
            "use_m2m": True
        })
        print('mask list received')
        list_output = [file_object.url for file_object in output['individual_masks']]
        with open('work/masks.json', 'w') as file:
            json.dump(list_output, file)

    def load_masks_urls(self):
        if not os.path.exists('work/masks.json'):
            self.generate_masks()
        with open('work/masks.json', 'r') as file:
            file_urls = json.load(fp=file)

        return file_urls

    def get_masks_files(self):
        files_list = []
        for url in self.file_urls:
            filesplit = url.split(sep='/mask_')
            filename = f'mask_{filesplit[1]}'
            if not os.path.exists(f'work/{filename}'):
                try:
                    print(f'downloading: {url}', end=" ")
                    response = requests.get(url=url)
                    response.raise_for_status()
                    print('...done')
                    with open(f'work/{filename}', 'wb') as downloaded_file:
                        downloaded_file.write(response.content)
                    print(f'file saved {filename}')
                    files_list.append(f'work/{filename}')
                except HTTPError:
                    print(f'error downloading {url}')
                    self.error_urls.append(url)
            else:
                files_list.append(f'work/{filename}')

        return files_list


while True:
    filepath = input('Please enter filename or "stop": ')
    if filepath == 'stop':
        exit(0)
    max_size = int(input('What should be the biggest icon allowed (300, 400, ect): '))
    sheet = IconSheet(image_path=f'assets/{filepath}', max_size=max_size)
    sheet.extract_icons()
