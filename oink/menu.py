import os

current_view = None
views = {}


# def register_section(section, help_text, handler):
#     """
#     Registers a section, which is basically just a set of specific commands.

#     """
#     sections_menu.append({
#         'name': section,
#         'help_text': help_text,
#     })
#     sections_handlers[section] = handler


# def register_command(command, help_text, handler):
#     """
#     Register available commands for the current section. These are cleared when
#     a section is changed.

#     """
#     commands_menu.append({
#         'name': command,
#         'help_text': help_text,
#     })
#     commands_handlers[command] = handler


def register_view(name, help_text, commands):
    views[name] = {
        'help_text': help_text,
        'commands': commands
    }


def show():
    """
    Display sections and commands available. Wait for a valid command.

    """
    print('Views')
    print('-' * 40)

    def print_cmd(name, help_text):
        print('{0}{1}'.format(name.ljust(16), help_text))

    for name, details in views.items():
        print_cmd(name, details['help_text'])

    print('\nCommands')
    print('-' * 40)

    if current_view:
        commands = views[current_view]['commands']

        for command in commands:
            print_cmd(command[0], command[1])

    print_cmd('exit', 'Exit Oink')


def clear_screen():
    """
    Clears the console screen.

    """
    os.system('clear' if os.name == 'posix' else 'clr')


def listen():
    global current_view

    while True:
        print('')
        command = input('> ')
        clear_screen()

        if command == '?':
            show()

        elif command == 'exit':
            return

        elif command in views:
            current_view = command
            show()

        elif current_view:
            # Find a matching command for the current view
            for view_command in views[current_view]['commands']:
                if view_command[0] == command:
                    view_command[2]()
                    continue
