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
        self.counter = Counter()
        self.flip_switch = FlipSwitch(
            label='Rotate',
            func_true=lambda : self.change_angle(self.counter.num_value),
            func_false=lambda : self.change_angle(0)
        )
        self.loop_button = ft.Button("Start loop", on_click=self.rotate_loop)
        self.content = ft.Column(controls=
                                 [
                                     container_to_rotate,
                                     self.flip_switch,
                                     self.counter,
                                     self.loop_button
                                 ])


    def change_angle(self, deg):
        self.object.rotate.angle = deg

    def stop_loop(self):

        #self.change_angle(0)
        #self.object.animate_rotation = ft.Animation(20, ft.AnimationCurve.DECELERATE)
        self.breaker = False
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
        loop_bumper = 10000000
        radian_counter = self.object.rotate.angle + 6.28
        while self.breaker:
            #self.counter.increment(e=None)
            if self.counter.num_value > loop_bumper:
                self.counter.num_value = 300
                #loop_bumper = random.randint(700, 1200)
            self.object.rotate.angle = radian_counter
            #self.object.animate_rotation = ft.Animation(loop_bumper - 250, ft.AnimationCurve.DECELERATE)
            self.object.update()
            radian_counter += 6.28
            await asyncio.sleep(self.object.animate_rotation.duration/1000)



def main(page: ft.Page):

    box = ft.Container(content=ft.Text("hello world", size=40), rotate=ft.Rotate(angle=0, alignment=ft.Alignment.CENTER), animate_rotation=ft.Animation(210, ft.AnimationCurve.DECELERATE))

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
        RotateTester(container_to_rotate=box)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))


ft.run(main, assets_dir='assets')