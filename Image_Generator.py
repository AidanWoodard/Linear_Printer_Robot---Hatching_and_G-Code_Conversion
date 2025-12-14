"""
#############################################################
SUMMARY: This script takes a .png image and...
1. Converts to grayscale
2. Adjusts the resolution
3. Removes spaces between units
4. Prepares a large array of all brightness vals

This image prepares the image for the 'hatch algorithm' which
will convert the pixels into a hatching pattern for printing.
#############################################################
"""

from Univ_Settings import *

from PIL import Image
import numpy as np

# consts inherited from 'Univ_Settings.py'
IMAGE_PATH = image_path
UNIT_WIDTH = pixels_per_unit_x    # these will always have the same value (just renamed for clarity)
UNIT_HEIGHT = pixels_per_unit_y

# other setup vars
total_dimensions = [units_wide, units_high]       # num of sticky notes in x and y (inhereted from 'Univ_Settings.py'
unit_deadspace = pixels_of_deadspace  # number of pixels in between sticky notes (spacing of sticky notes measure in pixels)

# list of all units (as arrays of brightness)
all_units = []

def calculate_brightness_arrays():
    # load image
    try:
        img_raw = Image.open(IMAGE_PATH)
        img = img_raw.convert('L')      # grayscale
    except FileNotFoundError:
        print(f"No image at {IMAGE_PATH}")
        quit()

    # resize
    img = resize_and_crop(img, total_dimensions, UNIT_WIDTH, UNIT_HEIGHT, unit_deadspace)

    # analyze brightness and store as array per unit
    curr_x, curr_y = 0, 0
    for y in range(total_dimensions[1]):
        for x in range(total_dimensions[0]):
            # get array using 'analyze_brightness' func
            new_unit = analyze_brightness(img, curr_x, curr_y, UNIT_WIDTH, UNIT_HEIGHT)
            all_units.append(new_unit)
            # create next starting point
            curr_x += UNIT_WIDTH + unit_deadspace
        curr_y += UNIT_HEIGHT + unit_deadspace
        curr_x = 0

    ######################## TEMP CODE for testing
    # print_ascii_representation(49)
    # print_ascii_representation()
    display_image(img)

    # func called by 'main.py'
    return all_units

def resize_and_crop(img_obj, print_dimensions, u_width, u_height, deadspace):
    """Shape image to desired size and crop excess"""
    # Find width and height in pixels
    len_x = u_width * print_dimensions[0]
    len_x += (print_dimensions[0] - 1) * deadspace
    len_y = u_height * print_dimensions[1]
    len_y += (print_dimensions[1] - 1) * deadspace
    target_size = (len_x, len_y)

    # find the larger scale factor
    og_w, og_h = img_obj.size
    ratio_w = target_size[0] / og_w
    ratio_h = target_size[1] / og_h
    scale_factor = max(ratio_w, ratio_h)

    # scale the image
    scaled_w = int(og_w * scale_factor)
    scaled_h = int(og_h * scale_factor)
    new_img = img_obj.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

    # calculate the crop (needs to be centered)
    crop_box = (
    int((scaled_w - target_size[0]) / 2),
    int((scaled_h - target_size[1]) / 2),
    int((scaled_w + target_size[0]) / 2),
    int((scaled_h + target_size[1]) / 2)
    )
    new_img = new_img.crop(crop_box)

    # return final image
    return new_img

def analyze_brightness(img, x_start, y_start, u_width, u_height):
    """Return an array representing the brightness values for the unit"""
    # take the clip of the image that will go on this unit only
    img_piece = img.crop((x_start, y_start, x_start + u_width, y_start + u_height))
    pixel_data = list(img_piece.getdata())
    new_unit_array = np.array(pixel_data).reshape((u_height, u_width))

    # return array of brightness vals (access like: if new_unit_array(y, x) < 255: ...)
    return new_unit_array

