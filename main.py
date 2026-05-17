import json
import flet as ft
from app.classes import TileGame

def main(page: ft.Page):



    images = [f'/new_levels/level_5/icon{i}.png' for i in range(16)]

    level_test = TileGame(image_paths=images)

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
                            level_test
                        ],
                        alignment = ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        )


ft.run(main, assets_dir='assets')
