"""
Handles routing commands to their respective handlers.
"""

from __future__ import print_function

from .colorize import colorize

# Commands stored via register function.
commands = []

# The number of padding between commands and help text
# This is determined by keeping track of the longest command string
print_padding = 0


def register(command, help_text, handler):
    '''
    Registers a command to a handler.

    The command "keyword" is the trigger for the handler. All other values
    are either required or optional arguments.

    Required arguments are written like <my_required_arg>.

    Optional arguments are written like [my_optional_arg]. Handlers implementing
    optional arguments should set a default value.

    Handlers will receive arguments in the order specified in the command.

    '''
    global commands
    global print_padding

    bits = command.split()
    keyword = ' '.join([x for x in bits if x[0] not in ['<', '[']])
    required_args = [x for x in bits if x[0] == '<']
    optional_args = [x for x in bits if x[0] == '[']

    commands.append({
        'keyword': keyword,
        'required_args': required_args,
        'optional_args': optional_args,
        'command': command,
        'help_text': help_text,
        'handler': handler
    })

    # print(commands)

    command_length = len(command)
    if command_length > print_padding:
        print_padding = command_length


def route(command):
    '''
    Attempts to match a command to a registered handler.

    Handles ensuring the required arguments, if any, are given.

    '''
    # Skip printing helper "commands"
    if command.lower() in ('separator', 'header'):
        print(colorize('[error]', 'red'), end='')
        print(' unkown command, type "?" to see commands.')
        return

    bits = command.split(' ')
    keyword = bits[0] # First word (only single word commands supported)
    argstr = ' '.join(bits[1:])
    args = []

    # Parse arguments and support spaces
    cur_arg = ''
    parsing_arg = False
    for character in argstr:
        # Check for quotes surrounding arguments that contain spaces
        if character == '"' or character == "'": # ' and " trigger parsing flag
            # Check if end of argument
            if parsing_arg:
                # End of argument, add to args list
                args.append(cur_arg)
                cur_arg = ''

            # Flip the parsing flag and skip the quote token
            parsing_arg = not parsing_arg
            continue

        # Check for spaces; if not parsing a quoted arg, space = delimeter
        if character == ' ' and not parsing_arg:
            args.append(cur_arg)
            cur_arg = ''
            continue

        # Append the character token to the current arg string
        cur_arg += character

    if cur_arg != '':
        args.append(cur_arg)

    while '' in args:
        args.remove('')

    # Try to find and execute the command
    for comm in commands:
        if comm['keyword'] == keyword:
            error = None
            given_args_length = len(args)
            command_args_length = len(comm['required_args'])
            max_args_length = len(comm['optional_args']) + command_args_length

            if given_args_length < command_args_length:
                arg_index = command_args_length - given_args_length
                if arg_index >= len(comm['required_args']):
                    arg_index = 0
                error = colorize(comm['required_args'][given_args_length], 'blue') + ' is required'
            elif given_args_length > max_args_length:
                error = '{} argument(s) were expected, but {} were given.'.format(
                    command_args_length, given_args_length)
            else:
                # Must be valid arguments list
                # Call the handler
                error = comm['handler'](*args)

            if error:
                print(colorize('[error]', 'red') + ' {}'.format(error))

            return

    print(colorize('[error]', 'red') + ' unkown command, type "?" to see commands.')


def show_help():
    '''
    Render commands to console.

    Typically triggered by typeing "?".

    '''
    for comm in commands:
        if comm['command'] == 'separator':
            print('\n')
        elif comm['command'] == 'header':
            print(colorize(
                '[ {0} Commands ]'.format(
                    comm['help_text']).center(print_padding + 4),
                'green'))
        else:
            print('{0}{1}'.format(
                comm['command'].ljust(print_padding + 4),
                comm['help_text']))


def wait():
    '''
    Start router and wait for commands.

    '''
    while True:
        print('') # Add some whitespace
        command = input('> ')

        if command == '?':
            show_help()

        else:
            route(command)
