from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())


class Encryption:
    @staticmethod
    def encrypt(value: str) -> str:
        encrypted_value = fernet.encrypt(value.encode())
        return encrypted_value.decode()

    @staticmethod
    def decrypt(encrypted_value: str) -> str:
        try:
            decrypted_value = fernet.decrypt(encrypted_value.encode())
            return decrypted_value.decode()
        except InvalidToken as exc:
            raise ValueError("Unable to decrypt stored credentials.") from exc
