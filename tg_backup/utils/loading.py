from typing import Any

from pyrogram.types.object import Object


def _get_pyrogram_types() -> dict[str, type]:
    from pyrogram import types

    objects = {name: getattr(types, name) for name in dir(types)}
    classes = {name: cls for name, cls in objects.items() if isinstance(cls, type)}
    pyrogram_classes = {name: cls for name, cls in classes.items() if cls.__module__.startswith('pyrogram.')}

    return pyrogram_classes


def _get_pyrogram_enums() -> dict[str, type]:
    from enum import Enum
    from pyrogram import enums

    objects = {name: getattr(enums, name) for name in dir(enums)}
    classes = {name: cls for name, cls in objects.items() if isinstance(cls, type)}
    enum_classes = {name: cls for name, cls in classes.items() if issubclass(cls, Enum)}
    pyrogram_enums = {name: cls for name, cls in enum_classes.items() if cls.__module__.startswith('pyrogram.')}

    return pyrogram_enums


def get_loader():
    from datetime import datetime as dt

    types = _get_pyrogram_types()
    enums = _get_pyrogram_enums()

    def load_enum_value(value):
        if not isinstance(value, str):
            raise ValueError(f"{value!r} is not a string")
        enum_name, member_name = value.split('.', maxsplit=1)
        enum = enums[enum_name]

        return getattr(enum, member_name)

    def load_list(lst_raw: list) -> list:
        return [
            loader(item) if isinstance(item, dict) else item
            for item in lst_raw
        ]

    MISSABLE = {
        'ChatPhoto': {'is_personal': None},
        'Video': {'codec': None},
        'WebPage': {'url': None},
        'ExternalReplyInfo': {'message_id': None},
        'SuccessfulPayment': {
            'invoice_payload': None,
            'telegram_payment_charge_id': None,
            'provider_payment_charge_id': None,
        },
        'Sticker': {'is_animated': None, 'is_video': None},
    }

    def loader(json: dict, ty: type | None = None) -> Object:
        type_name = json.pop("_")
        if not isinstance(type_name, str):
            raise ValueError(f"{type_name!r} is not a string")

        type = types[type_name]
        kwds: dict[str, Any] = MISSABLE.get(type_name, {}).copy()
        for name, value in json.items():
            if isinstance(value, dict):
                value = loader(value)
            elif isinstance(value, list):
                value = load_list(value)
            elif name in {'date', 'last_online_date'}:
                value = dt.fromisoformat(value)
            elif name in {'color', 'status', 'media', 'service'}:
                value = load_enum_value(value)
            elif name == 'type' and type_name != "WebPage":
                value = load_enum_value(value)
            elif name == 'media' and type_name != 'PaidMediaInfo':
                value = load_enum_value(value)
            kwds[name] = value

        return type(**kwds)

    return loader


load_object = get_loader()
