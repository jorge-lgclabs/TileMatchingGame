import json
import random

import flet as ft

from app.classes import NewGame


def main(page: ft.Page):
    new_game = NewGame(page=page)
    new_game.current_game.match_count.count = 15 # for speeding up testing only

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    new_game.load_level()


ft.run(main, assets_dir='assets')
