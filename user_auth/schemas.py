from dataclasses import dataclass


@dataclass
class AuthorizeUser:
    phone_number: str
    auth_code: str
