from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    # переводим в bytes
    password_bytes = password.encode("utf-8")

    # bcrypt максимум 72 bytes
    password_bytes = password_bytes[:72]

    # обратно в string
    safe_password = password_bytes.decode(
        "utf-8",
        errors="ignore"
    )

    return pwd_context.hash(safe_password)


def verify_password(
    plain_password: str,
    hashed_password: str
):

    password_bytes = plain_password.encode(
        "utf-8"
    )

    password_bytes = password_bytes[:72]
    safe_password = password_bytes.decode(
        "utf-8",
        errors="ignore"
    )

    return pwd_context.verify(
        safe_password,
        hashed_password
    )