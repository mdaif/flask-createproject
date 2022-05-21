import os.path
import uuid
from unittest import mock

import pytest
from _pytest.capture import CaptureResult

from createproject.main import aggregate_user_input
from createproject.main import is_one_word
from createproject.main import is_valid_bool
from createproject.main import is_valid_email
from createproject.main import prompt_user
from createproject.main import run
from createproject.main import touch


@pytest.fixture
def timeless(monkeypatch):
    monkeypatch.setattr('createproject.main.time.sleep', lambda *args, **kwargs: 0)


class TestPromptUser:
    @mock.patch('createproject.main.input')
    def test_simple_case(self, m_input, timeless, monkeypatch, capsys):
        m_input.side_effect = ('my input',)
        user_input = prompt_user('Hi there :wave:')
        captured = capsys.readouterr()

        # The funky escape characters are what instruct the terminal to show the color green.
        assert captured == CaptureResult(out='\x1b[38;5;2mHi there 👋\x1b[0m\n', err='')
        assert user_input == 'my input'

    @mock.patch('createproject.main.input')
    def test_with_is_one_word_validator(self, m_input, timeless, capsys):
        m_input.side_effect = ('something weird', 'oneword')
        user_input = prompt_user('What would you like to name the project ? :smiley:', validator=is_one_word)
        captured = capsys.readouterr()
        assert captured == CaptureResult(
            out='\x1b[38;5;2mWhat would you like to name the project ? 😃\x1b[0m\n'
                '\x1b[38;5;1m‼️  Input cannot contain spaces, try again\x1b[0m\n', err='')
        assert user_input == 'oneword'

    @mock.patch('createproject.main.input')
    def test_with_options_validator(self, m_input, timeless, capsys):
        m_input.side_effect = ('something weird', 'yes')
        user_input = prompt_user('Are you planning on having templates in your project ?', validator=is_valid_bool)
        captured = capsys.readouterr()
        assert captured == CaptureResult(
            out='\x1b[38;5;2mAre you planning on having templates in your project ?\x1b[0m\n'
                '\x1b[38;5;1m‼️  Only ("yes", "no") are valid choices, try again\x1b[0m\n', err='')
        assert user_input == 'yes'

    @mock.patch('createproject.main.input')
    def test_with_valid_email_validator(self, m_input, timeless, capsys):
        m_input.side_effect = ('something weird', 'a.b@example.com')
        user_input = prompt_user(
            'If someone needs to contact you, what would your email be ?', validator=is_valid_email)
        captured = capsys.readouterr()
        assert captured == CaptureResult(
            out='\x1b[38;5;2mIf someone needs to contact you, what would your email be ?\x1b[0m\n'
                '\x1b[38;5;1m‼️  invalid email, try again\x1b[0m\n', err='')
        assert user_input == 'a.b@example.com'

    def test_no_wait_input(self, capsys):
        user_input = prompt_user('I wait no input', wait_input=False)
        captured = capsys.readouterr()
        assert captured == CaptureResult(out='\x1b[38;5;2mI wait no input\x1b[0m\n', err='')
        assert user_input is None


@mock.patch('createproject.main.prompt_user')
def test_user_input(m_prompt_user, tmp_path):
    m_prompt_user.side_effect = [
        # First iteration
        None,
        None,
        'myproject',
        None,
        'myapp',
        'my name',
        'my.email@example.com',
        None,
        'description stuff',
        'yes',

        # second iteration with existing project name
        None,
        None,
        'myproject',
    ]
    user_input = aggregate_user_input(str(tmp_path))
    assert user_input == {
        'author_email': 'my.email@example.com',
        'author_name': 'my name',
        'include_templates': True,
        'main_package': 'myapp',
        'project_name': 'myproject',
        'short_description': 'description stuff',
    }
    d = tmp_path / 'myproject'
    d.mkdir()
    with pytest.raises(SystemExit):
        aggregate_user_input(str(tmp_path))


def test_touch(tmp_path):
    file_name = str(uuid.uuid4()) + '.txt'
    file_path = f'{tmp_path}/{file_name}'
    assert not os.path.exists(file_path)
    touch(file_path)
    assert os.path.exists(file_path)
    last_access_before_touch = os.stat(file_path).st_atime
    touch(file_path)
    last_access_after_touch = os.stat(file_path).st_atime
    assert last_access_after_touch > last_access_before_touch


@pytest.mark.parametrize('include_templates', (True, False))
@mock.patch('createproject.main.get_base_path')
@mock.patch('createproject.main.aggregate_user_input')
def test_run_no_include_template(m_aggregate_user_input, m_get_path, faker, tmp_path, include_templates):
    m_get_path.return_value = tmp_path
    email = faker.email()
    author_name = faker.name()
    main_package = faker.pystr()
    project_name = faker.pystr()
    description = faker.sentence()

    m_aggregate_user_input.return_value = {
        'author_email': email,
        'author_name': author_name,
        'include_templates': include_templates,
        'main_package': main_package,
        'project_name': project_name,
        'short_description': description,
    }
    run()
    created_directories = os.listdir(tmp_path)
    assert created_directories == [project_name]
    created_structure = os.listdir(os.path.join(tmp_path, project_name))
    assert created_structure == [
        'LICENSE',
        'requirements.txt',
        'pyproject.toml',
        'tests',
        'MANIFEST.in',
        'README.md',
        'setup.py',
        '.gitignore',
        'setup.cfg',
        'src',
    ]

    app_dir = os.listdir(os.path.join(tmp_path, project_name, 'src', main_package))

    with open(f'{tmp_path}/{project_name}/MANIFEST.in') as f:
        manifest_content = f.read()

    with open(f'{tmp_path}/{project_name}/setup.py') as f:
        setup_content = f.read()

    if include_templates:
        assert 'include templates/*' in manifest_content
        assert 'templates' in app_dir
        assert "install_requires=['Jinja2']" in setup_content
        assert "package_data={'': ['templates/*.txt']}" in setup_content
    else:
        assert 'include templates/*' not in manifest_content
        assert app_dir == ['__init__.py']  # no templates.
        assert "install_requires=['Jinja2']" not in setup_content
        assert "package_data={'': ['templates/*.txt']}" not in setup_content
