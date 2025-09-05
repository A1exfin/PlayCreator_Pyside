import os
from typing import Final
from collections import namedtuple
from dataclasses import dataclass

first_team_max_position = namedtuple('FirstTeamPosition', 'football flag')
thickness_range = namedtuple('Thickness', 'min max')
zoom_range = namedtuple('Zoom', 'min max')
font_size_range = namedtuple('FontSize', 'min max')

DEBUG: Final[bool] = True

DB_NAME: Final[str] = 'PlayCreator.db'
DB_URL: Final[str] = f'sqlite:///{os.getcwd()}/{DB_NAME}'

PLAYBOOK_NAME_MAX_LENGTH: Final[int] = 50

SCHEME_NAME_MAX_LENGTH: Final[int] = 50

UNDO_STACK_LIMIT: Final[int] = 15

FIRST_TEAM_MAX_POSITION = first_team_max_position(100, 50)
ZOOM_RANGE = zoom_range(0, 200)
LINE_THICKNESS_RANGE = thickness_range(2, 6)
SCENE_LABELS_FONT_SIZE_RANGE = font_size_range(8, 36)


@dataclass(frozen=True)
class WebAppUrls:
    _domain = 'http://localhost:8000' if DEBUG else 'https://playcreator.com'
    _api_base = '/api/desktop'
    _api_version = '/v1'
    signup = f'{_domain}?modal=signup'
    api_login = f'{_domain}{_api_base}{_api_version}/auth/token/login/'
    api_logout = f'{_domain}{_api_base}{_api_version}/auth/token/logout/'
    api_playbooks = f'{_domain}{_api_base}{_api_version}/playbooks/'
    api_user_info = f'{_domain}{_api_base}{_api_version}/users/me/'
