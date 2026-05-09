
import json

import flet as ft


def main(page: ft.Page):


    with open('tile_index.json', 'r') as file:
        tile_index = json.load(file)

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
        TileGame(tile_index=tile_index)
    ], alignment = ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))


ft.run(main, assets_dir='assets')
