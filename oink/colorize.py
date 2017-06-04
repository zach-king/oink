'''
File: colorize.py
Author: Zachary King

Utility for adding ANSI escape codes to a string
to add color to terminal output
'''

CODES = {
    'gray': '30',
    'red': '31',
    'green': '32',
    'yellow': '33',
    'blue': '34',
    'purple': '35',
    'cyan': '36',
    'white': '37',
    'hred': '41',
    'hgreen': '42',
    'hbrown': '43',
    'hblue': '44',
    'hpurple': '45',
    'hcyan': '46',
    'hgray': '47',
}

def colorize(string, color):
    '''Pads a string with ANSI esacpe codes to add color'''
    if color not in CODES or not isinstance(color, str):
        color = 'white'

    color = color.lower()

    padded_str = '\033[1;{0}m{1}\033[1;m\033[1;37m\033[1;m'
    return padded_str.format(CODES[color], string)


def reset():
    '''Resets buffer color'''
    reset_str = colorize('', 'white')
    print(reset_str, end='')


def set_color(color):
    '''Sets the buffer color'''
    if color not in CODES or not isinstance(color, str):
        color = 'white'
    color = color.lower()

    set_str = '\033[1;{}m\033[1;m'.format(CODES[color])
    print(set_str, end='')


def colorize_list(lyst_of_str, color_or_list):
    '''Colorizes each string in a list.
    Second argument can be a list of valid color strings
    to be applied to the corresponding list element'''
    colored_list = []
    if not isinstance(color_or_list, list):
        color_or_list = [color_or_list] * len(lyst_of_str) # ['blue', 'blue',  'blue', ...]

    for i, string in enumerate(lyst_of_str):
        colored_list.append(colorize(string, color_or_list[i]))
    return colored_list
