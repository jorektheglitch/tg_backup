from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime as dt  # , timedelta as td
from enum import StrEnum
from typing import Any, ClassVar, Literal, TypeAlias, TypeVar, cast, overload
from typing_extensions import Self

import pyrogram.types as pyrogram
import pyrogram.enums as pyrogram_enums
import pyrogram.raw.types as pyrogram_raw
from pyrogram.types.messages_and_media.message import Str
from pyrogram.enums import (
    ChatType,
    MessageEntityType,
    MessageMediaType,
    MessageServiceType,
    # MessageOriginType,
    PollType,
    UserStatus
)


@dataclass(frozen=True)
class Text:
    raw: str
    entities: Sequence[TextEntity] = ()

    __pyro_class__ = Str

    def __str__(self) -> str:
        return self.raw


@dataclass(frozen=True)
class Media(ABC):
    pass


@dataclass(frozen=True)
class FileMedia(Media, ABC):
    file_id: str
    file_unique_id: str


@dataclass(frozen=True)
class Thumbnail(FileMedia):
    width: int
    height: int
    file_size: int

    __pyro_class__ = pyrogram.Thumbnail


@dataclass(frozen=True)
class Sticker(FileMedia):
    width: int
    height: int
    is_animated: bool
    is_video: bool
    file_name: str | None
    mime_type: str | None
    file_size: int | None
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
    file_size: int | None
    date: dt | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Audio


@dataclass(frozen=True)
class Document(FileMedia):
    file_name: str | None
    mime_type: str | None
    file_size: int | None
    date: dt | None

    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.Document


@dataclass(frozen=True)
class Photo(FileMedia):
    width: int
    height: int
    file_size: int | None
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
    file_size: int | None
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
    file_size: int | None
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
    file_size: int | None
    date: dt | None

    __pyro_class__ = pyrogram.Voice


@dataclass(frozen=True)
class VideoNote(FileMedia):
    length: int
    duration: int
    mime_type: str | None
    file_size: int | None
    date: dt | None
    thumbs: Sequence[Thumbnail]

    __pyro_class__ = pyrogram.VideoNote


@dataclass
class Game():
    tg_id: int

    __pyro_class__ = pyrogram.Game


@dataclass
class GameDetailed(Game):
    tg_id: int
    title: str
    short_name: str
    description: str
    photo: Photo
    animation: Animation | None = None


@dataclass
class Giveaway(ABC):
    channels: Sequence[Channel] | None = field(default=None, kw_only=True)
    until_date: dt | None = field(default=None, kw_only=True)
    description: str | None = field(default=None, kw_only=True)
    only_new_subscribers: bool | None = field(default=None, kw_only=True)
    only_for_countries: Sequence[str] | None = field(default=None, kw_only=True)
    winners_are_visible: bool = field(kw_only=True)

    __pyro_class__ = pyrogram.Giveaway


@dataclass
class StarsGiveaway(Giveaway):
    stars: int


@dataclass
class SubscriptionsGiveaway(Giveaway):
    quantity: int
    months: int


@dataclass
class GiveawayCompleted:
    winner_count: int
    # unclaimed_prize_count: int = None
    # giveaway_message_id: int = None
    # giveaway_message: "types.Message" = None
    # is_star_giveaway: bool = None


@dataclass
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


@dataclass
class StarsGiveawayWinners(GiveawayWinners):
    prize_star_count: int


@dataclass
class SubscriptionsGiveawayWinners(GiveawayWinners):
    premium_subscription_month_count: int


@dataclass
class Story:
    # TODO: wtf is this shit???
    tg_id: int
    caption: Text | None
    type: Literal[MessageMediaType.PHOTO, MessageMediaType.VIDEO] | None
    date: dt

    __pyro_class__ = pyrogram.Story


@dataclass
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


@dataclass
class LabeledPrice:
    label: str
    amount: int

    __pyro_class__ = pyrogram.LabeledPrice


@dataclass
class PaidMedia:
    stars_amount: str
    media: Sequence[Photo | Video] | Sequence[PaidMediaPreview]

    __pyro_class__ = pyrogram.PaidMediaInfo


@dataclass
class PaidMediaPreview:
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    thumbnail: StrippedThumbnail | None = None

    __pyro_class__ = pyrogram.PaidMediaPreview


@dataclass
class StrippedThumbnail:
    data: bytes

    __pyro_class__ = pyrogram.StrippedThumbnail


@dataclass
class Checklist:
    title: Text
    tasks: Sequence[ChecklistTask]
    others_can_add_tasks: bool | None = None
    can_add_tasks: bool | None = None
    others_can_mark_tasks_as_done: bool | None = None
    can_mark_tasks_as_done: bool | None = None

    __pyro_class__ = pyrogram.Checklist


@dataclass
class ChecklistTask:
    tg_id: int
    text: Text
    completed_by: Chat | None = None
    completion_date: dt | None = None

    __pyro_class__ = pyrogram.ChecklistTask


@dataclass
class Contact():
    phone_number: str
    first_name: str
    last_name: str | None
    user_id: int | None
    vcard: str | None

    __pyro_class__ = pyrogram.Contact


