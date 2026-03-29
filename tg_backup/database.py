from __future__ import annotations

import enum
import re
from collections.abc import Awaitable, Callable, Mapping, Sequence
# from contextlib import contextmanager
from datetime import datetime as dt
from typing import Any, ClassVar, Literal, TypeAlias, TypeVar, overload

from sqlalchemy.types import Boolean, LargeBinary, DateTime, Enum, Float, Integer, String
from sqlalchemy.types import TypeDecorator
from sqlalchemy import ForeignKey, select
from sqlalchemy import MetaData
from sqlalchemy import orm
from sqlalchemy.engine import Dialect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_as_dataclass  # , with_polymorphic
from sqlalchemy.orm import Mapped, mapped_column, relationship  # , selectinload
# from sqlalchemy.sql import select  # , insert, func
from sqlalchemy.schema import Column, Table, ForeignKeyConstraint

from tg_backup import domain


T = TypeVar("T")
Return = TypeVar("Return", covariant=True)

DomainClass: TypeAlias = type[Any]


NAMING = {
    'ix': 'index_%(table_name)s_%(column_0_N_name)s',
    'uq': 'unique_%(table_name)s_%(column_0_N_name)s',
    'ck': 'check_%(table_name)s_%(column_0_N_name)s',
    'fk': 'foreign_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s_%(referred_column_0_N_name)s',
    'pk': 'primary_%(table_name)s',
}

registry = orm.registry(metadata=MetaData(naming_convention=NAMING))


class ChatType(enum.StrEnum):
    UserDialog = "UserDialog"
    "Chat is a private chat with a user"

    BotDialog = "BotDialog"
    "Chat is a private chat with a bot"

    Group = "Group"
    "Chat is a basic group"

    UnavailableGroup = "UnavailableGroup"
    "Chat is a basic group (unavailable for some reason)"

    Supergroup = "Supergroup"
    "Chat is a supergroup"

    UnavailableSupergroup = "UnavailableSupergroup"
    "Chat is a supergroup (unavailable for some reason)"

    Channel = "Channel"
    "Chat is a channel"

    Forum = "Forum"
    "Chat is a forum"

    Direct = "Direct"
    "Chat is a direct with a channel"


@mapped_as_dataclass(registry)
class Chat:
    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)
    type: Mapped[ChatType | None] = mapped_column(Enum(ChatType), init=False)

    __domain_class__ = domain.Chat
    __tablename__ = "chats"
    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "type",
        # "with_polymorphic": "*",  # TODO: investigate performance
    }


@mapped_as_dataclass(registry)
class Channel(Chat):
    # tg_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "channels"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.Channel,
    }


@mapped_as_dataclass(registry)
class Dialog(Chat):
    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "type",
    }


@mapped_as_dataclass(registry)
class User(Chat):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "users"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.UserDialog,
    }


@mapped_as_dataclass(registry)
class Bot(User):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "bots"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.BotDialog,
    }


@mapped_as_dataclass(registry)
class Group(Chat):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "groups"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.Group,
    }


@mapped_as_dataclass(registry)
class UnavailableGroup(Chat):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "groups"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.UnavailableGroup,
    }


@mapped_as_dataclass(registry)
class Supergroup(Chat):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "supergroups"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.Supergroup,
    }


@mapped_as_dataclass(registry)
class UnavailableSupergroup(Chat):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "supergroups"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.UnavailableSupergroup,
    }


@mapped_as_dataclass(registry)
class Forum(Chat):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "forums"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.Forum,
    }


@mapped_as_dataclass(registry)
class Direct(Chat):
    # tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False)

    # __tablename__ = "channels_dms"
    __mapper_args__ = {
        "polymorphic_identity": ChatType.Direct,
    }


@mapped_as_dataclass(registry)
class ChatPhoto:
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    small_file_id: Mapped[str] = mapped_column(String, nullable=False)
    small_photo_unique_id: Mapped[str] = mapped_column(String, nullable=False)
    big_file_id: Mapped[str] = mapped_column(String, nullable=False)
    big_photo_unique_id: Mapped[str] = mapped_column(String, nullable=False)

    __domain_class__ = domain.ChatPhoto
    __tablename__ = "chat_photos"


@mapped_as_dataclass(registry)
class CustomEmoji:
    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)

    __tablename__ = "custom_emojis"


class MessageSourceType(enum.StrEnum):
    USER = "USER"
    CHANNEL_ADMIN = "CHANNEL_ADMIN"
    CHANNEL = "CHANNEL"
    ANON_ADMIN = "ANON_ADMIN"


@mapped_as_dataclass(registry)
class MessageSource:
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    type: Mapped[MessageSourceType] = mapped_column(Enum(MessageSourceType), nullable=False, init=False)

    __tablename__ = "message_sources"
    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "type",
    }


@mapped_as_dataclass(registry)
class FromUser(MessageSource):
    rowid: Mapped[int] = mapped_column(ForeignKey(MessageSource.rowid), unique=True, autoincrement=False, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), primary_key=True, init=False)
    user: Mapped[User] = relationship(User, uselist=False)

    __tablename__ = "message_source_users"
    __mapper_args__ = {
        "polymorphic_identity": MessageSourceType.USER,
    }


@mapped_as_dataclass(registry)
class FromChannelAdmin(MessageSource):
    rowid: Mapped[int] = mapped_column(ForeignKey(MessageSource.rowid), unique=True, autoincrement=False, init=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey(Channel.tg_id), primary_key=True, nullable=False, init=False)
    channel: Mapped[Channel] = relationship(Channel, uselist=False)
    author_signature: Mapped[str | None] = mapped_column(String, primary_key=True, nullable=True)

    __tablename__ = "message_source_channnel_admins"
    __mapper_args__ = {
        "polymorphic_identity": MessageSourceType.CHANNEL_ADMIN,
    }


@mapped_as_dataclass(registry)
class FromChannel(MessageSource):
    rowid: Mapped[int] = mapped_column(ForeignKey(MessageSource.rowid),
                                       unique=True, nullable=False, autoincrement=False, init=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey(Channel.tg_id), primary_key=True, nullable=False, init=False)
    channel: Mapped[Channel] = relationship(Channel, uselist=False)

    __tablename__ = "message_source_channels"
    __mapper_args__ = {
        "polymorphic_identity": MessageSourceType.CHANNEL,
    }


@mapped_as_dataclass(registry)
class FromAnonAdmin(MessageSource):
    rowid: Mapped[int] = mapped_column(ForeignKey(MessageSource.rowid),
                                       unique=True, nullable=False, autoincrement=False, init=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), primary_key=True, init=False)
    chat: Mapped[Chat] = relationship(Chat, uselist=False)
    admin_mark: Mapped[str | None] = mapped_column(String, primary_key=True, nullable=True)

    __tablename__ = "message_source_anon_admins"
    __mapper_args__ = {
        "polymorphic_identity": MessageSourceType.ANON_ADMIN,
    }


class ForwardOriginType(enum.StrEnum):
    USER = "USER"
    HIDDEN_USER = "HIDDEN_USER"
    CHANNEL = "CHANNEL"
    LINKED_CHANNEL = "LINKED_CHANNEL"
    ANON_ADMIN = "ANON_ADMIN"


@mapped_as_dataclass(registry)
class ForwardOrigin:
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    type: Mapped[ForwardOriginType] = mapped_column(Enum(ForwardOriginType), nullable=False, init=False)
    # TODO: separate origin_date for origin reusabiility?
    origin_date: Mapped[dt | None] = mapped_column(DateTime, nullable=True)

    __tablename__ = "forward_from"
    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "type",
    }


@mapped_as_dataclass(registry)
class AnonUserOrigin(ForwardOrigin):
    rowid: Mapped[int] = mapped_column(ForeignKey(ForwardOrigin.rowid), primary_key=True, autoincrement=True, init=False)  # noqa: E501
    sender_name: Mapped[str]

    __tablename__ = "forward_from_hidden_user"
    __mapper_args__ = {
        "polymorphic_identity": ForwardOriginType.HIDDEN_USER,
    }


@mapped_as_dataclass(registry)
class UserOrigin(ForwardOrigin):
    rowid: Mapped[int] = mapped_column(ForeignKey(ForwardOrigin.rowid), primary_key=True, autoincrement=True, init=False)  # noqa: E501
    user_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), init=False)
    user: Mapped[User] = relationship(User, uselist=False)

    __tablename__ = "forward_from_user"
    __mapper_args__ = {
        "polymorphic_identity": ForwardOriginType.USER,
    }


@mapped_as_dataclass(registry)
class _ChannelOrigin(ForwardOrigin):
    rowid: Mapped[int] = mapped_column(ForeignKey(ForwardOrigin.rowid), primary_key=True, autoincrement=True, init=False)  # noqa: E501
    channel_id: Mapped[int] = mapped_column(ForeignKey(Channel.tg_id), init=False)
    channel: Mapped[Channel] = relationship(Channel, foreign_keys=[channel_id])
    source_message_id: Mapped[int]  # TODO: foreign key to BoundMessage?
    author_signature: Mapped[str | None]

    __tablename__ = "forward_from_channel"
    __mapper_args__ = {
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class LinkedChannelOrigin(_ChannelOrigin):
    __mapper_args__ = {
        "polymorphic_identity": ForwardOriginType.LINKED_CHANNEL,
    }


@mapped_as_dataclass(registry)
class ChannelOrigin(_ChannelOrigin):
    __mapper_args__ = {
        "polymorphic_identity": ForwardOriginType.CHANNEL,
    }


@mapped_as_dataclass(registry)
class AnonAdminOrigin(ForwardOrigin):
    rowid: Mapped[int] = mapped_column(ForeignKey(ForwardOrigin.rowid), primary_key=True, autoincrement=True, init=False)  # noqa: E501
    chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), init=False)
    chat: Mapped[Chat] = relationship(Chat, foreign_keys=[chat_id], uselist=False)
    admin_mark: Mapped[str | None] = mapped_column(String, nullable=True)

    __tablename__ = "forward_from_anon_admin"
    __mapper_args__ = {
        "polymorphic_identity": ForwardOriginType.ANON_ADMIN,
    }


class MessageType(enum.StrEnum):
    MESSAGE = "MESSAGE"
    POST = "POST"


@mapped_as_dataclass(registry)
class BoundMessage:
    chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    _type: Mapped[MessageType] = mapped_column("type", Enum(MessageType), nullable=False, init=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey(MessageSource.rowid), nullable=False, init=False)
    sender: Mapped[MessageSource] = relationship(MessageSource, uselist=False)
    payload: Mapped[Payload] = relationship(lambda: Payload, uselist=False)
    date: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=False)
    has_protected_content: Mapped[bool] = mapped_column(Boolean, nullable=False)
    forward_from_id: Mapped[int | None] = mapped_column(ForeignKey(ForwardOrigin.rowid), nullable=True, init=False)
    forward_from: Mapped[ForwardOrigin | None] = relationship(ForwardOrigin, foreign_keys=[forward_from_id])
    # TODO: replies
    # reply_to: Mapped[BoundMessage] = relationship(lambda: BoundMessage)

    __domain_class__: ClassVar[type | Any] = domain.BoundMessage
    __tablename__: ClassVar[str] = "messages_info"
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_abstract": True,
        "polymorphic_on": "_type",
    }


@mapped_as_dataclass(registry, kw_only=True)
class ChatMessage(BoundMessage):
    chat: Mapped[Chat] = relationship(Chat, uselist=False)

    __domain_class__ = domain.ChatMessage
    __mapper_args__ = {
        "polymorphic_identity": MessageType.MESSAGE,
    }


@mapped_as_dataclass(registry)
class ChannelPost(BoundMessage):
    chat_id: Mapped[int] = mapped_column(ForeignKey(Channel.tg_id), primary_key=True, init=False)
    channel: Mapped[Channel] = relationship(Channel, uselist=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    forwards: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __domain_class__ = domain.ChannelPost
    __tablename__ = "posts_info"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (BoundMessage.chat_id, BoundMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": MessageType.POST,
    }


@enum.unique
class _PayloadType(enum.StrEnum):
    TEXT = "text"
    FORWARDED = "forwarded"


_members = tuple(
    member
    for enum in (domain.MessageMediaType, domain.MessageServiceType, _PayloadType)
    for member in enum
)

MessagePayloadType: TypeAlias = domain.MessageMediaType | domain.MessageServiceType | _PayloadType


class SQLAPayloadType(TypeDecorator[MessagePayloadType]):
    impl = String
    cache_ok = True

    _values_to_members: ClassVar[Mapping[str, MessagePayloadType]] = {
        str(member.value): member
        for member in _members
    }
    _members_to_values: ClassVar[Mapping[MessagePayloadType, str]] = {
        member: str(member.value)
        for member in _members
    }

    def process_bind_param(
        self,
        value: domain.MessageMediaType | domain.MessageServiceType | _PayloadType | None,
        dialect: Dialect,
    ) -> str | None:
        if value is None:
            return None
        return self._members_to_values[value]

    def process_result_value(
        self,
        value: str | None,
        dialect: Dialect
    ) -> domain.MessageMediaType | domain.MessageServiceType | _PayloadType | None:
        if value is None:
            return None
        return self._values_to_members[value]


# _members_str = tuple(str(member.value) for member in _members)
# if (_duplicates := tuple(member for member in _members_str if _members_str.count(member) > 1)):
#     raise RuntimeError(
#         f"Found duplicate values: {', '.join(_duplicates)}, {SQLAPayloadType.__name__} will not work normally"
#     )


@mapped_as_dataclass(registry)
class Text:
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False, repr=False)
    raw: Mapped[str] = mapped_column(String, nullable=False)
    entities: Mapped[list[TextEntity]] = relationship(lambda: TextEntity, repr=False, default_factory=list)

    __domain_class__ = domain.Text
    __tablename__ = "texts"


