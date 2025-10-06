from typing import TYPE_CHECKING

import keyring
from cryptography.fernet import Fernet

import Core

if TYPE_CHECKING:
    pass


class Cipher:
    @staticmethod
    def get_cipher() -> 'Fernet':
        secret_key = keyring.get_password(Core.APP_NAME, Core.SECRET_KEY_NAME)
        if secret_key is None:
            secret_key = Cipher._get_new_secret_key()
            keyring.set_password(Core.APP_NAME, Core.SECRET_KEY_NAME, secret_key)
        return Fernet(secret_key)

    @staticmethod
    def _get_new_secret_key() -> str:
        return Fernet.generate_key().decode()