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

LOGIN_API_URL: Final = ''


@dataclass(frozen=True)
class APIEndpoints:
    domain = 'localhost:8000' if DEBUG else 'playcreator.com'
    api_base = '/api/desktop'
    api_version = '/v1'
    login = f'{domain}{api_base}{api_version}/authlogin/'
    logout = f'{domain}{api_base}{api_version}/authlogout/'############################
    playbooks = f'{domain}{api_base}{api_version}/playbooks/'