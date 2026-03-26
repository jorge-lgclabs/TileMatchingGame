# A tool for taking a sheet of icons and extracting them to separate files

from PIL import Image
import numpy as np
from scipy import ndimage

def extract_icons(icon_sheet_path, output_size, threshold):
    img = Image.open(icon_sheet_path).convert('RGBA')
    data = np.array(img)

    # Create mask: non-white pixels
    white_mask = (data[:, :, 0] > threshold) & (data[:, :, 1] > threshold) & (data[:, :, 2] > threshold)

    #visible_mask = Image.fromarray((~white_mask * 255).astype(np.uint8))
    #visible_mask.show()

    column_coords = []
    row_coords = []

    top_pixel_row = 0

    bottom_pixel_row = 1

    while bottom_pixel_row < len(white_mask):
        old_top = top_pixel_row
        left_most_pixel_column = 0
        right_most_pixel_column = 1
        for row_index in range(top_pixel_row, len(white_mask)): # start from the top-most row
            for pixel_index in range(left_most_pixel_column, len(white_mask[row_index])): # go pixel-by-pixel from the left-most column to right
                if white_mask[row_index][pixel_index] == False:  # if there is any black pixel (from an icon)
                    top_pixel_row = row_index  # mark that row as the top of the icon data
                    break # stop there
            if top_pixel_row > old_top: # once the top row is found, stop looking down any further rows
                old_top = top_pixel_row
                break

        for row_index in range(top_pixel_row, len(white_mask)):
            has_false = False
            for pixel_index in range(left_most_pixel_column, len(white_mask[row_index])):
                if white_mask[row_index][pixel_index] == False:
                    has_false = True
                    continue
            if has_false:
                continue
            else:
                bottom_pixel_row = row_index
                break

        #input(f'{top_pixel_row=}, {bottom_pixel_row=}')


        while right_most_pixel_column < len(white_mask[0]):
            old_left = left_most_pixel_column
            for column_index in range(left_most_pixel_column, len(white_mask[0])): # start from the left-most column
                for pixel_index in range(top_pixel_row, len(white_mask)): # go pixel-by-pixel from the top-most row to bottom
                    if white_mask[pixel_index][column_index] == False:  # if there is any black pixel (from an icon)
                        left_most_pixel_column = column_index  # mark that column as the left (beginning) of icon data
                        break # and stop there
                if left_most_pixel_column > old_left: # once the left column has been found, stop looking down further columns
                    old_left = left_most_pixel_column
                    break

            for column_index in range(left_most_pixel_column, len(white_mask[0])):
                has_false = False
                for pixel_index in range(top_pixel_row, len(white_mask)):
                    if white_mask[pixel_index][column_index] == False:
                        has_false = True
                        continue
                if has_false:
                    continue
                else:
                    right_most_pixel_column = column_index
                    break

            if left_most_pixel_column == right_most_pixel_column:
                break

            #input(f'{top_pixel_row=}, {bottom_pixel_row=}, {left_most_pixel_column=}, {right_most_pixel_column=}')
            img.crop((left_most_pixel_column, top_pixel_row, right_most_pixel_column, bottom_pixel_row)).show()

            left_most_pixel_column = right_most_pixel_column + 1

        top_pixel_row = bottom_pixel_row + 1

    # for index in range(len(white_mask[top_pixel_row])):
    #     white_mask[top_pixel_row][index] = False
    #
    # for index in range(len(white_mask)):
    #     white_mask[index][left_most_pixel_column] = False
    #
    # visible_mask = Image.fromarray((~white_mask * 255).astype(np.uint8))
    # visible_mask.show()

    input('stop')


    for row in range(50):
        for index in range(len(white_mask[row])):
            if white_mask[row][index] is False:
                print(row, index)
                input('first top pixel')



    # # Invert: icons are non-white
    # from scipy import ndimage
    # labeled, num_features = ndimage.label(~white_mask)
    #
    # icons = []
    # for i in range(1, num_features + 1):
    #     # Get bounding box of each connected component
    #     rows, cols = np.where(labeled == i)
    #     if len(rows) == 0:
    #         continue
    #
    #     min_row, max_row = rows.min(), rows.max()
    #     min_col, max_col = cols.min(), cols.max()
    #
    #     # Crop
    #     crop = img.crop((min_col, min_row, max_col + 1, max_row + 1))
    #
    #     # Center in square
    #     square = Image.new('RGBA', (output_size, output_size), (255, 255, 255, 0))
    #     # Paste centered...
    #
    #     square.show()
    #
    #     input('stop here')
    #
    #     icons.append(square)

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





#slice_icons(icon_sheet_path='assets/servo386_httpss.mj.runwjtgaTbSie0_httpss.mj.run6XyyZMmUbJk_http_ff688dae-4254-4c06-8d75-c20981017abd.png', row_begin=16, row_size=222, column_begin=52, column_size=222, column_gap=44)
extract_icons(icon_sheet_path='assets/servo386_httpss.mj.runwjtgaTbSie0_httpss.mj.run6XyyZMmUbJk_http_ff688dae-4254-4c06-8d75-c20981017abd.png', output_size=128, threshold=200)