from collections.abc import Iterable, Iterator
from enum import Enum
from typing import TypeVar, overload

from adaptix import Retort, bound, loader
from adaptix import Mediator, Loader
from adaptix.type_tools import exec_type_checking
from adaptix._internal.provider.loc_stack_filtering import OriginSubclassLSC
from adaptix._internal.morphing.provider_template import LoaderProvider
from adaptix._internal.morphing.request_cls import LoaderRequest
from adaptix._internal.provider.located_request import for_predicate
from adaptix._internal.provider.location import TypeHintLoc

import pyrogram
from pyrogram.enums.auto_name import AutoName
from pyrogram.types.object import Object


_needs_eval = (
    pyrogram.raw.types.access_point_rule,
    pyrogram.raw.types.account_days_ttl,
    pyrogram.raw.types.attach_menu_bot,
    pyrogram.raw.types.attach_menu_bot_icon,
    pyrogram.raw.types.attach_menu_bot_icon_color,
    pyrogram.raw.types.attach_menu_bots,
    pyrogram.raw.types.attach_menu_bots_bot,
    pyrogram.raw.types.attach_menu_bots_not_modified,
    pyrogram.raw.types.attach_menu_peer_type_bot_pm,
    pyrogram.raw.types.attach_menu_peer_type_chat,
    pyrogram.raw.types.attach_menu_peer_type_pm,
    pyrogram.raw.types.attach_menu_peer_type_same_bot_pm,
    pyrogram.raw.types.auction_bid_level,
    pyrogram.raw.types.authorization,
    pyrogram.raw.types.auto_download_settings,
    pyrogram.raw.types.auto_save_exception,
    pyrogram.raw.types.auto_save_settings,
    pyrogram.raw.types.available_effect,
    pyrogram.raw.types.available_reaction,
    pyrogram.raw.types.channel_full,
    pyrogram.raw.types.chat_full,
    pyrogram.raw.types.document,
    pyrogram.raw.types.invoice,
    pyrogram.raw.types.message_media_contact,
    pyrogram.raw.types.message_media_dice,
    pyrogram.raw.types.message_media_document,
    pyrogram.raw.types.message_media_empty,
    pyrogram.raw.types.message_media_game,
    pyrogram.raw.types.message_media_geo,
    pyrogram.raw.types.message_media_geo_live,
    pyrogram.raw.types.message_media_giveaway,
    pyrogram.raw.types.message_media_giveaway_results,
    pyrogram.raw.types.message_media_invoice,
    pyrogram.raw.types.message_media_paid_media,
    pyrogram.raw.types.message_media_photo,
    pyrogram.raw.types.message_media_poll,
    pyrogram.raw.types.message_media_story,
    pyrogram.raw.types.message_media_to_do,
    pyrogram.raw.types.message_media_unsupported,
    pyrogram.raw.types.message_media_venue,
    pyrogram.raw.types.message_media_video_stream,
    pyrogram.raw.types.message_media_web_page,
    pyrogram.raw.types.story_item,
    pyrogram.raw.types.user_full
)
for _module in _needs_eval:
    exec_type_checking(_module)


def load_enum_value(value: str) -> Enum:
    from pyrogram import enums

    type_name, name = value.split(".", maxsplit=1)
    enum = getattr(enums, type_name)

    return getattr(enum, name)


def _get_pyrogram_types() -> dict[str, type]:
    from pyrogram import types

    objects = {name: getattr(types, name) for name in dir(types)}
    classes = {name: cls for name, cls in objects.items() if isinstance(cls, type)}
    pyrogram_classes = {name: cls for name, cls in classes.items() if cls.__module__.startswith('pyrogram.')}

    return pyrogram_classes


@for_predicate(Object)
class PyrogramObjectsProvider(LoaderProvider):
    _pyrogram_types = _get_pyrogram_types()

    def provide_loader(self, mediator: Mediator[Loader], request: LoaderRequest) -> Loader:

        def pyrogram_object_loader(data):
            cls = self._pyrogram_types[data["_"]]
            loader = mediator.mandatory_provide(request=LoaderRequest(request.loc_stack.replace_last(TypeHintLoc(cls))))
            return loader(data)

        return pyrogram_object_loader


_pyrogram_objects = Retort(recipe=[
    loader(OriginSubclassLSC(AutoName), load_enum_value),
    bound(OriginSubclassLSC(Object), PyrogramObjectsProvider()),
])


AnyObject = TypeVar("AnyObject", bound=Object, covariant=True)


@overload
def load_object(raw: dict, type: type[AnyObject]) -> AnyObject: ...
@overload
def load_object(raw: dict, type: None = None) -> Object: ...


def load_object(raw: dict, type: type[AnyObject] | None = None) -> AnyObject | Object:
    if type is not None:
        return _pyrogram_objects.load(raw, type)
    return _pyrogram_objects.load(raw, Object)


def load_objects(iterable: Iterable[dict]) -> Iterator[Object]:
    for item in iterable:
        yield load_object(item)