@mapped_as_dataclass(registry)
class TextEntity:
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False, repr=False)
    text_id: Mapped[int] = mapped_column(ForeignKey(Text.rowid), nullable=False, init=False, repr=False)
    offset: Mapped[int] = mapped_column(Integer, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[domain.MessageEntityType] = mapped_column(
        Enum(domain.MessageEntityType),
        nullable=False, init=False, repr=False
    )

    __domain_class__ = domain.TextEntity
    __tablename__ = "text_entities"
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_on": "type",
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class Mention(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.MENTION,
    }


@mapped_as_dataclass(registry)
class Hashtag(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.HASHTAG,
    }


@mapped_as_dataclass(registry)
class Cashtag(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.CASHTAG,
    }


@mapped_as_dataclass(registry)
class BotCommand(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.BOT_COMMAND,
    }


@mapped_as_dataclass(registry)
class URL(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.URL,
    }


@mapped_as_dataclass(registry)
class Email(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.EMAIL,
    }


@mapped_as_dataclass(registry)
class PhoneNumber(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.PHONE_NUMBER,
    }


@mapped_as_dataclass(registry)
class Bold(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.BOLD,
    }


@mapped_as_dataclass(registry)
class Italic(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.ITALIC,
    }


@mapped_as_dataclass(registry)
class Underline(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.UNDERLINE,
    }


@mapped_as_dataclass(registry)
class Strikethrough(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.STRIKETHROUGH,
    }


@mapped_as_dataclass(registry)
class Spoiler(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.SPOILER,
    }


@mapped_as_dataclass(registry)
class Code(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.CODE,
    }


@mapped_as_dataclass(registry)
class Pre(TextEntity):
    rowid: Mapped[int] = mapped_column(ForeignKey(TextEntity.rowid), primary_key=True, autoincrement=False, init=False)
    language: Mapped[str | None] = mapped_column(String, nullable=True)

    __tablename__ = "texts_pres"
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.PRE,
    }


@mapped_as_dataclass(registry)
class BlockQuote(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.BLOCKQUOTE,
    }


@mapped_as_dataclass(registry)
class TextLink(TextEntity):
    rowid: Mapped[int] = mapped_column(
        ForeignKey(TextEntity.rowid),
        primary_key=True,
        autoincrement=False,
        init=False,
        repr=False
    )
    url: Mapped[str] = mapped_column(String, nullable=False)

    __tablename__ = "texts_links"
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.TEXT_LINK,
    }


@mapped_as_dataclass(registry)
class TextMention(TextEntity):
    rowid: Mapped[int] = mapped_column(ForeignKey(TextEntity.rowid), primary_key=True, autoincrement=False, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), nullable=False, init=False)
    user: Mapped[User] = relationship(User, uselist=False)

    __tablename__ = "texts_mentions"
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.TEXT_MENTION,
    }


@mapped_as_dataclass(registry)
class BankCard(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.BANK_CARD,
    }


@mapped_as_dataclass(registry)
class CustomEmojiEntity(TextEntity):
    rowid: Mapped[int] = mapped_column(ForeignKey(TextEntity.rowid), primary_key=True, autoincrement=False, init=False)
    custom_emoji_id: Mapped[int] = mapped_column(ForeignKey(CustomEmoji.tg_id), nullable=False, init=False)
    custom_emoji: Mapped[CustomEmoji] = relationship(CustomEmoji, uselist=False)

    __tablename__ = "texts_custom_emojis"
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.CUSTOM_EMOJI,
    }


@mapped_as_dataclass(registry)
class UnknownEntity(TextEntity):
    __mapper_args__ = {
        "polymorphic_identity": domain.MessageEntityType.UNKNOWN,
    }


class MediaType(enum.StrEnum):
    Disappeared = "Disappeared"
    Thumbnail = "Thumbnail"
    Sticker = "Sticker"
    Audio = "Audio"
    Document = "Document"
    Photo = "Photo"
    Animation = "Animation"
    Video = "Video"
    Voice = "Voice"
    VideoNote = "VideoNote"
    Game = "Game"
    StarsGiveaway = "StarsGiveaway"
    SubscriptionsGiveaway = "SubscriptionsGiveaway"
    StarsGiveawayWinners = "StarsGiveawayWinners"
    SubscriptionsGiveawayWinners = "SubscriptionsGiveawayWinners"
    Story = "Story"
    Invoice = "Invoice"
    PaidMedia = "PaidMedia"
    Checklist = "Checklist"
    Contact = "Contact"
    Location = "Location"
    LiveLocation = "LiveLocation"
    BusinessLocation = "BusinessLocation"
    Venue = "Venue"
    WebPage = "WebPage"
    WebPageEmpty = "WebPageEmpty"
    WebPagePending = "WebPagePending"
    Poll = "Poll"
    Quiz = "Quiz"
    Dice = "Dice"


@mapped_as_dataclass(registry)
class _Media():
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    _type: Mapped[MediaType] = mapped_column(Enum(MediaType), init=False)

    __domain_class__: ClassVar[type[Any]] = domain._Media
    __tablename__ = "medias"
    __mapper_args__ = {
        "polymorphic_on": "_type",
        "polymorphic_abstract": True,
    }


# @mapped_as_dataclass(registry)
# class File:
#     file_unique_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
#     file_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
#     file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, kw_only=True, default=None)

#     __domain_class__ = domain.File
#     __tablename__ = "files"


@mapped_as_dataclass(registry)
class FileMedia(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    _type: Mapped[MediaType] = mapped_column(Enum(MediaType), init=False)
    file_id: Mapped[str] = mapped_column(String, nullable=False)
    file_unique_id: Mapped[str] = mapped_column(String, nullable=False)

    __domain_class__: ClassVar[type[Any]] = domain.FileMedia
    __tablename__ = "medias_files"
    __mapper_args__ = {
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class Thumbnail(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    __domain_class__ = domain.Thumbnail
    __tablename__ = "thumbnails"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Thumbnail,
    }


@mapped_as_dataclass(registry)
class Sticker(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    is_animated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_video: Mapped[bool] = mapped_column(Boolean, nullable=False)
    file_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)
    emoji: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    set_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    thumbs: Mapped[list[Thumbnail]] = relationship(
        Thumbnail,
        secondary=lambda: stickers_thumbs,
        default_factory=list
    )

    __domain_class__ = domain.Sticker
    __tablename__ = "stickers"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Sticker,
    }


stickers_thumbs: Table = Table(
    "stickers_thumbs",
    registry.metadata,
    Column("sticker_id", ForeignKey(Sticker.id), primary_key=True),
    Column("thumb_id", ForeignKey(Thumbnail.id), primary_key=True),
)


@mapped_as_dataclass(registry)
class Audio(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    performer: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    title: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)

    thumbs: Mapped[list[Thumbnail]] = relationship(
        Thumbnail,
        secondary=lambda: audios_thumbs,
        default_factory=list
    )

    __domain_class__ = domain.Audio
    __tablename__ = "audios"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Audio,
    }


audios_thumbs: Table = Table(
    "audios_thumbs",
    registry.metadata,
    Column("audio_id", ForeignKey(Audio.id), primary_key=True),
    Column("thumb_id", ForeignKey(Thumbnail.id), primary_key=True),
)


@mapped_as_dataclass(registry)
class Document(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    file_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)

    thumbs: Mapped[list[Thumbnail]] = relationship(
        Thumbnail,
        secondary=lambda: documents_thumbs,
        default_factory=list
    )

    __domain_class__ = domain.Document
    __tablename__ = "document"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Document,
    }


documents_thumbs: Table = Table(
    "documents_thumbs",
    registry.metadata,
    Column("document_id", ForeignKey(Document.id), primary_key=True),
    Column("thumb_id", ForeignKey(Thumbnail.id), primary_key=True),
)


@mapped_as_dataclass(registry)
class Photo(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)
    ttl_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    thumbs: Mapped[list[Thumbnail]] = relationship(
        Thumbnail,
        secondary=lambda: photos_thumbs,
        default_factory=list
    )

    __domain_class__ = domain.Photo
    __tablename__ = "photos"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Photo,
    }


photos_thumbs: Table = Table(
    "photos_thumbs",
    registry.metadata,
    Column("photo_id", ForeignKey(Photo.id), primary_key=True),
    Column("thumb_id", ForeignKey(Thumbnail.id), primary_key=True),
)


@mapped_as_dataclass(registry)
class Animation(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)

    thumbs: Mapped[list[Thumbnail]] = relationship(
        Thumbnail,
        secondary=lambda: animations_thumbs,
        default_factory=list
    )

    __domain_class__ = domain.Animation
    __tablename__ = "animations"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Animation,
    }


animations_thumbs: Table = Table(
    "animations_thumbs",
    registry.metadata,
    Column("animation_id", ForeignKey(Animation.id), primary_key=True),
    Column("thumb_id", ForeignKey(Thumbnail.id), primary_key=True),
)


@mapped_as_dataclass(registry)
class Video(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    supports_streaming: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    ttl_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)

    thumbs: Mapped[list[Thumbnail]] = relationship(
        Thumbnail,
        secondary=lambda: videos_thumbs,
        default_factory=list
    )

    __domain_class__ = domain.Video
    __tablename__ = "videos"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Video,
    }


videos_thumbs: Table = Table(
    "videos_thumbs",
    registry.metadata,
    Column("video_id", ForeignKey(Video.id), primary_key=True),
    Column("thumb_id", ForeignKey(Thumbnail.id), primary_key=True),
)


@mapped_as_dataclass(registry)
class Voice(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    waveform: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)

    __domain_class__ = domain.Voice
    __tablename__ = "voices"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Voice,
    }


@mapped_as_dataclass(registry)
class VideoNote(FileMedia):
    id: Mapped[int] = mapped_column(ForeignKey(FileMedia.id), primary_key=True, autoincrement=False, init=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None)

    thumbs: Mapped[list[Thumbnail]] = relationship(
        Thumbnail,
        secondary=lambda: videonotes_thumbs,
        default_factory=list,
    )

    __domain_class__ = domain.VideoNote
    __tablename__ = "videonotes"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.VideoNote,
    }


videonotes_thumbs: Table = Table(
    "videonotes_thumbs",
    registry.metadata,
    Column("document_id", ForeignKey(VideoNote.id), primary_key=True),
    Column("thumb_id", ForeignKey(Thumbnail.id), primary_key=True),
)


@mapped_as_dataclass(registry)
class DisappearedMedia(_Media):
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Disappeared,
    }


@mapped_as_dataclass(registry)
class Contact(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    vcard: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    __domain_class__ = domain.Contact
    __tablename__ = "contacts"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Contact,
    }


@mapped_as_dataclass(registry)
class Location(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)

    __domain_class__ = domain.Location
    __tablename__ = "locations"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Location,
    }


@mapped_as_dataclass(registry)
class LiveLocation(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    location_id: Mapped[int] = mapped_column(ForeignKey(Location.id), nullable=False, init=False)
    location: Mapped[Location] = relationship(Location, foreign_keys=[location_id], uselist=False)
    heading: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    live_period: Mapped[int] = mapped_column(Integer, nullable=False, kw_only=True)
    proximity_alert_radius: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None, kw_only=True)

    __domain_class__ = domain.LiveLocation
    __tablename__ = "live_locations"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.LiveLocation,
    }


@mapped_as_dataclass(registry)
class BusinessLocation(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    location_id: Mapped[int | None] = mapped_column(ForeignKey(Location.id), nullable=False, init=False)
    location: Mapped[Location | None] = relationship(Location, foreign_keys=[location_id], uselist=False, default=None)

    __domain_class__ = domain.BusinessLocation
    __tablename__ = "business_locations"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.BusinessLocation,
    }


