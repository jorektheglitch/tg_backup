# TODO: get rid of this shitty-style config
# TODO: separate classes for specific parts (sqlalchemy, logging, pyrogram)
from typing import Any


SQLA_ECHO = False
SQLA_LOG = False

APP_NAME: str = ""
API_ID: int = 0
API_HASH: str = ""
PHONE: str = ""

TAKEOUT: bool = False

USE_PROXY: bool = False
PROXY: dict[str, Any] = {
    "scheme": "socks5",
    "hostname": "",
    "port": 0,
    "username": "",
    "password": "",
}
