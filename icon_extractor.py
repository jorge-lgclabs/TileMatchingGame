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



extract_icons(icon_sheet_path='assets/servo386_httpss.mj.runwjtgaTbSie0_httpss.mj.run6XyyZMmUbJk_http_ff688dae-4254-4c06-8d75-c20981017abd.png', output_size=128, threshold=200)