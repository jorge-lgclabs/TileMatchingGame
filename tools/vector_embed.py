import os
import flet as ft
import random
from app.classes import TileGame
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
    return f'{files[-2]}/{files[-1]}'

def cluster_avg_similarity(cluster_indices, embeddings):
    total = 0
    count = 0
    for i, j in combinations(cluster_indices, 2):
        total += cosine_sim(embeddings[i], embeddings[j])
        count += 1
    return float(total / count)  # Average of all pairs

def find_clusters(img_paths: list, embeddings: list, cluster_seed_index: int):
    target_size = 18
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
    target_size = 18

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

def show_images(img_path_sets, avgs, infos):
    def level(page: ft.Page):
        cluster_set, neighbor_set = img_path_sets
        cluster_highest_avg, neighbor_highest_avg = avgs
        cluster_info, neighbor_info = infos
        cluster_show = TileGame(image_paths=cluster_set, debug_mode=True)
        neighbor_show = TileGame(image_paths=neighbor_set, debug_mode=True)

        cluster_show.text_row.controls[0] = ft.Text(cluster_highest_avg)
        cluster_show.text_row.controls[1] = ft.Text(cluster_info, size=12)
        neighbor_show.text_row.controls[0] = ft.Text(neighbor_highest_avg)
        neighbor_show.text_row.controls[1]= ft.Text(neighbor_info, size=12)

        spacer = ft.Container(width=15, height=465, bgcolor='grey')

        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(ft.Row(controls=[
            cluster_show, spacer, neighbor_show
        ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

    ft.run(level, assets_dir='assets')


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
        select_index = input('Proceed to moving files? enter 0 for cluster, 1 for neighbor: ')
        select_index = int(select_index)
        root_folder = Path(f'{self.asset_dir}/new_levels')
        levels = list(root_folder.glob('level_*'))
        max_level = 0
        for level in levels:
            level_num = int(str(level).split('/')[-1].split('_')[1])
            max_level = max(max_level, level_num)
        destination_folder = f'{root_folder}/level_{max_level+1}'
        os.makedirs(destination_folder, exist_ok=True)

        with open(f'{destination_folder}/similarity.txt', 'w') as similarity_file:
            similarity_file.write(str(self.max_avgs[select_index]))

        print(f'moving files to {destination_folder}')

        for index, path in enumerate(self.max_sets[select_index]):
            shutil.move(src=path, dst=f'{destination_folder}/icon{index}.png')
            print(f'moved {path} to {destination_folder}/icon{index}.png')

        print('file moving done')
        self.get_input()

    def find_most_similar_set(self):
        self.max_avgs = [0,0]
        self.max_sets = [[],[]]
        self.max_set_infos = ["", ""]
        for key, value in self.results_json.items():
            key = key.strip('()')
            avg, info = key.split(',')
            avg = float(avg)
            if 'cluster' in info and  avg > self.max_avgs[0]:
                self.max_avgs[0] = avg
                self.max_sets[0] = value
                self.max_set_infos[0] = info
            elif 'neighbor' in info and avg > self.max_avgs[1]:
                self.max_avgs[1] = avg
                self.max_sets[1] = value
                self.max_set_infos[1] = info
            else:
                continue

        print(f'the nearest neighbor set with the highest similarity is {self.max_set_infos[1]} with a similarity of {self.max_avgs[1]}, consisting of \n{self.max_sets[1]}')
        print(f'the cluster set with the highest similarity is {self.max_set_infos[0]} with a similarity of {self.max_avgs[0]}, consisting of \n{self.max_sets[0]}')

        show_images(self.max_sets, self.max_avgs, self.max_set_infos)

    def open_results_json(self):
        working_dir = Path.cwd()
        jsons = sorted(working_dir.glob('*.json'), key=lambda p: os.path.getmtime(p), reverse=True)
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
        self.img_path_objs = list(self.set_dir.rglob('*.png'))
        self.img_paths = [str(path) for path in self.img_path_objs]
        print('getting emebds...', end="")
        self.img_embeds = [get_embedding(path, self.transform, self.model) for path in self.img_paths]
        print('done')

    def get_results(self):
        for i in range(len(self.img_paths)):
            cluster_paths, cluster_avg = find_clusters(img_paths=self.img_paths, embeddings=self.img_embeds, cluster_seed_index=i)
            self.results_dict[cluster_avg, f'cluster {just_filename(self.img_paths[i])}'] = cluster_paths

            neighbors_paths, neighbors_avg = find_nearest_neighbors(img_paths=self.img_paths, embeddings=self.img_embeds, cluster_seed_index=i)
            self.results_dict[neighbors_avg, f'nearest neighbors {just_filename(self.img_paths[i])}'] = neighbors_paths

    def save_results(self):
        print(f"saving file 'results_{self.folder_name}_{len(self.img_paths)}_files.json'....", end="")
        json_dict = {f'{key[0],key[1]}':value for key, value in self.results_dict.items()}
        with open(f'results_{self.folder_name}_{len(self.img_paths)}_files.json', 'w') as save_file:
            json.dump(json_dict, save_file, indent=4)
        print(f'done.')



test = SetCreator('redo7')



class DeleteDuplicates:
    def __init__(self):

        self.asset_dir = f'/home/jorge/Documents/jer_OSU/Portfolio/TileMatchingGame/assets/tiles_test'


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
        self.compare_all(self.asset_dir)

    def compare_all(self, folder: str):
        folder_path = Path(folder)
        pngs = [str(p) for p in sorted(folder_path.glob('*.png'))]
        embeds = {p : get_embedding(p, self.transform, self.model) for p in pngs}
        to_delete = set()
        for path1, path2 in combinations(embeds.keys(), 2):
            emb1 = embeds[path1]
            emb2 = embeds[path2]
            score = self.compare_two_images(emb1,emb2)
            if score >= .98:
                print(score, path1, path2)
                print(f'{path2} set to delete')
                to_delete.add(path2)

        for path in to_delete:
            print(f'deleting {path}')
            os.remove(path)
            print('done')


    def compare_two_images(self, emb1, emb2):

        # Cosine similarity (higher = more similar, range -1 to 1)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        cosine_similarity = np.dot(emb1, emb2) / (norm1 * norm2)
        # print(f"Cosine similarity: {cosine_similarity:.4f}")
        return cosine_similarity


# dup = DeleteDuplicates()



