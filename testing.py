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

class TextCounter(ft.Text):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.count = 0
        self.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_IN_EXPO)
        self.value = str(self.count)

    async def increment(self):
        self.count += 1
        self.opacity = 0
        self.update()
        await asyncio.sleep(.5)
        self.value = str(self.count)
        self.opacity = 1
        self.update()

    async def decrement(self):
        self.count -= 1
        self.value = str(self.count)
        self.update()


class TileGame(ft.Container):
    def __init__(self, set_num, tiles_num):
        super().__init__()

        self.target_width = self.target_height = 85
        self.grid_width = (self.target_width * 6) + 65
        self.width = self.grid_width
        self.master_grid = ft.GridView(
            width=self.grid_width,
            runs_count = 6,
            spacing=25)

        self.click_count = TextCounter(size=self.target_width * .5)
        self.match_count = TextCounter(size=self.target_width * .5)

        self.text_row = ft.Row(width=self.grid_width, alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[
            ft.Container(self.click_count, width=self.target_width, alignment=ft.Alignment.CENTER),
            ft.Container(self.match_count, width=self.target_width, alignment=ft.Alignment.CENTER)
        ])

        self.icon_numbers = random.sample(range(0,tiles_num), 18)
        self.icon_images = [ft.Image(f'/tiles_{set_num}/icon{num}.png', width=self.target_width, height=self.target_height) for num in self.icon_numbers for _ in range(2)]
        for _ in range(5):
            random.shuffle(self.icon_images)
        self.tiles = [TileRevealer(image) for image in self.icon_images]
        self.define_handlers()
        self.click_1_cache = None
        self.click_2_cache = None
        self.master_grid.controls = self.tiles
        self.content = ft.Column([self.text_row, self.master_grid])

    def define_handlers(self):
        for tile in self.tiles:
            tile.door.on_click = self.click_handler

    async def click_handler(self, e):
        open_func, close_func, src_str = e.control.data

        if self.click_1_cache is None:                                      # this is the first tile revealed
            await open_func()
            self.click_1_cache = e.control
        elif (self.click_1_cache is not None) and (self.click_1_cache != e.control)  and (self.click_2_cache is None): # this is the second tile revealed
            self.click_2_cache = e.control
            await open_func()
            await asyncio.sleep(1)
            if self.click_1_cache.data[2] == src_str:
                await self.special_increment()
                if self.match_count.count == 18:
                    await asyncio.sleep(.5)
                    await self.win_screen()
            else:
                await asyncio.sleep(.5)
                await close_func()
                await self.click_1_cache.data[1]()
                await self.click_count.increment()
            self.click_1_cache = None
            self.click_2_cache = None
        else:
            return

    async def win_screen(self):
        win_screen = ft.Container(width=self.grid_width, height = self.target_width * 3,
                                  bgcolor=ft.Colors.with_opacity(.7, ft.Colors.GREY_700), border_radius=self.target_width,
                                  animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN), opacity=0,
                                  alignment=ft.Alignment.CENTER)
        win_text = ft.Text('You win!', text_align=ft.TextAlign.CENTER, size=self.target_width)
        play_again_button = ft.Button('Play again', color='blue', on_click=self.reload_game)

        win_screen.content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                     alignment=ft.MainAxisAlignment.CENTER, controls=[
                                        win_text, play_again_button
                                        ])

        full_page_container = ft.Container(alignment=ft.Alignment.CENTER, content=win_screen, width=self.page.width,
                                           height=self.page.height)
        self.page.overlay.append(full_page_container)
        self.page.update()
        win_screen.opacity = 1
        self.page.update()

    async def reload_game(self):
        self.page.controls.clear()
        self.page.overlay.clear()
        self.page.add(TileGame())

    async def special_increment(self):
        self.click_count.count += 1
        self.match_count.count += 1
        self.click_count.opacity = 0
        self.match_count.opacity = 0
        self.text_row.update()
        await asyncio.sleep(.5)
        self.click_count.value = str(self.click_count.count)
        self.match_count.value = str(self.match_count.count)
        self.click_count.opacity = 1
        self.match_count.opacity = 1
        self.text_row.update()


def main(page: ft.Page):

    box = ft.Container(content=ft.Text("hello world", size=40), rotate=ft.Rotate(angle=0, alignment=ft.Alignment.CENTER), animate_rotation=ft.Animation(2100, ft.AnimationCurve.DECELERATE))


    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Column(controls=[
        TileGame(set_num=2, tiles_num=64)
    ], alignment = ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))


ft.run(main, assets_dir='assets')