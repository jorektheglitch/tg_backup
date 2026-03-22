from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, MutableMapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime as dt  # , timedelta as td
from enum import StrEnum
from logging import getLogger
from typing import Any, ClassVar, Generic, Literal, Protocol, Self, TypeAlias, TypeVar, cast, overload

# Kurigram==2.2.18
import pyrogram.types as pyrogram
import pyrogram.enums as pyrogram_enums
import pyrogram.raw.types as pyrogram_raw
from pyrogram.file_id import FileId
from pyrogram.types.messages_and_media.message import Str
from pyrogram.enums import (
    ChatType,
    MessageEntityType,
    MessageMediaType,
    MessageServiceType,
    # MessageOriginType,
    PhoneCallDiscardReason,
    PollType,
    # UserStatus,
)


T = TypeVar("T")
Arg = TypeVar("Arg", contravariant=True)
Return = TypeVar("Return", covariant=True)
Value = TypeVar("Value", covariant=True)


log = getLogger(__name__)


class Unavailable(StrEnum):
    UNAVAILABLE = "unavailable"


UNAVAILABLE = Unavailable.UNAVAILABLE


@dataclass(frozen=True)
class Text:
    raw: str
    entities: Sequence[TextEntity] = ()

    __pyro_class__ = Str

    def __str__(self) -> str:
        return self.raw


@dataclass(frozen=True)
class _Media(ABC):
    pass


@dataclass(frozen=True)
class DisappearedMedia(_Media):
    raw_json: OnDemand[JSON] | None = field(kw_only=True, default=None)


@dataclass(frozen=True)
class _File:
    # TODO: refactor for full file info stored without TL encoding
    unique_id: str  # file_unique_id
    access_key: str  # file_id

    __pyro_class__ = FileId


@dataclass(frozen=True)
class File(_File):
    file_size: int | None = field(kw_only=True, default=None)


@dataclass(frozen=True)
class SizedFile(_File):
    file_size: int = field(kw_only=True)


@dataclass(frozen=True)
class FileMedia(_Media, ABC):
    file: SizedFile


@dataclass(frozen=True)
class Thumbnail(FileMedia):
    width: int
    height: int
    # file_size: int  # moved to File

    __pyro_class__ = pyrogram.Thumbnail


@dataclass(frozen=True)
class Sticker(FileMedia):
    width: int
    height: int
    is_animated: bool
    is_video: bool
    file_name: str | None
    mime_type: str | None
    # file_size: int  # moved to File
    date: dt | None
    emoji: str | None
    set_name: str | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Sticker


@dataclass(frozen=True)
class Audio(FileMedia):
    duration: int
    performer: str | None
    title: str | None
    file_name: str | None
    mime_type: str | None
    # file_size: int  # moved to File
    date: dt | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Audio


@dataclass(frozen=True)
class Document(FileMedia):
    file_name: str | None
    mime_type: str | None
    # file_size: int  # moved to File
    date: dt | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Document


@dataclass(frozen=True)
class Photo(FileMedia):
    width: int
    height: int
    # file_size: int  # moved to File
    date: dt | None
    ttl_seconds: int | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Photo


@dataclass(frozen=True)
class Animation(FileMedia):
    width: int
    height: int
    duration: int
    file_name: str | None
    mime_type: str | None
    # file_size: int  # moved to File
    date: dt | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Animation


@dataclass(frozen=True)
class Video(FileMedia):
    width: int
    height: int
    duration: int
    file_name: str | None
    mime_type: str | None
    # file_size: int  # moved to File
    supports_streaming: bool | None
    ttl_seconds: int | None
    date: dt | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Video


@dataclass(frozen=True)
class Voice(FileMedia):
    duration: int
    waveform: bytes | None
    mime_type: str | None
    # file_size: int  # moved to File
    date: dt | None

    __pyro_class__ = pyrogram.Voice


@dataclass(frozen=True)
class VideoNote(FileMedia):
    length: int
    duration: int
    mime_type: str | None
    # file_size: int  # moved to File
    date: dt | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.VideoNote


@dataclass(frozen=True)
class Game():
    tg_id: int

    __pyro_class__ = pyrogram.Game


@dataclass(frozen=True)
class GameDetailed(Game):
    tg_id: int
    title: str
    short_name: str
    description: str
    photo: Photo
    animation: Animation | None = None


@dataclass(frozen=True)
class Giveaway(ABC):
    channels_to_subscribe: Sequence[Channel] | None = field(default=None, kw_only=True)
    until_date: dt | None = field(default=None, kw_only=True)
    description: str | None = field(default=None, kw_only=True)
    only_new_subscribers: bool | None = field(default=None, kw_only=True)
    only_for_countries: Sequence[str] | None = field(default=None, kw_only=True)
    winners_are_visible: bool = field(kw_only=True)

    __pyro_class__ = pyrogram.Giveaway


@dataclass(frozen=True)
class StarsGiveaway(Giveaway):
    stars: int


@dataclass(frozen=True)
class SubscriptionsGiveaway(Giveaway):
    quantity: int
    months: int


@dataclass(frozen=True)
class GiveawayWinners(ABC):
    chat: Chat
    giveaway_message_id: int
    winners_selection_date: dt
    quantity: int
    winner_count: int
    unclaimed_prize_count: int
    winners: Sequence[User]
    # giveaway_message: Optional["types.Message"] = None  # pyro trying to get message from id internally
    was_refunded: bool = field(kw_only=True)

    __pyro_class__ = pyrogram.GiveawayWinners


@dataclass(frozen=True)
class StarsGiveawayWinners(GiveawayWinners):
    prize_star_count: int


@dataclass(frozen=True)
class SubscriptionsGiveawayWinners(GiveawayWinners):
    premium_subscription_month_count: int


@dataclass(frozen=True)
class Story:
    # TODO: wtf is this shit???
    tg_id: int
    caption: Text | None
    type: Literal[MessageMediaType.PHOTO, MessageMediaType.VIDEO] | None
    date: dt

    __pyro_class__ = pyrogram.Story


@dataclass(frozen=True)
class Invoice:
    # tg_id: int
    currency: str  # ISO 4217
    is_test: bool
    title: str | None = None
    description: str | None = None
    total_amount: int | None = None
    start_parameter: str | None = None
    prices: Sequence[LabeledPrice] | None = None
    is_name_requested: bool | None = None
    is_phone_requested: bool | None = None
    is_email_requested: bool | None = None
    is_shipping_address_requested: bool | None = None
    is_flexible: bool | None = None
    is_phone_to_provider: bool | None = None
    is_email_to_provider: bool | None = None
    is_recurring: bool | None = None
    max_tip_amount: int | None = None
    suggested_tip_amounts: Sequence[int] | None = None
    terms_url: str | None = None

    __pyro_class__ = pyrogram.Invoice


@dataclass(frozen=True)
class LabeledPrice:
    label: str
    amount: int

    __pyro_class__ = pyrogram.LabeledPrice


@dataclass(frozen=True)
class PaidMedia:
    stars_amount: int
    media: Sequence[Photo | Video] | Sequence[PaidMediaPreview]

    __pyro_class__ = pyrogram.PaidMediaInfo


@dataclass(frozen=True)
class PaidMediaPreview:
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    thumbnail: StrippedThumbnail | None = None

    __pyro_class__ = pyrogram.PaidMediaPreview


@dataclass(frozen=True)
class StrippedThumbnail:
    data: bytes

    __pyro_class__ = pyrogram.StrippedThumbnail


@dataclass(frozen=True)
class Checklist:
    title: Text
    tasks: Sequence[ChecklistTask]
    others_can_add_tasks: bool | None = None
    can_add_tasks: bool | None = None
    others_can_mark_tasks_as_done: bool | None = None
    can_mark_tasks_as_done: bool | None = None

    __pyro_class__ = pyrogram.Checklist


@dataclass(frozen=True)
class ChecklistTask:
    tg_id: int
    text: Text
    completed_by: Chat | None = None
    completion_date: dt | None = None

    __pyro_class__ = pyrogram.ChecklistTask


@dataclass(frozen=True)
class Contact:
    phone_number: str
    first_name: str
    last_name: str | None
    user_id: int | None
    vcard: str | None

    __pyro_class__ = pyrogram.Contact


@dataclass(frozen=True)
class Location:
    longitude: float
    latitude: float
    accuracy: int | None = None

    __pyro_class__ = pyrogram.Location


@dataclass(frozen=True)
class LiveLocation:
    location: Location
    heading: int | None = None
    live_period: int = field(kw_only=True)
    proximity_alert_radius: int | None = field(default=None, kw_only=True)

    __pyro_class__ = pyrogram.Location


@dataclass(frozen=True)
class BusinessLocation:
    address: str
    location: Location | None = None

    __pyro_class__ = pyrogram.Location


@dataclass(frozen=True)
class Venue:
    location: Location
    title: str
    address: str
    foursquare_id: str | None
    foursquare_type: str | None

    __pyro_class__ = pyrogram.Venue


@dataclass(frozen=True)
class WebPage(ABC):
    tg_id: str

    __pyro_class__ = pyrogram.WebPage


@dataclass(frozen=True)
class WebPageEmpty(WebPage):
    pass


@dataclass(frozen=True)
class WebPagePending(WebPage):
    pass


@dataclass(frozen=True)
class WebPageDetails(WebPage):
    """A webpage preview

    Parameters:
        id (``str``):
            Unique identifier for this webpage.

        url (``str``):
            Full URL for this webpage.

        display_url (``str``, *optional*):
            Display URL for this webpage.

        type (``str``, *optional*):
            Type of webpage preview.
            One of the following:

            - video
            - gif
            - photo
            - document
            - profile
            - telegram_background
            - telegram_theme
            - telegram_story
            - telegram_channel
            - telegram_channel_request
            - telegram_megagroup
            - telegram_chat
            - telegram_megagroup_request
            - telegram_chat_request
            - telegram_album
            - telegram_message
            - telegram_bot
            - telegram_voicechat
            - telegram_livestream
            - telegram_user
            - telegram_botapp
            - telegram_channel_boost
            - telegram_group_boost
            - telegram_giftcode
            - telegram_stickerset

        site_name (``str``, *optional*):
            Webpage site name.

        title (``str``, *optional*):
            Title of this webpage.

        description (``str``, *optional*):
            Description of this webpage.

        audio (:obj:`~pyrogram.types.Audio`, *optional*):
            Webpage preview is an audio file, information about the file.

        document (:obj:`~pyrogram.types.Document`, *optional*):
            Webpage preview is a general file, information about the file.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Webpage preview is a photo, information about the photo.

        animation (:obj:`~pyrogram.types.Animation`, *optional*):
            Webpage preview is an animation, information about the animation.

        video (:obj:`~pyrogram.types.Video`, *optional*):
            Webpage preview is a video, information about the video.

        embed_url (``str``, *optional*):
            Embedded content URL.

        embed_type (``str``, *optional*):
            Embedded content type, like `iframe`

        embed_width (``int``, *optional*):
            Embedded content width.

        embed_height (``int``, *optional*):
            Embedded content height.

        has_large_media (``bool``, *optional*):
            Whether the webpage preview is large.

        prefer_large_media (``bool``, *optional*):
            Whether the webpage preview is large.

        prefer_small_media (``bool``, *optional*):
            Whether the webpage preview is small.

        manual (``bool``, *optional*):
            Whether the webpage preview was changed by the user.

        safe (``bool``, *optional*):
            Whether the webpage preview is safe.

        duration (``int``, *optional*):
            Unknown at the time of writing.

        author (``str``, *optional*):
            Author of the webpage, eg the Twitter user for a tweet, or the author in an article.
    """

    tg_id: str
    url: str
    display_url: str
    type: str | None
    site_name: str | None
    title: str | None
    description: str | None
    audio: Audio | None
    document: Document | None
    photo: Photo | None
    animation: Animation | None
    video: Video | None
    embed_url: str | None
    embed_type: str | None
    embed_width: int | None
    embed_height: int | None
    # TODO
    # has_large_media: bool
    # """has_large_media (``bool``, *optional*):
    #     Whether the webpage preview is large."""
    # prefer_large_media: bool
    # """prefer_large_media (``bool``, *optional*):
    #     Whether the webpage preview is large."""
    # prefer_small_media: bool
    # """prefer_small_media (``bool``, *optional*):
    #     Whether the webpage preview is small."""
    # manual: bool
    # """manual (``bool``, *optional*):
    #     Whether the webpage preview was changed by the user."""
    duration: int | None
    author: str | None

    __pyro_class__ = pyrogram.WebPage


@dataclass(frozen=True)
class PollLike(ABC):
    # TODO: map all fields
    # TODO: add AnsweredPoll / AnsweredQuiz
    tg_id: int
    question: Text
    is_anonymous: bool | None
    open_period: int | None
    close_date: dt | None
    total_voter_count: int
    options: Sequence[PollOption]

    __pyro_class__ = pyrogram.Poll


@dataclass(frozen=True)
class PollOption:
    text: Text
    # voter_count: int

    __pyro_class__ = pyrogram.PollOption


@dataclass(frozen=True)
class Poll(PollLike):
    allows_multiple_answers: bool


@dataclass(frozen=True)
class Quiz(PollLike):
    pass
    # explanation: Text


@dataclass(frozen=True)
class Dice:
    emoji: str
    value: int

    __pyro_class__ = pyrogram.Dice


@dataclass(frozen=True)
class ChatPhoto:
    small: File
    big: File
    has_animation: bool
    is_personal: bool

    __pyro_class__ = pyrogram.ChatPhoto


@dataclass(frozen=True)
class User:
    tg_id: int


@dataclass(frozen=True)
class UserDetailed(User):
    user_id: int
    is_contact: bool
    is_mutual_contact: bool
    is_deleted: bool
    verification_status: VerificationStatus
    is_restricted: bool
    is_support: bool
    is_premium: bool
    first_name: str
    last_name: str | None
    username: str | None
    language_code: str | None
    emoji_status: EmojiStatus | None
    phone_number: str | None
    photo: ChatPhoto | None

    __pyro_class__ = pyrogram.User

    @property
    def is_verified(self) -> bool:
        return self.verification_status.is_verified

    @property
    def is_scam(self) -> bool:
        return self.verification_status.is_scam

    @property
    def is_fake(self) -> bool:
        return self.verification_status.is_fake


@dataclass(frozen=True)
class CustomEmoji:
    tg_id: int


@dataclass(frozen=True)
class EmojiStatus:
    custom_emoji_id: int
    until_date: dt | None

    __pyro_class__ = pyrogram.EmojiStatus


@dataclass(frozen=True)
class Restriction:
    platform: str
    reason: str
    text: str

    __pyro_class__ = pyrogram.Restriction


@dataclass(frozen=True)
class ChatPermissions:
    # Text, contacts, locations and venues
    can_send_messages: bool | None
    # Audio files, documents, photos, videos, video notes and voice notes
    can_send_media_messages: bool | None
    # Stickers, animations, games, inline bots
    can_send_other_messages: bool | None
    can_send_polls: bool | None
    can_add_web_page_previews: bool | None
    can_change_info: bool | None
    can_invite_users: bool | None
    can_pin_messages: bool | None

    __pyro_class__ = pyrogram.ChatPermissions


@dataclass(frozen=True)
class VerificationStatus:
    is_verified: bool
    is_scam: bool
    is_fake: bool
    bot_verification_icon_custom_emoji_id: int | None = None


@dataclass(frozen=True)
class ReplyColor:
    color: pyrogram_enums.ReplyColor | None
    bg_emoji: CustomEmoji | None


@dataclass(frozen=True)
class ProfileColor:
    color: pyrogram_enums.ProfileColor | None
    bg_emoji: CustomEmoji | None


JSON: TypeAlias = str | int | float | None | list["JSON"] | dict[str, "JSON"]


