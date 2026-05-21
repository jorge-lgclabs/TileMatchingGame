import json
import random

import flet as ft

from app.classes import NewGame


def main(page: ft.Page):
    new_game = NewGame(page=page)

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
                            new_game.current_game
                        ],
                        alignment = ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        )


ft.run(main, assets_dir='assets')
