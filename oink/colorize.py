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
    'magenta': '35',
    'cyan': '36',
    'white': '37',
    'hred': '41',
    'hgreen': '42',
    'hbrown': '43',
    'hblue': '44',
    'hmagenta': '45',
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
