from enum import Enum


class TeamType(Enum):
    OFFENCE = 0
    KICKOFF = 1
    PUNT = 2
    FIELD_GOAL_OFF = 3
    DEFENCE = 4
    KICK_RET = 5
    PUNT_RET = 6
    FIELD_GOAL_DEF = 7
    OFFENCE_ADD = 8