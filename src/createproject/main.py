import time

import emoji
from colored import stylize, fg
from halo import Halo
from jinja2 import Environment, PackageLoader, select_autoescape


def print_stylish(msg, color='green', spinner_time=1, wait_input=True):
    if wait_input:
        spinner = Halo(text='Loading', spinner='dots')
        print(stylize(emoji.emojize(msg, language='alias'), fg(color)))
        result = input()
        spinner.start()
        time.sleep(spinner_time)
        spinner.stop()
        return result
    print(stylize(emoji.emojize(msg, language='alias'), fg(color)))


def get_user_input():
    print_stylish('Hi there :wave:. Let''s create a new Flask project', wait_input=False)
    print_stylish('I need to set up some values in the setup.py file ...', wait_input=False)
    project_name = print_stylish('What would you like to name the project ? :smiley:')
    print_stylish('Good choice ! :thumbs_up:', 'blue', wait_input=False)
    author_name = print_stylish('Sorry ! I didn''t catch your name ?')
    author_email = print_stylish('If someone needs to contact you, what would your email be ?')
    print_stylish('You cannot get nice emails like that anymore :fire:', wait_input=False)
    short_description = print_stylish('How would you shortly describe our new project ? :sunglasses:')
    return locals()


def run():
    setup_data = get_user_input()
    env = Environment(
        loader=PackageLoader('createproject'),
        autoescape=select_autoescape()
    )
    template = env.get_template('setup.tmpl')

    print(template.render(**setup_data))
