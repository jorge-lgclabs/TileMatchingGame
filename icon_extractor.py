# A tool for taking a sheet of icons and extracting them to separate files

from PIL import Image
import numpy as np
from scipy import ndimage

def extract_icons(icon_sheet_path, output_size, threshold):
    img = Image.open(icon_sheet_path).convert('RGBA')
    data = np.array(img)

    # Create mask: non-white pixels
    white_mask = (data[:, :, 0] > threshold) & (data[:, :, 1] > threshold) & (data[:, :, 2] > threshold)

    visible_mask = Image.fromarray((~white_mask * 255).astype(np.uint8))
    visible_mask.show()

    # Invert: icons are non-white
    from scipy import ndimage
    labeled, num_features = ndimage.label(~white_mask)

    icons = []
    for i in range(1, num_features + 1):
        # Get bounding box of each connected component
        rows, cols = np.where(labeled == i)
        if len(rows) == 0:
            continue

        min_row, max_row = rows.min(), rows.max()
        min_col, max_col = cols.min(), cols.max()

        # Crop
        crop = img.crop((min_col, min_row, max_col + 1, max_row + 1))

        # Center in square
        square = Image.new('RGBA', (output_size, output_size), (255, 255, 255, 0))
        # Paste centered...

        square.show()

        input('stop here')

        icons.append(square)

def slice_icons(icon_sheet_path, row_begin, row_size, column_begin, column_size, column_gap):
    img = Image.open(icon_sheet_path)
    count = 0
    top_left_x = column_begin
    top_left_y = row_begin
    bottom_right_x = top_left_x + column_size
    bottom_right_y = top_left_y + row_size
    for column in range(8):
        for row in range(8):
            #print(f'{top_left_x=}, {top_left_y=}, {bottom_right_x=}, {bottom_right_y=}')
            icon = img.crop((
                top_left_x, top_left_y,
                bottom_right_x, bottom_right_y
            ))
            #icon.show()
            #input('wait here')
            icon.save(f'assets/test_icon_set/icon{count}.png')
            count += 1
            top_left_x += column_gap + column_size
            bottom_right_x += column_gap + column_size
        top_left_x = column_begin
        bottom_right_x = top_left_x + column_size
        top_left_y += row_size
        bottom_right_y += row_size





slice_icons(icon_sheet_path='assets/servo386_httpss.mj.runwjtgaTbSie0_httpss.mj.run6XyyZMmUbJk_http_ff688dae-4254-4c06-8d75-c20981017abd.png', row_begin=16, row_size=222, column_begin=52, column_size=222, column_gap=44)