class OnDemand(Protocol[Value]):
    @abstractmethod
    def get(self) -> Value:
        raise NotImplementedError


@dataclass(frozen=True, eq=False)
class Chat:
    # TODO: map fields properly
    tg_id: int
    type: ChatType | Literal[Unavailable.UNAVAILABLE] = field(kw_only=True)
    raw_json: OnDemand[JSON] | None = field(kw_only=True, default=None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chat):
            return False

        if self.tg_id == other.tg_id and self.type == other.type:
            return True

        return False


@dataclass(frozen=True, repr=False)
class DeletedUserDialog(Chat):
    type: Literal[ChatType.PRIVATE] = field(kw_only=True, default=ChatType.PRIVATE)

    def __repr__(self) -> str:
        return f"<Deleted User #{self.tg_id}>"


@dataclass(frozen=True)
class Dialog(Chat, ABC):
    type: Literal[ChatType.PRIVATE, ChatType.BOT, ChatType.DIRECT] = field(kw_only=True)
    is_restricted: bool
    is_support: bool
    verification_status: VerificationStatus
    username: str | None
    usernames: list[str] | None
    # bio: str | None  # Returned only in :meth:`~pyrogram.Client.get_chat`
    photo: ChatPhoto | None
    restrictions: Sequence[Restriction]

    @property
    def is_verified(self) -> bool:
        return self.verification_status.is_verified

    @property
    def is_scam(self) -> bool:
        return self.verification_status.is_scam

    @property
    def is_fake(self) -> bool:
        return self.verification_status.is_fake


@dataclass(frozen=True, repr=False)
class UserDialog(Dialog):
    type: Literal[ChatType.PRIVATE] = field(kw_only=True, default=ChatType.PRIVATE)
    first_name: str
    last_name: str | None
    # is_stories_hidden: bool
    # is_stories_unavailable: bool
    reply_color: ReplyColor | None
    profile_color: ProfileColor | None
    paid_message_star_count: int | None

    def __repr__(self) -> str:
        if self.last_name:
            qualname = f"{self.first_name} {self.last_name}"
        else:
            qualname = self.first_name
        return f"<Dialog (User) '{qualname}'>"


@dataclass(frozen=True, repr=False)
class BotDialog(Dialog, ABC):
    type: Literal[ChatType.BOT] = field(kw_only=True, default=ChatType.BOT)
    first_name: str
    is_business_bot: bool

    def __repr__(self) -> str:
        return f"<Dialog (Bot) '{self.first_name}'>"


@dataclass(frozen=True, repr=False)
class UsualBotDialog(BotDialog):
    username: str


@dataclass(frozen=True, repr=False)
class SpecialBotDialog(BotDialog):
    pass


@dataclass(frozen=True)
class GroupChat(Chat, ABC):
    title: str
    is_deactivated: bool
    is_call_active: bool
    is_call_not_empty: bool
    usernames: Sequence[str] | None
    photo: ChatPhoto | None
    permissions: ChatPermissions | None  # None for unavailable


@dataclass(frozen=True, repr=False)
class UnavailableChat(GroupChat):
    # NOTE: basically same fields as in GroupChat
    type: Literal[Unavailable.UNAVAILABLE] = field(kw_only=True, default=Unavailable.UNAVAILABLE)

    def __repr__(self) -> str:
        return f"<ForbiddenChat '{self.title}'>"


@dataclass(frozen=True, repr=False)
class Group(GroupChat):
    type: Literal[ChatType.GROUP] = field(kw_only=True, default=ChatType.GROUP)
    tg_id: int
    title: str
    usernames: Sequence[str] | None
    permissions: ChatPermissions | None
    has_protected_content: bool

    def __repr__(self) -> str:
        return f"<Chat '{self.title}'>"


@dataclass(frozen=True, repr=False)
class GroupDetails(Group):
    """
    Including all the info from :meth:`~pyrogram.Client.get_chat`.
    """
    description: str
    invite_link: str | None
    members_count: int


@dataclass(frozen=True, repr=False)
class Supergroup(GroupChat):
    type: Literal[ChatType.SUPERGROUP] = field(kw_only=True, default=ChatType.SUPERGROUP)
    verification_status: VerificationStatus | None
    is_restricted: bool
    is_forum: bool
    # is_creator: bool
    restrictions: Sequence[Restriction]
    permissions: ChatPermissions  # default permissions

    def __repr__(self) -> str:
        return f"<Chat '{self.title}'>"


@dataclass(frozen=True, repr=False)
class SupergroupDetails(Supergroup):
    """
    Including all the info from :meth:`~pyrogram.Client.get_chat`.
    """
    description: str | None
    members_count: int
    sticket_set_name: str | None
    can_set_sticker_set: bool | None
    invite_link: str | None
    pinned_message: ChannelPost | None
    linked_channel: Channel | None


@dataclass(frozen=True, repr=False)
class Channel(Chat):
    type: Literal[ChatType.CHANNEL] = field(kw_only=True, default=ChatType.CHANNEL)
    title: str
    photo: ChatPhoto | None
    verification_status: VerificationStatus | None
    is_restricted: bool
    restrictions: Sequence[Restriction]
    permissions: ChatPermissions | None

    def __repr__(self) -> str:
        return f"<Channel '{self.title}'>"


@dataclass(frozen=True, repr=False)
class ChannelDetails(Channel):
    """
    Including all the info from :meth:`~pyrogram.Client.get_chat`.
    """
    description: str | None
    invite_link: str | None
    members_count: int
    pinned_message: ChannelPost | None
    linked_chat: Supergroup | None


@dataclass(frozen=True)
class ChannelDM(Channel):
    type: Literal[ChatType.DIRECT] = field(kw_only=True, default=ChatType.DIRECT)  # type: ignore

    def __repr__(self) -> str:
        return f"<Channel DM '{self.title}'>"


# @dataclass
class ChatReactions:
    """
    A chat reactions

    Parameters:
        all_are_enabled (``bool``, *optional*)

        allow_custom_emoji (``bool``, *optional*):
            Whether custom emoji are allowed or not.

        reactions (List of :obj:`~pyrogram.types.Reaction`, *optional*):
            Reactions available.
    """
    all_are_enabled: bool | None
    allow_custom_emoji: bool | None
    # reactions: Sequence[Reaction] = None


# @dataclass
class Reaction:
    """
    Contains information about a reaction.

    Parameters:
        emoji (``str``, *optional*):
            Reaction emoji.

        custom_emoji_id (``int``, *optional*):
            Custom emoji id.

        count (``int``, *optional*):
            Reaction count.

        chosen_order (``int``, *optional*):
            Chosen reaction order.
            Available for chosen reactions.
    """
    emoji: str | None
    custom_emoji_id: int | None
    count: int | None
    chosen_order: int | None


@dataclass(frozen=True)
class TextEntity(ABC):
    offset: int
    length: int

    __pyro_mark__: ClassVar[MessageEntityType]


@dataclass(frozen=True)
class Mention(TextEntity):
    __pyro_mark__ = MessageEntityType.MENTION


@dataclass(frozen=True)
class Hashtag(TextEntity):
    __pyro_mark__ = MessageEntityType.HASHTAG


@dataclass(frozen=True)
class Cashtag(TextEntity):
    __pyro_mark__ = MessageEntityType.CASHTAG


@dataclass(frozen=True)
class BotCommand(TextEntity):
    __pyro_mark__ = MessageEntityType.BOT_COMMAND


@dataclass(frozen=True)
class URL(TextEntity):
    __pyro_mark__ = MessageEntityType.URL


@dataclass(frozen=True)
class Email(TextEntity):
    __pyro_mark__ = MessageEntityType.EMAIL


@dataclass(frozen=True)
class PhoneNumber(TextEntity):
    __pyro_mark__ = MessageEntityType.PHONE_NUMBER


@dataclass(frozen=True)
class Bold(TextEntity):
    __pyro_mark__ = MessageEntityType.BOLD


@dataclass(frozen=True)
class Italic(TextEntity):
    __pyro_mark__ = MessageEntityType.ITALIC


@dataclass(frozen=True)
class Underline(TextEntity):
    __pyro_mark__ = MessageEntityType.UNDERLINE


@dataclass(frozen=True)
class Strikethrough(TextEntity):
    __pyro_mark__ = MessageEntityType.STRIKETHROUGH


@dataclass(frozen=True)
class Spoiler(TextEntity):
    __pyro_mark__ = MessageEntityType.SPOILER


@dataclass(frozen=True)
class Code(TextEntity):
    __pyro_mark__ = MessageEntityType.CODE


@dataclass(frozen=True)
class Pre(TextEntity):
    language: str | None

    __pyro_mark__ = MessageEntityType.PRE


@dataclass(frozen=True)
class BlockQuote(TextEntity):
    __pyro_mark__ = MessageEntityType.BLOCKQUOTE


@dataclass(frozen=True)
class TextLink(TextEntity):
    url: str

    __pyro_mark__ = MessageEntityType.TEXT_LINK


@dataclass(frozen=True)
class TextMention(TextEntity):
    user: User

    __pyro_mark__ = MessageEntityType.TEXT_MENTION


@dataclass(frozen=True)
class BankCard(TextEntity):
    __pyro_mark__ = MessageEntityType.BANK_CARD


@dataclass(frozen=True)
class CustomEmojiEntity(TextEntity):
    custom_emoji: CustomEmoji

    __pyro_mark__ = MessageEntityType.CUSTOM_EMOJI


@dataclass(frozen=True)
class UnknownEntity(TextEntity):
    __pyro_mark__ = MessageEntityType.UNKNOWN


MessagePayloadType: TypeAlias = MessageMediaType | MessageServiceType


@dataclass(frozen=True)
class Message(ABC):
    __pyro_class__: ClassVar[type] = pyrogram.Message
    __pyro_mark__: ClassVar[MessagePayloadType]


# Message sources:
#  From user - from_user: User
#  On behalf of a chat - sender_chat: Chat
#  Channel post - sender_chat: Chat, author_signature: str None
#  From anon admin - sender_chat: Chat, author_signature: str None
#  Fwded to linked group - sender_chat: Chat


@dataclass(frozen=True)
class MessageSource(ABC):
    pass


@dataclass(frozen=True)
class FromUser(MessageSource):
    user: User


@dataclass(frozen=True)
class FromChannelAdmin(MessageSource):
    channel: Channel
    author_signature: str | None


@dataclass(frozen=True)
class FromChannel(MessageSource):
    channel: Channel


@dataclass(frozen=True)
class FromAnonAdmin(MessageSource):
    chat: Chat
    admin_mark: str | None


@dataclass(frozen=True)
class ForwardOrigin(ABC):
    pass

# Forward sources:
#  From user - forward_from: User
#  From anon user - forward_sender_name: str
#  Auto from linked channel - sender_chat: Chat
#  From channdel - forward_from_chat: Chat, forward_from_message_id: int, forward_signature: str None
#  From chat - forward_from_chat: Chat
#  From anon chat admin - forward_from_chat: Chat


@dataclass(frozen=True)
class AnonUserOrigin(ForwardOrigin):
    sender_name: str


@dataclass(frozen=True)
class UserOrigin(ForwardOrigin):
    user: User


@dataclass(frozen=True)
class _ChannelOrigin(ForwardOrigin):
    channel: Channel
    source_message_id: int
    author_signature: str | None


@dataclass(frozen=True)
class LinkedChannelOrigin(_ChannelOrigin):
    pass


@dataclass(frozen=True)
class ChannelOrigin(_ChannelOrigin):
    pass


@dataclass(frozen=True)
class AnonAdminOrigin(ForwardOrigin):
    chat: Chat
    admin_mark: str | None


@dataclass(frozen=True)
class ChatMessage:
    chat: Chat
    msg_no: int
    sender: MessageSource
    has_protected_content: bool
    date: dt
    payload: Message


@dataclass(frozen=True)
class ChannelPost:
    channel: Channel
    msg_no: int
    sender: MessageSource
    has_protected_content: bool
    date: dt
    payload: Message
    views: int
    forwards: int


BoundMessage: TypeAlias = ChatMessage | ChannelPost


class Quote:
    text: Text
    position: int
    is_manual: bool


class MessageReply:
    message_id: int
    thread_starter_id: int
    quote: Quote


class ExtenalReply:
    origin: ForwardOrigin
    message_id: int
    chat: Chat
    quote: Quote

    __pyro_class__ = pyrogram.ExternalReplyInfo


class ExternalPrivateReply:
    origin: ForwardOrigin
    quote: Quote


class StoryReply:
    story: Story


class ChecklistTaskReply:
    checklist_task_id: int


class ReplyInfo:
    # reply_to_message_id: int
    # reply_to_story_id: int
    # reply_to_story_user_id: int
    # reply_to_top_message_id: int

    reply_to_message_id: int | None
    """(``int``, *optional*) The id of the message which this message directly replied to."""

    reply_to_story_id: int | None
    """(``int``, *optional*) The id of the story which this message directly replied to."""

    reply_to_story_user_id: int | None
    """(``int``, *optional*) The id of the story sender which this message directly replied to."""

    reply_to_top_message_id: int | None
    """(``int``, *optional*) The id of the first message which started this message thread."""

    # reply_to_message
    # """(:obj:`~pyrogram.types.Message`, *optional*) For replies, the original message. Note that the Message object in this field will not contain  # noqa
    # further reply_to_message fields even if it itself is a reply."""

    reply_to_story: Story | None
    """(:obj:`~pyrogram.types.Story`, *optional*) For replies, the original story."""

    reply_to_checklist_task_id: int | None
    """(``int``, *optional*) Identifier of the specific checklist task that is being replied to."""


class ExternalReplyInfo:
    __pyro_class__ = pyrogram.ExternalReplyInfo


@dataclass(frozen=True)
class Forwarded(Message):
    origin: ForwardOrigin
    origin_date: dt | None
    message: Message


@dataclass(frozen=True)
class TextMessage(Message):
    text: Text


@dataclass(frozen=True)
class ServiceMessage(Message, ABC):
    __pyro_mark__: ClassVar[MessageServiceType]  # type: ignore


@dataclass(frozen=True)
class BorkedServiceMessage(ServiceMessage):
    raw_json: OnDemand[JSON] | None = field(kw_only=True, default=None)

    __pyro_mark__ = None


@dataclass(frozen=True)
class UnsupportedServiceMessage(ServiceMessage):
    raw_json: OnDemand[JSON] | None = field(kw_only=True, default=None)

    __pyro_mark__ = MessageServiceType.UNSUPPORTED


@dataclass(frozen=True)
class CustomAction(ServiceMessage):
    message: str  # NOTE: is it really hust unformatted string?

    __pyro_mark__ = MessageServiceType.CUSTOM_ACTION


@dataclass(frozen=True)
class NewChatMembers(ServiceMessage):
    new_chat_members: Sequence[User]

    __pyro_mark__ = MessageServiceType.NEW_CHAT_MEMBERS


@dataclass(frozen=True)
class LeftChatMember(ServiceMessage):
    left_user: User

    __pyro_mark__ = MessageServiceType.LEFT_CHAT_MEMBER


@dataclass(frozen=True)
class ChatOwnerLeft(ServiceMessage):
    new_owner: User | None

    __pyro_class__ = pyrogram.ChatOwnerLeft
    __pyro_mark__ = MessageServiceType.CHAT_OWNER_LEFT


@dataclass(frozen=True)
class ChatOwnerChanged(ServiceMessage):
    new_owner: User

    __pyro_class__ = pyrogram.ChatOwnerChanged
    __pyro_mark__ = MessageServiceType.CHAT_OWNER_CHANGED


@dataclass(frozen=True)
class NewChatTitle(ServiceMessage):
    new_chat_title: str

    __pyro_mark__ = MessageServiceType.NEW_CHAT_TITLE