@dataclass
class Location:
    longitude: float
    latitude: float
    accuracy: int | None = None

    __pyro_class__ = pyrogram.Location


@dataclass
class LiveLocation:
    location: Location
    heading: int | None = None
    live_period: int = field(kw_only=True)
    proximity_alert_radius: int | None = field(default=None, kw_only=True)

    __pyro_class__ = pyrogram.Location


@dataclass
class BusinessLocation:
    address: str
    location: Location | None = None

    __pyro_class__ = pyrogram.Location


@dataclass
class Venue():
    location: Location
    title: str
    address: str
    foursquare_id: str | None
    foursquare_type: str | None

    __pyro_class__ = pyrogram.Venue


@dataclass
class WebPage:
    tg_id: str

    __pyro_class__ = pyrogram.WebPage


@dataclass
class WebPageEmpty(WebPage):
    pass


@dataclass
class WebPagePending(WebPage):
    pass


@dataclass
class WebPageDetails(WebPage):
    """A webpage preview

    Parameters:
        id (``str``):
            Unique identifier for this webpage.

        url (``str``):
            Full URL for this webpage.

        display_url (``str``):
            Display URL for this webpage.

        type (``str``, *optional*):
            Type of webpage preview, known types (at the time of writing) are:
            *"article"*, *"photo"*, *"gif"*, *"video"* and *"document"*,
            *"telegram_user"*, *"telegram_bot"*, *"telegram_channel"*, *"telegram_megagroup"*.

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
    duration: int | None
    author: str | None

    __pyro_class__ = pyrogram.WebPage


@dataclass
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


@dataclass
class PollOption:
    text: Text
    # voter_count: int

    __pyro_class__ = pyrogram.PollOption


@dataclass
class Poll(PollLike):
    allows_multiple_answers: bool


@dataclass
class Quiz(PollLike):
    pass
    # explanation: Text


@dataclass
class Dice:
    emoji: str
    value: int

    __pyro_class__ = pyrogram.Dice


@dataclass
class ChatPhoto:
    small_file_id: str
    small_photo_unique_id: str
    big_file_id: str
    big_photo_unique_id: str


@dataclass
class User:
    tg_id: int


@dataclass
class UserDetailed(User):
    user_id: int
    # is_self: bool None
    is_contact: bool | None
    is_mutual_contact: bool | None
    is_deleted: bool | None
    is_bot: bool | None
    is_verified: bool | None
    is_restricted: bool | None
    is_scam: bool | None
    is_fake: bool | None
    is_support: bool | None
    is_premium: bool | None
    first_name: str | None
    last_name: str | None
    status: UserStatus | None
    last_online_date: dt | None
    next_offline_date: dt | None
    username: str | None
    language_code: str | None
    emoji_status: EmojiStatus | None
    dc_id: int | None
    phone_number: str | None
    photo_id: int
    photo: ChatPhoto | None
    restrictions: Sequence[Restriction]

    __pyro_class__ = pyrogram.User


@dataclass
class CustomEmoji:
    tg_id: int


@dataclass
class EmojiStatus:
    custom_emoji_id: int
    until_date: dt | None

    __pyro_class__ = pyrogram.EmojiStatus


@dataclass
class Restriction:
    platform: str
    reason: str
    text: str

    __pyro_class__ = pyrogram.Restriction


@dataclass
class Chat_():
    """
    A chat.

    Parameters:
        id (``int``):
            Unique identifier for this chat.

        type (:obj:`~pyrogram.enums.ChatType`):
            Type of chat.

        is_verified (``bool``, *optional*):
            True, if this chat has been verified by Telegram. Supergroups, channels and bots only.

        is_restricted (``bool``, *optional*):
            True, if this chat has been restricted. Supergroups, channels and bots only.
            See *restriction_reason* for details.

        is_creator (``bool``, *optional*):
            True, if this chat owner is the current user. Supergroups, channels and groups only.

        is_scam (``bool``, *optional*):
            True, if this chat has been flagged for scam.

        is_fake (``bool``, *optional*):
            True, if this chat has been flagged for impersonation.

        is_support (``bool``):
            True, if this chat is part of the Telegram support team. Users and bots only.

        title (``str``, *optional*):
            Title, for supergroups, channels and basic group chats.

        username (``str``, *optional*):
            Username, for private chats, bots, supergroups and channels if available.

        first_name (``str``, *optional*):
            First name of the other party in a private chat, for private chats and bots.

        last_name (``str``, *optional*):
            Last name of the other party in a private chat, for private chats.

        photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            Chat photo. Suitable for downloads only.

        bio (``str``, *optional*):
            Bio of the other party in a private chat.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        description (``str``, *optional*):
            Description, for groups, supergroups and channel chats.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        dc_id (``int``, *optional*):
            The chat assigned DC (data center). Available only in case the chat has a photo.
            Note that this information is approximate; it is based on where Telegram stores the current chat photo.
            It is accurate only in case the owner has set the chat photo, otherwise the dc_id will be the one assigned
            to the administrator who set the current chat photo.

        has_protected_content (``bool``, *optional*):
            True, if messages from the chat can't be forwarded to other chats.

        invite_link (``str``, *optional*):
            Chat invite link, for groups, supergroups and channels.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        pinned_message (:obj:`~pyrogram.types.Message`, *optional*):
            Pinned message, for groups, supergroups channels and own chat.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        sticker_set_name (``str``, *optional*):
            For supergroups, name of group sticker set.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        can_set_sticker_set (``bool``, *optional*):
            True, if the group sticker set can be changed by you.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        members_count (``int``, *optional*):
            Chat members count, for groups, supergroups and channels only.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        restrictions (List of :obj:`~pyrogram.types.Restriction`, *optional*):
            The list of reasons why this chat might be unavailable to some users.
            This field is available only in case *is_restricted* is True.

        permissions (:obj:`~pyrogram.types.ChatPermissions` *optional*):
            Default chat member permissions, for groups and supergroups.

        distance (``int``, *optional*):
            Distance in meters of this group chat from your location.
            Returned only in :meth:`~pyrogram.Client.get_nearby_chats`.

        linked_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            The linked discussion group (in case of channels) or the linked channel (in case of supergroups).
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        send_as_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            The default "send_as" chat.
            Returned only in :meth:`~pyrogram.Client.get_chat`.

        available_reactions (:obj:`~pyrogram.types.ChatReactions`, *optional*):
            Available reactions in the chat.
            Returned only in :meth:`~pyrogram.Client.get_chat`.
    """

    oid: int
    id: int
    type: ChatType
    # is_verified: bool | None
    # is_restricted: bool | None
    # is_creator: bool | None
    # is_scam: bool | None
    # is_fake: bool | None
    # is_support: bool | None
    # title: str | None
    # username: str | None
    # first_name: str | None
    # last_name: str | None
    photo: ChatPhoto | None
    # bio: str | None
    # description: str | None
    # dc_id: int | None
    # has_protected_content: bool | None
    # invite_link: str | None
    # pinned_message: Message | None
    # # pinned_message_id: int | None
    # sticker_set_name: str | None
    # can_set_sticker_set: bool | None
    # members_count: int | None
    # restrictions: Sequence["types.Restriction"] = None
    # permissions: "types.ChatPermissions" = None
    # distance: int | None
    # linked_chat: "types.Chat" = None
    # linked_chat_id: int | None
    # send_as_chat: "types.Chat" = None
    # send_as_chat_id: int | None
    # available_reactions: ChatReactions = None


# PRIVATE = auto()  # "Chat is a private chat with a user"
# BOT = auto()  # "Chat is a private chat with a bot"
# GROUP = auto()  # "Chat is a basic group"
# SUPERGROUP = auto()  # "Chat is a supergroup"
# CHANNEL = auto()  # "Chat is a channel"
"""
General:
    is_scam: bool
    is_fake: bool
    photo: ChatPhoto | None
    dc_id: int | None  # useless
    has_protected_content: bool | None
    ? send_as_chat: Chat | None  # Returned only in :meth:`~pyrogram.Client.get_chat`.
    available_reactions: ChatReations | None  # Returned only in :meth:`~pyrogram.Client.get_chat`.
