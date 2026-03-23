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
        self.border_radius = 10
        self.alignment = ft.Alignment.CENTER
        self.door = ft.Container(
            border_radius = 5,
            width=self.width, height=self.height,
            image=ft.DecorationImage(src='door.jpg'),
            offset = ft.Offset(0,0),
            animate_offset = ft.Animation(
                duration=700,
                curve=ft.AnimationCurve.EASE_IN
            ),
            on_click = self.door_open,
            data=[self.door_open, self.door_close, self.image_obj.src]
        )

        self.content = ft.Stack([self.image_obj, self.door])

    async def door_open(self):
        self.door.offset = ft.Offset(0,-1.1)
        self.door.update()

    async def door_close(self):
        #await asyncio.sleep(3)
        self.door.offset = ft.Offset(0, 0)
        self.door.update()

class TileGame(ft.Container):
    def __init__(self):
        super().__init__()
        self.target_width = self.target_height = 85
        self.master_grid = ft.GridView(
            width=(self.target_width*6) + 65,
            runs_count = 6,
            spacing=25)

        self.icon_numbers = random.sample(range(0,63), 18)
        self.icon_images = [ft.Image(f'/test_icon_set/icon{num}.png', width=self.target_width, height=self.target_height) for num in self.icon_numbers for _ in range(2)]
        for _ in range(5):
            random.shuffle(self.icon_images)
        self.tiles = [TileRevealer(image) for image in self.icon_images]
        self.define_handlers()
        self.click_1_cache = None
        self.click_1_close_func = None
        self.master_grid.controls = self.tiles
        self.content = self.master_grid

    def define_handlers(self):
        for tile in self.tiles:
            tile.door.on_click = self.click_handler

    async def click_handler(self, e):
        open_func, close_func, src_str = e.control.data

        if self.click_1_cache is None: # this is the first tile revealed
            await open_func()
            self.click_1_close_func = close_func
            self.click_1_cache = src_str
        else:                         # this is the second tile revealed
            await open_func()
            await asyncio.sleep(1.5)
            if self.click_1_cache == src_str:
                print('match found')
            else:
                await close_func()
                await self.click_1_close_func()
            self.click_1_cache = None
            self.click_1_close_func = None


def main(page: ft.Page):

    box = ft.Container(content=ft.Text("hello world", size=40), rotate=ft.Rotate(angle=0, alignment=ft.Alignment.CENTER), animate_rotation=ft.Animation(2100, ft.AnimationCurve.DECELERATE))

    # img = Image.open('assets/tmpv7rnyd_z.jpeg')
    # new_img = img.crop((20,0,148,128))
    #orig_width, orig_height = Image.open('assets/test_icon.png').size

    # target_width = target_height = 85
    #
    # image_reveals = []
    # for _ in range(36):
    #     icon_num = random.randint(0, 63)
    #     image = ft.Image(f'/test_icon_set/icon{icon_num}.png', width=target_width, height=target_height)
    #     print(image.src)
    #     image_reveals.append(TileRevealer(image))
    #
    # grid = ft.GridView(controls=image_reveals,
    #                    width=(target_width*6) + 65,
    #                    runs_count = 6,
    #                    spacing=25)

    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
        TileGame()
    ], alignment = ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))


ft.run(main, assets_dir='assets')