def print_ascii_representation(unit=None):
    """This is a test function that prints out the image as an ASCII art conversion, using numbers, letters,
    and symbols to represent brightness. It's a little buggy, but it should work"""
    # (stolen from internet) BRIGHTNESS LEVELS:  `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@
    chars = [' ', ' ', '.', '-', "'", ':', '_', ',', '^', '=', ';', '>', '<', '+', '!', 'r', 'c', '*', '/',
             'z', '?', 's', 'L', 'T', 'v', ')', 'J', '7', '(', '|', 'F', 'i', '{', 'C', '}', 'f', 'I', '3',
             '1', 't', 'l', 'u', '[', 'n', 'e', 'o', 'Z', '5', 'Y', 'x', 'j', 'y', 'a', ']', '2', 'E', 'S',
             'w', 'q', 'k', 'P', '6', 'h', '9', 'd', '4', 'V', 'p', 'O', 'G', 'b', 'U', 'A', 'K', 'X', 'H',
             'm', '8', 'R', 'D', '#', '$', 'B', 'g', '0', 'M', 'N', 'W', 'Q', '%', '&', '@']
    values = [0, 0.0751, 0.0829, 0.0848, 0.1227, 0.1403, 0.1559, 0.185, 0.2183, 0.2417, 0.2571, 0.2852,
              0.2902, 0.2919, 0.3099, 0.3192, 0.3232, 0.3294, 0.3384, 0.3609, 0.3619, 0.3667, 0.3737,
              0.3747, 0.3838, 0.3921, 0.396, 0.3984, 0.3993, 0.4075, 0.4091, 0.4101, 0.42, 0.423, 0.4247,
              0.4274, 0.4293, 0.4328, 0.4382, 0.4385, 0.442, 0.4473, 0.4477, 0.4503, 0.4562, 0.458, 0.461,
              0.4638, 0.4667, 0.4686, 0.4693, 0.4703, 0.4833, 0.4881, 0.4944, 0.4953, 0.4992, 0.5509,
              0.5567, 0.5569, 0.5591, 0.5602, 0.5602, 0.565, 0.5776, 0.5777, 0.5818, 0.587, 0.5972, 0.5999,
              0.6043, 0.6049, 0.6093, 0.6099, 0.6465, 0.6561, 0.6595, 0.6631, 0.6714, 0.6759, 0.6809,
              0.6816, 0.6925, 0.7039, 0.7086, 0.7235, 0.7302, 0.7332, 0.7602, 0.7834, 0.8037, 0.9999]

    # if you want to print just one unit:
    if unit:
        for y in range(UNIT_HEIGHT):
            for x in range(UNIT_WIDTH):
                curr_val = 1 - all_units[unit][y, x] / 255
                # brightness vals mapped to their corresponding character
                for i in range(len(values)):
                    if curr_val <= values[i]:
                        print(chars[i], end="   ")
                        break
                if x == UNIT_WIDTH - 1:
                    print('')
    else:
        unit_num = 0
        # loop through units vertically
        for a in range(total_dimensions[1]):
            # loop through each level of a unit
            for y in range(UNIT_HEIGHT):
                # loop through each unit on that level
                for b in range(total_dimensions[0]):
                    # loop through each x val of that unit
                    for x in range(UNIT_WIDTH):
                        if x == UNIT_WIDTH - 1:
                            print("   ", end="")
                            continue
                        else:
                            curr_val = 1 - all_units[unit_num][y, x] / 255
                        # brightness vals mapped to their corresponding character
                        for i in range(len(values)):
                            if curr_val <= values[i]:
                                if unit_num + 1 % total_dimensions[0] == 0:
                                    print(chars[i])
                                    break
                                else:
                                    print(chars[i], end="   ")
                                    break
                    unit_num += 1
                    if b == total_dimensions[0] - 1:
                        print('')
                unit_num = a * total_dimensions[0]
            print()

def display_image(new_img):
    # (just for readability)
    new_img.show()

def return_brightness_arrays():
    # called by 'Hatch_Algorithm.py'
    return all_units



# run the code
#calculate_brightness_arrays()