@mapped_as_dataclass(registry)
class Venue(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    location_id: Mapped[int] = mapped_column(ForeignKey(Location.id), nullable=False, init=False)
    location: Mapped[Location] = relationship(Location, foreign_keys=[location_id], uselist=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    foursquare_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    foursquare_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    __domain_class__ = domain.Venue
    __tablename__ = "venues"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Venue,
    }


@mapped_as_dataclass(registry)
class WebPage(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    tg_id: Mapped[str] = mapped_column(String)  # TODO: enable unique when versioning will be done

    __domain_class__ = domain.WebPage
    __tablename__ = "webpages"
    __mapper_args__ = {
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class WebPageEmpty(WebPage):
    __mapper_args__ = {
        "polymorphic_identity": MediaType.WebPageEmpty,
    }


@mapped_as_dataclass(registry)
class WebPagePending(WebPage):
    __mapper_args__ = {
        "polymorphic_identity": MediaType.WebPagePending,
    }


@mapped_as_dataclass(registry)
class WebPageDetails(WebPage):
    id: Mapped[int] = mapped_column(ForeignKey(WebPage.id), primary_key=True, autoincrement=False, init=False)
    # tg_id: Mapped[str] = mapped_column(ForeignKey(WebPage.tg_id), primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    display_url: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    site_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    title: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    description: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    audio_id: Mapped[int | None] = mapped_column(ForeignKey(Audio.id), nullable=True, init=False)
    audio: Mapped[Audio | None] = relationship(Audio, uselist=False, default=None)
    document_id: Mapped[int | None] = mapped_column(ForeignKey(Document.id), nullable=True, init=False)
    document: Mapped[Document | None] = relationship(Document, uselist=False, default=None)
    photo_id: Mapped[int | None] = mapped_column(ForeignKey(Photo.id), nullable=True, init=False)
    photo: Mapped[Photo | None] = relationship(Photo, uselist=False, default=None)
    animation_id: Mapped[int | None] = mapped_column(ForeignKey(Animation.id), nullable=True, init=False)
    animation: Mapped[Animation | None] = relationship(Animation, uselist=False, default=None)
    video_id: Mapped[int | None] = mapped_column(ForeignKey(Video.id), nullable=True, init=False)
    video: Mapped[Video | None] = relationship(Video, uselist=False, default=None)
    embed_url: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    embed_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    embed_width: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    embed_height: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    author: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    __domain_class__ = domain.WebPage
    __tablename__ = "webpage_details"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.WebPage,
    }


@mapped_as_dataclass(registry)
class PollLike(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    tg_id: Mapped[int]
    question_id: Mapped[int] = mapped_column(ForeignKey(Text.rowid), nullable=False, init=False)
    question: Mapped[Text] = relationship(Text, uselist=False)
    is_anonymous: Mapped[bool | None]
    open_period: Mapped[int | None]
    close_date: Mapped[dt | None]
    total_voter_count: Mapped[int]
    options: Mapped[list[PollOption]] = relationship(lambda: PollOption, uselist=True)

    __domain_class__: ClassVar[type] = domain.PollLike
    __tablename__ = "polllike_info"
    __mapper_args__ = {
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class PollOption:
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    poll_id: Mapped[int] = mapped_column(ForeignKey(_Media.id), init=False)
    text_id: Mapped[int] = mapped_column(ForeignKey(Text.rowid), nullable=False, init=False)
    text: Mapped[Text] = relationship(Text, uselist=False)
    # voter_count: int

    __domain_class__ = domain.PollOption
    __tablename__ = "polllike_options"


@mapped_as_dataclass(registry)
class Poll(PollLike):
    id: Mapped[int] = mapped_column(ForeignKey(PollLike.id), primary_key=True, autoincrement=False, init=False)
    allows_multiple_answers: bool

    __domain_class__ = domain.Poll
    __tablename__ = "polls"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Poll,
    }


@mapped_as_dataclass(registry)
class Quiz(PollLike):
    id: Mapped[int] = mapped_column(ForeignKey(PollLike.id), primary_key=True, autoincrement=False, init=False)
    # explanation: Text

    __domain_class__ = domain.Quiz
    __tablename__ = "quizes"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Quiz,
    }


@mapped_as_dataclass(registry)
class Dice(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    emoji: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)

    __domain_class__ = domain.Dice
    __tablename__ = "dices"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Dice,
    }


@mapped_as_dataclass(registry)
class SharedGame(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    game_id: Mapped[int] = mapped_column(Integer, nullable=False)  # TODO: enable unique after versioning done?

    __domain_class__ = domain.Game
    __tablename__ = "games"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Game,
    }


@mapped_as_dataclass(registry)
class GameInfo():
    tg_id: Mapped[int] = mapped_column(ForeignKey(SharedGame.game_id), primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    photo_id: Mapped[int] = mapped_column(ForeignKey(Photo.id), nullable=False)
    photo: Mapped[Photo] = relationship(Photo)
    animation_id: Mapped[int] = mapped_column(ForeignKey(Animation.id), nullable=True, default=None)
    animation: Mapped[Animation | None] = relationship(Animation, default=None)

    __domain_class__ = domain.Game
    __tablename__ = "game_infos"


class SemicolonSeparated(TypeDecorator[tuple[str, ...]]):
    impl = String
    cache_ok = True

    _separator = ';'
    _pattern = re.compile(rf'(?:[^{re.escape(_separator)}\\]|\\.)+')

    def process_bind_param(
        self,
        value: tuple[str, ...] | None,
        dialect: Dialect,
    ) -> str | None:
        if value is None:
            return None
        return ";".join(s.replace('\\', '\\\\').replace(';', '\\;') for s in value)

    def process_result_value(
        self,
        value: str | None,
        dialect: Dialect,
    ) -> tuple[str, ...] | None:
        if value is None:
            return None
        return tuple(
            s.replace('\\;', ';').replace('\\\\', '\\')
            for s in self._pattern.findall(value)
        )


@mapped_as_dataclass(registry)
class Giveaway(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    channels: Mapped[list[Channel]] = relationship(
        Channel, secondary=lambda: GiveawayChannelRequirement.__table__,
        default_factory=list, kw_only=True
    )
    until_date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=None, kw_only=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True, default=None, kw_only=True)
    only_new_subscribers: Mapped[bool | None] = mapped_column(Boolean, default=None, nullable=True, kw_only=True)
    only_for_countries: Mapped[tuple[str, ...] | None] = mapped_column(SemicolonSeparated, nullable=True, default=None, kw_only=True)  # noqa: E501
    winners_are_visible: Mapped[bool] = mapped_column(Boolean, kw_only=True)

    __domain_class__: ClassVar[type[Any]] = domain.Giveaway
    __tablename__ = "giveaways"
    __mapper_args__ = {
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class GiveawayChannelRequirement:
    giveaway_id: Mapped[int] = mapped_column(ForeignKey(Giveaway.id), primary_key=True)
    required_channel_id: Mapped[int] = mapped_column(ForeignKey(Channel.tg_id), primary_key=True)

    __table__: ClassVar[Table]
    __tablename__ = "giveaways_required_channels"


@mapped_as_dataclass(registry)
class StarsGiveaway(Giveaway):
    id: Mapped[int] = mapped_column(ForeignKey(Giveaway.id), primary_key=True, autoincrement=False, init=False)
    stars: int

    __domain_class__ = domain.StarsGiveaway
    __tablename__ = "star_giveaways"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.StarsGiveaway,
    }


@mapped_as_dataclass(registry)
class SubscriptionsGiveaway(Giveaway):
    id: Mapped[int] = mapped_column(ForeignKey(Giveaway.id), primary_key=True, autoincrement=False, init=False)
    quantity: int
    months: int

    __domain_class__ = domain.SubscriptionsGiveaway
    __tablename__ = "subs_giveaways"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.SubscriptionsGiveaway,
    }


@mapped_as_dataclass(registry)
class GiveawayWinners(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), init=False)
    chat: Mapped[Chat] = relationship(Chat, uselist=False)
    giveaway_message_id: Mapped[int]
    winners_selection_date: Mapped[dt]
    quantity: Mapped[int]
    winner_count: Mapped[int]
    unclaimed_prize_count: Mapped[int]
    winners: Mapped[list[User]] = relationship(
        User,
        secondary=lambda: giveaway_winners_users,
    )
    # giveaway_message: Optional["types.Message"] = None  # pyro trying to get message from id internally
    was_refunded: Mapped[bool] = mapped_column(Boolean, kw_only=True)

    __domain_class__: ClassVar[type[Any]] = domain.GiveawayWinners
    __tablename__ = "giveaway_winners"
    __mapper_args__ = {
        "polymorphic_abstract": True,
    }


giveaway_winners_users: Table = Table(
    "giveaway_winners_users",
    registry.metadata,
    Column("giweaway_winners_id", ForeignKey(GiveawayWinners.id), primary_key=True),
    Column("user_id", ForeignKey(User.tg_id), primary_key=True),
)


@mapped_as_dataclass(registry)
class StarsGiveawayWinners(GiveawayWinners):
    id: Mapped[int] = mapped_column(ForeignKey(GiveawayWinners.id), primary_key=True, autoincrement=False, init=False)
    prize_star_count: Mapped[int]

    __domain_class__ = domain.StarsGiveawayWinners
    __tablename__ = "star_giveaway_winners"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.StarsGiveawayWinners,
    }


@mapped_as_dataclass(registry)
class SubscriptionsGiveawayWinners(GiveawayWinners):
    id: Mapped[int] = mapped_column(ForeignKey(GiveawayWinners.id), primary_key=True, autoincrement=False, init=False)
    premium_subscription_month_count: int

    __domain_class__ = domain.SubscriptionsGiveawayWinners
    __tablename__ = "subs_giveaway_winners"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.SubscriptionsGiveawayWinners,
    }


@mapped_as_dataclass(registry)
class Story(_Media):
    # TODO: wtf is this shit???
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    tg_id: int
    caption: Text | None
    type: Literal[domain.MessageMediaType.PHOTO, domain.MessageMediaType.VIDEO] | None
    date: dt

    __domain_class__ = domain.Story
    __tablename__ = "stories"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Story,
    }


@mapped_as_dataclass(registry)
class Invoice(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    # tg_id: int
    currency: str  # ISO 4217
    is_test: bool
    title: str | None = None
    description: str | None = None
    total_amount: int | None = None
    start_parameter: str | None = None
    # prices: Sequence[LabeledPrice] | None = None
    is_name_requested: bool | None = None
    is_phone_requested: bool | None = None
    is_email_requested: bool | None = None
    is_shipping_address_requested: bool | None = None
    is_flexible: bool | None = None
    is_phone_to_provider: bool | None = None
    is_email_to_provider: bool | None = None
    is_recurring: bool | None = None
    max_tip_amount: int | None = None
    # suggested_tip_amounts: Sequence[int] | None = None
    terms_url: str | None = None

    __domain_class__ = domain.Invoice
    __tablename__ = "invoices"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Invoice,
    }


# @mapped_as_dataclass(registry)
# class LabeledPrice:
#     label: str
#     amount: int

#     __domain_class__ = domain.LabeledPrice


@mapped_as_dataclass(registry)
class PaidMedia(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    stars_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    # media: Sequence[Photo | Video] | Sequence[PaidMediaPreview]

    __domain_class__ = domain.PaidMedia
    __tablename__ = "paid_medias"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.PaidMedia,
    }