Supergroups:
    sticket_set_name: str | None  # Returned only in :meth:`~pyrogram.Client.get_chat`.
    can_set_sticker_set: bool | None  # Returned only in :meth:`~pyrogram.Client.get_chat`.
Users and bots only:
    is_support: bool
Supergroups, channels and basic group chats:
    title: str
Private chats and bots:
    first_name: str
Private chats:
    last_name: str
    bio: str (or None?)  # Returned only in :meth:`~pyrogram.Client.get_chat`.
Supergroups, channels and bots only:
    is_verified: bool
    is_restricted: bool
    restrictions: list[Restriction]
Groups and supergroups:
    permissions: list[ChatPermissions]  # default permissions
Supergroups, channels and groups only:
    is_creator: bool
Groups, supergroups and channel chats:
    description: str | None  # Returned only in :meth:`~pyrogram.Client.get_chat`.
Groups, supergroups and channels:
    invite_link: str | None  # Returned only in :meth:`~pyrogram.Client.get_chat`.
    members_count: int  # Returned only in :meth:`~pyrogram.Client.get_chat`.
Groups, supergroups channels and own chat:
    pinned_message: Message | None
Channels and supergroups:
    # The linked discussion group (in case of channels) or the linked channel (in case of supergroups).
    linked_chat: Chat | None  # Returned only in :meth:`~pyrogram.Client.get_chat`.
