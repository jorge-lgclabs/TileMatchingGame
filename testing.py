import random
import asyncio
from PIL import Image
import flet as ft
from PIL.ImageChops import offset

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
            self.object.animate_rotation.duration += 4
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
        self.object.animate_rotation.duration = 1
        radian_counter = self.object.rotate.angle + (6.28 / self.divide_factor)
        while self.breaker:
            self.object.rotate.angle = radian_counter
            self.object.update()
            radian_counter += (6.28 / self.divide_factor)
            print(self.object.rotate.angle)
            await asyncio.sleep((self.object.animate_rotation.duration/1000) / self.divide_factor)

class TileRevealer(ft.Container):
    def __init__(self, image_to_reveal):
        super().__init__()
        self.image_obj = image_to_reveal
        self.width = self.image_obj.width
        self.height = self.image_obj.height
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.border_radius = 5
        self.alignment = ft.Alignment.CENTER
        self.door = ft.Container(
            width=self.width, height=self.height,
            image=ft.DecorationImage(src='door.jpg'),
            offset = ft.Offset(0,0),
            animate_offset = ft.Animation(
                duration=700,
                curve=ft.AnimationCurve.EASE_IN
            ),
            on_click = self.start_reveal
        )

        self.content = ft.Stack([self.image_obj, self.door])

    async def start_reveal(self):
        self.door.offset = ft.Offset(0,-1)
        self.door.update()
        await asyncio.sleep(3)
        self.door.offset = ft.Offset(0,0)
        self.door.update()


def main(page: ft.Page):

    box = ft.Container(content=ft.Text("hello world", size=40), rotate=ft.Rotate(angle=0, alignment=ft.Alignment.CENTER), animate_rotation=ft.Animation(2100, ft.AnimationCurve.DECELERATE))

    # img = Image.open('assets/tmpv7rnyd_z.jpeg')
    # new_img = img.crop((20,0,148,128))

    orig_width, orig_height = Image.open('assets/test_icon.png').size
    image = ft.Image('test_icon.png', width=orig_width, height=orig_height)
    container_test = ft.Container(content=image, width=orig_width, height=orig_height)

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
        TileRevealer(image)
    ], alignment = ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))


ft.run(main, assets_dir='assets')