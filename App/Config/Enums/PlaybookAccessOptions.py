from enum import Enum


class PlaybookAccessOptions(Enum):
    TEAM_HEAD = 0
    TEAM_MANAGEMENT = 1
    REGULAR_TEAM_PLAYERS = 2
    ALL_TEAM_PLAYERS = 3
    EVERYBODY = 4