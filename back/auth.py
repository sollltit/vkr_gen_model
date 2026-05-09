from passlib.context import CryptContext


# =========================
# bcrypt config
# =========================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================
# HASH PASSWORD
# =========================
def hash_password(password: str):

    # Переводим в bytes
    password_bytes = password.encode("utf-8")

    # bcrypt максимум 72 bytes
    password_bytes = password_bytes[:72]

    # Обратно в string
    safe_password = password_bytes.decode(
        "utf-8",
        errors="ignore"
    )

    return pwd_context.hash(safe_password)


# =========================
# VERIFY PASSWORD
# =========================
def verify_password(
    plain_password: str,
    hashed_password: str
):

    # То же самое для verify
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