import random
import asyncio

import flet as ft

CELL_SIZE = 4
RECTANGLE_WIDTH = CELL_SIZE * 4

class FlipSwitch(ft.Button):
    flipped: bool = True
    def __init__(self, label, func_true, func_false):
        super().__init__(f'{label}')
        self.func_true = func_true
        self.func_false = func_false
        self.on_click = self.fire_and_switch

    def fire_and_switch(self):
        if self.flipped:
            self.func_true()
            self.flipped = False
        else:
            self.func_false()
            self.flipped = True

class Counter(ft.Row):
    num_value: int = 6.28
    increment_value: float = 1
    decrement_value: float = -1

    def __init__(self):
        super().__init__()
        self.plus_button = ft.Button("+", on_click=self.increment)
        self.minus_button = ft.Button("-", on_click=self.decrement)
        self.num_text = ft.Text(value=f'{self.num_value: .2f}')
        self.controls = [
            self.minus_button, self.num_text, self.plus_button

        ]
        self.spacing = 15
        self.alignment = ft.MainAxisAlignment.CENTER
        self.height = CELL_SIZE * 9
        self.width = self.height * 6

    def increment(self, e):
        self.num_value += self.increment_value
        self.num_text.value=f'{self.num_value: .2f}'
        self.num_text.update()

    def decrement(self, e):
        self.num_value += self.decrement_value
        self.num_text.value = f'{self.num_value: .2f}'
        self.num_text.update()

class RotateTester(ft.Container):
    def __init__(self, container_to_rotate):
        super().__init__()
        self.object = container_to_rotate
        self.breaker = True
        self.divide_factor = 360 * 2
        self.loop_button = ft.Button("Start loop", on_click=self.rotate_loop)
        self.content = ft.Column(controls=
                                 [
                                     container_to_rotate,
                                     self.loop_button
                                 ])

    def stop_loop(self):
        self.breaker = False

        self.object.animate_rotation.curve = ft.AnimationCurve.DECELERATE

        while self.object.animate_rotation.duration < 2000:
            self.object.animate_rotation.duration += 1
            self.object.rotate.angle += 6.28 / (self.divide_factor / 2)

        print(f'Final pos: {self.object.rotate.angle % 6.28}')
        self.loop_button.content = 'Start loop'
        self.loop_button.on_click = self.rotate_loop
        self.loop_button.color=None
        self.loop_button.update()


    async def rotate_loop(self):
        self.breaker = True
        self.loop_button.content = 'Stop loop'
        self.loop_button.color='red'
        self.loop_button.on_click = self.stop_loop
        self.loop_button.update()
        self.object.animate_rotation.curve = ft.AnimationCurve.EASE_IN
        self.object.animate_rotation.duration = 12
        radian_counter = self.object.rotate.angle + (6.28 / self.divide_factor)
        while self.breaker:
            self.object.rotate.angle = radian_counter
            self.object.update()
            radian_counter += (6.28 / self.divide_factor)
            print(self.object.rotate.angle)
            await asyncio.sleep((self.object.animate_rotation.duration/1000) / self.divide_factor)



def main(page: ft.Page):

    box = ft.Container(content=ft.Text("hello world", size=40), rotate=ft.Rotate(angle=0, alignment=ft.Alignment.CENTER), animate_rotation=ft.Animation(2100, ft.AnimationCurve.DECELERATE))

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
        RotateTester(container_to_rotate=box)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))


ft.run(main, assets_dir='assets')