@dataclass(frozen=True)
class NewChatPhoto(ServiceMessage):
    new_chat_photo: Photo | None  # None for cases when photo unavailable (deleted)

    __pyro_mark__ = MessageServiceType.NEW_CHAT_PHOTO


@dataclass(frozen=True)
class ChatPhotoDeleted(ServiceMessage):
    __pyro_mark__ = MessageServiceType.DELETE_CHAT_PHOTO


@dataclass(frozen=True)
class ForumTopicCreated(ServiceMessage):
    id: int
    title: str
    icon_color: int
    custom_emoji: CustomEmoji | None = None

    __pyro_class__ = pyrogram.ForumTopicCreated
    __pyro_mark__ = MessageServiceType.FORUM_TOPIC_CREATED


@dataclass(frozen=True)
class ForumTopicClosed(ServiceMessage):
    __pyro_class__ = pyrogram.ForumTopicClosed
    __pyro_mark__ = MessageServiceType.FORUM_TOPIC_CLOSED


@dataclass(frozen=True)
class ForumTopicReopened(ServiceMessage):
    __pyro_class__ = pyrogram.ForumTopicReopened
    __pyro_mark__ = MessageServiceType.FORUM_TOPIC_REOPENED


@dataclass(frozen=True)
class ForumTopicEdited(ServiceMessage):
    title: str | None = None
    icon_color: int | None = None
    custom_emoji: CustomEmoji | None = None
    is_closed: bool | None = None
    is_hidden: bool | None = None
    """
    True, if the topic is hidden.
    Valid only for the "General" topic with id=1
    """

    __pyro_class__ = pyrogram.ForumTopicEdited
    __pyro_mark__ = MessageServiceType.FORUM_TOPIC_EDITED


@dataclass(frozen=True)
class GeneralForumTopicHidden(ServiceMessage):
    __pyro_class__ = pyrogram.GeneralForumTopicHidden
    __pyro_mark__ = MessageServiceType.GENERAL_FORUM_TOPIC_HIDDEN


@dataclass(frozen=True)
class GeneralForumTopicUnhidden(ServiceMessage):
    __pyro_class__ = pyrogram.GeneralForumTopicUnhidden
    __pyro_mark__ = MessageServiceType.GENERAL_FORUM_TOPIC_UNHIDDEN


@dataclass(frozen=True)
class GroupCreated(ServiceMessage):
    __pyro_mark__ = MessageServiceType.GROUP_CHAT_CREATED


@dataclass(frozen=True)
class SupergroupCreated(ServiceMessage):
    # NOTE: weird shit in pyro
    __pyro_mark__ = MessageServiceType.SUPERGROUP_CHAT_CREATED


@dataclass(frozen=True)
class ChannelCreated(ServiceMessage):
    __pyro_mark__ = MessageServiceType.CHANNEL_CHAT_CREATED


@dataclass(frozen=True)
class MigrateToSupergroup(ServiceMessage):
    migrate_to_chat: Chat

    __pyro_mark__ = MessageServiceType.MIGRATE_TO_CHAT_ID


@dataclass(frozen=True)
class MigrateFromGroup(ServiceMessage):
    migrate_from_chat: Chat

    __pyro_mark__ = MessageServiceType.MIGRATE_FROM_CHAT_ID


@dataclass(frozen=True)
class MessagePinned(ServiceMessage):
    # TODO: decide on referring to actual messages table
    pinned_message_id: int

    __pyro_mark__ = MessageServiceType.PINNED_MESSAGE


@dataclass(frozen=True)
class GameHighScore(ServiceMessage):
    user: User
    score: int

    __pyro_mark__ = MessageServiceType.GAME_HIGH_SCORE


@dataclass(frozen=True)
class GiveawayCreated(ServiceMessage):
    # TODO: add info from pyro
    __pyro_class__ = pyrogram.GiveawayCreated
    __pyro_mark__ = MessageServiceType.GIVEAWAY_CREATED


@dataclass(frozen=True)
class GiveawayCompleted(ServiceMessage):
    winner_count: int
    unclaimed_prize_count: int
    giveaway_message_id: int
    # giveaway_message: "types.Message" = None
    is_star_giveaway: bool

    __pyro_class__ = pyrogram.GiveawayCompleted
    __pyro_mark__ = MessageServiceType.GIVEAWAY_COMPLETED


@dataclass(frozen=True)
class CurrencyAmount:
    currency: str
    """ISO name"""

    amount: int


@dataclass(frozen=True)
class CryptocurrencyAmount:
    currency: str
    amount: int


MoneyAmount: TypeAlias = CurrencyAmount | CryptocurrencyAmount


@dataclass(frozen=True)
class PremiumGiftCode(ServiceMessage):
    # creator: User | Chat  # TODO: look into kurigram and decide how to map this shit
    code: str
    caption: Text | None
    month_count: int
    day_count: int
    price: MoneyAmount
    is_unclaimed: bool
    is_from_giveaway: bool

    __pyro_class__ = pyrogram.PremiumGiftCode
    __pyro_mark__ = MessageServiceType.PREMIUM_GIFT_CODE


@dataclass(frozen=True)
class GiftedPremium(ServiceMessage):
    receiver: User
    gifter: User | None = field(kw_only=True)
    price: MoneyAmount = field(kw_only=True)
    month_count: int = field(kw_only=True)
    day_count: int = field(kw_only=True)
    sticker: Sticker | None = field(kw_only=True, default=None)
    caption: Text | None = field(kw_only=True, default=None)

    __pyro_class__ = pyrogram.GiftedPremium
    __pyro_mark__ = MessageServiceType.GIFTED_PREMIUM