@mapped_as_dataclass(registry)
class PaidMediaPreview:
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    paid_media_id: Mapped[int] = mapped_column(ForeignKey(PaidMedia.id), nullable=False, init=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    thumbnail: Mapped[StrippedThumbnail | None] = relationship(
        lambda: StrippedThumbnail,
        uselist=False, default=None,
    )

    __domain_class__ = domain.PaidMediaPreview
    __tablename__ = "paid_media_previews"


@mapped_as_dataclass(registry)
class StrippedThumbnail:
    rowid: Mapped[int] = mapped_column(
        ForeignKey(PaidMediaPreview.rowid),
        primary_key=True, autoincrement=False, init=False
    )
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    __domain_class__ = domain.StrippedThumbnail
    __tablename__ = "stripped_thumbnails"


@mapped_as_dataclass(registry)
class Checklist(_Media):
    id: Mapped[int] = mapped_column(ForeignKey(_Media.id), primary_key=True, autoincrement=False, init=False)
    title: Text
    tasks: Sequence[ChecklistTask]
    others_can_add_tasks: bool | None = None
    can_add_tasks: bool | None = None
    others_can_mark_tasks_as_done: bool | None = None
    can_mark_tasks_as_done: bool | None = None

    __domain_class__ = domain.Checklist
    __tablename__ = "checklists"
    __mapper_args__ = {
        "polymorphic_identity": MediaType.Checklist,
    }


@mapped_as_dataclass(registry)
class ChecklistTask:
    id: Mapped[int] = mapped_column(ForeignKey(Checklist.id), primary_key=True, autoincrement=False, init=False)
    tg_id: Mapped[int]
    text_id: Mapped[int] = mapped_column(ForeignKey(Text.rowid), nullable=False, init=False)
    text: Mapped[Text] = relationship(Text, uselist=False)
    completed_by_id: Mapped[int | None] = mapped_column(ForeignKey(Chat.tg_id), nullable=True, init=False)
    completed_by: Mapped[Chat | None] = relationship(Chat, uselist=False, default=False)
    completion_date: Mapped[dt | None] = mapped_column(DateTime, nullable=True, default=False)

    __domain_class__ = domain.ChecklistTask
    __tablename__ = "checklists_tasks"


Media: TypeAlias = (
    Audio
    | Document
    | Photo
    | Sticker
    | Video
    | Animation
    | Voice
    | VideoNote
    | Contact
    | Location
    | LiveLocation
    | BusinessLocation
    | Venue
    | Poll
    | Quiz
    | WebPage
    | Dice
    | SharedGame
    | StarsGiveaway
    | SubscriptionsGiveaway
    | StarsGiveawayWinners
    | SubscriptionsGiveawayWinners
    | Story
    | Invoice
    | PaidMedia
    | Checklist
    | DisappearedMedia
)


@enum.unique
class PayloadType(enum.StrEnum):
    Empty = "Empty"
    Text = "Text"
    Media = "Media"
    Forwarded = "Forwarded"

    # service messages
    Unsupported = "Unsupported"
    Borked = "Borked"
    CustomAction = "CustomAction"
    NewChatMembers = "NewChatMembers"
    LeftChatMember = "LeftChatMember"
    NewChatTitle = "NewChatTitle"
    NewChatPhoto = "NewChatPhoto"
    ChatPhotoDeleted = "ChatPhotoDeleted"
    ForumTopicCreated = "ForumTopicCreated"
    ForumTopicClosed = "ForumTopicClosed"
    ForumTopicReopened = "ForumTopicReopened"
    ForumTopicEdited = "ForumTopicEdited"
    GeneralForumTopicHidden = "GeneralForumTopicHidden"
    GeneralForumTopicUnhidden = "GeneralForumTopicUnhidden"
    GroupCreated = "GroupCreated"
    ChannelCreated = "ChannelCreated"
    SupergroupCreated = "SupergroupChatCreated"
    MigrateToSupergroup = "MigrateToSupergroup"
    MigrateFromGroup = "MigrateFromGroup"
    MessagePinned = "MessagePinned"
    GameHighScore = "GameHighScore"
    GiveawayCreated = "GiveawayCreated"
    GiveawayCompleted = "GiveawayCompleted"
    PremiumGiftCode = "PremiumGiftCode"
    GiftedPremium = "GiftedPremium"
    GiftedStars = "GiftedStars"
    GiftedTON = "GiftedTON"
    VideoChatStarted = "VideoChatStarted"
    VideoChatEnded = "VideoChatEnded"
    VideoChatScheduled = "VideoChatScheduled"
    VideoChatMembersInvited = "VideoChatMembersInvited"
    PhoneCallStarted = "PhoneCallStarted"
    PhoneCallEnded = "PhoneCallEnded"
    WebAppData = "WebAppData"
    UsersShared = "UsersShared"
    ChatShared = "ChatShared"
    SuccessfulSubscriptionPayment = "SuccessfulSubscriptionPayment"
    SuccessfulPayment = "SuccessfulPayment"
    RefundedPayment = "RefundedPayment"
    SuggestedPostApprovalFailed = "SuggestedPostApprovalFailed"
    SuggestedPostApproved = "SuggestedPostApproved"
    SuggestedPostDeclined = "SuggestedPostDeclined"
    SuggestedPostPaid = "SuggestedPostPaid"
    SuggestedPostRefunded = "SuggestedPostRefunded"
    SetMessageAutodeleteTime = "SetMessageAutodeleteTime"
    MessageAutodeleteDisabled = "MessageAutodeleteDisabled"
    ChatBoost = "ChatBoost"
    Gifted = "Gifted"
    ConnectedWebsite = "Connectedwebsite"
    WriteAccessAllowed = "WriteAccessAllowed"
    ScreenshotTaken = "ScreenshotTaken"
    ContactRegistered = "ContactRegistered"
    ProximityAlertTriggered = "ProximityAlertTriggered"
    HistoryCleared = "HistoryCleared"
    SuggestedProfilePhoto = "SuggestedProfilePhoto"
    SuggestedBirthday = "SuggestedBirthday"
    SetChatBackground = "SetChatBackground"
    SetChatEmojiTheme = "SetChatEmojiTheme"
    SetChatGiftTheme = "SetChatGiftTheme"
    GiveawayPrizeStars = "GiveawayPrizeStars"
    PaidMessagesRefunded = "PaidMessagesRefunded"
    PaidMessagesPriceChanged = "PaidMessagesPriceChanged"
    DirectMessagesPriceChanged = "DirectMessagesPriceChanged"
    ChecklistTasksDone = "ChecklistTasksDone"
    ChecklistTasksAdded = "ChecklistTasksAdded"
    UpgradedGiftPurchaseOffer = "UpgradedGiftPurchaseOffer"
    UpgradedGiftPurchaseOfferRejected = "UpgradedGiftPurchaseOfferRejected"


@mapped_as_dataclass(registry)
class Payload:
    chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    type: Mapped[PayloadType] = mapped_column(Enum(PayloadType), nullable=False, init=False)

    __domain_class__: ClassVar[DomainClass] = domain.Message
    __tablename__ = "messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (BoundMessage.chat_id, BoundMessage.msg_id),
        ),
    )
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_on": "type",
    }


@mapped_as_dataclass(registry)
class EmptyMessage(Payload):
    __domain_class__ = domain.Message
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.Empty,
    }


@mapped_as_dataclass(registry)
class TextMessage(Payload):
    chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    text_id: Mapped[int] = mapped_column(ForeignKey(Text.rowid), nullable=False, init=False)
    text: Mapped[Text] = relationship(Text, uselist=False)

    __domain_class__ = domain.TextMessage
    __tablename__ = "text_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (Payload.chat_id, Payload.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.Text,
    }


@mapped_as_dataclass(registry)
class MediaMessage(Payload):
    chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    text_id: Mapped[int | None] = mapped_column(ForeignKey(Text.rowid), nullable=True, init=False)
    caption: Mapped[Text | None] = relationship(Text, uselist=False)
    media_id: Mapped[int] = mapped_column(ForeignKey(_Media.id), nullable=False, init=False)
    media: Mapped[_Media] = relationship(_Media, uselist=False)
    media_group_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_media_spoiler: Mapped[bool | None]

    __domain_class__ = domain.MediaMessage
    __tablename__ = "media_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (Payload.chat_id, Payload.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.Media,
    }


@mapped_as_dataclass(registry)
class _ServiceMessage(Payload):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)

    __domain_class__: ClassVar[DomainClass] = domain.ServiceMessage
    __tablename__ = "service_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (Payload.chat_id, Payload.msg_id),
        ),
    )
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_abstract": True,
        "polymorphic_on": "type",
    }


@mapped_as_dataclass(registry)
class ServiceMessage(_ServiceMessage):
    __domain_class__: ClassVar[type[Any]] = domain.ServiceMessage
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class ServiceMessageBorked(ServiceMessage):
    __domain_class__: ClassVar[type[Any]] = domain.ServiceMessage
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": PayloadType.Borked,
    }


@mapped_as_dataclass(registry)
class UnsupportedServiceMessage(ServiceMessage):
    __domain_class__: ClassVar[type[Any]] = domain.UnsupportedServiceMessage
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": PayloadType.Unsupported,
    }


@mapped_as_dataclass(registry)
class CustomAction(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    message: Mapped[str] = mapped_column(String, nullable=False)

    __domain_class__: ClassVar[type[Any]] = domain.CustomAction
    __tablename__ = "custom_action_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": PayloadType.CustomAction,
    }


@mapped_as_dataclass(registry)
class NewChatMembers(ServiceMessage):
    new_chat_members: Mapped[list[User]] = relationship(User, secondary=lambda: NewChatMember.__table__)

    __domain_class__ = domain.NewChatMembers
    # __tablename__ = "new_chat_members_messages"
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.NewChatMembers,
    }


@mapped_as_dataclass(registry)
class NewChatMember:
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), primary_key=True)

    __tablename__ = "new_chat_members"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (NewChatMembers.chat_id, NewChatMembers.msg_id),
        ),
    )
    __table__: ClassVar[Table]


@mapped_as_dataclass(registry)
class LeftChatMember(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    left_user: Mapped[User] = relationship(User, uselist=False)
    left_user_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), init=False)

    __domain_class__ = domain.LeftChatMember
    __tablename__ = "left_chat_member_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.LeftChatMember,
    }


@mapped_as_dataclass(registry)
class NewChatTitle(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    new_chat_title: Mapped[str] = mapped_column(String, nullable=False)

    __domain_class__ = domain.NewChatTitle
    __tablename__ = "new_chat_title_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.NewChatTitle,
    }


@mapped_as_dataclass(registry)
class NewChatPhoto(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    new_chat_photo: Mapped[Photo | None] = relationship(Photo, uselist=False)
    new_chat_photo_id: Mapped[int | None] = mapped_column(ForeignKey(Photo.id), nullable=True, init=False)

    __domain_class__ = domain.NewChatPhoto
    __tablename__ = "new_chat_photo_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.NewChatPhoto,
    }


@mapped_as_dataclass(registry)
class ChatPhotoDeleted(ServiceMessage):
    __domain_class__ = domain.ChatPhotoDeleted
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ChatPhotoDeleted,
    }


@mapped_as_dataclass(registry)
class ForumTopicCreated(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    topic_id: Mapped[int]
    title: Mapped[str]
    icon_color: Mapped[int]
    custom_emoji_id: Mapped[int | None] = mapped_column(ForeignKey(CustomEmoji.tg_id), nullable=True, init=False)
    custom_emoji: Mapped[CustomEmoji | None] = relationship(CustomEmoji, uselist=False, default=None)

    __domain_class__ = domain.ForumTopicCreated
    __tablename__ = "forum_topic_creation_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ForumTopicCreated,
    }


@mapped_as_dataclass(registry)
class ForumTopicClosed(ServiceMessage):
    __domain_class__ = domain.ForumTopicClosed
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ForumTopicClosed,
    }


@mapped_as_dataclass(registry)
class ForumTopicReopened(ServiceMessage):
    __domain_class__ = domain.ForumTopicReopened
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ForumTopicReopened,
    }


@mapped_as_dataclass(registry)
class ForumTopicEdited(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    icon_color: Mapped[int | None] = mapped_column(String, nullable=True)
    custom_emoji_id: Mapped[int | None] = mapped_column(ForeignKey(CustomEmoji.tg_id), nullable=True, init=False)
    custom_emoji: Mapped[CustomEmoji | None] = relationship(CustomEmoji, uselist=False, default=None)
    is_closed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    is_hidden: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    """
    True, if the topic is hidden.
    Valid only for the "General" topic with id=1
    """

    __domain_class__ = domain.ForumTopicEdited
    __tablename__ = "forum_topic_edition_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ForumTopicEdited,
    }


@mapped_as_dataclass(registry)
class GeneralForumTopicHidden(ServiceMessage):
    __domain_class__ = domain.GeneralForumTopicHidden
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GeneralForumTopicHidden,
    }


@mapped_as_dataclass(registry)
class GeneralForumTopicUnhidden(ServiceMessage):
    __domain_class__ = domain.GeneralForumTopicUnhidden
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GeneralForumTopicUnhidden,
    }


@mapped_as_dataclass(registry)
class GroupCreated(ServiceMessage):
    __domain_class__ = domain.GroupCreated
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GroupCreated,
    }


@mapped_as_dataclass(registry)
class SupergroupCreated(ServiceMessage):
    __domain_class__ = domain.SupergroupCreated
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SupergroupCreated,
    }


@mapped_as_dataclass(registry)
class ChannelCreated(ServiceMessage):
    __domain_class__ = domain.ChannelCreated
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ChannelCreated,
    }


@mapped_as_dataclass(registry)
class MigrateToSupergroup(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    migrate_to_chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), nullable=False, init=False)
    migrate_to_chat: Mapped[Chat] = relationship(Chat, uselist=False)

    __domain_class__ = domain.MigrateToSupergroup
    __tablename__ = "to_supergroup_migration_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.MigrateToSupergroup,
    }


@mapped_as_dataclass(registry)
class MigrateFromGroup(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    migrate_from_chat_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), nullable=False, init=False)
    migrate_from_chat: Mapped[Chat] = relationship(Chat, uselist=False)

    __domain_class__ = domain.MigrateFromGroup
    __tablename__ = "from_group_migration_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.MigrateFromGroup,
    }


