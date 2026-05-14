import os
import random
from itertools import combinations
import json
from pathlib import Path
import torch
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights
from PIL import Image
import numpy as np
import shutil

def get_embedding(image_path, transform, model):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224), Image.Resampling.LANCZOS)  # Manual resize, no crop
    tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        embedding = model(tensor).squeeze().numpy().flatten()
    return embedding  # Raw, unnormalized

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def just_filename(filepath: str):
    files = str(filepath).split('/')
    return files[-1]

def cluster_avg_similarity(cluster_indices, embeddings):
    total = 0
    count = 0
    for i, j in combinations(cluster_indices, 2):
        total += cosine_sim(embeddings[i], embeddings[j])
        count += 1
    return float(total / count)  # Average of all pairs

def find_clusters(img_paths: list, embeddings: list, cluster_seed_index: int):
    target_size = 16
    cluster = {cluster_seed_index}  # Start with one image
    print(f'beginning work on cluster for seed image {just_filename(img_paths[cluster_seed_index])}')
    while len(cluster) < target_size:
        best_idx = None
        best_score = -1

        # Check every image not yet in cluster
        for i in range(len(embeddings)):
            if i in cluster:
                continue

            # How similar is this image to the whole cluster on average?
            score = sum(cosine_sim(embeddings[i], embeddings[j]) for j in cluster) / len(cluster)

            if score > best_score:
                best_score = score
                best_idx = i
        print(f'adding to current cluster for {just_filename(img_paths[cluster_seed_index])}: {just_filename(img_paths[best_idx])}')
        cluster.add(best_idx)  # Add the most similar one
    cluster_list = list(cluster)
    cluster_list.remove(cluster_seed_index)
    cluster_list.sort()
    cluster_list.insert(0, cluster_seed_index)
    cluster_paths = [img_paths[i] for i in cluster_list]
    avg = cluster_avg_similarity(cluster_list, embeddings)
    print(f'cluster set finished for {just_filename(cluster_paths[0])} with average similarity of {avg}')

    return cluster_paths, avg

def find_nearest_neighbors(img_paths: list, embeddings: list, cluster_seed_index: int):
    target_size = 16

    # Score every other image against the seed only
    scores = []
    print(f'calculating nearest neighbors to {just_filename(img_paths[cluster_seed_index])}..', end="")
    for i in range(len(embeddings)):
        if i == cluster_seed_index:
            continue
        score = cosine_sim(embeddings[cluster_seed_index], embeddings[i])
        print('.', end= "")
        scores.append((score, i))

    # Sort by similarity, take top 15
    scores.sort(reverse=True)
    neighbors = [i for _, i in scores[:target_size - 1]]
    neighbors.sort()
    neighbors.insert(0, cluster_seed_index)
    neighbors_paths = [img_paths[i] for i in neighbors]
    avg = cluster_avg_similarity(neighbors, embeddings)
    print(f'\nnearest neighbors for {just_filename(img_paths[cluster_seed_index])} done, avg similarity = {avg}')

    return neighbors_paths, avg

