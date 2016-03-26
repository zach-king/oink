"""
Handles routing commands to their respective handlers.
"""

# Commands stored via register function.
commands = []

# The number of padding between commands and help text
# This is determined by keeping track of the longest command string
print_padding = 0 


def register(command, help_text, handler):
    """
    Registers a command to a handler. 

    The command "keyword" is the trigger for the handler. All other values
    are either required or optional arguments. 

    Required arguments are written like <my_required_arg>.

    Optional arguments are written like [my_optional_arg]. Handlers implementing
    optional arguments should set a default value.

    Handlers will receive arguments in the order specified in the command.

    """
    global commands
    global print_padding

    bits = command.split()
    keyword = ' '.join([x for x in bits if x[0] not in ['<', '[']])
    args = [x for x in bits if x[0] == '<']

    commands.append({
        'keyword': keyword, 
        'args': args,
        'command': command, 
        'help_text': help_text, 
        'handler': handler
    })

    print(commands)

    command_length = len(command)
    if command_length > print_padding:
        print_padding = command_length


def route(command):
    """
    Attempts to match a command to a registered handler.

    Handles ensuring the required arguments, if any, are given.

    """
    bits = command.split()
    keywords = []

    for bit in bits:
        keywords.append(bit)
        keyword = ' '.join(keywords)

        for command in commands:
            if command['keyword'] == keyword:
                error = None
                args = bits[len(keywords):]

                given_args_length = len(args)
                command_args_length = len(command['args'])

                if given_args_length < command_args_length:
                    arg_index = (command_args_length - given_args_length) - 1
                    error = '{0} is required'.format(command['args'][arg_index])
                else:
                    error = command['handler'](*args)

                if error:
                    print('[error] {0}'.format(error))

                return

    print('[error] unkown command, type "?" to see commands.')


def show():
    """
    Render commands to console.

    Typically triggered by typeing "?".

    """
    for command in commands:
        print('{0}{1}'.format(
            command['command'].ljust(print_padding + 4), 
            command['help_text']))


def wait():
    """
    Start router and wait for commands.

    """
    while True:
        print('') # Add some whitespace
        command = input('> ')

        if command == '?':
            show()

        else:
            route(command)