"""


@dataclass
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


@dataclass
class VerificationStatus:
    is_verified: bool
    is_scam: bool
    is_fake: bool
    bot_verification_icon_custom_emoji_id: int | None = None


@dataclass
class ReplyColor:
    color: pyrogram_enums.ReplyColor
    bg_emoji: CustomEmoji | None


@dataclass
class ProfileColor:
    color: pyrogram_enums.ProfileColor
    bg_emoji: CustomEmoji | None


@dataclass
class Chat:
    # TODO: map fields properly
    tg_id: int
    type: ChatType = field(kw_only=True)


@dataclass
class DialogFull(ABC):
    tg_id: int

    __pyro_class__ = pyrogram.Chat


@dataclass
class PrivateChat(DialogFull):
    tg_id: int
    type: ChatType = field(kw_only=True, default=ChatType.PRIVATE)
    is_restricted: bool
    is_support: bool
    is_stories_hidden: bool
    is_stories_unavailable: bool
    is_business_bot: bool
    verification_status: VerificationStatus
    username: str | None
    usernames: list[str] | None
    first_name: str
    last_name: str | None
    photo: ChatPhoto | None
    restrictions: Sequence[Restriction]
    reply_color: ReplyColor | None
    profile_color: ProfileColor | None
    paid_message_star_count: int | None

    @property
    def is_verified(self) -> bool:
        return self.verification_status.is_verified

    @property
    def is_scam(self) -> bool:
        return self.verification_status.is_scam

    @property
    def is_fake(self) -> bool:
        return self.verification_status.is_fake


@dataclass
class BotChat(DialogFull):
    tg_id: int
    type: ChatType = field(kw_only=True, default=ChatType.BOT)
    is_restricted: bool
    is_support: bool
    is_business_bot: bool
    verification_status: VerificationStatus
    username: str
    title: str
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


@dataclass
class UnavailableChat(DialogFull):
    tg_id: int
    title: str


@dataclass
class ChatFull(DialogFull):
    tg_id: int
    type: ChatType = field(kw_only=True, default=ChatType.GROUP)
    title: str
    # is_creator: bool
    # is_admin: bool
    is_deactivated: bool
    is_call_active: bool
    is_call_not_empty: bool
    usernames: Sequence[str] | None
    photo: ChatPhoto | None
    permissions: ChatPermissions
    members_count: int
    has_protected_content: bool


@dataclass
class Group(ChatFull):
    # tg_id: int
    # title: str
    # permissions_ref: int
    # permissions: ChatPermissions  # default permissions
    # # is_creator: bool
    # description: str | None
    tg_id: int
    type: ChatType = field(kw_only=True, default=ChatType.GROUP)
    title: str
    # is_creator: bool
    # is_admin: bool
    is_deactivated: bool
    is_call_active: bool
    is_call_not_empty: bool
    usernames: Sequence[str] | None
    photo: ChatPhoto | None
    permissions: ChatPermissions
    members_count: int
    has_protected_content: bool


@dataclass
class GroupDetails(Group):
    """
    Including all the info from :meth:`~pyrogram.Client.get_chat`.
    """
    invite_link: str | None
    members_count: int


@dataclass
class Supergroup(DialogFull):
    tg_id: int
    title: str
    is_verified: bool
    is_restricted: bool
    is_forum: bool
    # is_creator: bool
    description: str | None
    restrictions: Sequence[Restriction]
    permissions: ChatPermissions  # default permissions


@dataclass
class SupergroupDetails(Supergroup):
    """
    Including all the info from :meth:`~pyrogram.Client.get_chat`.
    """
    members_count: int
    sticket_set_name: str | None
    can_set_sticker_set: bool | None
    invite_link: str | None
    pinned_message: ChannelPost | None
    linked_channel: Channel | None


@dataclass
class Channel(DialogFull):
    tg_id: int
    title: str
    is_verified: bool
    is_restricted: bool
    restrictions: Sequence[Restriction]
    # is_creator: bool
    description: str | None


@dataclass
class ChannelDetails(Channel):
    """
    Including all the info from :meth:`~pyrogram.Client.get_chat`.
    """
    invite_link: str | None
    members_count: int
    pinned_message: ChannelPost | None
    linked_chat: Supergroup | None


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


@dataclass
class TextEntity(ABC):
    offset: int
    length: int

    __pyro_mark__: ClassVar[MessageEntityType]


@dataclass
class Mention(TextEntity):
    __pyro_mark__ = MessageEntityType.MENTION


@dataclass
class Hashtag(TextEntity):
    __pyro_mark__ = MessageEntityType.HASHTAG


@dataclass
class Cashtag(TextEntity):
    __pyro_mark__ = MessageEntityType.CASHTAG


@dataclass
class BotCommand(TextEntity):
    __pyro_mark__ = MessageEntityType.BOT_COMMAND


@dataclass
class URL(TextEntity):
    __pyro_mark__ = MessageEntityType.URL


@dataclass
class Email(TextEntity):
    __pyro_mark__ = MessageEntityType.EMAIL


@dataclass
class PhoneNumber(TextEntity):
    __pyro_mark__ = MessageEntityType.PHONE_NUMBER


@dataclass
class Bold(TextEntity):
    __pyro_mark__ = MessageEntityType.BOLD


@dataclass
class Italic(TextEntity):
    __pyro_mark__ = MessageEntityType.ITALIC


@dataclass
class Underline(TextEntity):
    __pyro_mark__ = MessageEntityType.UNDERLINE


@dataclass
class Strikethrough(TextEntity):
    __pyro_mark__ = MessageEntityType.STRIKETHROUGH


@dataclass
class Spoiler(TextEntity):
    __pyro_mark__ = MessageEntityType.SPOILER


@dataclass
class Code(TextEntity):
    __pyro_mark__ = MessageEntityType.CODE


@dataclass
class Pre(TextEntity):
    language: str | None

    __pyro_mark__ = MessageEntityType.PRE


@dataclass
class BlockQuote(TextEntity):
    __pyro_mark__ = MessageEntityType.BLOCKQUOTE


@dataclass
class TextLink(TextEntity):
    url: str

    __pyro_mark__ = MessageEntityType.TEXT_LINK


@dataclass
class TextMention(TextEntity):
    user: User

    __pyro_mark__ = MessageEntityType.TEXT_MENTION


@dataclass
class BankCard(TextEntity):
    __pyro_mark__ = MessageEntityType.BANK_CARD


@dataclass
class CustomEmojiEntity(TextEntity):
    custom_emoji: CustomEmoji

    __pyro_mark__ = MessageEntityType.CUSTOM_EMOJI


@dataclass
class UnknownEntity(TextEntity):
    __pyro_mark__ = MessageEntityType.UNKNOWN


MessagePayloadType: TypeAlias = MessageMediaType | MessageServiceType


@dataclass
class Message(ABC):
    __pyro_class__ = pyrogram.Message
    __pyro_mark__: ClassVar[MessagePayloadType]


# Message sources:
#  From user - from_user: User
#  On behalf of a chat - sender_chat: Chat
#  Channel post - sender_chat: Chat, author_signature: str None
#  From anon admin - sender_chat: Chat, author_signature: str None
#  Fwded to linked group - sender_chat: Chat


@dataclass
class MessageSource(ABC):
    pass


@dataclass
class FromUser(MessageSource):
    user: User


@dataclass
class FromChannelAdmin(MessageSource):
    channel: Channel
    author_signature: str | None


@dataclass
class FromChannel(MessageSource):
    channel: Channel


@dataclass
class FromAnonAdmin(MessageSource):
    chat: Chat
    admin_mark: str | None


@dataclass
class ForwardOrigin(ABC):
    pass

# Forward sources:
#  From user - forward_from: User
#  From anon user - forward_sender_name: str
#  Auto from linked channel - sender_chat: Chat
#  From channdel - forward_from_chat: Chat, forward_from_message_id: int, forward_signature: str None
#  From chat - forward_from_chat: Chat
#  From anon chat admin - forward_from_chat: Chat


@dataclass
class AnonUserOrigin(ForwardOrigin):
    sender_name: str


@dataclass
class UserOrigin(ForwardOrigin):
    user: User


@dataclass
class _ChannelOrigin(ForwardOrigin):
    channel: Channel
    source_message_id: int
    author_signature: str | None


@dataclass
class LinkedChannelOrigin(_ChannelOrigin):
    pass


@dataclass
class ChannelOrigin(_ChannelOrigin):
    pass


@dataclass
class AnonAdminOrigin(ForwardOrigin):
    chat: Chat
    admin_mark: str | None


@dataclass
class ChatMessage:
    chat: Chat
    msg_no: int
    sender: MessageSource
    has_protected_content: bool
    date: dt
    payload: Message


@dataclass
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


@dataclass
class Forwarded(Message):
    origin: ForwardOrigin
    origin_date: dt | None
    message: Message


@dataclass
class TextMessage(Message):
    text: Text


@dataclass
class ServiceMessage(Message, ABC):
    __pyro_mark__: ClassVar[MessageServiceType]  # type: ignore


@dataclass
class NewChatMembers(ServiceMessage):
    new_chat_members: Sequence[User]

    __pyro_mark__ = MessageServiceType.NEW_CHAT_MEMBERS


@dataclass
class LeftChatMember(ServiceMessage):
    left_user: User

    __pyro_mark__ = MessageServiceType.LEFT_CHAT_MEMBER


@dataclass
class NewChatTitle(ServiceMessage):
    new_chat_title: str

    __pyro_mark__ = MessageServiceType.NEW_CHAT_TITLE


@dataclass
class NewChatPhoto(ServiceMessage):
    new_chat_photo: Photo

    __pyro_mark__ = MessageServiceType.NEW_CHAT_PHOTO


@dataclass
class ChatPhotoDeleted(ServiceMessage):
    __pyro_mark__ = MessageServiceType.DELETE_CHAT_PHOTO


@dataclass
class GroupCreated(ServiceMessage):
    __pyro_mark__ = MessageServiceType.GROUP_CHAT_CREATED


# TODO: wtf in pyro
# @dataclass
# class SupergroupChatCreated(ServiceMessage):
#     __pyro_mark__ = MessageServiceType


@dataclass
class ChannelCreated(ServiceMessage):
    __pyro_mark__ = MessageServiceType.CHANNEL_CHAT_CREATED


@dataclass
class MigrateToSupergroup(ServiceMessage):
    migrate_to_chat: Chat

    __pyro_mark__ = MessageServiceType.MIGRATE_TO_CHAT_ID


@dataclass
class MigrateFromGroup(ServiceMessage):
    migrate_from_chat: Chat

    __pyro_mark__ = MessageServiceType.MIGRATE_FROM_CHAT_ID


@dataclass
class MessagePinned(ServiceMessage):
    # TODO: decide on referring to actual messages table
    pinned_message_id: int

    __pyro_mark__ = MessageServiceType.PINNED_MESSAGE


@dataclass
class GameHighScore(ServiceMessage):
    user: User
    score: int

    # not actual for message
    # position: int None

    __pyro_mark__ = MessageServiceType.GAME_HIGH_SCORE


@dataclass
class VideoChatScheduled(ServiceMessage):
    start_date: dt

    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_SCHEDULED


@dataclass
class VideoChatStarted(ServiceMessage):
    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_STARTED


@dataclass
class VideoChatEnded(ServiceMessage):
    duratioin: int

    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_ENDED


@dataclass
class VideoChatMembersInvited(ServiceMessage):
    video_chat_members_invited: Sequence[User]

    __pyro_mark__ = MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED


@dataclass
class WebAppData(ServiceMessage):
    data: str
    button_text: str

    __pyro_mark__ = MessageServiceType.WEB_APP_DATA


Media_: TypeAlias = (
    Audio | Document | Photo | Sticker | Video | Animation | Voice | VideoNote
    | Contact | Location | LiveLocation | BusinessLocation | Venue | Poll | Quiz | WebPage | Dice | Game
    | StarsGiveaway | SubscriptionsGiveaway | StarsGiveawayWinners | SubscriptionsGiveawayWinners
    | GiveawayCompleted | Story | Invoice | PaidMedia | Checklist
)


@dataclass
class MediaMessage(Message, ABC):
    caption: Text | None
    media: Media_
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
    | pyrogram.GiveawayCompleted
    | pyrogram.Story
    | pyrogram.Invoice
    | pyrogram.PaidMediaInfo
    | pyrogram.Checklist
)


class LocationType(StrEnum):
    USUAL = "USUAL"
    LIVE = "LIVE"
    BUSINESS = "BUSINESS"


T = TypeVar("T")


@dataclass
class TransformError(Exception, ABC):
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


class FromPyrogram:
    async def store_message(self, tg_message: pyrogram.Message) -> BoundMessage:
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
                origin_date=tg_message.forward_date,
                message=payload,
            )

        sender = self.get_message_source(tg_message)

        message: BoundMessage
        if not tg_message.chat:
            raise TransformValueError("Message missing chat info", tg_message)

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

    def from_string(self, string: Str | str) -> Text:
        match string:
            case Str() if string.entities:
                text = self.from_string_with_entities(string=string, tg_entities=string.entities)
            case str():
                text = Text(raw=str(string))
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
        if tg_chat.id is None:
            raise TransformMissingRequiredField("pyrogram.Chat missing value for 'id' field",
                                                tg_chat, 'id')
        if tg_chat.type is None:
            raise TransformMissingRequiredField("pyrogram.Chat missing value for 'type' field",
                                                tg_chat, 'type')

        chat: DialogFull
        match tg_chat.type:
            case ChatType.PRIVATE:
                chat = PrivateChat(
                    tg_id=tg_chat.id,
                    # is_restricted=tg_chat.is_restricted,
                    # is_support=tg_chat.is_support,
                    # is_stories_hidden=tg_chat.is_stories_hidden,
                    # is_stories_unavailable=tg_chat.is_stories_unavailable,
                    # is_business_bot=tg_chat.is_business_bot,
                    # verification_status=tg_chat.verification_status,
                    # username=tg_chat.username,
                    # usernames=tg_chat.usernames,
                    # first_name=tg_chat.first_name,
                    # last_name=tg_chat.last_name,
                    # photo=self.from_chat_photo(tg_chat.photo) if tg_chat.photo else None,
                    # restrictions=self.from_restrictions(tg_channel.restrictions) if tg_channel.restrictions else [],
                    # dc_id=tg_chat.dc_id,
                    # reply_color=tg_chat.reply_color,
                    # profile_color=tg_chat.profile_color,
                    # paid_message_star_count=tg_chat.paid_message_star_count,
                )
            case ChatType.BOT:
                pass
        return Chat(tg_id=tg_chat.id, type=tg_chat.type)

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

        return Channel(
            tg_id=tg_channel.id,
            type=tg_channel.type,
            is_scam=self.from_optional(tg_channel.is_scam),
            is_fake=self.from_optional(tg_channel.is_fake),
            has_protected_content=tg_channel.has_protected_content,
            title=self.from_optional(tg_channel.title),
            is_verified=self.from_optional(tg_channel.is_verified),
            is_restricted=self.from_optional(tg_channel.is_restricted),
            restrictions=self.from_restrictions(tg_channel.restrictions) if tg_channel.restrictions else [],
            description=tg_channel.description,
            photo=self.from_chat_photo(tg_channel.photo) if tg_channel.photo else None,
        )

    def from_chat_photo(self, tg_chat_photo: pyrogram.ChatPhoto) -> ChatPhoto:
        return ChatPhoto(
            small_file_id=tg_chat_photo.small_file_id,
            small_photo_unique_id=tg_chat_photo.small_photo_unique_id,
            big_file_id=tg_chat_photo.big_file_id,
            big_photo_unique_id=tg_chat_photo.big_photo_unique_id,
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
            raise ValueError(f"Can")

        caption = None
        if tg_message.caption is not None:
            caption = self.from_string_with_entities(tg_message.caption, tg_entities=tg_message.caption_entities)

        tg_media: TGMedia
        match tg_message.media:
            case MessageMediaType.AUDIO if tg_message.audio: tg_media = tg_message.audio
            case MessageMediaType.DOCUMENT if tg_message.document: tg_media = tg_message.document
            case MessageMediaType.PHOTO if tg_message.photo: tg_media = tg_message.photo
            case MessageMediaType.STICKER if tg_message.sticker: tg_media = tg_message.sticker
            case MessageMediaType.VIDEO if tg_message.video: tg_media = tg_message.video
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
                raise TransformValueError(f"Can not {tg_message} as service message", tg_message)
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
            case MessageServiceType.NEW_CHAT_TITLE if tg_message.new_chat_title:
                message = NewChatTitle(new_chat_title=tg_message.new_chat_title)
            case MessageServiceType.NEW_CHAT_TITLE:
                raise TransformMissingRequiredField(f"Message missing 'new_chat_title': {tg_message}",
                                                    tg_message, 'new_chat_title')
            case MessageServiceType.NEW_CHAT_PHOTO if tg_message.new_chat_photo:
                message = NewChatPhoto(
                    new_chat_photo=self.from_media(tg_message.new_chat_photo)
                )
            case MessageServiceType.NEW_CHAT_PHOTO:
                raise TransformMissingRequiredField(f"Message missing 'new_chat_photo': {tg_message}",
                                                    tg_message, 'new_chat_photo')
            case MessageServiceType.DELETE_CHAT_PHOTO:
                message = ChatPhotoDeleted()
            case MessageServiceType.GROUP_CHAT_CREATED:
                message = GroupCreated()
            case MessageServiceType.CHANNEL_CHAT_CREATED:
                message = ChannelCreated()
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
            case MessageServiceType.PINNED_MESSAGE:
                raise TransformMissingRequiredField(f"Message missing 'pinned_message': {tg_message}",
                                                    tg_message, 'pinned_message')
            case MessageServiceType.GAME_HIGH_SCORE if tg_message.game_high_score is not None:
                high_score = cast(pyrogram.GameHighScore, tg_message.game_high_score)
                user = self.from_user(high_score.user)
                message = GameHighScore(
                    user=user,
                    score=high_score.score,
                )
            case MessageServiceType.GAME_HIGH_SCORE:
                raise TransformMissingRequiredField(f"Message missing 'game_high_score': {tg_message}",
                                                    tg_message, 'game_high_score')
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
            case MessageServiceType.WEB_APP_DATA if tg_message.web_app_data:
                message = WebAppData(
                    data=tg_message.web_app_data.data,
                    button_text=tg_message.web_app_data.button_text,
                )
            case MessageServiceType.WEB_APP_DATA:
                raise TransformMissingRequiredField(f"Message missing 'web_app_data': {tg_message}",
                                                    tg_message, 'web_app_data')
            case unknown:
                raise ValueError(f"Unknown service message type: {unknown}")

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

    def from_media(self, tg_media: TGMedia | pyrogram.PaidMediaPreview) -> Media_ | PaidMediaPreview:
        media: Media_ | PaidMediaPreview
        match tg_media:
            case pyrogram.Audio() as tg_audio:
                media = Audio(
                    file_id=tg_audio.file_id,
                    file_unique_id=tg_audio.file_unique_id,
                    duration=tg_audio.duration,
                    performer=tg_audio.performer,
                    title=tg_audio.title,
                    file_name=tg_audio.file_name,
                    mime_type=tg_audio.mime_type,
                    file_size=tg_audio.file_size,
                    date=tg_audio.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file_id,
                            file_unique_id=thumb.file_unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file_size,
                        )
                        for thumb in tg_audio.thumbs
                    ],
                )
            case pyrogram.Document() as tg_document:
                media = Document(
                    file_id=tg_document.file_id,
                    file_unique_id=tg_document.file_unique_id,
                    file_name=tg_document.file_name,
                    mime_type=tg_document.mime_type,
                    file_size=tg_document.file_size,
                    date=tg_document.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file_id,
                            file_unique_id=thumb.file_unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file_size,
                        )
                        for thumb in tg_document.thumbs
                    ],
                )
            case pyrogram.Photo() as tg_photo:
                media = Photo(
                    file_id=tg_photo.file_id,
                    file_unique_id=tg_photo.file_unique_id,
                    width=tg_photo.width,
                    height=tg_photo.height,
                    file_size=tg_photo.file_size,
                    date=tg_photo.date,
                    ttl_seconds=tg_photo.ttl_seconds,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file_id,
                            file_unique_id=thumb.file_unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file_size,
                        )
                        for thumb in tg_photo.thumbs
                    ],
                )
            case pyrogram.Sticker() as tg_sticker:
                media = Sticker(
                    file_id=tg_sticker.file_id,
                    file_unique_id=tg_sticker.file_unique_id,
                    width=tg_sticker.width,
                    height=tg_sticker.height,
                    is_animated=tg_sticker.is_animated,
                    is_video=tg_sticker.is_video,
                    file_name=tg_sticker.file_name,
                    mime_type=tg_sticker.mime_type,
                    file_size=tg_sticker.file_size,
                    date=tg_sticker.date,
                    emoji=tg_sticker.emoji,
                    set_name=tg_sticker.set_name,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file_id,
                            file_unique_id=thumb.file_unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file_size,
                        )
                        for thumb in tg_sticker.thumbs
                    ],
                )
            case pyrogram.Animation() as tg_animation:
                media = Animation(
                    file_id=tg_animation.file_id,
                    file_unique_id=tg_animation.file_unique_id,
                    width=tg_animation.width,
                    height=tg_animation.height,
                    duration=tg_animation.duration,
                    file_name=tg_animation.file_name,
                    mime_type=tg_animation.mime_type,
                    file_size=tg_animation.file_size,
                    date=tg_animation.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file_id,
                            file_unique_id=thumb.file_unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file_size,
                        )
                        for thumb in tg_animation.thumbs
                    ],
                )
            case pyrogram.Video() as tg_video:
                media = Video(
                    file_id=tg_video.file_id,
                    file_unique_id=tg_video.file_unique_id,
                    width=tg_video.width,
                    height=tg_video.height,
                    duration=tg_video.duration,
                    file_name=tg_video.file_name,
                    mime_type=tg_video.mime_type,
                    file_size=tg_video.file_size,
                    supports_streaming=tg_video.supports_streaming,
                    ttl_seconds=tg_video.ttl_seconds,
                    date=tg_video.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file_id,
                            file_unique_id=thumb.file_unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file_size,
                        )
                        for thumb in (tg_video.thumbs or ())
                    ],
                )
            case pyrogram.Voice() as tg_voice:
                media = Voice(
                    file_id=tg_voice.file_id,
                    file_unique_id=tg_voice.file_unique_id,
                    duration=tg_voice.duration,
                    waveform=tg_voice.waveform,
                    mime_type=tg_voice.mime_type,
                    file_size=tg_voice.file_size,
                    date=tg_voice.date
                )
            case pyrogram.VideoNote() as tg_video_note:
                media = VideoNote(
                    file_id=tg_video_note.file_id,
                    file_unique_id=tg_video_note.file_unique_id,
                    length=tg_video_note.length,
                    duration=tg_video_note.duration,
                    mime_type=tg_video_note.mime_type,
                    file_size=tg_video_note.file_size,
                    date=tg_video_note.date,
                    thumbs=[
                        Thumbnail(
                            file_id=thumb.file_id,
                            file_unique_id=thumb.file_unique_id,
                            width=thumb.width,
                            height=thumb.height,
                            file_size=thumb.file_size,
                        )
                        for thumb in tg_video_note.thumbs
                    ],
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
                tg_webpage_raw = tg_webpage.raw.webpage  # type: ignore
                if isinstance(tg_webpage_raw, pyrogram_raw.web_page_empty.WebPageEmpty):
                    media = WebPageEmpty(tg_id=tg_webpage.id)
                elif isinstance(tg_webpage_raw, pyrogram_raw.web_page_pending.WebPagePending):
                    media = WebPagePending(tg_id=tg_webpage.id)
                else:
                    media = WebPageDetails(
                        tg_id=tg_webpage.id,
                        url=tg_webpage.url,
                        display_url=cast(str, tg_webpage.display_url),
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
                        channels=[
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
                        channels=[
                            self.from_channel(tg_chat) for tg_chat in tg_giveaway.chats
                        ] if tg_giveaway.chats else None,
                        until_date=tg_giveaway.until_date,
                        description=tg_giveaway.description,
                        only_new_subscribers=tg_giveaway.only_new_subscribers,
                        only_for_countries=tg_giveaway.only_for_countries,
                        winners_are_visible=tg_giveaway.winners_are_visible,
                    )
                else:
                    raise ValueError
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
                    stars_amount=tg_paid_media.stars_amount,
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
                    tasks=[],
                    others_can_add_tasks=tg_checklist.others_can_add_tasks,
                    can_add_tasks=tg_checklist.can_add_tasks,
                    others_can_mark_tasks_as_done=tg_checklist.others_can_mark_tasks_as_done,
                    can_mark_tasks_as_done=tg_checklist.can_mark_tasks_as_done,
                )
            case wtf:
                raise TypeError(f"Unknown media type: {type(wtf)}")

        return media

    @overload
    def from_location(
        self, tg_location: pyrogram.Location, *, type: Literal[LocationType.USUAL]
    ) -> Location: pass
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

    def from_optional(self, value: T | None, description: str | None = None) -> T:
        if value is None:
            raise TransformValueError()
        return value