@dataclass(frozen=True)
class GiftedStars(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.GiftedStars
    __pyro_mark__ = MessageServiceType.GIFTED_STARS


@dataclass(frozen=True)
class GiftedTON(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.GiftedTon
    __pyro_mark__ = MessageServiceType.GIFTED_TON


@dataclass(frozen=True)
class VideoChatStarted(ServiceMessage):
    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_STARTED


@dataclass(frozen=True)
class VideoChatEnded(ServiceMessage):
    duratioin: int

    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_ENDED


@dataclass(frozen=True)
class VideoChatScheduled(ServiceMessage):
    start_date: dt

    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_SCHEDULED


@dataclass(frozen=True)
class VideoChatMembersInvited(ServiceMessage):
    video_chat_members_invited: Sequence[User]

    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED


@dataclass(frozen=True)
class PhoneCallStarted(ServiceMessage):
    tg_id: int
    is_video: bool = False

    __pyro_class__ = pyrogram.PhoneCallStarted
    __pyro_mark__ = MessageServiceType.PHONE_CALL_STARTED


@dataclass(frozen=True)
class PhoneCallEnded(ServiceMessage):
    # TODO: separated classes for different reasons?
    call_id: int
    is_video: bool
    reason: PhoneCallDiscardReason
    duration: int | None = None

    __pyro_class__ = pyrogram.PhoneCallEnded
    __pyro_mark__ = MessageServiceType.PHONE_CALL_ENDED


@dataclass(frozen=True)
class WebAppData(ServiceMessage):
    data: str
    button_text: str

    __pyro_class__ = pyrogram.WebAppData
    __pyro_mark__ = MessageServiceType.WEB_APP_DATA


@dataclass(frozen=True)
class UsersShared(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.UsersShared
    __pyro_mark__ = MessageServiceType.USERS_SHARED


@dataclass(frozen=True)
class ChatShared(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.ChatShared
    __pyro_mark__ = MessageServiceType.CHAT_SHARED


@dataclass(frozen=True)
class SuccessfulPayment(ServiceMessage):
    currency: str
    """
    (``str``) Three-letter ISO 4217 `currency <https://core.telegram.org/bots/payments#supported-currencies>`_ code,
     or ``XTR`` for payments in `Telegram Stars <https://t.me/BotNews/90>`_.
    """

    total_amount: int
    """
    (``int``) Total price in the smallest units of the currency (integer, **not** float/double).
    For example, for a price of ``US$ 1.45`` pass ``amount = 145``.
    See the __exp__ parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_,
     it shows the number of digits past the decimal point for each currency (2 for the majority of currencies).
    """

    # invoice_payload: int | None
    # """(``str``, *optional*) Bot specified invoice payload. Only available to the bot that received the payment."""

    # telegram_payment_charge_id: int | None
    # """(``str``, *optional*) Telegram payment identifier. Only available to the bot that received the payment."""

    # provider_payment_charge_id: int | None
    # """(``str``, *optional*) Provider payment identifier. Only available to the bot that received the payment."""

    # shipping_option_id: int | None
    # """(``str``, *optional*) Identifier of the shipping option chosen by the user. Only available to the bot that received the payment."""  # noqa

    # payment_info: Any | None
    # """(:obj:`~pyrogram.types.PaymentInfo`, *optional*) Payment information provided by the user. Only available to the bot that received the payment."""  # noqa

    invoice_slug: str | None
    """(``str``, *optional*) Name of the invoice."""

    __pyro_class__ = pyrogram.SuccessfulPayment
    __pyro_mark__ = MessageServiceType.SUCCESSFUL_PAYMENT


@dataclass(frozen=True)
class SuccessfulSubscriptionPayment(SuccessfulPayment):
    first_time: bool
    """(``bool``, *optional*) True, if the payment is the first payment for a subscription."""

    subscription_expiration_date: dt | None
    """
    (:py:obj:`~datetime.datetime`, *optional*) Expiration date of the subscription, in Unix time;
    for recurring payments only.
    """


@dataclass(frozen=True)
class RefundedPayment(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.RefundedPayment
    __pyro_mark__ = MessageServiceType.REFUNDED_PAYMENT


@dataclass(frozen=True)
class SuggestedPostApprovalFailed(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.SuggestedPostApprovalFailed
    __pyro_mark__ = MessageServiceType.SUGGESTED_POST_APPROVAL_FAILED


@dataclass(frozen=True)
class SuggestedPostApproved(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.SuggestedPostApproved
    __pyro_mark__ = MessageServiceType.SUGGESTED_POST_APPROVED


@dataclass(frozen=True)
class SuggestedPostDeclined(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.SuggestedPostDeclined
    __pyro_mark__ = MessageServiceType.SUGGESTED_POST_DECLINED


@dataclass(frozen=True)
class SuggestedPostPaid(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.SuggestedPostPaid
    __pyro_mark__ = MessageServiceType.SUGGESTED_POST_PAID


@dataclass(frozen=True)
class SuggestedPostRefunded(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.SuggestedPostRefunded
    __pyro_mark__ = MessageServiceType.SUGGESTED_POST_REFUNDED


@dataclass(frozen=True)
class SetMessageAutodeleteTime(ServiceMessage):
    message_ttl: int

    __pyro_mark__ = MessageServiceType.SET_MESSAGE_AUTO_DELETE_TIME


@dataclass(frozen=True)
class MessageAutodeleteDisabled(ServiceMessage):
    __pyro_mark__ = MessageServiceType.SET_MESSAGE_AUTO_DELETE_TIME


@dataclass(frozen=True)
class ChatBoost(ServiceMessage):
    amount: int

    __pyro_mark__ = MessageServiceType.CHAT_BOOST


class ChatBoostDetails:
    # TODO: map fields from pyro class

    # id: str
    # """(``str``) Unique identifier for this set of boosts."""

    # date: dt
    # """(:py:obj:`~datetime.datetime`) Date the boost was applied."""

    # expire_date: dt
    # """(:py:obj:`~datetime.datetime`) Point in time when the boost will expire."""

    # multiplier: int
    # """(``int``) If set, this boost counts as multiplier boosts, otherwise it counts as a single boost."""

    __pyro_class__ = pyrogram.ChatBoost


@dataclass(frozen=True)
class Gifted(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.Gift
    __pyro_mark__ = MessageServiceType.GIFT


@dataclass(frozen=True)
class ConnectedWebsite(ServiceMessage):
    domain: str

    __pyro_mark__ = MessageServiceType.CONNECTED_WEBSITE


@dataclass(frozen=True)
class WriteAccessAllowed(ServiceMessage):
    from_request: bool
    from_attachment_menu: bool
    web_app_name: str | None = None

    __pyro_class__ = pyrogram.WriteAccessAllowed
    __pyro_mark__ = MessageServiceType.WRITE_ACCESS_ALLOWED


@dataclass(frozen=True)
class ScreenshotTaken(ServiceMessage):
    __pyro_class__ = pyrogram.ScreenshotTaken
    __pyro_mark__ = MessageServiceType.SCREENSHOT_TAKEN


@dataclass(frozen=True)
class ContactRegistered(ServiceMessage):
    __pyro_class__ = pyrogram.ContactRegistered
    __pyro_mark__ = MessageServiceType.CONTACT_REGISTERED


@dataclass(frozen=True)
class ProximityAlertTriggered(ServiceMessage):
    traveler: Chat
    watcher: Chat
    distance: int

    __pyro_class__ = pyrogram.ProximityAlertTriggered
    __pyro_mark__ = MessageServiceType.PROXIMITY_ALERT_TRIGGERED


@dataclass(frozen=True)
class HistoryCleared(ServiceMessage):
    __pyro_class__ = pyrogram.HistoryCleared
    __pyro_mark__ = MessageServiceType.HISTORY_CLEARED


@dataclass(frozen=True)
class SuggestedProfilePhoto(ServiceMessage):
    photo: Photo

    __pyro_mark__ = MessageServiceType.SUGGEST_PROFILE_PHOTO


@dataclass(frozen=True)
class Birthday:
    day: int
    month: int
    year: int | None = None


@dataclass(frozen=True)
class SuggestedBirthday(ServiceMessage):
    birthday: Birthday

    __pyro_class__ = pyrogram.Birthday
    __pyro_mark__ = MessageServiceType.SUGGEST_BIRTHDAY


@dataclass(frozen=True)
class SetChatBackground(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.ChatBackground
    __pyro_mark__ = MessageServiceType.CHAT_SET_BACKGROUND


@dataclass(frozen=True)
class SetChatEmojiTheme(ServiceMessage):
    name: str

    __pyro_class__ = pyrogram.ChatTheme
    __pyro_mark__ = MessageServiceType.CHAT_SET_THEME


@dataclass(frozen=True)
class SetChatGiftTheme(ServiceMessage):
    # TODO
    # gift: Gift  # pyrogram.Gift

    __pyro_class__ = pyrogram.ChatTheme
    __pyro_mark__ = MessageServiceType.CHAT_SET_THEME


@dataclass(frozen=True)
class GiveawayPrizeStars(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.GiveawayPrizeStars
    __pyro_mark__ = MessageServiceType.GIVEAWAY_PRIZE_STARS


@dataclass(frozen=True)
class PaidMessagesRefunded(ServiceMessage):
    messages_count: int
    stars_amount: int

    __pyro_class__ = pyrogram.PaidMessagesRefunded
    __pyro_mark__ = MessageServiceType.PAID_MESSAGES_REFUNDED


@dataclass(frozen=True)
class PaidMessagesPriceChanged(ServiceMessage):
    new_price: int

    __pyro_class__ = pyrogram.PaidMessagesPriceChanged
    __pyro_mark__ = MessageServiceType.PAID_MESSAGES_PRICE_CHANGED


@dataclass(frozen=True)
class DirectMessagesPriceChanged(ServiceMessage):
    is_enabed: bool  # need a None check?
    new_price: int

    __pyro_class__ = pyrogram.DirectMessagePriceChanged
    __pyro_mark__ = MessageServiceType.DIRECT_MESSAGE_PRICE_CHANGED


@dataclass(frozen=True)
class ChecklistTasksDone(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.ChecklistTasksDone
    __pyro_mark__ = MessageServiceType.CHECKLIST_TASKS_DONE


@dataclass(frozen=True)
class ChecklistTasksAdded(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.ChecklistTasksAdded
    __pyro_mark__ = MessageServiceType.CHECKLIST_TASKS_ADDED


@dataclass(frozen=True)
class UpgradedGiftPurchaseOffer(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.UpgradedGiftPurchaseOffer
    __pyro_mark__ = MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER


@dataclass(frozen=True)
class UpgradedGiftPurchaseOfferRejected(ServiceMessage):
    # TODO: map fields from pyro class
    __pyro_class__ = pyrogram.UpgradedGiftPurchaseOfferRejected
    __pyro_mark__ = MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER_REJECTED



Media: TypeAlias = (
    Audio | Document | Photo | Sticker | Video | Animation | Voice | VideoNote
    | Contact | Location | LiveLocation | BusinessLocation | Venue | Poll | Quiz | WebPage | Dice | Game
    | StarsGiveaway | SubscriptionsGiveaway | StarsGiveawayWinners | SubscriptionsGiveawayWinners
    | Story | Invoice | PaidMedia | Checklist | DisappearedMedia
)


@dataclass(frozen=True)
class MediaMessage(Message, ABC):
    caption: Text | None
    media: Media
    media_group_id: int | None
    has_media_spoiler: bool | None

    __pyro_marks__ = (
        MessageMediaType.AUDIO,
        MessageMediaType.DOCUMENT,
        MessageMediaType.PHOTO,
        MessageMediaType.STICKER,
        MessageMediaType.VIDEO,
        MessageMediaType.ANIMATION,
        MessageMediaType.VOICE,
        MessageMediaType.VIDEO_NOTE,
        MessageMediaType.CONTACT,
        MessageMediaType.LOCATION,
        MessageMediaType.VENUE,
        MessageMediaType.POLL,
        MessageMediaType.WEB_PAGE,
        MessageMediaType.DICE,
        MessageMediaType.GAME,
        MessageMediaType.GIVEAWAY,
        MessageMediaType.GIVEAWAY_WINNERS,
        MessageMediaType.STORY,
        MessageMediaType.INVOICE,
        MessageMediaType.PAID_MEDIA,
        MessageMediaType.CHECKLIST,
    )


TGMedia: TypeAlias = (
    pyrogram.Audio
    | pyrogram.Document
    | pyrogram.Photo
    | pyrogram.Sticker
    | pyrogram.Video
    | pyrogram.Animation
    | pyrogram.Voice
    | pyrogram.VideoNote
    | pyrogram.Contact
    | pyrogram.Location
    | pyrogram.Venue
    | pyrogram.Poll
    | pyrogram.WebPage
    | pyrogram.Dice
    | pyrogram.Game
    | pyrogram.Giveaway
    | pyrogram.GiveawayWinners
    | pyrogram.Story
    | pyrogram.Invoice
    | pyrogram.PaidMediaInfo
    | pyrogram.Checklist
)


class LocationType(StrEnum):
    USUAL = "USUAL"
    LIVE = "LIVE"
    BUSINESS = "BUSINESS"


class HasPriceInfo(Protocol):
    currency: str | None
    amount: int | None = None
    cryptocurrency: str | None
    cryptocurrency_amount: int | None = None


@dataclass
class Export:
    started_at: date
    finished_at: date | None
    chats: MutableMapping[Chat, ChatExportPending | InfoExported | MessagesExporting]


@dataclass
class ChatExportPending:
    pass


@dataclass
class InfoExported:
    pass


@dataclass
class MessagesExporting:
    total_count: int
    exported_count: int
    last_exported: BoundMessage


@dataclass
class ChatExportDone:
    pass


@dataclass
class ExceptionDataclass(Exception, ABC):
    message: str

    def __new__(cls, message: str | None = None, *args: Any, **kwds: Any) -> Self:
        if message is not None:
            args = (message, *args)
        return super().__new__(cls, *args, **kwds)

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            super().__init__()
        else:
            super().__init__(message)
        self.message = message  # type: ignore

    def __str__(self) -> str:
        if self.message is not None:
            return self.message
        return super().__str__()


@dataclass
class UnexpectedEvaluationPath(ExceptionDataclass):
    pass


@dataclass
class TransformError(ExceptionDataclass, ABC):
    pass


@dataclass
class TransformValueError(TransformError, ValueError):
    value: Any | None = None


@dataclass
class TransformTypeError(TransformError, TypeError):
    value: Any | None = None


@dataclass
class TransformNotImplemented(TransformError):
    subject: Any | None = None


@dataclass
class TransformMissingRequiredField(TransformError, AttributeError):
    object: Any
    field_name: str | None = None


_PyroObj = TypeVar("_PyroObj", covariant=True, bound=pyrogram.object.Object)


@dataclass(frozen=True)
class PyroObject(OnDemand[JSON], Generic[_PyroObj]):
    obj: _PyroObj  # type: ignore

    def get(self) -> JSON:
        return pyrogram.object.Object.default(self.obj)


class FromPyrogram:
    def from_message(self, tg_message: pyrogram.Message) -> BoundMessage:
        payload: Message
        if tg_message.service is not None:
            payload = self.from_service_message(tg_message)
        elif tg_message.media is not None:
            payload = self.from_media_message(tg_message)
        elif tg_message.text:
            payload = TextMessage(text=self.from_string(tg_message.text))
        else:
            raise TransformValueError("I can't :(", tg_message)

        forward_source = self.get_forward_origin(tg_message)
        if forward_source is not None:
            payload = Forwarded(
                origin=forward_source,
                origin_date=cast(pyrogram.MessageOrigin, tg_message.forward_origin).date,
                message=payload,
            )

        sender = self.get_message_source(tg_message)

        message: BoundMessage
        if not tg_message.chat:
            raise TransformValueError("Message missing chat info", tg_message)

        reply_to_message_id = tg_message.reply_to_message_id
        reply_to_top_message_id = tg_message.reply_to_top_message_id
        reply_to_external = tg_message.external_reply
        reply_to_story_id = tg_message.reply_to_story_id
        reply_to_story_user_id = tg_message.reply_to_story_user_id
        reply_quote = tg_message.quote
        if reply_to_message_id:
            None  # pyright: ignore[reportUnusedExpression] # noqa
            if reply_to_top_message_id:
                None  # pyright: ignore[reportUnusedExpression] # noqa
        if reply_to_top_message_id and not reply_to_message_id:
            None  # never happens  # pyright: ignore[reportUnusedExpression] 
        if reply_to_external:
            None  # pyright: ignore[reportUnusedExpression] # noqa
            if not (reply_to_external.chat and reply_to_external.origin):
               None  # pyright: ignore[reportUnusedExpression] # noqa
        if reply_to_external and reply_quote:
            None  # pyright: ignore[reportUnusedExpression] # noqa
        if reply_to_story_id or reply_to_story_user_id:
            None  # pyright: ignore[reportUnusedExpression] # noqa
        if reply_quote:
            None  # pyright: ignore[reportUnusedExpression] # noqa

        if tg_message.chat.type == ChatType.CHANNEL:
            channel = self.from_channel(tg_message.chat)
            message = ChannelPost(
                channel=channel,
                msg_no=tg_message.id,
                sender=sender,
                has_protected_content=tg_message.has_protected_content,  # type: ignore
                date=tg_message.date,  # type: ignore
                payload=payload,
                views=tg_message.views,  # type: ignore
                forwards=tg_message.forwards,  # type: ignore
            )
        else:
            chat = self.from_chat(tg_message.chat)
            message = ChatMessage(
                chat=chat,
                msg_no=tg_message.id,
                sender=sender,
                has_protected_content=tg_message.has_protected_content,  # type: ignore
                date=tg_message.date,  # type: ignore
                payload=payload,
            )

        return message

    def get_message_source(self, tg_message: pyrogram.Message):
        if tg_message.from_user:
            user = self.from_user(tg_message.from_user)
            return FromUser(user=user)

        if not tg_message.sender_chat:
            raise ValueError("Message has no linking to chat/channel")

        if tg_message.sender_chat.type == ChatType.CHANNEL:
            return FromChannelAdmin(
                channel=self.from_channel(tg_message.sender_chat),
                author_signature=tg_message.author_signature,
            )
        if tg_message.sender_chat.type == ChatType.DIRECT:
            return FromChannel(
                channel=self.from_channel(tg_message.sender_chat),
            )
        if tg_message.sender_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.FORUM):
            chat = self.from_chat(tg_message.sender_chat)
            return FromAnonAdmin(
                chat=chat,
                admin_mark=tg_message.author_signature,
            )
        raise ValueError(f"Can't get any sender info from message {tg_message}")

    def get_forward_origin(
        self,
        tg_message: pyrogram.Message
    ) -> UserOrigin | LinkedChannelOrigin | ChannelOrigin | AnonUserOrigin | AnonAdminOrigin | None:
        forward_origin = tg_message.forward_origin
        if forward_origin is None:
            return None

        match forward_origin:
            case pyrogram.MessageOriginUser():
                user = self.from_user(forward_origin.sender_user)
                return UserOrigin(user=user)
            case pyrogram.MessageOriginHiddenUser():
                return AnonUserOrigin(sender_name=forward_origin.sender_user_name)
            case pyrogram.MessageOriginChat():
                return AnonAdminOrigin(
                    chat=self.from_chat(forward_origin.sender_chat),
                    admin_mark=forward_origin.author_signature
                )
            case pyrogram.MessageOriginChannel():
                channel = self.from_channel(forward_origin.chat)
                if tg_message.automatic_forward:
                    return LinkedChannelOrigin(
                        channel=channel,
                        source_message_id=forward_origin.message_id,
                        author_signature=forward_origin.author_signature,
                    )
                else:
                    return ChannelOrigin(
                        channel=channel,
                        source_message_id=forward_origin.message_id,
                        author_signature=forward_origin.author_signature,
                    )
            case pyrogram.MessageOriginImport():
                raise RuntimeError()
            case wtf:
                raise ValueError(f"Unknown forward origin: {wtf}")

        return None

    def from_string(self, string: Str | pyrogram.FormattedText | str) -> Text:
        match string:
            case Str() if string.entities:
                text = self.from_string_with_entities(string=string, tg_entities=string.entities)
            case str():
                text = Text(raw=str(string))
            case pyrogram.FormattedText():
                text = self.from_string_with_entities(string=string.text, tg_entities=string.entities)
            case unknown:
                raise ValueError(f"Can't represent {unknown!r} as text")

        return text

    def from_string_with_entities(self, string: str, *, tg_entities: Sequence[pyrogram.MessageEntity] | None) -> Text:
        tg_entities = tg_entities or []
        entities = [
            self.from_text_entity(entity)
            for entity in tg_entities
        ]
        text = Text(raw=str(string), entities=entities)
        return text

    def from_text_entity(self, tg_entity: pyrogram.MessageEntity) -> TextEntity:
        entity: TextEntity
        match tg_entity.type:
            case MessageEntityType.MENTION:
                entity = Mention(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.HASHTAG:
                entity = Hashtag(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.CASHTAG:
                entity = Cashtag(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.BOT_COMMAND:
                entity = BotCommand(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.URL:
                entity = URL(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.EMAIL:
                entity = Email(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.PHONE_NUMBER:
                entity = PhoneNumber(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.BOLD:
                entity = Bold(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.ITALIC:
                entity = Italic(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.UNDERLINE:
                entity = Underline(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.STRIKETHROUGH:
                entity = Strikethrough(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.SPOILER:
                entity = Spoiler(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.CODE:
                entity = Code(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.PRE:
                entity = Pre(offset=tg_entity.offset, length=tg_entity.length, language=tg_entity.language)
            case MessageEntityType.BLOCKQUOTE:
                entity = BlockQuote(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.TEXT_LINK:
                entity = TextLink(offset=tg_entity.offset, length=tg_entity.length, url=tg_entity.url)
            case MessageEntityType.TEXT_MENTION:
                entity = TextMention(
                    offset=tg_entity.offset,
                    length=tg_entity.length,
                    user=self.from_user(tg_entity.user),
                )
            case MessageEntityType.BANK_CARD:
                entity = BankCard(offset=tg_entity.offset, length=tg_entity.length)
            case MessageEntityType.CUSTOM_EMOJI:
                entity = CustomEmojiEntity(
                    offset=tg_entity.offset,
                    length=tg_entity.length,
                    custom_emoji=self.from_custom_emoji(tg_emoji_id=tg_entity.custom_emoji_id),
                )
            case MessageEntityType.UNKNOWN:
                entity = UnknownEntity(offset=tg_entity.offset, length=tg_entity.length)
            case unrecognised:
                raise ValueError(f"Unrecognized text entity type: {unrecognised}")

        return entity

    def from_user(self, tg_user: pyrogram.User) -> User:
        return User(tg_id=tg_user.id)
        return UserDetailed()  # TODO: map all accessible fields

    def from_chat(self, tg_chat: pyrogram.Chat) -> Chat:
        # TODO: map to specific chats types
        # TODO: find something with `tg_chat.public_photo`
        if tg_chat.id is None:
            raise TransformMissingRequiredField("pyrogram.Chat missing value for 'id' field",
                                                tg_chat, 'id')
        if tg_chat.type is None:
            raise TransformMissingRequiredField("pyrogram.Chat missing value for 'type' field",
                                                tg_chat, 'type')

        chat: UserDialog | BotDialog | Group | Supergroup | UnavailableChat | Channel | DeletedUserDialog
        match tg_chat.type:
            case ChatType.PRIVATE if tg_chat.first_name or tg_chat.last_name or tg_chat.bio:
                chat = UserDialog(
                    tg_id=tg_chat.id,
                    is_restricted=tg_chat.is_restricted or False,
                    is_support=tg_chat.is_support or False,
                    # is_stories_hidden=tg_chat.is_stories_hidden,
                    # is_stories_unavailable=tg_chat.is_stories_unavailable,
                    # is_business_bot=tg_chat.is_business_bot,
                    verification_status=self.from_verification_status(not_none(tg_chat.verification_status)),
                    username=tg_chat.username,
                    usernames=[u.username for u in tg_chat.usernames] if tg_chat.usernames else None,
                    first_name=not_none(tg_chat.first_name),
                    last_name=tg_chat.last_name,
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    restrictions=self.from_restrictions(tg_chat.restrictions) if tg_chat.restrictions else [],
                    # dc_id=tg_chat.dc_id,
                    reply_color=optional(self.from_reply_color, tg_chat.reply_color),
                    profile_color=optional(self.from_profile_color, tg_chat.profile_color),
                    paid_message_star_count=tg_chat.paid_message_star_count,
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.BOT if tg_chat.username:
                chat = UsualBotDialog(
                    tg_id=tg_chat.id,
                    first_name=not_none(tg_chat.first_name),
                    is_restricted=tg_chat.is_restricted or False,
                    is_support=tg_chat.is_support or False,
                    verification_status=self.from_verification_status(not_none(tg_chat.verification_status)),  # noqa: E501
                    username=tg_chat.username,
                    usernames=[u.username for u in tg_chat.usernames] if tg_chat.usernames else None,
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    restrictions=self.from_restrictions(tg_chat.restrictions) if tg_chat.restrictions else [],
                    is_business_bot=tg_chat.is_business_bot or False,
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.BOT:
                chat = SpecialBotDialog(
                    tg_id=tg_chat.id,
                    first_name=not_none(tg_chat.first_name),
                    is_restricted=tg_chat.is_restricted or False,
                    is_support=tg_chat.is_support or False,
                    verification_status=self.from_verification_status(not_none(tg_chat.verification_status)),  # noqa: E501
                    username=tg_chat.username,
                    usernames=[u.username for u in tg_chat.usernames] if tg_chat.usernames else None,
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    restrictions=self.from_restrictions(tg_chat.restrictions) if tg_chat.restrictions else [],
                    is_business_bot=tg_chat.is_business_bot or False,
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.GROUP | ChatType.SUPERGROUP if tg_chat.is_banned:
                chat = UnavailableChat(
                    tg_id=tg_chat.id,
                    title=not_none(tg_chat.title),
                    is_deactivated=tg_chat.is_deactivated or False,
                    is_call_active=tg_chat.is_call_active or False,
                    is_call_not_empty=tg_chat.is_call_not_empty or False,
                    usernames=[u.username for u in tg_chat.usernames] if tg_chat.usernames else None,
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    permissions=self.from_permissions(tg_chat.permissions) if tg_chat.permissions else None,
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.GROUP:
                chat = Group(
                    tg_id=tg_chat.id,
                    title=not_none(tg_chat.title),
                    is_deactivated=tg_chat.is_deactivated or False,
                    is_call_active=tg_chat.is_call_active or False,
                    is_call_not_empty=tg_chat.is_call_not_empty or False,
                    usernames=[u.username for u in tg_chat.usernames] if tg_chat.usernames else None,
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    permissions=self.from_permissions(tg_chat.permissions) if tg_chat.permissions else None,
                    has_protected_content=tg_chat.has_protected_content or False,
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.SUPERGROUP:
                chat = Supergroup(
                    tg_id=tg_chat.id,
                    title=not_none(tg_chat.title),
                    is_deactivated=tg_chat.is_deactivated or False,
                    verification_status=self.from_verification_status(tg_chat.verification_status) if tg_chat.verification_status else None,  # noqa: E501
                    is_forum=tg_chat.is_forum or False,
                    is_call_active=tg_chat.is_call_active or False,
                    is_call_not_empty=tg_chat.is_call_not_empty or False,
                    is_restricted=tg_chat.is_restricted or False,
                    restrictions=self.from_restrictions(tg_chat.restrictions) if tg_chat.restrictions else [],
                    usernames=[u.username for u in tg_chat.usernames] if tg_chat.usernames else None,
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    permissions=self.from_permissions(not_none(tg_chat.permissions)),
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.CHANNEL:
                chat = Channel(
                    tg_id=tg_chat.id,
                    title=not_none(tg_chat.title),
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    verification_status=self.from_verification_status(tg_chat.verification_status) if tg_chat.verification_status else None,  # noqa: E501
                    is_restricted=tg_chat.is_restricted or False,
                    restrictions=self.from_restrictions(tg_chat.restrictions) if tg_chat.restrictions else [],
                    permissions=self.from_permissions(tg_chat.permissions) if tg_chat.permissions else None,
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.FORUM:
                chat = Supergroup(
                    tg_id=tg_chat.id,
                    title=not_none(tg_chat.title),
                    is_deactivated=tg_chat.is_deactivated or False,
                    verification_status=self.from_verification_status(not_none(tg_chat.verification_status)),
                    is_forum=tg_chat.is_forum or False,
                    is_call_active=tg_chat.is_call_active or False,
                    is_call_not_empty=tg_chat.is_call_not_empty or False,
                    is_restricted=tg_chat.is_restricted or False,
                    restrictions=self.from_restrictions(tg_chat.restrictions) if tg_chat.restrictions else [],
                    usernames=[u.username for u in tg_chat.usernames] if tg_chat.usernames else None,
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    permissions=self.from_permissions(not_none(tg_chat.permissions)),
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.DIRECT:
                chat = ChannelDM(
                    tg_id=tg_chat.id,
                    title=not_none(tg_chat.title),
                    photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    verification_status=self.from_verification_status(tg_chat.verification_status) if tg_chat.verification_status else None,  # noqa: E501
                    is_restricted=tg_chat.is_restricted or False,
                    restrictions=self.from_restrictions(tg_chat.restrictions) if tg_chat.restrictions else [],
                    permissions=self.from_permissions(tg_chat.permissions) if tg_chat.permissions else None,
                    raw_json=PyroObject(tg_chat),
                )
            case ChatType.PRIVATE:
                chat = DeletedUserDialog(tg_id=tg_chat.id, raw_json=PyroObject(tg_chat))
        return chat

    def from_channel(self, tg_channel: pyrogram.Chat) -> Channel:
        # TODO: map properly
        if tg_channel.id is None:
            raise TransformMissingRequiredField("pyrogram.Chat missing value for 'id' field",
                                                tg_channel, 'id')
        if tg_channel.type is None:
            raise TransformMissingRequiredField("pyrogram.Chat missing value for 'type' field",
                                                tg_channel, 'type')
        if tg_channel.type != ChatType.CHANNEL:
            raise TransformValueError(f"Not a channel: {tg_channel}", value=tg_channel)

        return cast(Channel, self.from_chat(tg_chat=tg_channel))
        return Channel(
            tg_id=tg_channel.id,
            title=self.from_optional(tg_channel.title),
            is_verified=self.from_optional(tg_channel.is_verified),
            is_restricted=self.from_optional(tg_channel.is_restricted),
            restrictions=self.from_restrictions(tg_channel.restrictions) if tg_channel.restrictions else [],
            photo=self.from_chat_photo(tg_channel.photo) if tg_channel.photo else None,
        )

    def from_chat_photo(self, tg_chat_photo: pyrogram.ChatPhoto) -> ChatPhoto:
        small = File(
            unique_id=tg_chat_photo.small_photo_unique_id,
            access_key=tg_chat_photo.small_file_id,
        )
        big = File(
            unique_id=tg_chat_photo.big_photo_unique_id,
            access_key=tg_chat_photo.big_file_id,
        )
        return ChatPhoto(
            small=small,
            big=big,
            has_animation=tg_chat_photo.has_animation or False,
            is_personal=tg_chat_photo.is_personal or False,
        )

    def from_verification_status(self, tg_verifivation_status: pyrogram.VerificationStatus) -> VerificationStatus:
        return VerificationStatus(
            is_verified=tg_verifivation_status.is_verified or False,
            is_scam=tg_verifivation_status.is_scam or False,
            is_fake=tg_verifivation_status.is_fake or False,
            bot_verification_icon_custom_emoji_id=tg_verifivation_status.bot_verification_icon_custom_emoji_id,
        )

    def from_reply_color(self, tg_reply_color: pyrogram.ChatColor) -> ReplyColor:
        match tg_reply_color.color:
            case None:
                color = None
            case pyrogram_enums.ReplyColor():
                color = tg_reply_color.color
            case _:
                raise TransformValueError("Color value is not ReplyColor", value=tg_reply_color)

        return ReplyColor(
            color=color,
            bg_emoji=optional(self.from_custom_emoji, tg_reply_color.background_emoji_id),
        )

    def from_profile_color(self, tg_reply_color: pyrogram.ChatColor) -> ProfileColor:
        match tg_reply_color.color:
            case None:
                color = None
            case pyrogram_enums.ProfileColor():
                color = tg_reply_color.color
            case _:
                raise TransformValueError("Color value is not ReplyColor", value=tg_reply_color)

        return ProfileColor(
            color=color,
            bg_emoji=self.from_custom_emoji(tg_reply_color.background_emoji_id),
        )

    def from_permissions(self, tg_chat_permissions: pyrogram.ChatPermissions) -> ChatPermissions:
        return ChatPermissions(
            can_send_messages=tg_chat_permissions.can_send_messages,
            can_send_media_messages=tg_chat_permissions.can_send_media_messages,
            can_send_other_messages=tg_chat_permissions.can_send_other_messages,
            can_send_polls=tg_chat_permissions.can_send_polls,
            can_add_web_page_previews=tg_chat_permissions.can_add_web_page_previews,
            can_change_info=tg_chat_permissions.can_change_info,
            can_invite_users=tg_chat_permissions.can_invite_users,
            can_pin_messages=tg_chat_permissions.can_pin_messages,
        )

    def from_restrictions(self, tg_restrictions: Sequence[pyrogram.Restriction]) -> list[Restriction]:
        return [
            self.from_restriction(tg_restriction)
            for tg_restriction in tg_restrictions
        ]

    def from_restriction(self, tg_restriction: pyrogram.Restriction) -> Restriction:
        return Restriction(
            platform=tg_restriction.platform,
            reason=tg_restriction.reason,
            text=tg_restriction.text,
        )

    def from_custom_emoji(self, tg_emoji_id: int) -> CustomEmoji:
        return CustomEmoji(tg_id=tg_emoji_id)

    def from_media_message(self, tg_message: pyrogram.Message) -> MediaMessage:
        if tg_message.media is None:
            raise TransformValueError(f"Not a media message: {tg_message}", value=tg_message)

        caption = None
        if tg_message.caption is not None:
            caption = self.from_string_with_entities(tg_message.caption, tg_entities=tg_message.caption_entities)

        tg_media: TGMedia | DisappearedMedia
        match tg_message.media:
            case MessageMediaType.AUDIO if tg_message.audio: tg_media = tg_message.audio
            case MessageMediaType.DOCUMENT if tg_message.document: tg_media = tg_message.document
            case MessageMediaType.PHOTO if tg_message.photo: tg_media = tg_message.photo
            case MessageMediaType.PHOTO: tg_media = DisappearedMedia(raw_json=PyroObject(tg_message))
            case MessageMediaType.STICKER if tg_message.sticker: tg_media = tg_message.sticker
            case MessageMediaType.VIDEO if tg_message.video: tg_media = tg_message.video
            case MessageMediaType.VIDEO: tg_media = DisappearedMedia(raw_json=PyroObject(tg_message))
            case MessageMediaType.ANIMATION if tg_message.animation: tg_media = tg_message.animation
            case MessageMediaType.VOICE if tg_message.voice: tg_media = tg_message.voice
            case MessageMediaType.VIDEO_NOTE if tg_message.video_note: tg_media = tg_message.video_note
            case MessageMediaType.CONTACT if tg_message.contact: tg_media = tg_message.contact
            case MessageMediaType.LOCATION if tg_message.location: tg_media = tg_message.location
            case MessageMediaType.VENUE if tg_message.venue: tg_media = tg_message.venue
            case MessageMediaType.POLL if tg_message.poll: tg_media = tg_message.poll
            case MessageMediaType.WEB_PAGE if tg_message.web_page: tg_media = tg_message.web_page
            case MessageMediaType.DICE if tg_message.dice: tg_media = tg_message.dice
            case MessageMediaType.GAME if tg_message.game: tg_media = tg_message.game
            case MessageMediaType.GIVEAWAY if tg_message.giveaway: tg_media = tg_message.giveaway
            case MessageMediaType.GIVEAWAY_WINNERS if tg_message.giveaway_winners: tg_media = tg_message.giveaway_winners  # noqa: E501
            case MessageMediaType.STORY if tg_message.story: tg_media = tg_message.story
            case MessageMediaType.INVOICE if tg_message.invoice: tg_media = tg_message.invoice
            case MessageMediaType.PAID_MEDIA if tg_message.paid_media: tg_media = tg_message.paid_media
            case MessageMediaType.CHECKLIST if tg_message.checklist: tg_media = tg_message.checklist
            case media_type:
                raise TransformMissingRequiredField(f"Message missing value in field for {media_type}: {tg_message}",
                                                    tg_message)

        media: Media
        if isinstance(tg_media, DisappearedMedia):
            media = tg_media
        else:
            media = self.from_media(tg_media)

        return MediaMessage(
            caption=caption,
            media=media,
            media_group_id=tg_message.media_group_id,
            has_media_spoiler=tg_message.has_media_spoiler
        )

    def from_service_message(self, tg_message: pyrogram.Message) -> ServiceMessage:
        message: ServiceMessage
        match tg_message.service:
            case None:
                raise TransformValueError(f"Can not use {tg_message} as service message", tg_message)
            case MessageServiceType.NEW_CHAT_MEMBERS if tg_message.new_chat_members is not None:
                users = [self.from_user(tg_user) for tg_user in tg_message.new_chat_members]
                message = NewChatMembers(new_chat_members=users)
            case MessageServiceType.NEW_CHAT_MEMBERS:
                raise TransformMissingRequiredField(f"Message missing 'new_chat_members': {tg_message}",
                                                    tg_message, 'new_chat_members')
            case MessageServiceType.LEFT_CHAT_MEMBER if tg_message.left_chat_member:
                user = self.from_user(tg_message.left_chat_member)
                message = LeftChatMember(left_user=user)
            case MessageServiceType.LEFT_CHAT_MEMBER:
                raise TransformMissingRequiredField(f"Message missing 'left_chat_member': {tg_message}",
                                                    tg_message, 'left_chat_member')
            case MessageServiceType.CHAT_OWNER_LEFT if tg_message.chat_owner_left:
                new_owner = optional(self.from_user, tg_message.chat_owner_left.new_owner)
                message = ChatOwnerLeft(new_owner=new_owner)
            case MessageServiceType.CHAT_OWNER_LEFT if tg_message.chat_owner_left:
                raise TransformMissingRequiredField(f"Message missing 'chat_owner_left': {tg_message}",  # noqa: E501
                                                    tg_message, 'chat_owner_left')
            case MessageServiceType.CHAT_OWNER_CHANGED if tg_message.chat_owner_changed:
                new_owner = self.from_user(tg_message.chat_owner_changed.new_owner)
                message = ChatOwnerChanged(new_owner=new_owner)
            case MessageServiceType.CHAT_OWNER_CHANGED:
                raise TransformMissingRequiredField(f"Message missing 'chat_owner_changed': {tg_message}",  # noqa: E501
                                                    tg_message, 'chat_owner_changed')
            case MessageServiceType.NEW_CHAT_TITLE if tg_message.new_chat_title:
                message = NewChatTitle(new_chat_title=tg_message.new_chat_title)
            case MessageServiceType.NEW_CHAT_TITLE:
                raise TransformMissingRequiredField(f"Message missing 'new_chat_title': {tg_message}",
                                                    tg_message, 'new_chat_title')
            case MessageServiceType.NEW_CHAT_PHOTO:
                if not tg_message.new_chat_photo:
                    log.warning("New chat photo missing photo (chat %s, msg %s)",
                                tg_message.chat.id, tg_message.id)  # type: ignore[union-attr]
                message = NewChatPhoto(
                    new_chat_photo=optional(self.from_media, tg_message.new_chat_photo),
                )
            # case MessageServiceType.NEW_CHAT_PHOTO:
            #     raise TransformMissingRequiredField(f"Message missing 'new_chat_photo': {tg_message}",
            #                                         tg_message, 'new_chat_photo')
            case MessageServiceType.DELETE_CHAT_PHOTO:
                message = ChatPhotoDeleted()
            case MessageServiceType.FORUM_TOPIC_CREATED if tg_message.forum_topic_created:
                message = ForumTopicCreated(
                    id=tg_message.forum_topic_created.id,
                    title=tg_message.forum_topic_created.title,
                    icon_color=tg_message.forum_topic_created.icon_color,
                    custom_emoji=optional(self.from_custom_emoji, tg_message.forum_topic_created.custom_emoji_id),
                )
            case MessageServiceType.FORUM_TOPIC_CREATED:
                raise TransformMissingRequiredField(f"Message missing 'forum_topic_created': {tg_message}",
                                                    tg_message, 'forum_topic_created')
            case MessageServiceType.FORUM_TOPIC_CLOSED if tg_message.forum_topic_closed:
                message = ForumTopicClosed()
            case MessageServiceType.FORUM_TOPIC_CLOSED:
                raise TransformMissingRequiredField(f"Message missing 'forum_topic_closed': {tg_message}",
                                                    tg_message, 'forum_topic_closed')
            case MessageServiceType.FORUM_TOPIC_REOPENED if tg_message.forum_topic_reopened:
                message = ForumTopicReopened()
            case MessageServiceType.FORUM_TOPIC_REOPENED:
                raise TransformMissingRequiredField(f"Message missing 'forum_topic_reopened': {tg_message}",
                                                    tg_message, 'forum_topic_reopened')
            case MessageServiceType.FORUM_TOPIC_EDITED if tg_message.forum_topic_edited:
                message = ForumTopicEdited(
                    title=tg_message.forum_topic_edited.title,
                    icon_color=tg_message.forum_topic_edited.icon_color,
                    custom_emoji=optional(self.from_custom_emoji, tg_message.forum_topic_edited.custom_emoji_id),
                    is_closed=tg_message.forum_topic_edited.is_closed,
                    is_hidden=tg_message.forum_topic_edited.is_hidden,
                )
            case MessageServiceType.FORUM_TOPIC_EDITED:
                raise TransformMissingRequiredField(f"Message missing 'forum_topic_edited': {tg_message}",
                                                    tg_message, 'forum_topic_edited')
            case MessageServiceType.GENERAL_FORUM_TOPIC_HIDDEN if tg_message.general_forum_topic_hidden:
                message = GeneralForumTopicHidden()
            case MessageServiceType.GENERAL_FORUM_TOPIC_HIDDEN:
                raise TransformMissingRequiredField(f"Message missing 'general_forum_topic_hidden': {tg_message}",
                                                    tg_message, 'general_forum_topic_hidden')
            case MessageServiceType.GENERAL_FORUM_TOPIC_UNHIDDEN if tg_message.general_forum_topic_unhidden:
                message = GeneralForumTopicUnhidden()
            case MessageServiceType.GENERAL_FORUM_TOPIC_UNHIDDEN:
                raise TransformMissingRequiredField(f"Message missing 'general_forum_topic_unhidden': {tg_message}",
                                                    tg_message, 'general_forum_topic_unhidden')
            case MessageServiceType.GROUP_CHAT_CREATED:
                message = GroupCreated()
            case MessageServiceType.CHANNEL_CHAT_CREATED:
                message = ChannelCreated()
            case MessageServiceType.SUPERGROUP_CHAT_CREATED if tg_message.supergroup_chat_created:
                message = SupergroupCreated()
            case MessageServiceType.SUPERGROUP_CHAT_CREATED:
                raise TransformMissingRequiredField(f"Message missing 'supergroup_chat_created': {tg_message}",
                                                    tg_message, 'supergroup_chat_created')
            case MessageServiceType.MIGRATE_TO_CHAT_ID if tg_message.migrate_to_chat_id:
                to_chat_id = tg_message.migrate_to_chat_id
                chat = Chat(tg_id=to_chat_id, type=ChatType.SUPERGROUP)
                message = MigrateToSupergroup(migrate_to_chat=chat)
            case MessageServiceType.MIGRATE_TO_CHAT_ID:
                raise TransformMissingRequiredField(f"Message missing 'migrate_to_chat_id': {tg_message}",
                                                    tg_message, 'migrate_to_chat_id')
            case MessageServiceType.MIGRATE_FROM_CHAT_ID if tg_message.migrate_from_chat_id:
                from_chat_id = tg_message.migrate_from_chat_id
                chat = Chat(tg_id=from_chat_id, type=ChatType.GROUP)
                message = MigrateFromGroup(migrate_from_chat=chat)
            case MessageServiceType.MIGRATE_FROM_CHAT_ID:
                raise TransformMissingRequiredField(f"Message missing 'migrate_from_chat_id': {tg_message}",
                                                    tg_message, 'migrate_from_chat_id')
            case MessageServiceType.PINNED_MESSAGE if tg_message.pinned_message:
                message = MessagePinned(pinned_message_id=tg_message.pinned_message.id)
            case MessageServiceType.PINNED_MESSAGE if tg_message.reply_to_message_id:
                message = MessagePinned(pinned_message_id=tg_message.reply_to_message_id)
            # NOTE: special case, IDK why
            case MessageServiceType.PINNED_MESSAGE if (
                isinstance(tg_message.raw, pyrogram_raw.message_service.MessageService)
                and
                tg_message.raw.reply_to
            ):
                pinned_msg_id = tg_message.raw.reply_to.reply_to_msg_id  # pyright: ignore[reportAttributeAccessIssue]
                if pinned_msg_id is None:
                    raise TransformMissingRequiredField(f"Message missing 'raw.reply_to.reply_to_msg_id': {tg_message}",
                                                        tg_message, 'raw.reply_to.reply_to_msg_id')
                message = MessagePinned(pinned_message_id=pinned_msg_id)
            # tg_message.reply_to_message_id
            case MessageServiceType.PINNED_MESSAGE:
                # TODO: find workaround for loaded messages
                message = BorkedServiceMessage(raw_json=PyroObject(tg_message))
                # raise TransformMissingRequiredField(f"Message missing 'pinned_message': {tg_message}",
                #                                     tg_message, 'pinned_message')
            case MessageServiceType.GAME_HIGH_SCORE if tg_message.game_high_score is not None:
                # TODO: get Game from reply_to
                high_score = cast(pyrogram.GameHighScore, tg_message.game_high_score)
                user = self.from_user(high_score.user)
                message = GameHighScore(
                    user=user,
                    score=high_score.score,
                )
            case MessageServiceType.GAME_HIGH_SCORE:
                raise TransformMissingRequiredField(f"Message missing 'game_high_score': {tg_message}",
                                                    tg_message, 'game_high_score')
            case MessageServiceType.GIVEAWAY_CREATED if tg_message.giveaway_created:
                message = GiveawayCreated()
            case MessageServiceType.GIVEAWAY_CREATED:
                raise TransformMissingRequiredField(f"Message missing 'giveaway_created': {tg_message}",
                                                    tg_message, 'giveaway_created')
            case MessageServiceType.GIVEAWAY_COMPLETED if tg_message.giveaway_completed:
                message = GiveawayCompleted(
                    winner_count=tg_message.giveaway_completed.winner_count,
                    unclaimed_prize_count=tg_message.giveaway_completed.unclaimed_prize_count,
                    giveaway_message_id=tg_message.giveaway_completed.giveaway_message_id,
                    is_star_giveaway=tg_message.giveaway_completed.is_star_giveaway or False,
                )
            case MessageServiceType.GIVEAWAY_COMPLETED:
                raise TransformMissingRequiredField(f"Message missing 'giveaway_completed': {tg_message}",
                                                    tg_message, 'giveaway_completed')
            case MessageServiceType.PREMIUM_GIFT_CODE if tg_message.premium_gift_code:
                message = PremiumGiftCode(
                    code=tg_message.premium_gift_code.code,
                    caption=optional(self.from_string, tg_message.premium_gift_code.text),
                    month_count=tg_message.premium_gift_code.month_count,
                    day_count=tg_message.premium_gift_code.day_count,
                    price=self.get_price(tg_message.premium_gift_code),
                    is_unclaimed=tg_message.premium_gift_code.is_unclaimed or False,
                    is_from_giveaway=tg_message.premium_gift_code.is_from_giveaway or False,
                )
            case MessageServiceType.PREMIUM_GIFT_CODE:
                raise TransformMissingRequiredField(f"Message missing 'premium_gift_code': {tg_message}",
                                                    tg_message, 'premium_gift_code')
            case MessageServiceType.GIFTED_PREMIUM if tg_message.gifted_premium:
                message = GiftedPremium(
                    receiver=self.from_user(not_none(tg_message.gifted_premium.receiver)),
                    gifter=optional(self.from_user, tg_message.gifted_premium.gifter),
                    price=self.get_price(tg_message.gifted_premium),
                    month_count=not_none(tg_message.gifted_premium.month_count),
                    day_count=not_none(tg_message.gifted_premium.day_count),
                    sticker=optional(self.from_media, tg_message.gifted_premium.sticker),
                    caption=self.from_string_with_entities(
                        string=tg_message.gifted_premium.caption,
                        tg_entities=tg_message.gifted_premium.caption_entities,
                    ) if tg_message.gifted_premium.caption is not None else None,
                )
            case MessageServiceType.GIFTED_PREMIUM:
                raise TransformMissingRequiredField(f"Message missing 'gifted_premium': {tg_message}",
                                                    tg_message, 'gifted_premium')
            case MessageServiceType.GIFTED_STARS if tg_message.gifted_stars:
                # TODO: fill info
                message = GiftedStars()
            case MessageServiceType.GIFTED_STARS:
                raise TransformMissingRequiredField(f"Message missing 'gifted_stars': {tg_message}",
                                                    tg_message, 'gifted_stars')
            case MessageServiceType.GIFTED_TON if tg_message.gifted_ton:
                # TODO: fill info
                message = GiftedTON()
            case MessageServiceType.GIFTED_TON:
                raise TransformMissingRequiredField(f"Message missing 'gifted_ton': {tg_message}",
                                                    tg_message, 'gifted_ton')
            case MessageServiceType.VIDEO_CHAT_STARTED:
                message = VideoChatStarted()
            case MessageServiceType.VIDEO_CHAT_ENDED if tg_message.video_chat_ended:
                message = VideoChatEnded(duratioin=tg_message.video_chat_ended.duration)
            case MessageServiceType.VIDEO_CHAT_ENDED:
                raise TransformMissingRequiredField(f"Message missing 'video_chat_ended': {tg_message}",
                                                    tg_message, 'video_chat_ended')
            case MessageServiceType.VIDEO_CHAT_SCHEDULED if tg_message.video_chat_scheduled:
                message = VideoChatScheduled(start_date=tg_message.video_chat_scheduled.start_date)
            case MessageServiceType.VIDEO_CHAT_SCHEDULED:
                raise TransformMissingRequiredField(f"Message missing 'video_chat_scheduled': {tg_message}",
                                                    tg_message, 'video_chat_scheduled')
            case MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED if tg_message.video_chat_members_invited:
                users = [self.from_user(tg_user) for tg_user in tg_message.video_chat_members_invited.users]
                message = VideoChatMembersInvited(video_chat_members_invited=users)
            case MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED:
                raise TransformMissingRequiredField(f"Message missing 'video_chat_members_invited': {tg_message}",
                                                    tg_message, 'video_chat_members_invited')
            case MessageServiceType.PHONE_CALL_STARTED if tg_message.phone_call_started:
                message = PhoneCallStarted(
                    tg_id=tg_message.phone_call_started.id,
                    is_video=tg_message.phone_call_started.is_video,
                )
            case MessageServiceType.PHONE_CALL_STARTED:
                raise TransformMissingRequiredField(f"Message missing 'phone_call_started': {tg_message}",
                                                    tg_message, 'phone_call_started')
            case MessageServiceType.PHONE_CALL_ENDED if tg_message.phone_call_ended:
                message = PhoneCallEnded(
                    call_id=tg_message.phone_call_ended.id,
                    is_video=tg_message.phone_call_ended.is_video,
                    reason=tg_message.phone_call_ended.reason,
                    duration=tg_message.phone_call_ended.duration,
                )
            case MessageServiceType.PHONE_CALL_ENDED:
                raise TransformMissingRequiredField(f"Message missing 'phone_call_ended': {tg_message}",
                                                    tg_message, 'phone_call_ended')
            case MessageServiceType.WEB_APP_DATA if tg_message.web_app_data:
                message = WebAppData(
                    data=tg_message.web_app_data.data,
                    button_text=tg_message.web_app_data.button_text,
                )
            case MessageServiceType.WEB_APP_DATA:
                raise TransformMissingRequiredField(f"Message missing 'web_app_data': {tg_message}",
                                                    tg_message, 'web_app_data')
            case MessageServiceType.USERS_SHARED if tg_message.users_shared:
                # TODO: fill info
                message = UsersShared()
            case MessageServiceType.USERS_SHARED:
                raise TransformMissingRequiredField(f"Message missing 'users_shared': {tg_message}",
                                                    tg_message, 'users_shared')
            case MessageServiceType.CHAT_SHARED if tg_message.chat_shared:
                # TODO: fill info
                message = ChatShared()
            case MessageServiceType.CHAT_SHARED:
                raise TransformMissingRequiredField(f"Message missing 'chat_shared': {tg_message}",
                                                    tg_message, 'chat_shared')
            case MessageServiceType.SUCCESSFUL_PAYMENT if tg_message.successful_payment:
                if tg_message.successful_payment.is_recurring:
                    message = SuccessfulSubscriptionPayment(
                        currency=tg_message.successful_payment.currency,
                        total_amount=int(tg_message.successful_payment.total_amount),
                        invoice_slug=tg_message.successful_payment.invoice_slug,
                        first_time=tg_message.successful_payment.is_first_recurring or False,
                        subscription_expiration_date=tg_message.successful_payment.subscription_expiration_date,  # noqa: E501
                    )
                else:
                    message = SuccessfulPayment(
                        currency=tg_message.successful_payment.currency,
                        total_amount=int(tg_message.successful_payment.total_amount),
                        invoice_slug=tg_message.successful_payment.invoice_slug,
                    )
            case MessageServiceType.SUCCESSFUL_PAYMENT:
                raise TransformMissingRequiredField(f"Message missing 'successful_payment': {tg_message}",
                                                    tg_message, 'successful_payment')
            case MessageServiceType.REFUNDED_PAYMENT if tg_message.refunded_payment:
                # TODO: fill info
                message = RefundedPayment()
            case MessageServiceType.REFUNDED_PAYMENT:
                raise TransformMissingRequiredField(f"Message missing 'refunded_payment': {tg_message}",
                                                    tg_message, 'refunded_payment')
            case MessageServiceType.SUGGESTED_POST_APPROVAL_FAILED if tg_message.suggested_post_approval_failed:
                # TODO: fill info
                message = SuggestedPostApprovalFailed()
            case MessageServiceType.SUGGESTED_POST_APPROVAL_FAILED:
                raise TransformMissingRequiredField(f"Message missing 'suggested_post_approval_failed': {tg_message}",
                                                    tg_message, 'suggested_post_approval_failed')
            case MessageServiceType.SUGGESTED_POST_APPROVED if tg_message.suggested_post_approved:
                # TODO: fill info
                message = SuggestedPostApproved()
            case MessageServiceType.SUGGESTED_POST_APPROVED:
                raise TransformMissingRequiredField(f"Message missing 'suggested_post_approved': {tg_message}",
                                                    tg_message, 'suggested_post_approved')
            case MessageServiceType.SUGGESTED_POST_DECLINED if tg_message.suggested_post_declined:
                # TODO: fill info
                message = SuggestedPostDeclined()
            case MessageServiceType.SUGGESTED_POST_DECLINED:
                raise TransformMissingRequiredField(f"Message missing 'suggested_post_declined': {tg_message}",
                                                    tg_message, 'suggested_post_declined')
            case MessageServiceType.SUGGESTED_POST_PAID if tg_message.suggested_post_paid:
                # TODO: fill info
                message = SuggestedPostPaid()
            case MessageServiceType.SUGGESTED_POST_PAID:
                raise TransformMissingRequiredField(f"Message missing 'suggested_post_paid': {tg_message}",
                                                    tg_message, 'suggested_post_paid')
            case MessageServiceType.SUGGESTED_POST_REFUNDED if tg_message.suggested_post_refunded:
                # TODO: fill info
                message = SuggestedPostRefunded()
            case MessageServiceType.SUGGESTED_POST_REFUNDED:
                raise TransformMissingRequiredField(f"Message missing 'suggested_post_refunded': {tg_message}",
                                                    tg_message, 'suggested_post_refunded')
            case MessageServiceType.SET_MESSAGE_AUTO_DELETE_TIME if tg_message.set_message_auto_delete_time is not None:  # noqa: E501
                if tg_message.set_message_auto_delete_time:
                    message = SetMessageAutodeleteTime(message_ttl=tg_message.set_message_auto_delete_time)
                else:
                    message = MessageAutodeleteDisabled()
            case MessageServiceType.SET_MESSAGE_AUTO_DELETE_TIME:
                raise TransformMissingRequiredField(f"Message missing 'set_message_auto_delete_time': {tg_message}",
                                                    tg_message, 'set_message_auto_delete_time')
            case MessageServiceType.CHAT_BOOST if tg_message.chat_boost is not None:
                message = ChatBoost(
                    amount=tg_message.chat_boost,
                )
            case MessageServiceType.CHAT_BOOST:
                raise TransformMissingRequiredField(f"Message missing 'chat_boost': {tg_message}",
                                                    tg_message, 'chat_boost')
            case MessageServiceType.GIFT if tg_message.gift:
                # TODO: fill info
                message = Gifted()
            case MessageServiceType.GIFT:
                raise TransformMissingRequiredField(f"Message missing 'gift': {tg_message}",
                                                    tg_message, 'gift')
            case MessageServiceType.CONNECTED_WEBSITE if tg_message.connected_website is not None:
                message = ConnectedWebsite(domain=tg_message.connected_website)
            case MessageServiceType.CONNECTED_WEBSITE:
                raise TransformMissingRequiredField(f"Message missing 'connected_website': {tg_message}",
                                                    tg_message, 'connected_website')
            case MessageServiceType.WRITE_ACCESS_ALLOWED if tg_message.write_access_allowed:
                message = WriteAccessAllowed(
                    from_request=tg_message.write_access_allowed.from_request,
                    from_attachment_menu=tg_message.write_access_allowed.from_attachment_menu,
                    web_app_name=tg_message.write_access_allowed.web_app_name,
                )
            case MessageServiceType.WRITE_ACCESS_ALLOWED:
                raise TransformMissingRequiredField(f"Message missing 'write_access_allowed': {tg_message}",
                                                    tg_message, 'write_access_allowed')
            case MessageServiceType.SCREENSHOT_TAKEN if tg_message.screenshot_taken:
                message = ScreenshotTaken()
            case MessageServiceType.SCREENSHOT_TAKEN:
                raise TransformMissingRequiredField(f"Message missing 'screenshot_taken': {tg_message}",
                                                    tg_message, 'screenshot_taken')
            case MessageServiceType.CONTACT_REGISTERED if tg_message.contact_registered:
                message = ContactRegistered()
            case MessageServiceType.CONTACT_REGISTERED:
                raise TransformMissingRequiredField(f"Message missing 'contact_registered': {tg_message}",
                                                    tg_message, 'contact_registered')
            case MessageServiceType.PROXIMITY_ALERT_TRIGGERED if tg_message.proximity_alert_triggered:
                message = ProximityAlertTriggered(
                    traveler=self.from_chat(not_none(tg_message.proximity_alert_triggered.traveler)),  # type: ignore
                    watcher=self.from_chat(not_none(tg_message.proximity_alert_triggered.watcher)),  # type: ignore
                    distance=int(tg_message.proximity_alert_triggered.distance),
                )
            case MessageServiceType.PROXIMITY_ALERT_TRIGGERED:
                raise TransformMissingRequiredField(f"Message missing 'proximity_alert_triggered': {tg_message}",
                                                    tg_message, 'proximity_alert_triggered')
            case MessageServiceType.HISTORY_CLEARED if tg_message.history_cleared:
                message = HistoryCleared()
            case MessageServiceType.HISTORY_CLEARED:
                raise TransformMissingRequiredField(f"Message missing 'history_cleared': {tg_message}",
                                                    tg_message, 'history_cleared')
            case MessageServiceType.SUGGEST_PROFILE_PHOTO if tg_message.suggest_profile_photo:
                message = SuggestedProfilePhoto(photo=self.from_media(tg_message.suggest_profile_photo))
            case MessageServiceType.SUGGEST_PROFILE_PHOTO:
                raise TransformMissingRequiredField(f"Message missing 'suggest_profile_photo': {tg_message}",
                                                    tg_message, 'suggest_profile_photo')
            case MessageServiceType.SUGGEST_BIRTHDAY if tg_message.suggest_birthday:
                birthday = Birthday(
                    day=tg_message.suggest_birthday.day,
                    month=tg_message.suggest_birthday.month,
                    year=tg_message.suggest_birthday.year,
                )
                message = SuggestedBirthday(birthday=birthday)
            case MessageServiceType.SUGGEST_BIRTHDAY:
                raise TransformMissingRequiredField(f"Message missing 'suggest_birthday': {tg_message}",
                                                    tg_message, 'suggest_birthday')
            case MessageServiceType.CHAT_SET_BACKGROUND if tg_message.chat_set_background:
                # TODO: fill info
                message = SetChatBackground()
            case MessageServiceType.CHAT_SET_BACKGROUND:
                raise TransformMissingRequiredField(f"Message missing 'chat_set_background': {tg_message}",
                                                    tg_message, 'chat_set_background')
            case MessageServiceType.CHAT_SET_THEME if tg_message.chat_set_theme:
                if tg_message.chat_set_theme.name:
                    message = SetChatEmojiTheme(name=tg_message.chat_set_theme.name)
                elif tg_message.chat_set_theme.gift:
                    # TODO: fill Gift info
                    message = SetChatGiftTheme()
                else:
                    raise TransformValueError(f"Message.chat_set_theme.name and Message.chat_set_theme.gift both is None: {tg_message}",  # noqa: E501
                                              tg_message.chat_set_theme)
            case MessageServiceType.CHAT_SET_THEME:
                raise TransformMissingRequiredField(f"Message missing 'chat_set_theme': {tg_message}",
                                                    tg_message, 'chat_set_theme')
            case MessageServiceType.GIVEAWAY_PRIZE_STARS if tg_message.giveaway_prize_stars:
                # TODO: fill info
                message = GiveawayPrizeStars()
            case MessageServiceType.GIVEAWAY_PRIZE_STARS:
                raise TransformMissingRequiredField(f"Message missing 'giveaway_prize_stars': {tg_message}",
                                                    tg_message, 'giveaway_prize_stars')
            case MessageServiceType.PAID_MESSAGES_REFUNDED if tg_message.paid_messages_refunded:
                message = PaidMessagesRefunded(
                    messages_count=tg_message.paid_messages_refunded.message_count,
                    stars_amount=tg_message.paid_messages_refunded.star_count,
                )
            case MessageServiceType.PAID_MESSAGES_REFUNDED:
                raise TransformMissingRequiredField(f"Message missing 'paid_messages_refunded': {tg_message}",
                                                    tg_message, 'paid_messages_refunded')
            case MessageServiceType.PAID_MESSAGES_PRICE_CHANGED if tg_message.paid_messages_price_changed:
                message = PaidMessagesPriceChanged(
                    new_price=tg_message.paid_messages_price_changed.paid_message_star_count,
                )
            case MessageServiceType.PAID_MESSAGES_PRICE_CHANGED:
                raise TransformMissingRequiredField(f"Message missing 'paid_messages_price_changed': {tg_message}",
                                                    tg_message, 'paid_messages_price_changed')
            case MessageServiceType.DIRECT_MESSAGE_PRICE_CHANGED if tg_message.direct_message_price_changed:
                message = DirectMessagesPriceChanged(
                    is_enabed=tg_message.direct_message_price_changed.is_enabled,
                    new_price=tg_message.direct_message_price_changed.paid_message_star_count,
                )
            case MessageServiceType.DIRECT_MESSAGE_PRICE_CHANGED:
                raise TransformMissingRequiredField(f"Message missing 'direct_message_price_changed': {tg_message}",
                                                    tg_message, 'direct_message_price_changed')
            case MessageServiceType.CHECKLIST_TASKS_DONE if tg_message.checklist_tasks_done:
                # TODO: fill info
                message = ChecklistTasksDone()
            case MessageServiceType.CHECKLIST_TASKS_DONE:
                raise TransformMissingRequiredField(f"Message missing 'checklist_tasks_done': {tg_message}",
                                                    tg_message, 'checklist_tasks_done')
            case MessageServiceType.CHECKLIST_TASKS_ADDED if tg_message.checklist_tasks_added:
                # TODO: fill info
                message = ChecklistTasksAdded()
            case MessageServiceType.CHECKLIST_TASKS_ADDED:
                raise TransformMissingRequiredField(f"Message missing 'checklist_tasks_added': {tg_message}",
                                                    tg_message, 'checklist_tasks_added')
            case MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER if tg_message.upgraded_gift_purchase_offer:
                # TODO: fill info
                message = UpgradedGiftPurchaseOffer()
            case MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER:
                raise TransformMissingRequiredField(f"Message missing 'upgraded_gift_purchase_offer': {tg_message}",
                                                    tg_message, 'upgraded_gift_purchase_offer')
            case MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER_REJECTED if tg_message.upgraded_gift_purchase_offer_rejected:  # noqa: E501
                # TODO: fill info
                message = UpgradedGiftPurchaseOfferRejected()
            case MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER_REJECTED:
                raise TransformMissingRequiredField(f"Message missing 'upgraded_gift_purchase_offer_rejected': {tg_message}",  # noqa: E501
                                                    tg_message, 'upgraded_gift_purchase_offer_rejected')
            case MessageServiceType.UNSUPPORTED:
                log.warning("Usupported service message (chat %s, msg %s)",
                            tg_message.chat.id, tg_message.id)  # type: ignore[union-attr]
                message = UnsupportedServiceMessage(raw_json=None)
            case MessageServiceType.CUSTOM_ACTION:
                log.warning("Usupported service message (custom action at chat %s, msg %s)",
                            tg_message.chat.id, tg_message.id)  # type: ignore[union-attr]
                message = CustomAction(message=not_none(tg_message.text))
            case unknown:
                log.warning(f"Usupported service message of type {unknown.name}")
                message = UnsupportedServiceMessage(raw_json=PyroObject(obj=tg_message))

        return message

    @overload
    def from_media(self, tg_media: pyrogram.Audio) -> Audio: pass
    @overload
    def from_media(self, tg_media: pyrogram.Document) -> Document: pass
    @overload
    def from_media(self, tg_media: pyrogram.Photo) -> Photo: pass
    @overload
    def from_media(self, tg_media: pyrogram.Sticker) -> Sticker: pass
    @overload
    def from_media(self, tg_media: pyrogram.Video) -> Video: pass
    @overload
    def from_media(self, tg_media: pyrogram.Animation) -> Animation: pass
    @overload
    def from_media(self, tg_media: pyrogram.Voice) -> Voice: pass
    @overload
    def from_media(self, tg_media: pyrogram.VideoNote) -> VideoNote: pass
    @overload
    def from_media(self, tg_media: pyrogram.Contact) -> Contact: pass
    @overload
    def from_media(self, tg_media: pyrogram.Location) -> Location | LiveLocation | BusinessLocation: pass
    @overload
    def from_media(self, tg_media: pyrogram.Venue) -> Venue: pass
    @overload
    def from_media(self, tg_media: pyrogram.Poll) -> Poll: pass
    @overload
    def from_media(self, tg_media: pyrogram.WebPage) -> WebPage: pass
    @overload
    def from_media(self, tg_media: pyrogram.Dice) -> Dice: pass
    @overload
    def from_media(self, tg_media: pyrogram.Game) -> Game: pass
    @overload
    def from_media(self, tg_media: pyrogram.Giveaway) -> StarsGiveaway | SubscriptionsGiveaway: pass
    @overload
    def from_media(self, tg_media: pyrogram.GiveawayWinners) -> StarsGiveawayWinners | SubscriptionsGiveawayWinners: pass  # noqa: E501
    @overload
    def from_media(self, tg_media: pyrogram.Story) -> Story: pass
    @overload
    def from_media(self, tg_media: pyrogram.Invoice) -> Invoice: pass
    @overload
    def from_media(self, tg_media: pyrogram.PaidMediaInfo) -> PaidMedia: pass
    @overload
    def from_media(self, tg_media: pyrogram.PaidMediaPreview) -> PaidMediaPreview: pass
    @overload
    def from_media(self, tg_media: pyrogram.Checklist) -> Checklist: pass

    def from_media(self, tg_media: TGMedia | pyrogram.PaidMediaPreview) -> Media | PaidMediaPreview:
        media: Media | PaidMediaPreview
        match tg_media:
            case pyrogram.Audio() as tg_audio:
                file = SizedFile(
                    unique_id=tg_audio.file_unique_id,
                    access_key=tg_audio.file_id,
                    file_size=tg_audio.file_size,
                )
                media = Audio(
                    file=file,
                    duration=tg_audio.duration,
                    performer=tg_audio.performer,
                    title=tg_audio.title,
                    file_name=tg_audio.file_name,
                    mime_type=tg_audio.mime_type,
                    date=tg_audio.date,
                    thumbs=[
                        Thumbnail(
                            file=SizedFile(
                                unique_id=thumb.file_unique_id,
                                access_key=thumb.file_id,
                                file_size=thumb.file_size,
                            ),
                            width=thumb.width,
                            height=thumb.height,
                        )
                        for thumb in tg_audio.thumbs
                    ] if tg_audio.thumbs else [],
                )
            case pyrogram.Document() as tg_document:
                file = SizedFile(
                    unique_id=tg_document.file_unique_id,
                    access_key=tg_document.file_id,
                    file_size=tg_document.file_size,
                )
                media = Document(
                    file=file,
                    file_name=tg_document.file_name,
                    mime_type=tg_document.mime_type,
                    date=tg_document.date,
                    thumbs=[
                        Thumbnail(
                            file=SizedFile(
                                unique_id=thumb.file_unique_id,
                                access_key=thumb.file_id,
                                file_size=thumb.file_size,
                            ),
                            width=thumb.width,
                            height=thumb.height,
                        )
                        for thumb in tg_document.thumbs
                    ] if tg_document.thumbs else [],
                )
            case pyrogram.Photo() as tg_photo:
                file = SizedFile(
                    unique_id=tg_photo.file_unique_id,
                    access_key=tg_photo.file_id,
                    file_size=tg_photo.file_size,
                )
                media = Photo(
                    file=file,
                    width=tg_photo.width,
                    height=tg_photo.height,
                    date=tg_photo.date,
                    ttl_seconds=tg_photo.ttl_seconds,
                    thumbs=[
                        Thumbnail(
                            file=SizedFile(
                                unique_id=thumb.file_unique_id,
                                access_key=thumb.file_id,
                                file_size=thumb.file_size,
                            ),
                            width=thumb.width,
                            height=thumb.height,
                        )
                        for thumb in tg_photo.thumbs
                    ] if tg_photo.thumbs else [],
                )
            case pyrogram.Sticker() as tg_sticker:
                file = SizedFile(
                    unique_id=tg_sticker.file_unique_id,
                    access_key=tg_sticker.file_id,
                    file_size=tg_sticker.file_size,
                )
                media = Sticker(
                    file=file,
                    width=tg_sticker.width,
                    height=tg_sticker.height,
                    is_animated=tg_sticker.is_animated,
                    is_video=tg_sticker.is_video,
                    file_name=tg_sticker.file_name,
                    mime_type=tg_sticker.mime_type,
                    date=tg_sticker.date,
                    emoji=tg_sticker.emoji,
                    set_name=tg_sticker.set_name,
                    thumbs=[
                        Thumbnail(
                            file=SizedFile(
                                unique_id=thumb.file_unique_id,
                                access_key=thumb.file_id,
                                file_size=thumb.file_size,
                            ),
                            width=thumb.width,
                            height=thumb.height,
                        )
                        for thumb in tg_sticker.thumbs
                    ] if tg_sticker.thumbs else [],
                )
            case pyrogram.Animation() as tg_animation:
                file = SizedFile(
                    unique_id=tg_animation.file_unique_id,
                    access_key=tg_animation.file_id,
                    file_size=tg_animation.file_size,
                )
                media = Animation(
                    file=file,
                    width=tg_animation.width,
                    height=tg_animation.height,
                    duration=tg_animation.duration,
                    file_name=tg_animation.file_name,
                    mime_type=tg_animation.mime_type,
                    date=tg_animation.date,
                    thumbs=[
                        Thumbnail(
                            file=SizedFile(
                                unique_id=thumb.file_unique_id,
                                access_key=thumb.file_id,
                                file_size=thumb.file_size,
                            ),
                            width=thumb.width,
                            height=thumb.height,
                        )
                        for thumb in tg_animation.thumbs
                    ] if tg_animation.thumbs else [],
                )
            case pyrogram.Video() as tg_video:
                file = SizedFile(
                    unique_id=tg_video.file_unique_id,
                    access_key=tg_video.file_id,
                    file_size=cast(int, tg_video.file_size),
                )
                media = Video(
                    file=file,
                    width=tg_video.width,
                    height=tg_video.height,
                    duration=tg_video.duration,
                    file_name=tg_video.file_name,
                    mime_type=tg_video.mime_type,
                    supports_streaming=tg_video.supports_streaming,
                    ttl_seconds=tg_video.ttl_seconds,
                    date=tg_video.date,
                    thumbs=[
                        Thumbnail(
                            file=SizedFile(
                                unique_id=thumb.file_unique_id,
                                access_key=thumb.file_id,
                                file_size=thumb.file_size,
                            ),
                            width=thumb.width,
                            height=thumb.height,
                        )
                        for thumb in (tg_video.thumbs or ())
                    ] if tg_video.thumbs else [],
                )
            case pyrogram.Voice() as tg_voice:
                file = SizedFile(
                    unique_id=tg_voice.file_unique_id,
                    access_key=tg_voice.file_id,
                    file_size=tg_voice.file_size,
                )
                media = Voice(
                    file=file,
                    duration=tg_voice.duration,
                    waveform=tg_voice.waveform,
                    mime_type=tg_voice.mime_type,
                    date=tg_voice.date
                )
            case pyrogram.VideoNote() as tg_video_note:
                file = SizedFile(
                    unique_id=tg_video_note.file_unique_id,
                    access_key=tg_video_note.file_id,
                    file_size=tg_video_note.file_size,
                )
                media = VideoNote(
                    file=file,
                    length=tg_video_note.length,
                    duration=tg_video_note.duration,
                    mime_type=tg_video_note.mime_type,
                    date=tg_video_note.date,
                    thumbs=[
                        Thumbnail(
                            file=SizedFile(
                                unique_id=thumb.file_unique_id,
                                access_key=thumb.file_id,
                                file_size=thumb.file_size,
                            ),
                            width=thumb.width,
                            height=thumb.height,
                        )
                        for thumb in tg_video_note.thumbs
                    ] if tg_video_note.thumbs else [],
                )
            case pyrogram.Contact() as tg_contact:
                media = Contact(
                    phone_number=tg_contact.phone_number,
                    first_name=tg_contact.first_name,
                    last_name=tg_contact.last_name,
                    user_id=tg_contact.user_id,
                    vcard=tg_contact.vcard,
                )
            case pyrogram.Location() as tg_location:
                media = self.from_location(tg_location=tg_location)
            case pyrogram.Venue() as tg_venue:
                media = Venue(
                    location=self.from_location(tg_location=tg_venue.location, type=LocationType.USUAL),
                    title=tg_venue.title,
                    address=tg_venue.address,
                    foursquare_id=tg_venue.foursquare_id,
                    foursquare_type=tg_venue.foursquare_type,
                )
            case pyrogram.Poll() as tg_poll:
                if tg_poll.type == PollType.REGULAR:
                    media = Poll(
                        tg_id=int(tg_poll.id),
                        question=self.from_string(tg_poll.question),
                        options=[
                            PollOption(text=self.from_string(option.text))
                            for option in tg_poll.options
                        ],
                        allows_multiple_answers=tg_poll.allows_multiple_answers,
                        total_voter_count=tg_poll.total_voter_count,
                        is_anonymous=tg_poll.is_anonymous,
                        open_period=tg_poll.open_period,
                        close_date=tg_poll.close_date,
                    )
                elif tg_poll.type == PollType.QUIZ:
                    media = Quiz(
                        tg_id=int(tg_poll.id),
                        question=self.from_string(tg_poll.question),
                        options=[
                            PollOption(text=self.from_string(option.text))
                            for option in tg_poll.options
                        ],
                        total_voter_count=tg_poll.total_voter_count,
                        is_anonymous=tg_poll.is_anonymous,
                        open_period=tg_poll.open_period,
                        close_date=tg_poll.close_date,
                    )
                else:
                    raise ValueError(f"Unsupported poll type: {tg_poll.type}")
            case pyrogram.WebPage() as tg_webpage:
                # tg_webpage_raw = tg_webpage.raw.webpage  # type: ignore
                # if isinstance(tg_webpage_raw, pyrogram_raw.web_page_empty.WebPageEmpty):
                #     media = WebPageEmpty(tg_id=tg_webpage.id)
                # if isinstance(tg_webpage_raw, pyrogram_raw.web_page_pending.WebPagePending):
                #     media = WebPagePending(tg_id=tg_webpage.id)

                # TODO: check is this is correct
                if tg_webpage.display_url is None:
                    media = WebPageEmpty(tg_id=tg_webpage.id)
                else:
                    media = WebPageDetails(
                        tg_id=tg_webpage.id,
                        url=tg_webpage.url,
                        display_url=tg_webpage.display_url,
                        type=tg_webpage.type,
                        site_name=tg_webpage.site_name,
                        title=tg_webpage.title,
                        description=tg_webpage.description,
                        audio=self.from_media(tg_webpage.audio) if tg_webpage.audio else None,
                        document=self.from_media(tg_webpage.document) if tg_webpage.document else None,
                        photo=self.from_media(tg_webpage.photo) if tg_webpage.photo else None,
                        animation=self.from_media(tg_webpage.animation) if tg_webpage.animation else None,
                        video=self.from_media(tg_webpage.video) if tg_webpage.video else None,
                        embed_url=tg_webpage.embed_url,
                        embed_type=tg_webpage.embed_type,
                        embed_width=tg_webpage.embed_width,
                        embed_height=tg_webpage.embed_height,
                        duration=tg_webpage.duration,
                        author=tg_webpage.author,
                    )
            case pyrogram.Dice() as tg_dice:
                media = Dice(emoji=tg_dice.emoji, value=tg_dice.value)
            case pyrogram.Game() as tg_game:
                media = GameDetailed(
                    tg_id=tg_game.id,
                    title=tg_game.title,
                    short_name=tg_game.short_name,
                    description=tg_game.description,
                    photo=self.from_media(tg_game.photo),
                    animation=self.from_media(tg_game.animation) if tg_game.animation else None,
                )
            case pyrogram.Giveaway() as tg_giveaway:
                if tg_giveaway.stars is not None:
                    media = StarsGiveaway(
                        stars=tg_giveaway.stars,
                        channels_to_subscribe=[
                            self.from_channel(tg_chat) for tg_chat in tg_giveaway.chats
                        ] if tg_giveaway.chats else None,
                        until_date=tg_giveaway.until_date,
                        description=tg_giveaway.description,
                        only_new_subscribers=tg_giveaway.only_new_subscribers,
                        only_for_countries=tg_giveaway.only_for_countries,
                        winners_are_visible=tg_giveaway.winners_are_visible,
                    )
                elif tg_giveaway.quantity is not None:
                    media = SubscriptionsGiveaway(
                        quantity=tg_giveaway.quantity,
                        months=tg_giveaway.months,
                        channels_to_subscribe=[
                            self.from_channel(tg_chat) for tg_chat in tg_giveaway.chats
                        ] if tg_giveaway.chats else None,
                        until_date=tg_giveaway.until_date,
                        description=tg_giveaway.description,
                        only_new_subscribers=tg_giveaway.only_new_subscribers,
                        only_for_countries=tg_giveaway.only_for_countries,
                        winners_are_visible=tg_giveaway.winners_are_visible,
                    )
                else:
                    raise TransformValueError(f"Can't get info about giveaway from {tg_media}", tg_media)
            case pyrogram.GiveawayWinners() as tg_giveaway_winners:
                winners = [self.from_user(tg_user) for tg_user in tg_giveaway_winners.winners]
                if tg_giveaway_winners.prize_star_count is not None:
                    media = StarsGiveawayWinners(
                        chat=self.from_chat(tg_giveaway_winners.chat),
                        prize_star_count=tg_giveaway_winners.prize_star_count,
                        giveaway_message_id=tg_giveaway_winners.giveaway_message_id,
                        winners_selection_date=tg_giveaway_winners.winners_selection_date,
                        quantity=tg_giveaway_winners.quantity,
                        winner_count=tg_giveaway_winners.winner_count,
                        unclaimed_prize_count=tg_giveaway_winners.unclaimed_prize_count,  # type: ignore
                        winners=winners,
                        was_refunded=tg_giveaway_winners.was_refunded or False,
                    )
                elif tg_giveaway_winners.premium_subscription_month_count is not None:
                    media = SubscriptionsGiveawayWinners(
                        chat=self.from_chat(tg_giveaway_winners.chat),
                        premium_subscription_month_count=tg_giveaway_winners.premium_subscription_month_count,
                        giveaway_message_id=tg_giveaway_winners.giveaway_message_id,
                        winners_selection_date=tg_giveaway_winners.winners_selection_date,
                        quantity=tg_giveaway_winners.quantity,
                        winner_count=tg_giveaway_winners.winner_count,
                        unclaimed_prize_count=tg_giveaway_winners.unclaimed_prize_count,  # type: ignore
                        winners=winners,
                        was_refunded=tg_giveaway_winners.was_refunded or False,
                    )
                else:
                    raise ValueError
            case pyrogram.Story() as tg_story:
                media = Story(
                    tg_id=tg_story.id,
                    caption=(
                        self.from_string_with_entities(tg_story.caption, tg_entities=tg_story.caption_entities)
                        if tg_story.caption else None
                    ),
                    type=cast(Literal[MessageMediaType.PHOTO, MessageMediaType.VIDEO] | None, tg_story.media),
                    date=cast(dt, tg_story.date),
                )
            case pyrogram.Invoice() as tg_invoice:
                media = Invoice(
                    currency=tg_invoice.currency,
                    is_test=tg_invoice.is_test,
                    title=tg_invoice.title,
                    description=tg_invoice.description,
                    total_amount=tg_invoice.total_amount,
                    start_parameter=tg_invoice.start_parameter,
                    prices=[
                        LabeledPrice(label=tg_price.label, amount=tg_price.amount)
                        for tg_price in tg_invoice.prices
                    ] if tg_invoice.prices else None,
                    is_name_requested=tg_invoice.is_name_requested,
                    is_phone_requested=tg_invoice.is_phone_requested,
                    is_email_requested=tg_invoice.is_email_requested,
                    is_shipping_address_requested=tg_invoice.is_shipping_address_requested,
                    is_flexible=tg_invoice.is_flexible,
                    is_phone_to_provider=tg_invoice.is_phone_to_provider,
                    is_email_to_provider=tg_invoice.is_email_to_provider,
                    is_recurring=tg_invoice.is_recurring,
                    max_tip_amount=tg_invoice.max_tip_amount,
                    suggested_tip_amounts=tg_invoice.suggested_tip_amounts,
                    terms_url=tg_invoice.terms_url,
                )
            case pyrogram.PaidMediaInfo() as tg_paid_media:
                media = PaidMedia(
                    stars_amount=cast(int, tg_paid_media.stars_amount),
                    media=cast(
                        Sequence[Photo | Video] | Sequence[PaidMediaPreview],
                        [self.from_media(tg_media=tg_media) for tg_media in tg_media.media]
                    ),
                )
            case pyrogram.PaidMediaPreview() as tg_paid_media_preview:
                media = PaidMediaPreview(
                    width=tg_paid_media_preview.width,
                    height=tg_paid_media_preview.height,
                    duration=tg_paid_media_preview.duration,
                    thumbnail=None  # TODO
                )
            case pyrogram.Checklist() as tg_checklist:
                media = Checklist(
                    title=self.from_string_with_entities(tg_checklist.title, tg_entities=tg_checklist.entities),
                    tasks=[
                        ChecklistTask(
                            tg_id=task.id,
                            text=self.from_string_with_entities(task.text, tg_entities=task.entities),
                            completed_by=optional(self.from_chat, task.completed_by),
                            completion_date=task.completion_date,
                        )
                        for task in tg_checklist.tasks or ()
                    ],
                    others_can_add_tasks=tg_checklist.others_can_add_tasks,
                    can_add_tasks=tg_checklist.can_add_tasks,
                    others_can_mark_tasks_as_done=tg_checklist.others_can_mark_tasks_as_done,
                    can_mark_tasks_as_done=tg_checklist.can_mark_tasks_as_done,
                )
            case wtf:
                raise TypeError(f"Unknown media type: {type(wtf)}")

        return media

    def get_price(self, priced: HasPriceInfo) -> MoneyAmount:
        if priced.amount is not None and priced.currency is not None:
            return CurrencyAmount(currency=priced.currency, amount=priced.amount)
        elif priced.cryptocurrency_amount is not None and priced.cryptocurrency is not None:
            return CryptocurrencyAmount(currency=priced.cryptocurrency, amount=priced.cryptocurrency_amount)

        missed_field = ''
        if priced.amount is None and priced.currency is not None:
            missed_field = 'amount'
        elif priced.amount is not None and priced.currency is None:
            missed_field = 'currency'
        elif priced.cryptocurrency_amount is None and priced.cryptocurrency is not None:
            missed_field = 'cryptocurrency_amount'
        elif priced.cryptocurrency_amount is not None and priced.cryptocurrency is None:
            missed_field = 'cryptocurrency'

        raise TransformMissingRequiredField(f"Priced item missing value for '{missed_field}' field: {priced}",
                                            object=priced, field_name=missed_field)

    @overload
    def from_location(
        self, tg_location: pyrogram.Location, *, type: Literal[LocationType.USUAL]
    ) -> Location: pass
    # TODO: map specific required types of locations
    # @overload
    # def from_location(
    #     self, tg_location: pyrogram.Location, *, type: Literal[LocationType.LIVE]
    # ) -> LiveLocation: pass
    # @overload
    # def from_location(
    #     self, tg_location: pyrogram.Location, *, type: Literal[LocationType.BUSINESS]
    # ) -> BusinessLocation: pass

    @overload
    def from_location(
        self, tg_location: pyrogram.Location, *, type: Literal[None] = None
    ) -> LiveLocation | BusinessLocation | Location: pass

    def from_location(
        self,
        tg_location: pyrogram.Location,
        *,
        type: LocationType | None = None
    ) -> LiveLocation | BusinessLocation | Location:
        geo: Location | None = None
        if tg_location.latitude is not None and tg_location.longitude is not None:
            geo = Location(
                longitude=tg_location.longitude,
                latitude=tg_location.latitude,
                accuracy=tg_location.accuracy_radius,
            )

        location: LiveLocation | BusinessLocation | Location
        if tg_location.live_period is not None:
            if geo is None:
                raise ValueError(f"Live location {tg_location} missing 'longitude' or 'latitude'")
            location = LiveLocation(
                location=geo,
                heading=tg_location.heading,
                live_period=tg_location.live_period,
                proximity_alert_radius=tg_location.proximity_alert_radius,
            )
        elif tg_location.address is not None:
            location = BusinessLocation(address=tg_location.address, location=geo)
        elif geo:
            location = geo
        elif geo is None:
            raise ValueError(f"Location {tg_location} missing 'longitude' or 'latitude'")

        return location


def not_none(value: T | None, description: str | None = None) -> T:
    if value is None:
        if description is None:
            description = "Unexpeted None value"
        else:
            description = f"Unexpeted None value in {description}"
        raise TransformValueError(description)
    return value


def optional(fn: Callable[[T], Return], value: T | None) -> Return | None:
    if value is None:
        return None
    return fn(value)


class OptionalFn(Protocol[Arg, Return]):
    @overload
    def __call__(self, value: Arg) -> Return: ...
    @overload
    def __call__(self, value: None) -> None: ...

    def __call__(self, value: Arg | None) -> Return | None:
        pass
