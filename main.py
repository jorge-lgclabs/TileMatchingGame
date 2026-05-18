import json
import random

import flet as ft
from app.classes import TileGame

def main(page: ft.Page):
    def create_game():
        level = random.randrange(1, 54)
        images = [f'/new_levels/level_{level}/icon{i}.png' for i in range(18)]

        return TileGame(image_paths=images, reload_func=create_game)

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
                            create_game()
                        ],
                        alignment = ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        )


ft.run(main, assets_dir='assets')
