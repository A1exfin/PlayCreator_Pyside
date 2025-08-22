import os
from collections import namedtuple

first_team_position = namedtuple('FirstTeamPosition', 'football flag')
thickness = namedtuple('Thickness', 'min max')
zoom = namedtuple('Zoom', 'min max')
font_size = namedtuple('FontSize', 'min max')

DEBUG = True

DB_NAME = 'PlayCreator.db'
DB_URL = f'sqlite:///{os.getcwd()}/{DB_NAME}'

PLAYBOOK_NAME_MAX_LENGTH = 50

SCHEME_NAME_MAX_LENGTH = 50

UNDO_STACK_LIMIT = 15

FIRST_TEAM_POSITION_MAX = first_team_position(100, 50)
ZOOM = zoom(0, 200)

LINE_THICKNESS = thickness(2, 6)

SCENE_LABELS_FONT_SIZE = font_size(8, 36)