@mapped_as_dataclass(registry)
class MessagePinned(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    # TODO: decide on referring to actual messages table
    pinned_message_id: Mapped[int] = mapped_column(Integer, nullable=False)

    __domain_class__ = domain.MessagePinned
    __tablename__ = "message_pins"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.MessagePinned,
    }


@mapped_as_dataclass(registry)
class GameHighScore(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    user: Mapped[User] = relationship(User, uselist=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), nullable=False, init=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    # not actual for message
    # position: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    __domain_class__ = domain.GameHighScore
    __tablename__ = "game_highscore_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GameHighScore,
    }


@mapped_as_dataclass(registry)
class GiveawayCreated(ServiceMessage):
    __domain_class__ = domain.GiveawayCreated
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GiveawayCreated,
    }


@mapped_as_dataclass(registry)
class GiveawayCompleted(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    winner_count: Mapped[int]
    unclaimed_prize_count: Mapped[int]
    giveaway_message_id: Mapped[int]
    # giveaway_message: "types.Message" = None
    is_star_giveaway: Mapped[bool]

    __domain_class__ = domain.GiveawayCompleted
    __tablename__ = "giveaway_completion_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GiveawayCompleted,
    }


@mapped_as_dataclass(registry)
class _MoneyAmount():
    rowid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    currency: Mapped[str]
    amount: Mapped[int]
    is_crypto: Mapped[bool] = mapped_column(Boolean, nullable=False, init=False)

    __domain_class__: ClassVar[Any] = domain.MoneyAmount
    __tablename__ = "money_amounts"
    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_on": "is_crypto",
        "polymorphic_abstract": True,
    }


@mapped_as_dataclass(registry)
class CurrencyAmount(_MoneyAmount):
    currency: Mapped[str] = mapped_column(use_existing_column=True)
    """ISO name"""

    __domain_class__ = domain.CurrencyAmount
    __mapper_args__ = {
        "polymorphic_identity": False,
    }


@mapped_as_dataclass(registry)
class CryptocurrencyAmount(_MoneyAmount):
    __domain_class__ = domain.CryptocurrencyAmount
    __mapper_args__ = {
        "polymorphic_identity": True,
    }


@mapped_as_dataclass(registry)
class PremiumGiftCode(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    # creator: User | Chat
    code: Mapped[str]
    caption_id: Mapped[int | None] = mapped_column(ForeignKey(Text.rowid), nullable=True, init=False)
    caption: Mapped[Text | None] = relationship(Text, uselist=False)
    month_count: Mapped[int]
    day_count: Mapped[int]
    price_id: Mapped[int] = mapped_column(ForeignKey(_MoneyAmount.rowid), nullable=False, init=False)
    price: Mapped[_MoneyAmount] = relationship(_MoneyAmount, uselist=False)
    is_unclaimed: Mapped[bool]
    is_from_giveaway: Mapped[bool]

    __domain_class__ = domain.PremiumGiftCode
    __tablename__ = "premuim_gift_code_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.PremiumGiftCode,
    }


@mapped_as_dataclass(registry)
class GiftedPremium(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), nullable=False, init=False)
    receiver: Mapped[User] = relationship(User, foreign_keys=[receiver_id])
    giftter_id: Mapped[int | None] = mapped_column(ForeignKey(User.tg_id), nullable=True, init=False)
    gifter: Mapped[User | None] = relationship(User, foreign_keys=[giftter_id])
    price_id: Mapped[int] = mapped_column(ForeignKey(_MoneyAmount.rowid), nullable=False, init=False)
    price: Mapped[_MoneyAmount] = relationship(_MoneyAmount, uselist=False)
    month_count: Mapped[int]
    day_count: Mapped[int]
    sticker_id: Mapped[int | None] = mapped_column(ForeignKey(Sticker.id), nullable=True, init=False)
    sticker: Mapped[Sticker | None] = relationship(Sticker, uselist=False)
    caption_id: Mapped[int | None] = mapped_column(ForeignKey(Text.rowid), nullable=True, init=False)
    caption: Mapped[Text | None] = relationship(Text, uselist=False)

    __domain_class__ = domain.GiftedPremium
    __tablename__ = "premuim_gift_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GiftedPremium,
    }


@mapped_as_dataclass(registry)
class GiftedStars(ServiceMessage):
    __domain_class__ = domain.GiftedStars
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GiftedStars,
    }


@mapped_as_dataclass(registry)
class GiftedTON(ServiceMessage):
    __domain_class__ = domain.GiftedTON
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GiftedTON,
    }


@mapped_as_dataclass(registry)
class VideoChatScheduled(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    start_date: Mapped[dt] = mapped_column(DateTime, nullable=False)

    __domain_class__ = domain.VideoChatScheduled
    __tablename__ = "videochat_scheduled_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.VideoChatScheduled,
    }


@mapped_as_dataclass(registry)
class VideoChatStarted(ServiceMessage):
    __domain_class__ = domain.VideoChatStarted
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.VideoChatStarted,
    }


@mapped_as_dataclass(registry)
class VideoChatEnded(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    duratioin: Mapped[int] = mapped_column(Integer, nullable=False)

    __domain_class__ = domain.VideoChatEnded
    __tablename__ = "videochat_ended_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.VideoChatEnded,
    }


@mapped_as_dataclass(registry)
class VideoChatMembersInvited(ServiceMessage):
    video_chat_members_invited: Mapped[list[User]] = relationship(
        User,
        secondary=lambda: VideoChatMemberInvited.__table__
    )

    __domain_class__ = domain.VideoChatMembersInvited
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.VideoChatMembersInvited,
    }


@mapped_as_dataclass(registry)
class VideoChatMemberInvited:
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id), primary_key=True)

    __tablename__ = "videochat_invites"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (VideoChatMembersInvited.chat_id, VideoChatMembersInvited.msg_id),
        ),
    )
    __table__: ClassVar[Table]


@mapped_as_dataclass(registry)
class PhoneCallStarted(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    call_id: Mapped[int]
    is_video: Mapped[bool]

    __domain_class__ = domain.PhoneCallStarted
    __tablename__ = "call_start_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.PhoneCallStarted,
    }


@mapped_as_dataclass(registry)
class PhoneCallEnded(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    call_id: Mapped[int]
    is_video: Mapped[bool]
    reason: Mapped[domain.PhoneCallDiscardReason] = mapped_column(Enum(domain.PhoneCallDiscardReason), nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __domain_class__ = domain.PhoneCallEnded
    __tablename__ = "call_end_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.PhoneCallEnded,
    }


@mapped_as_dataclass(registry)
class WebAppData(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    data: Mapped[str]
    button_text: Mapped[str]

    __domain_class__ = domain.WebAppData
    __tablename__ = "webapp_data_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.WebAppData,
    }


@mapped_as_dataclass(registry)
class UsersShared(ServiceMessage):
    __domain_class__ = domain.UsersShared
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.UsersShared,
    }


@mapped_as_dataclass(registry)
class ChatShared(ServiceMessage):
    __domain_class__ = domain.ChatShared
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ChatShared,
    }


@mapped_as_dataclass(registry)
class SuccessfulPayment(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    currency: Mapped[str]
    total_amount: Mapped[int]
    invoice_slug: Mapped[str | None]

    __domain_class__: ClassVar[type[Any]] = domain.SuccessfulPayment
    __tablename__ = "successful_payment_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuccessfulPayment,
    }


@mapped_as_dataclass(registry)
class SuccessfulSubscriptionPayment(SuccessfulPayment):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    first_time: Mapped[bool]
    subscription_expiration_date: Mapped[dt | None]

    __domain_class__ = domain.SuccessfulSubscriptionPayment
    __tablename__ = "successful_subscription_payment_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (SuccessfulPayment.chat_id, SuccessfulPayment.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuccessfulSubscriptionPayment,
    }


@mapped_as_dataclass(registry)
class RefundedPayment(ServiceMessage):
    __domain_class__ = domain.RefundedPayment
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.RefundedPayment,
    }


@mapped_as_dataclass(registry)
class SuggestedPostApprovalFailed(ServiceMessage):
    __domain_class__ = domain.SuggestedPostApprovalFailed
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuggestedPostApprovalFailed,
    }


@mapped_as_dataclass(registry)
class SuggestedPostApproved(ServiceMessage):
    __domain_class__ = domain.SuggestedPostApproved
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuggestedPostApproved,
    }


@mapped_as_dataclass(registry)
class SuggestedPostDeclined(ServiceMessage):
    __domain_class__ = domain.SuggestedPostDeclined
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuggestedPostDeclined,
    }


@mapped_as_dataclass(registry)
class SuggestedPostPaid(ServiceMessage):
    __domain_class__ = domain.SuggestedPostPaid
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuggestedPostPaid,
    }


@mapped_as_dataclass(registry)
class SuggestedPostRefunded(ServiceMessage):
    __domain_class__ = domain.SuggestedPostRefunded
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuggestedPostRefunded,
    }


@mapped_as_dataclass(registry)
class SetMessageAutodeleteTime(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    message_ttl: Mapped[int]

    __domain_class__ = domain.SetMessageAutodeleteTime
    __tablename__ = "set_autodelete_time_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SetMessageAutodeleteTime,
    }


@mapped_as_dataclass(registry)
class MessageAutodeleteDisabled(ServiceMessage):
    __domain_class__ = domain.MessageAutodeleteDisabled
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.MessageAutodeleteDisabled,
    }


@mapped_as_dataclass(registry)
class ChatBoost(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    amount: Mapped[int]

    __domain_class__ = domain.ChatBoost
    __tablename__ = "chat_boost_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ChatBoost,
    }


@mapped_as_dataclass(registry)
class Gifted(ServiceMessage):
    # TODO: map fields from pyro class
    __domain_class__ = domain.Gifted
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.Gifted,
    }


@mapped_as_dataclass(registry)
class Connectedwebsite(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    site: Mapped[str]  # name 'domain' occupied by module of domain models

    __domain_class__ = domain.ConnectedWebsite
    __tablename__ = "website_connection_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ConnectedWebsite,
    }


@mapped_as_dataclass(registry)
class WriteAccessAllowed(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    from_request: Mapped[bool]
    from_attachment_menu: Mapped[bool]
    web_app_name: Mapped[str | None] = mapped_column(String, nullable=True)

    __domain_class__ = domain.WriteAccessAllowed
    __tablename__ = "write_access_allowance_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.WriteAccessAllowed,
    }


@mapped_as_dataclass(registry)
class ScreenshotTaken(ServiceMessage):
    __domain_class__ = domain.ScreenshotTaken
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ScreenshotTaken,
    }


@mapped_as_dataclass(registry)
class ContactRegistered(ServiceMessage):
    __domain_class__ = domain.ContactRegistered
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ContactRegistered,
    }


@mapped_as_dataclass(registry)
class ProximityAlertTriggered(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    traveler_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), nullable=False, init=False)
    traveler: Mapped[Chat] = relationship(Chat, foreign_keys=[traveler_id], uselist=False)
    watcher_id: Mapped[int] = mapped_column(ForeignKey(Chat.tg_id), nullable=False, init=False)
    watcher: Mapped[Chat] = relationship(Chat, foreign_keys=[watcher_id], uselist=False)
    distance: Mapped[int] = mapped_column(Integer, nullable=False)

    __domain_class__ = domain.ProximityAlertTriggered
    __tablename__ = "proximity_alert_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ProximityAlertTriggered,
    }


@mapped_as_dataclass(registry)
class HistoryCleared(ServiceMessage):
    __domain_class__ = domain.HistoryCleared
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.HistoryCleared,
    }


@mapped_as_dataclass(registry)
class SuggestedProfilePhoto(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    photo_id: Mapped[int] = mapped_column(ForeignKey(Photo.id), nullable=False, init=False)
    photo: Mapped[Photo] = relationship(Photo, uselist=False)

    __domain_class__ = domain.SuggestedProfilePhoto
    __tablename__ = "profile_photo_suggestion_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuggestedProfilePhoto,
    }


@mapped_as_dataclass(registry)
class SuggestedBirthday(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    __domain_class__ = domain.SuggestedBirthday
    __tablename__ = "birthday_suggestion_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SuggestedBirthday,
    }


@mapped_as_dataclass(registry)
class SetChatBackground(ServiceMessage):
    __domain_class__ = domain.SetChatBackground
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SetChatBackground,
    }


@mapped_as_dataclass(registry)
class SetChatEmojiTheme(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    name: Mapped[str]

    __domain_class__ = domain.SetChatEmojiTheme
    __tablename__ = "chat_emoji_theme_set_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SetChatEmojiTheme,
    }


@mapped_as_dataclass(registry)
class SetChatGiftTheme(ServiceMessage):
    __domain_class__ = domain.SetChatGiftTheme
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.SetChatGiftTheme,
    }


