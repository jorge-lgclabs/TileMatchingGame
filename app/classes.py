import flet as ft
import asyncio
import random
import uuid
import time

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
        self.opacity = 0
        self.update()
        await asyncio.sleep(.5)
        self.value = str(self.count)
        self.opacity = 1
        self.update()

class TileRevealer(ft.Container):
    def __init__(self, image_to_reveal, debug_mode=False):
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
        if debug_mode:
            self.content = ft.Stack([self.image_obj])
        else:
            self.content = ft.Stack([self.image_obj, self.door])


    async def door_open(self):
        self.door.offset = ft.Offset(0,-1.1)
        self.door.update()

    async def door_close(self):
        #await asyncio.sleep(3)
        self.door.offset = ft.Offset(0, 0)
        self.door.update()

class TileGame(ft.Container):
    def __init__(self, image_paths, state_change_func, scorekeeper: dict, debug_mode=False):
        super().__init__()
        self.state_change = state_change_func
        self.scorekeeper = scorekeeper
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
        self.icon_images = self.create_double_and_shuffle_images(image_paths)
        self.tiles = [TileRevealer(image, debug_mode) for image in self.icon_images]
        self.define_handlers()
        self.click_1_cache = None
        self.click_2_cache = None
        self.master_grid.controls = self.tiles
        self.content = ft.Column([self.text_row, self.master_grid])

    def define_handlers(self):
        for tile in self.tiles:
            tile.door.on_click = self.click_handler

    def create_double_and_shuffle_images(self, image_paths):
        result = [
            ft.Image(path, width=self.target_width, height=self.target_height) for path
            in image_paths for _ in range(2)]
        for _ in range(5):
            random.shuffle(result)
        return result

    def end_game(self):
        self.scorekeeper['current_level_complete'] = True
        self.state_change()

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
                self.scorekeeper['current_match_count'] = self.match_count.count
                self.scorekeeper['current_click_count'] = self.click_count.count
                self.state_change()
                if self.match_count.count == 18:
                    await asyncio.sleep(.5)
                    await self.win_screen()
            else:
                await asyncio.sleep(.5)
                await close_func()
                await self.click_1_cache.data[1]()
                await self.click_count.increment()
                self.scorekeeper['current_click_count'] = self.click_count.count
                self.state_change()
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
        play_again_button = ft.Button('Next Level', color='blue', on_click=self.end_game)

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

class NewGame:
    def __init__(self, page: ft.Page, max_level=52):
        self.page = page
        self.session_id = uuid.uuid1()
        self.timestamp = self.session_id.time
        self.max_level = max_level

        self.scorekeeper = {
            'current_level' : 1,
            'score' : 0,
            'current_click_count' : 0,
            'current_match_count' : 0,
            'current_level_complete' : False
        }

        self.current_level = self.scorekeeper['current_level']
        self.level_label = f'Current Level: {self.current_level}'
        self.score = self.scorekeeper['score']
        self.current_click_count = self.scorekeeper['current_click_count']
        self.current_match_count = self.scorekeeper['current_match_count']
        self.current_level_complete = self.scorekeeper['current_level_complete']
        self.current_game = None
        self.create_level()

    def create_level(self):
        images = [f'/new_levels/level_{self.current_level}/icon{i}.png' for i in range(18)]
        self.current_game = TileGame(image_paths=images, state_change_func=self.state_change, scorekeeper=self.scorekeeper)

    def next_level(self):
        self.current_level_complete = self.scorekeeper['current_level_complete'] = False
        self.current_level = self.scorekeeper['current_level'] = self.current_level + 1
        self.level_label = f'Current Level: {self.current_level}'
        self.create_level()
        self.load_level()

    def load_level(self):
        self.page.overlay.clear()
        self.page.clean()
        self.page.add(
            ft.Column(controls=[
                            ft.Text(self.level_label),
                            self.current_game
                            ],
                        alignment = ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        )
        self.page.update()

    def read_scorekeeper(self):
        self.current_level = self.scorekeeper['current_level']
        self.score = self.scorekeeper['score']
        self.current_click_count = self.scorekeeper['current_click_count']
        self.current_match_count = self.scorekeeper['current_match_count']
        self.current_level_complete = self.scorekeeper['current_level_complete']

    def state_change(self):
        self.read_scorekeeper()
        print(f'{self.current_level=}\n{self.score=}\n{self.current_click_count=}\n{self.current_match_count=}\n{self.current_level_complete=}')
        if self.current_level_complete:
            self.next_level()