class SetCreator:
    def __init__(self, folder_name: str):
        self.folder_name = folder_name
        self.asset_dir = f'/home/jorge/Documents/jer_OSU/Portfolio/TileMatchingGame/assets'
        self.set_dir = Path(f'{self.asset_dir}/{folder_name}')

        # 1. Load model with updated weights API
        weights = ResNet50_Weights.DEFAULT
        self.model = models.resnet50(weights=weights)
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model.eval()

        # 2. Manual transform: no crop, just normalize
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.get_input()

    def get_input(self):
        response = input('enter 1 to calculate results, enter 2 to open results and split up files based on it, enter 3 to quit: ')
        if response == '1':
            self.calculate_results()
        elif response == '2':
            self.process_results()
        else:
            exit(0)

    def process_results(self):
        self.open_results_json()
        self.find_most_similar_set()
        self.copy_files()

    def copy_files(self):
        input('Proceed to moving files? press enter')
        root_folder = Path(f'{self.asset_dir}/new_levels')
        levels = list(root_folder.glob('level_*'))
        max_level = 0
        for level in levels:
            level_num = int(str(level).split('/')[-1].split('_')[1])
            max_level = max(max_level, level_num)
        destination_folder = f'{root_folder}/level_{max_level+1}'
        os.makedirs(destination_folder, exist_ok=True)

        with open(f'{destination_folder}/similarity.txt', 'w') as similarity_file:
            similarity_file.write(str(self.max_avg))

        print(f'moving files to {destination_folder}')

        for index, path in enumerate(self.max_set):
            shutil.move(src=path, dst=f'{destination_folder}/icon{index}.png')
            print(f'moved {path} to {destination_folder}/icon{index}.png')

        print('file moving done')
        self.get_input()


    def find_most_similar_set(self):
        self.max_avg = 0
        for key, value in self.results_json.items():
            key = key.strip('()')
            avg, info = key.split(',')
            avg = float(avg)
            if avg > self.max_avg:
                self.max_avg = avg
                self.max_set = value
                self.max_set_info = info
        print(f'the set with the highest similarity is {self.max_set_info} with a similarity of {self.max_avg}, consisting of \n{self.max_set}')

        for path in self.max_set:
            img = Image.open(path)
            img.show()
            img.close()

    def open_results_json(self):
        working_dir = Path.cwd()
        jsons = list(working_dir.glob('*.json'))
        selections = {}
        for num, path in enumerate(jsons):
            selections[num] = path
            print(num, ': ', just_filename(str(path)))
        num_choice = input('please enter the number of the filename of the json to open: ')
        filename = selections[int(num_choice)]

        try:
            with open(filename, 'r') as results:
                self.results_json = json.load(results)
            print(f'{filename} opened')
        except FileNotFoundError:
            print('file not found, try again')
            self.open_results_json()

    def calculate_results(self):
        print(f'starting process for {self.folder_name}')
        self.results_dict = {}
        self.load_image_paths_and_embeds()
        self.get_results()
        self.save_results()
        self.get_input()

    def load_image_paths_and_embeds(self):
        self.img_path_objs = list(self.set_dir.glob('*.png'))
        self.img_paths = [str(path) for path in self.img_path_objs]
        print('getting emebds...', end="")
        self.img_embeds = [get_embedding(path, self.transform, self.model) for path in self.img_paths]
        print('done')

    def get_results(self):
        for i in range(len(self.img_paths)):
            cluster_paths, cluster_avg = find_clusters(img_paths=self.img_paths, embeddings=self.img_embeds, cluster_seed_index=i)
            self.results_dict[cluster_avg, f'cluster {self.folder_name}/{just_filename(self.img_paths[i])}'] = cluster_paths

            neighbors_paths, neighbors_avg = find_nearest_neighbors(img_paths=self.img_paths, embeddings=self.img_embeds, cluster_seed_index=i)
            self.results_dict[neighbors_avg, f'nearest neighbors {self.folder_name}/{just_filename(self.img_paths[i])}'] = neighbors_paths

    def save_results(self):
        print(f"saving file 'results_{self.folder_name}_{len(self.img_paths)}_files.json'....", end="")
        json_dict = {f'{key[0],key[1]}':value for key, value in self.results_dict.items()}
        with open(f'results_{self.folder_name}_{len(self.img_paths)}_files.json', 'w') as save_file:
            json.dump(json_dict, save_file, indent=4)
        print(f'done.')




test = SetCreator('tiles_8')




# def compare_two_images(path1, path2):
#     emb1 = get_embedding(path1)
#     emb2 = get_embedding(path2)
#
#     # Cosine similarity (higher = more similar, range -1 to 1)
#     norm1 = np.linalg.norm(emb1)
#     norm2 = np.linalg.norm(emb2)
#     cosine_similarity = np.dot(emb1, emb2) / (norm1 * norm2)
#     #print(f"Cosine similarity: {cosine_similarity:.4f}")
#     return cosine_similarity
#
#     # # Raw L1 distance (lower = more similar)
#     # l1_distance = np.sum(np.abs(emb1 - emb2))
#     # print(f"L1 distance: {l1_distance:.4f}")
#
# def compare_two_random_images(tileset_folder: str, last_num_in_set: int):
#     random_image_nums = random.sample(range(0, last_num_in_set), 2)
#     random_image_paths = [f'{asset_dir}/{tileset_folder}/icon{num}.png' for num in random_image_nums]
#     print(random_image_nums)
#     return random_image_nums, compare_two_images(random_image_paths[0], random_image_paths[1])
#
# def compare_subset_of_16(tileset_folder: str, last_num_in_set: int):
#     total = 0
#     count = 0
#     random_image_nums = random.sample(range(0, last_num_in_set), 16)
#     random_image_paths = [f'{asset_dir}/{tileset_folder}/icon{num}.png' for num in random_image_nums]
#
#     # for path in random_image_paths:
#     #     img = Image.open(path)
#     #     img.show()
#
#
#     image_embeddings = [get_embedding(img_path) for img_path in random_image_paths]
#
#     for a, b in combinations(image_embeddings, 2):
#         # Normalize each vector first
#         a_norm = a / np.linalg.norm(a)
#         b_norm = b / np.linalg.norm(b)
#         similarity = np.dot(a_norm, b_norm)
#         total += (1 - similarity)
#         count += 1
#     if total / count > .6:
#         print('high value found: ', total / count)
#         for path in random_image_paths:
#             img = Image.open(path)
#             img.show()
#         input('press enter to continue')
#         return
#
#     return total / count  # Mean of (1 - cosine similarity)




# with open("results.json", "r") as json_file:
#     datadict = json.load(json_file)
#     avgs = list(datadict.keys())
#     avgs.sort(reverse=True)
#     best_cluster = datadict[avgs[0]][0]
#     print(best_cluster)



