import secrets
import string


def generate_secret_string(length: int) -> string:
    alphabet = string.ascii_letters
    return "".join(secrets.choice(alphabet) for _ in range(length))
