import os

DEBUG = True

DB_NAME = 'PlayCreator.db'
DB_URL = f'sqlite:///{os.getcwd()}/{DB_NAME}'

PLAYBOOK_NAME_MAX_LENGTH = 50

SCHEME_NAME_MAX_LENGTH = 50

UNDO_STACK_LIMIT = 15