@mapped_as_dataclass(registry)
class GiveawayPrizeStars(ServiceMessage):
    __domain_class__ = domain.GiveawayPrizeStars
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.GiveawayPrizeStars,
    }


@mapped_as_dataclass(registry)
class PaidMessagesRefunded(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    messages_count: Mapped[int]
    stars_amount: Mapped[int]

    __domain_class__ = domain.PaidMessagesRefunded
    __tablename__ = "paid_message_refund_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.PaidMessagesRefunded,
    }


@mapped_as_dataclass(registry)
class PaidMessagesPriceChanged(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    new_price: Mapped[int]

    __domain_class__ = domain.PaidMessagesPriceChanged
    __tablename__ = "paid_messages_price_change_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.PaidMessagesPriceChanged,
    }


@mapped_as_dataclass(registry)
class DirectMessagesPriceChanged(ServiceMessage):
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, init=False)
    is_enabed: Mapped[bool]
    new_price: Mapped[int]

    __domain_class__ = domain.DirectMessagesPriceChanged
    __tablename__ = "direct_message_price_change_messages"
    __table_args__ = (
        ForeignKeyConstraint(
            (chat_id, msg_id),
            (ServiceMessage.chat_id, ServiceMessage.msg_id),
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.DirectMessagesPriceChanged,
    }


@mapped_as_dataclass(registry)
class ChecklistTasksDone(ServiceMessage):
    __domain_class__ = domain.ChecklistTasksDone
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ChecklistTasksDone,
    }


@mapped_as_dataclass(registry)
class ChecklistTasksAdded(ServiceMessage):
    __domain_class__ = domain.ChecklistTasksAdded
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.ChecklistTasksAdded,
    }


@mapped_as_dataclass(registry)
class UpgradedGiftPurchaseOffer(ServiceMessage):
    __domain_class__ = domain.UpgradedGiftPurchaseOffer
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.UpgradedGiftPurchaseOffer,
    }


@mapped_as_dataclass(registry)
class UpgradedGiftPurchaseOfferRejected(ServiceMessage):
    __domain_class__ = domain.UpgradedGiftPurchaseOfferRejected
    __mapper_args__ = {
        "polymorphic_identity": PayloadType.UpgradedGiftPurchaseOfferRejected,
    }


class SQLARepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def store_message(self, message_info: domain.BoundMessage) -> ChannelPost | ChatMessage:
        sender = await self.get_or_create_sender(message_info.sender)
        payload_info = message_info.payload
        forward_from: ForwardOrigin | None = None
        if isinstance(payload_info, domain.Forwarded):
            forward_from = await self.store_forward_origin(payload_info)
            payload_info = payload_info.message

        payload = await self.store_message_payload(payload_info)

        message: ChannelPost | ChatMessage
        match message_info:
            case domain.ChannelPost():
                channel = await self.get_or_create_chat(message_info.channel)
                message = ChannelPost(
                    channel=channel,
                    msg_id=message_info.msg_no,
                    sender=sender,
                    has_protected_content=message_info.has_protected_content,
                    forward_from=forward_from,
                    date=message_info.date,
                    payload=payload,
                    views=message_info.views,
                    forwards=message_info.forwards,
                )
            case domain.ChatMessage():
                chat = await self.get_or_create_chat(message_info.chat)
                message = ChatMessage(
                    chat=chat,
                    msg_id=message_info.msg_no,
                    sender=sender,
                    has_protected_content=message_info.has_protected_content,
                    forward_from=forward_from,
                    date=message_info.date,
                    payload=payload,
                )

        self._session.add(message)
        return message

    async def get_or_create_sender(self, sender_info: domain.MessageSource) -> MessageSource:
        sender: MessageSource | None
        match sender_info:
            case domain.FromUser():
                sender = await self._session.scalar(
                    select(FromUser)
                    .where(FromUser.user_id == sender_info.user.tg_id)
                )
                if sender is None:
                    user = await self.get_or_create_user(sender_info.user)
                    sender = FromUser(user=user)
            case domain.FromChannel():
                sender = await self._session.scalar(
                    select(FromChannel)
                    .where(FromChannel.channel_id == sender_info.channel.tg_id)
                )
                if sender is None:
                    channel = await self.get_or_create_chat(sender_info.channel)
                    sender = FromChannel(channel=channel)
            case domain.FromChannelAdmin():
                sender = await self._session.scalar(
                    select(FromChannelAdmin)
                    .where(
                        FromChannelAdmin.channel_id == sender_info.channel.tg_id,
                        FromChannelAdmin.author_signature == sender_info.author_signature
                    )
                )
                if sender is None:
                    channel = await self.get_or_create_chat(sender_info.channel)
                    sender = FromChannelAdmin(channel=channel, author_signature=sender_info.author_signature)
            case domain.FromAnonAdmin():
                sender = await self._session.scalar(
                    select(FromAnonAdmin).where(
                        FromAnonAdmin.chat_id == sender_info.chat.tg_id,
                        FromAnonAdmin.admin_mark == sender_info.admin_mark,
                    ),
                )
                if sender is None:
                    chat = await self.get_or_create_chat(sender_info.chat)
                    sender = FromAnonAdmin(chat=chat, admin_mark=sender_info.admin_mark)
            case unknown:
                raise ValueError(f"Unknown message sender type: {unknown}", unknown)

        self._session.add(sender)

        return sender

    async def store_forward_origin(self, forwarded_info: domain.Forwarded) -> ForwardOrigin:
        origin: ForwardOrigin
        match forwarded_info.origin:
            case domain.UserOrigin():
                origin = UserOrigin(
                    origin_date=forwarded_info.origin_date,
                    user=await self.get_or_create_user(forwarded_info.origin.user),
                )
            case domain.AnonUserOrigin():
                origin = AnonUserOrigin(
                    origin_date=forwarded_info.origin_date,
                    sender_name=forwarded_info.origin.sender_name,
                )
            case domain.ChannelOrigin():
                origin = ChannelOrigin(
                    origin_date=forwarded_info.origin_date,
                    channel=await self.get_or_create_chat(forwarded_info.origin.channel),
                    source_message_id=forwarded_info.origin.source_message_id,
                    author_signature=forwarded_info.origin.author_signature,
                )
            case domain.LinkedChannelOrigin():
                origin = LinkedChannelOrigin(
                    origin_date=forwarded_info.origin_date,
                    channel=await self.get_or_create_chat(forwarded_info.origin.channel),
                    source_message_id=forwarded_info.origin.source_message_id,
                    author_signature=forwarded_info.origin.author_signature,
                )
            case domain.AnonAdminOrigin():
                origin = AnonAdminOrigin(
                    origin_date=forwarded_info.origin_date,
                    chat=await self.get_or_create_chat(forwarded_info.origin.chat),
                    admin_mark=forwarded_info.origin.admin_mark,
                )
            case _:
                raise ValueError(f"Unknown forward origin: {forwarded_info}")

        return origin

    async def store_message_payload(self, payload_info: domain.Message) -> Payload:
        payload: Payload
        match payload_info:
            case domain.TextMessage():
                text = await self.store_text(payload_info.text)
                payload = TextMessage(text=text)
            case domain.Forwarded():
                raise ValueError(
                    f"{domain.Forwarded.__qualname__} and its subclasses should be handled in {self.store_message}"
                )
            case domain.MediaMessage():
                caption = await self.store_text(payload_info.caption) if payload_info.caption else None
                payload = MediaMessage(
                    caption=caption,
                    media=await self.store_media_info(payload_info.media),
                    media_group_id=payload_info.media_group_id,
                    has_media_spoiler=payload_info.has_media_spoiler,
                )
            case domain.ServiceMessage():
                payload = await self.store_service_message(payload_info)
            case unexpected:
                raise ValueError(f"Can not store {unexpected} as message payload")

        # comment out to avoid integrity errors
        # self._session.add(payload)
        return payload

    async def store_text(self, text_info: domain.Text) -> Text:
        entities: list[TextEntity] = []
        for entity_info in text_info.entities:
            entity: TextEntity
            match entity_info:
                case domain.Mention():
                    entity = Mention(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Hashtag():
                    entity = Hashtag(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Cashtag():
                    entity = Cashtag(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.BotCommand():
                    entity = BotCommand(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.URL():
                    entity = URL(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Email():
                    entity = Email(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.PhoneNumber():
                    entity = PhoneNumber(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Bold():
                    entity = Bold(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Italic():
                    entity = Italic(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Underline():
                    entity = Underline(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Strikethrough():
                    entity = Strikethrough(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Spoiler():
                    entity = Spoiler(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Code():
                    entity = Code(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.Pre():
                    entity = Pre(
                        offset=entity_info.offset,
                        length=entity_info.length,
                        language=entity_info.language,
                    )
                case domain.BlockQuote():
                    entity = BlockQuote(
                        offset=entity_info.offset,
                        length=entity_info.length
                    )
                case domain.TextLink():
                    entity = TextLink(
                        offset=entity_info.offset,
                        length=entity_info.length,
                        url=entity_info.url,
                    )
                case domain.TextMention():
                    entity = TextMention(
                        offset=entity_info.offset,
                        length=entity_info.length,
                        user=await self.get_or_create_user(entity_info.user),
                    )
                case domain.BankCard():
                    entity = BankCard(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case domain.CustomEmojiEntity():
                    entity = CustomEmojiEntity(
                        offset=entity_info.offset,
                        length=entity_info.length,
                        custom_emoji=await self.get_or_create_custom_emoji(entity_info.custom_emoji),
                    )
                case domain.UnknownEntity():
                    entity = UnknownEntity(
                        offset=entity_info.offset,
                        length=entity_info.length,
                    )
                case unexpected:
                    raise ValueError(f"Unexpected text entity: {unexpected}")
            entities.append(entity)

        text = Text(raw=text_info.raw, entities=entities)
        self._session.add(text)
        return text

    async def store_service_message(self, message_info: domain.ServiceMessage) -> ServiceMessage:
        message: ServiceMessage
        match message_info:
            case domain.NewChatMembers():
                users = [await self.get_or_create_user(user) for user in message_info.new_chat_members]
                message = NewChatMembers(new_chat_members=users)
            case domain.LeftChatMember():
                user = await self.get_or_create_user(message_info.left_user)
                message = LeftChatMember(left_user=user)
            case domain.NewChatTitle():
                message = NewChatTitle(new_chat_title=message_info.new_chat_title)
            case domain.NewChatPhoto():
                photo = await aoptional(self.store_media_info, message_info.new_chat_photo)
                message = NewChatPhoto(new_chat_photo=photo)
            case domain.ChatPhotoDeleted():
                message = ChatPhotoDeleted()
            case domain.ForumTopicCreated():
                message = ForumTopicCreated(
                    topic_id=message_info.id,
                    title=message_info.title,
                    icon_color=message_info.icon_color,
                    custom_emoji=await self.get_or_create_custom_emoji(message_info.custom_emoji) if message_info.custom_emoji else None,  # noqa: E501
                )
            case domain.ForumTopicClosed():
                message = ForumTopicClosed()
            case domain.ForumTopicReopened():
                message = ForumTopicReopened()
            case domain.ForumTopicEdited():
                message = ForumTopicEdited(
                    title=message_info.title,
                    icon_color=message_info.icon_color,
                    custom_emoji=await self.get_or_create_custom_emoji(message_info.custom_emoji) if message_info.custom_emoji else None,  # noqa: E501
                    is_closed=message_info.is_closed,
                    is_hidden=message_info.is_hidden,
                )
            case domain.GeneralForumTopicHidden():
                message = GeneralForumTopicHidden()
            case domain.GeneralForumTopicUnhidden():
                message = GeneralForumTopicUnhidden()
            case domain.GroupCreated():
                message = GroupCreated()
            case domain.ChannelCreated():
                message = ChannelCreated()
            case domain.SupergroupCreated():
                message = SupergroupCreated()
            case domain.MigrateToSupergroup():
                chat = await self.get_or_create_chat(message_info.migrate_to_chat)
                message = MigrateToSupergroup(migrate_to_chat=chat)
            case domain.MigrateFromGroup():
                chat = await self.get_or_create_chat(message_info.migrate_from_chat)
                message = MigrateFromGroup(migrate_from_chat=chat)
            case domain.MessagePinned():
                message = MessagePinned(pinned_message_id=message_info.pinned_message_id)
            case domain.GameHighScore():
                user = await self.get_or_create_user(message_info.user)
                message = GameHighScore(user=user, score=message_info.score)
            case domain.GiveawayCreated():
                message = GiveawayCreated()
            case domain.GiveawayCompleted():
                message = GiveawayCompleted(
                    winner_count=message_info.winner_count,
                    unclaimed_prize_count=message_info.unclaimed_prize_count,
                    giveaway_message_id=message_info.giveaway_message_id,
                    is_star_giveaway=message_info.is_star_giveaway,
                )
            case domain.PremiumGiftCode():
                message = PremiumGiftCode(
                    code=message_info.code,
                    caption=await self.store_text(message_info.caption) if message_info.caption else None,
                    month_count=message_info.month_count,
                    day_count=message_info.day_count,
                    price=await self.store_price(message_info.price),
                    is_unclaimed=message_info.is_unclaimed,
                    is_from_giveaway=message_info.is_from_giveaway,
                )
            case domain.GiftedPremium():
                message = GiftedPremium(
                    receiver=await self.get_or_create_user(message_info.receiver),
                    gifter=await aoptional(self.get_or_create_user, message_info.receiver),
                    price=await self.store_price(message_info.price),
                    month_count=message_info.month_count,
                    day_count=message_info.day_count,
                    sticker=await aoptional(self.store_media_info, message_info.sticker),
                    caption=await aoptional(self.store_text, message_info.caption)
                )
            case domain.GiftedStars():
                message = GiftedStars()
            case domain.GiftedTON():
                message = GiftedTON()
            case domain.VideoChatStarted():
                message = VideoChatStarted()
            case domain.VideoChatEnded():
                message = VideoChatEnded(duratioin=message_info.duratioin)
            case domain.VideoChatScheduled():
                message = VideoChatScheduled(start_date=message_info.start_date)
            case domain.VideoChatMembersInvited():
                users = [await self.get_or_create_user(user) for user in message_info.video_chat_members_invited]
                message = VideoChatMembersInvited(video_chat_members_invited=users)
            case domain.PhoneCallStarted():
                message = PhoneCallStarted(
                    call_id=message_info.tg_id,
                    is_video=message_info.is_video,
                )
            case domain.PhoneCallEnded():
                message = PhoneCallEnded(
                    call_id=message_info.call_id,
                    is_video=message_info.is_video,
                    reason=message_info.reason,
                    duration=message_info.duration,
                )
            case domain.WebAppData():
                message = WebAppData(
                    data=message_info.data,
                    button_text=message_info.button_text,
                )
            case domain.UsersShared():
                message = UsersShared()
            case domain.ChatShared():
                message = ChatShared()
            case domain.SuccessfulSubscriptionPayment():
                message = SuccessfulSubscriptionPayment(
                    currency=message_info.currency,
                    total_amount=message_info.total_amount,
                    invoice_slug=message_info.invoice_slug,
                    first_time=message_info.first_time,
                    subscription_expiration_date=message_info.subscription_expiration_date,
                )
            case domain.SuccessfulPayment():
                message = SuccessfulPayment(
                    currency=message_info.currency,
                    total_amount=message_info.total_amount,
                    invoice_slug=message_info.invoice_slug,
                )
            case domain.RefundedPayment():
                message = RefundedPayment()
            case domain.SuggestedPostApprovalFailed():
                message = SuggestedPostApprovalFailed()
            case domain.SuggestedPostApproved():
                message = SuggestedPostApproved()
            case domain.SuggestedPostDeclined():
                message = SuggestedPostDeclined()
            case domain.SuggestedPostPaid():
                message = SuggestedPostPaid()
            case domain.SuggestedPostRefunded():
                message = SuggestedPostRefunded()
            case domain.SetMessageAutodeleteTime():
                message = SetMessageAutodeleteTime(message_ttl=message_info.message_ttl)
            case domain.MessageAutodeleteDisabled():
                message = MessageAutodeleteDisabled()
            case domain.ChatBoost():
                message = ChatBoost(message_info.amount)
            case domain.Gifted():
                message = Gifted()
            case domain.ConnectedWebsite():
                message = Connectedwebsite(site=message_info.domain)
            case domain.WriteAccessAllowed():
                message = WriteAccessAllowed(
                    from_request=message_info.from_request,
                    from_attachment_menu=message_info.from_attachment_menu,
                    web_app_name=message_info.web_app_name,
                )
            case domain.ScreenshotTaken():
                message = ScreenshotTaken()
            case domain.ContactRegistered():
                message = ContactRegistered()
            case domain.ProximityAlertTriggered():
                message = ProximityAlertTriggered(
                    traveler=await self.get_or_create_chat(message_info.traveler),
                    watcher=await self.get_or_create_chat(message_info.watcher),
                    distance=message_info.distance,
                )
            case domain.HistoryCleared():
                message = HistoryCleared()
            case domain.SuggestedProfilePhoto():
                message = SuggestedProfilePhoto(
                    photo=await self.store_media_info(message_info.photo),
                )
            case domain.SuggestedBirthday():
                message = SuggestedBirthday(
                    day=message_info.birthday.day,
                    month=message_info.birthday.month,
                    year=message_info.birthday.year,
                )
            case domain.SetChatBackground():
                message = SetChatBackground()
            case domain.SetChatEmojiTheme():
                message = SetChatEmojiTheme(
                    name=message_info.name,
                )
            case domain.SetChatGiftTheme():
                message = SetChatGiftTheme()
            case domain.GiveawayPrizeStars():
                message = GiveawayPrizeStars()
            case domain.PaidMessagesRefunded():
                message = PaidMessagesRefunded(
                    messages_count=message_info.messages_count,
                    stars_amount=message_info.stars_amount,
                )
            case domain.PaidMessagesPriceChanged():
                message = PaidMessagesPriceChanged(
                    new_price=message_info.new_price,
                )
            case domain.DirectMessagesPriceChanged():
                message = DirectMessagesPriceChanged(
                    is_enabed=message_info.is_enabed,
                    new_price=message_info.new_price,
                )
            case domain.ChecklistTasksDone():
                message = ChecklistTasksDone()
            case domain.ChecklistTasksAdded():
                message = ChecklistTasksAdded()
            case domain.UpgradedGiftPurchaseOffer():
                message = UpgradedGiftPurchaseOffer()
            case domain.UpgradedGiftPurchaseOfferRejected():
                message = UpgradedGiftPurchaseOfferRejected()
            case domain.UnsupportedServiceMessage():
                message = UnsupportedServiceMessage()
            case domain.CustomAction():
                message = CustomAction(message=message_info.message)
            case domain.BorkedServiceMessage():
                message = ServiceMessageBorked()
            case unknown:
                raise ValueError(f"Can not store {unknown} as service message.")

        return message

    @overload
    async def store_media_info(self, media_info: domain.Audio) -> Audio: pass
    @overload
    async def store_media_info(self, media_info: domain.Document) -> Document: pass
    @overload
    async def store_media_info(self, media_info: domain.Photo) -> Photo: pass
    @overload
    async def store_media_info(self, media_info: domain.Sticker) -> Sticker: pass
    @overload
    async def store_media_info(self, media_info: domain.Video) -> Video: pass

    @overload
    async def store_media_info(self, media_info: domain.Animation) -> Animation: pass
    @overload
    async def store_media_info(self, media_info: domain.Voice) -> Voice: pass
    @overload
    async def store_media_info(self, media_info: domain.VideoNote) -> VideoNote: pass
    @overload
    async def store_media_info(self, media_info: domain.Contact) -> Contact: pass
    @overload
    async def store_media_info(self, media_info: domain.Location) -> Location: pass

    @overload
    async def store_media_info(self, media_info: domain.LiveLocation) -> LiveLocation: pass
    @overload
    async def store_media_info(self, media_info: domain.BusinessLocation) -> BusinessLocation: pass
    @overload
    async def store_media_info(self, media_info: domain.Venue) -> Venue: pass
    @overload
    async def store_media_info(self, media_info: domain.Poll) -> Poll: pass
    @overload
    async def store_media_info(self, media_info: domain.Quiz) -> Quiz: pass

    @overload
    async def store_media_info(self, media_info: domain.WebPage) -> WebPage: pass
    @overload
    async def store_media_info(self, media_info: domain.Dice) -> Dice: pass
    @overload
    async def store_media_info(self, media_info: domain.Game) -> SharedGame: pass
    @overload
    async def store_media_info(self, media_info: domain.StarsGiveaway) -> StarsGiveaway: pass
    @overload
    async def store_media_info(self, media_info: domain.SubscriptionsGiveaway) -> SubscriptionsGiveaway: pass

    @overload
    async def store_media_info(self, media_info: domain.StarsGiveawayWinners) -> StarsGiveawayWinners: pass  # noqa: E501
    @overload
    async def store_media_info(self, media_info: domain.SubscriptionsGiveawayWinners) -> SubscriptionsGiveawayWinners: pass  # noqa: E501
    @overload
    async def store_media_info(self, media_info: domain.Story) -> Story: pass
    @overload
    async def store_media_info(self, media_info: domain.Invoice) -> Invoice: pass
    @overload
    async def store_media_info(self, media_info: domain.PaidMedia) -> PaidMedia: pass

    @overload
    async def store_media_info(self, media_info: domain.Checklist) -> Checklist: pass
    @overload
    async def store_media_info(self, media_info: domain.DisappearedMedia) -> DisappearedMedia: pass

    async def store_media_info(
        self,
        media_info: domain.Media,
    ) -> Media:
        media: Media
        match media_info:
            case domain.Audio():
                media = Audio(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    duration=media_info.duration,
                    performer=media_info.performer,
                    title=media_info.title,
                    file_name=media_info.file_name,
                    mime_type=media_info.mime_type,
                    file_size=media_info.file.file_size,
                    date=media_info.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file.access_key,
                            file_unique_id=thumb.file.unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file.file_size,
                        )
                        for thumb in media_info.thumbs
                    ],
                )
            case domain.Document():
                media = Document(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    file_name=media_info.file_name,
                    mime_type=media_info.mime_type,
                    file_size=media_info.file.file_size,
                    date=media_info.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file.access_key,
                            file_unique_id=thumb.file.unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file.file_size,
                        )
                        for thumb in media_info.thumbs
                    ],
                )
            case domain.Photo():
                media = Photo(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    width=media_info.width,
                    height=media_info.height,
                    file_size=media_info.file.file_size,
                    date=media_info.date,
                    ttl_seconds=media_info.ttl_seconds,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file.access_key,
                            file_unique_id=thumb.file.unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file.file_size,
                        )
                        for thumb in media_info.thumbs
                    ],
                )
            case domain.Sticker():
                media = Sticker(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    width=media_info.width,
                    height=media_info.height,
                    is_animated=media_info.is_animated,
                    is_video=media_info.is_video,
                    file_name=media_info.file_name,
                    mime_type=media_info.mime_type,
                    file_size=media_info.file.file_size,
                    date=media_info.date,
                    emoji=media_info.emoji,
                    set_name=media_info.set_name,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file.access_key,
                            file_unique_id=thumb.file.unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file.file_size,
                        )
                        for thumb in media_info.thumbs
                    ],
                )
            case domain.Video():
                media = Video(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    width=media_info.width,
                    height=media_info.height,
                    duration=media_info.duration,
                    file_name=media_info.file_name,
                    mime_type=media_info.mime_type,
                    file_size=media_info.file.file_size,
                    supports_streaming=media_info.supports_streaming,
                    ttl_seconds=media_info.ttl_seconds,
                    date=media_info.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file.access_key,
                            file_unique_id=thumb.file.unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file.file_size,
                        )
                        for thumb in media_info.thumbs
                    ],
                )
            case domain.Animation():
                media = Animation(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    width=media_info.width,
                    height=media_info.height,
                    duration=media_info.duration,
                    file_name=media_info.file_name,
                    mime_type=media_info.mime_type,
                    file_size=media_info.file.file_size,
                    date=media_info.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file.access_key,
                            file_unique_id=thumb.file.unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file.file_size,
                        )
                        for thumb in media_info.thumbs
                    ],
                )
            case domain.Voice():
                media = Voice(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    duration=media_info.duration,
                    waveform=media_info.waveform,
                    mime_type=media_info.mime_type,
                    file_size=media_info.file.file_size,
                    date=media_info.date,
                )
            case domain.VideoNote():
                media = VideoNote(
                    file_id=media_info.file.access_key,
                    file_unique_id=media_info.file.unique_id,
                    length=media_info.length,
                    duration=media_info.duration,
                    mime_type=media_info.mime_type,
                    file_size=media_info.file.file_size,
                    date=media_info.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file.access_key,
                            file_unique_id=thumb.file.unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file.file_size,
                        )
                        for thumb in media_info.thumbs
                    ],
                )
            case domain.Contact():
                media = Contact(
                    phone_number=media_info.phone_number,
                    first_name=media_info.first_name,
                    last_name=media_info.last_name,
                    user_id=media_info.user_id,
                    vcard=media_info.vcard,
                )
            case domain.Location():
                media = Location(
                    longitude=media_info.longitude,
                    latitude=media_info.latitude
                )
            case domain.LiveLocation():
                media = LiveLocation(
                    location=await self.store_media_info(media_info.location),
                    heading=media_info.heading,
                    live_period=media_info.live_period,
                    proximity_alert_radius=media_info.proximity_alert_radius,
                )
            case domain.BusinessLocation():
                media = BusinessLocation(
                    address=media_info.address,
                    location=await self.store_media_info(media_info.location) if media_info.location else None,
                )
            case domain.Venue():
                media = Venue(
                    location=await self.store_media_info(media_info.location),
                    title=media_info.title,
                    address=media_info.address,
                    foursquare_id=media_info.foursquare_id,
                    foursquare_type=media_info.foursquare_type,
                )
            case domain.Poll() | domain.Quiz():
                media = await self.store_poll_info(media_info, add_to_session=False)
            case domain.WebPageEmpty():
                media = WebPageEmpty(tg_id=media_info.tg_id)
            case domain.WebPageDetails():
                media = WebPageDetails(
                    tg_id=media_info.tg_id,
                    url=media_info.url,
                    display_url=media_info.display_url,
                    type=media_info.type,
                    site_name=media_info.site_name,
                    title=media_info.title,
                    description=media_info.description,
                    audio=await aoptional(self.store_media_info, media_info.audio),
                    document=await aoptional(self.store_media_info, media_info.document),
                    photo=await aoptional(self.store_media_info, media_info.photo),
                    animation=await aoptional(self.store_media_info, media_info.animation),
                    video=await aoptional(self.store_media_info, media_info.video),
                    embed_url=media_info.embed_url,
                    embed_type=media_info.embed_type,
                    embed_width=media_info.embed_width,
                    embed_height=media_info.embed_height,
                    duration=media_info.duration,
                    author=media_info.author,
                )
            case domain.WebPagePending():
                media = WebPagePending(tg_id=media_info.tg_id)
            case domain.Dice():
                media = Dice(emoji=media_info.emoji, value=media_info.value)
            case domain.Game():
                media = SharedGame(game_id=media_info.tg_id)
                # TODO: add details
            case domain.StarsGiveaway():
                media = StarsGiveaway(
                    stars=media_info.stars,
                    channels=[
                        await self.get_or_create_chat(channel_info)
                        for channel_info in media_info.channels_to_subscribe or ()
                    ],
                    until_date=media_info.until_date,
                    description=media_info.description,
                    only_new_subscribers=media_info.only_new_subscribers,
                    only_for_countries=tuple(media_info.only_for_countries) if media_info.only_for_countries else None,
                    winners_are_visible=media_info.winners_are_visible,
                )
            case domain.SubscriptionsGiveaway():
                media = SubscriptionsGiveaway(
                    quantity=media_info.quantity,
                    months=media_info.months,
                    channels=[
                        await self.get_or_create_chat(channel_info)
                        for channel_info in media_info.channels_to_subscribe or ()
                    ],
                    until_date=media_info.until_date,
                    description=media_info.description,
                    only_new_subscribers=media_info.only_new_subscribers,
                    only_for_countries=tuple(media_info.only_for_countries) if media_info.only_for_countries else None,
                    winners_are_visible=media_info.winners_are_visible,
                )
            case domain.StarsGiveawayWinners():
                media = StarsGiveawayWinners(
                    chat=await self.get_or_create_chat(media_info.chat),
                    giveaway_message_id=media_info.giveaway_message_id,
                    winners_selection_date=media_info.winners_selection_date,
                    quantity=media_info.quantity,
                    winner_count=media_info.winner_count,
                    unclaimed_prize_count=media_info.unclaimed_prize_count,
                    winners=[
                        await self.get_or_create_user(user_info)
                        for user_info in media_info.winners
                    ],
                    prize_star_count=media_info.prize_star_count,
                    was_refunded=media_info.was_refunded,
                )
            case domain.SubscriptionsGiveawayWinners():
                media = SubscriptionsGiveawayWinners(
                    chat=await self.get_or_create_chat(media_info.chat),
                    giveaway_message_id=media_info.giveaway_message_id,
                    winners_selection_date=media_info.winners_selection_date,
                    quantity=media_info.quantity,
                    winner_count=media_info.winner_count,
                    unclaimed_prize_count=media_info.unclaimed_prize_count,
                    winners=[
                        await self.get_or_create_user(user_info)
                        for user_info in media_info.winners
                    ],
                    premium_subscription_month_count=media_info.premium_subscription_month_count,
                    was_refunded=media_info.was_refunded,
                )
            case domain.Story():
                # TODO: add details
                media = Story(
                    tg_id=media_info.tg_id,
                    caption=await self.store_text(media_info.caption) if media_info.caption else None,
                    type=media_info.type,
                    date=media_info.date,
                )
            case domain.Invoice():
                media = Invoice(
                    currency=media_info.currency,
                    is_test=media_info.is_test,
                    title=media_info.title,
                    description=media_info.description,
                    total_amount=media_info.total_amount,
                    start_parameter=media_info.start_parameter,
                    # prices=[],  # TODO: media_info.prices
                    is_name_requested=media_info.is_name_requested,
                    is_phone_requested=media_info.is_phone_requested,
                    is_email_requested=media_info.is_email_requested,
                    is_shipping_address_requested=media_info.is_shipping_address_requested,
                    is_flexible=media_info.is_flexible,
                    is_phone_to_provider=media_info.is_phone_to_provider,
                    is_email_to_provider=media_info.is_email_to_provider,
                    is_recurring=media_info.is_recurring,
                    max_tip_amount=media_info.max_tip_amount,
                    # suggested_tip_amounts=[],  # TODO: media_info.suggested_tip_amounts
                    terms_url=media_info.terms_url,
                )
            case domain.PaidMedia():
                media = PaidMedia(
                    stars_amount=media_info.stars_amount,
                )
            case domain.Checklist():
                media = Checklist(
                    title=await self.store_text(media_info.title),
                    tasks=[
                        ChecklistTask(
                            tg_id=task.tg_id,
                            text=await self.store_text(task.text),
                            completed_by=await self.get_or_create_chat(task.completed_by) if task.completed_by else None,  # noqa: E501
                            completion_date=task.completion_date,
                        )
                        for task in media_info.tasks
                    ],
                    can_add_tasks=media_info.can_add_tasks,
                    can_mark_tasks_as_done=media_info.can_mark_tasks_as_done,
                    others_can_add_tasks=media_info.others_can_add_tasks,
                    others_can_mark_tasks_as_done=media_info.others_can_mark_tasks_as_done,
                )
            case domain.DisappearedMedia():
                media = DisappearedMedia()
            case unknown:
                raise ValueError(f"{type(unknown).__qualname__} object is not recognised as media")
        return media

    async def store_poll_info(self, poll_info: domain.Poll | domain.Quiz, add_to_session: bool = True) -> Poll | Quiz:
        tg_id = poll_info.tg_id
        question = await self.store_text(poll_info.question)
        is_anonymous = poll_info.is_anonymous
        open_period = poll_info.open_period
        close_date = poll_info.close_date
        total_voter_count = poll_info.total_voter_count
        options = [
            PollOption(text=await self.store_text(text_info=option.text))
            for option in poll_info.options
        ]

        poll: Poll | Quiz
        match poll_info:
            case domain.Poll():
                poll = Poll(
                    tg_id=tg_id,
                    question=question,
                    is_anonymous=is_anonymous,
                    open_period=open_period,
                    close_date=close_date,
                    total_voter_count=total_voter_count,
                    options=options,
                    allows_multiple_answers=poll_info.allows_multiple_answers,
                )
            case domain.Quiz():
                poll = Quiz(
                    tg_id=tg_id,
                    question=question,
                    is_anonymous=is_anonymous,
                    open_period=open_period,
                    close_date=close_date,
                    total_voter_count=total_voter_count,
                    options=options,
                )

        if add_to_session:
            self._session.add(poll)

        return poll

    async def store_paid_media_preview(self, paid_media_preview_info: domain.PaidMediaPreview) -> PaidMediaPreview:
        thumbnail: StrippedThumbnail | None = None
        if paid_media_preview_info.thumbnail:
            thumbnail = StrippedThumbnail(data=paid_media_preview_info.thumbnail.data)

        paid_media_preview = PaidMediaPreview(
            width=paid_media_preview_info.width,
            height=paid_media_preview_info.height,
            duration=paid_media_preview_info.duration,
            thumbnail=thumbnail,
        )
        return paid_media_preview

    async def store_price(self, price_info: domain.MoneyAmount) -> CurrencyAmount | CryptocurrencyAmount:
        price: CurrencyAmount | CryptocurrencyAmount
        match price_info:
            case domain.CurrencyAmount():
                price = CurrencyAmount(
                    currency=price_info.currency,
                    amount=price_info.amount
                )
            case domain.CryptocurrencyAmount():
                price = CryptocurrencyAmount(
                    currency=price_info.currency,
                    amount=price_info.amount,
                )
            case unknown:
                raise ValueError(f"Can not store {unknown} as price")

        return price

    async def get_or_create_user(self, user_info: domain.User) -> User:
        user = await self._session.get(User, user_info.tg_id)
        if user is None:
            user = User(tg_id=user_info.tg_id)
            self._session.add(user)
        return user

    @overload
    async def get_or_create_chat(self, chat_info: domain.UserDialog) -> User: pass
    @overload
    async def get_or_create_chat(self, chat_info: domain.BotDialog) -> Bot: pass
    @overload
    async def get_or_create_chat(self, chat_info: domain.Group) -> Group: pass
    @overload
    async def get_or_create_chat(self, chat_info: domain.Supergroup) -> Supergroup: pass
    @overload
    async def get_or_create_chat(self, chat_info: domain.Channel) -> Channel: pass
    @overload
    async def get_or_create_chat(self, chat_info: domain.UnavailableChat) -> UnavailableGroup | UnavailableSupergroup: pass  # noqa: E501
    @overload
    async def get_or_create_chat(self, chat_info: domain.DeletedUserDialog) -> User: pass
    @overload
    async def get_or_create_chat(self, chat_info: domain.Chat) -> Chat: pass

    async def get_or_create_chat(self, chat_info: domain.Chat) -> Chat:
        # any_chat = with_polymorphic(Chat, "*")
        chat: Chat | None = await self._session.get(Chat, chat_info.tg_id)
        if chat is not None:
            return chat

        match chat_info:
            case domain.UserDialog():
                chat = User(tg_id=chat_info.tg_id)
            case domain.BotDialog():
                chat = Bot(tg_id=chat_info.tg_id)
            case domain.Group():
                chat = Group(tg_id=chat_info.tg_id)
            case domain.Supergroup():
                chat = Supergroup(tg_id=chat_info.tg_id)
            case domain.Channel():
                chat = Channel(tg_id=chat_info.tg_id)
            case domain.UnavailableChat() if chat_info.type == domain.ChatType.GROUP:
                chat = UnavailableGroup(tg_id=chat_info.tg_id)
            case domain.UnavailableChat() if chat_info.type == domain.ChatType.SUPERGROUP:
                chat = UnavailableSupergroup(tg_id=chat_info.tg_id)
            case domain.DeletedUserDialog():
                chat = User(tg_id=chat_info.tg_id)
            case domain.Chat() if chat_info.type == domain.ChatType.GROUP:
                chat = Group(tg_id=chat_info.tg_id)
            case domain.Chat() if chat_info.type == domain.ChatType.SUPERGROUP:
                chat = Supergroup(tg_id=chat_info.tg_id)
            case unknowwn:
                raise ValueError(f"Can't store {unknowwn} as chat")

        self._session.add(chat)
        return chat

    async def get_or_create_custom_emoji(self, cusom_emoji_info: domain.CustomEmoji) -> CustomEmoji:
        custom_emoji = await self._session.get(CustomEmoji, cusom_emoji_info.tg_id)
        if custom_emoji is None:
            custom_emoji = CustomEmoji(tg_id=cusom_emoji_info.tg_id)
            self._session.add(custom_emoji)
        return custom_emoji


async def aoptional(fn: Callable[[T], Awaitable[Return]], value: T | None) -> Return | None:
    if value is None:
        return None
    return await fn(value)


async def test(session: AsyncSession) -> None:
    msg = await session.get(BoundMessage, (1, 1))
    print("got", msg)


async def _main() -> None:
    import logging
    from asyncio import sleep
    # from itertools import count

    import sqlalchemy.log
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.sql import text

    ECHO = False
    SQLA_LOG = False
    if SQLA_LOG:
        sqlalchemy.log.rootlogger.setLevel(logging.INFO)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=ECHO)

    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys = 1;"))
        logging.info("Create schema")
        await conn.run_sync(registry.metadata.create_all)

    sessions_factory = async_sessionmaker(engine, class_=AsyncSession)
    async with sessions_factory() as session:
        await test(session)

    await sleep(0.5)


def main() -> None:
    from asyncio import run

    run(_main())


if __name__ == "__main__":
    main()
