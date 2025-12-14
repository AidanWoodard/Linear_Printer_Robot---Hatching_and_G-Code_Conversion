"""
#############################################################
SUMMARY: The printing gantry can cover a space of 4 units in
a 2x2 area, meaning the units need to be rearranged before
converted into g-code. This script will take the first 4 units
of each list and rearrange them into this 2x2 pattern and keep
each pattern separate for printing. This new list is passed
onto the 'G-Code Converter.'
#############################################################
"""

from Univ_Settings import *

def reorder_units_groups_of_four(total_lines_set, group_div=4):
    """Take list and return it converted into units by groups of 4"""
    converted_total_lines = []

    temp_unit_group = []
    for i, unit in enumerate(total_lines_set):
        if i != 0 and i % group_div == 0:
            converted_total_lines.append(temp_unit_group)
            temp_unit_group = [unit]        # reset temporary list
        else:
            temp_unit_group.append(unit)

        # edge case - add extra empty units to fill in set
        # print(i, len(total_lines_set)-1)
        if i == len(total_lines_set) - 1:
            for empty_space in range(group_div - len(temp_unit_group)):
                temp_unit_group.append([])
            converted_total_lines.append(temp_unit_group)

    for unit_group in converted_total_lines:
        # add offsets for printing (2x2 orientation)
        #print(len(unit_group))
        _add_offset(unit_group[1], pixels_per_unit_x, 0)        # upper right corner
        _add_offset(unit_group[2], 0, pixels_per_unit_y)        # bottom left corner
        _add_offset(unit_group[3], pixels_per_unit_x, pixels_per_unit_y)    # bottom right corner

    return converted_total_lines

def get_raw_converted_total_lines(new_converted_total_lines):
    """The converted total lines set originally comes grouped by 4, and this func puts those groups
    in one single long list of lines ordered top left to bottom right (for g-code conversion ease)"""
    raw_converted_total_lines = []

    # empty out the lines into each unit group and reorder them top left to bottom right using 'sorted()'
    for unit_group in new_converted_total_lines:
        new_unit_group = []
        for unit in unit_group:
            for line in unit:
                new_unit_group.append(line)
        # reorder whole group
        new_unit_group = sorted(new_unit_group, key=lambda line: (line[1], min(line[0], line[2])))
        raw_converted_total_lines.append(new_unit_group)

    return raw_converted_total_lines

def _add_offset(unit_line_set, x_offset, y_offset):
    """Add offset to unit_line_set depending on corner of the print"""
    # line: [x1, y1, x2, y2]
    for line in unit_line_set:
        line[0] += x_offset
        line[2] += x_offset
        line[1] += y_offset
        line[3] += y_offset