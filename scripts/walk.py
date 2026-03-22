from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from collections.abc import AsyncIterator, Iterable, Iterator, Mapping
from concurrent.futures import Executor, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime as dt
from functools import cached_property
from logging import getLogger, Logger
from pathlib import Path
from urllib.parse import quote
from typing import ContextManager, NamedTuple, TypeAlias, cast

from pyrogram.client import Client
from pyrogram.enums import ChatType
from pyrogram.errors import UserIdInvalid, FloodWait, ChannelPrivate
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES
from pyrogram.types import Chat
from pyrogram.types import Audio, Document, Photo, Sticker, Animation, Video, Voice, VideoNote
from pyrogram.types import Message
from pyrogram.types.object import Object

from tg_backup.tg_interface import get_qualname
from tg_backup.utils.json_streaming import JSONListWriter, list_writer


TGMedia: TypeAlias = Audio | Document | Photo | Sticker | Animation | Video | Voice | VideoNote

IMAGE_EXTS = {type: ".jpg" for type in PHOTO_TYPES}
ANIMATED_EXTS = {
    type: ".mp4" for type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE)
}
DEFAULT_EXTS = defaultdict(lambda: ".unknown", {
    **IMAGE_EXTS,
    **ANIMATED_EXTS,
    FileType.VOICE: ".ogg",
    FileType.STICKER: ".webp",
    FileType.AUDIO: ".mp3",
})

WINDOWS_FORBIDDEN_NAMES = {
    "CON", "PRN", "AUX", "NUL"
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}
WINDOWS_ESCAPING_SCHEMA: Mapping[str, str] = {"%": quote("%", safe='')}  # % is escaping symbol
WINDOWS_FILENAME_FORBIDDEN_CHARS = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
WINDOWS_FILENAME_FORBIDDEN_CHARS.extend(chr(no) for no in range(32))  # ASCII control chars are forbidden too
for char in WINDOWS_FILENAME_FORBIDDEN_CHARS:
    cast(dict[str, str], WINDOWS_ESCAPING_SCHEMA)[char] = quote(char, safe='')


logger: Logger = getLogger(__name__)


class ChatBrief(NamedTuple):
    type: ChatType
    username: str | None
    qualname: str
    id: int

    @classmethod
    def from_chat(cls, chat: Chat) -> ChatBrief:
        if chat.type is None:
            raise ValueError()
        if chat.id is None:
            raise ValueError()

        qualname = get_qualname(chat)
        info = ChatBrief(type=chat.type, username=chat.username, qualname=qualname, id=chat.id)
        return info


@dataclass(frozen=True)
class MediaFileInfo:
    raw_file_id: str | FileId
    file_name: str
    file_size: int | None

    @cached_property
    def file_id(self) -> FileId:
        if isinstance(self.raw_file_id, FileId):
            return self.raw_file_id
        return FileId.decode(self.raw_file_id)

    @property
    def file_type(self) -> FileType:
        return self.file_id.file_type

    @classmethod
    def from_media(cls, media: TGMedia, client: Client | None = None) -> MediaFileInfo | None:
        if (client, media._client) == (None, None):
            raise RuntimeError("Can't get media info - client is None")
        if client is None:
            client = media._client

        for attrname in ('big_file_id', 'file_id'):
            file_id = getattr(media, attrname, None)
            if file_id is not None:
                break

        if not isinstance(file_id, str):
            logger.warning("Non-string file_id or big_file_id in %s", type(media).__name__)
            return None

        file_info = FileId.decode(file_id)
        if file_info is None:
            logger.warning("Can't decode file id %s (%s) ", file_id, type(media).__name__)
            return None

        file_type = file_info.file_type
        file_name = getattr(media, "file_name", "")
        file_size = getattr(media, "file_size", 0)
        mime_type = getattr(media, "mime_type", "")
        date = getattr(media, "date", None)

        if not file_name:
            guessed_extension = client.guess_extension(mime_type)
            default_extension = DEFAULT_EXTS[file_type]
            extension = guessed_extension or default_extension
            file_name = (
                f"{file_type.name.lower()}"
                f"_{date or dt.now().strftime('%Y-%m-%d_%H-%M-%S')}"
                f".{extension}"
            )
        if isinstance(media, Sticker):
            file_name = f"sticker_{media.set_name}_{media.emoji}_{media.file_unique_id}.webp"

        name, ext = file_name.rsplit(".", maxsplit=1) if "." in file_name else (file_name, "unknown")
        uniq_id = getattr(media, "file_unique_id", None)
        file_name = f"{name}_{uniq_id}.{ext}"

        return MediaFileInfo(file_info, file_name, file_size)


def tgobject_list_writer(
    fp,
    indent: int | str | None = 2,
    executor: Executor | None = None
) -> ContextManager[JSONListWriter]:
    return list_writer(fp=fp, indent=indent, default=Object.default, ensure_ascii=False, executor=executor)


def get_media(source: Message) -> TGMedia | None:
    media: TGMedia | None = (
        source.animation or source.audio or source.document or source.new_chat_photo or source.photo or
        source.sticker or source.video or source.video_note or source.voice
    )
    if media is None:
        return None
    return media


async def get_chat_avatars(client: Client, chat_id: int) -> list[Photo] | None:
    retry = True
    while retry:
        retry = False
        try:
            avatars: list[Photo] | None = [
                avatar async for avatar in
                client.get_chat_photos(chat_id)  # type: ignore  # FUCK TYPEHINTS IN PYROGRAM'S METHODS!
            ]
        except UserIdInvalid:
            logger.warning("Failed to get chat avatars.")
            avatars = None
        except FloodWait as flood:
            logger.warning("Got floodwait from Telegram", exc_info=flood)
            retry = True
            await asyncio.sleep(30)
    return avatars


def windows_escape_filename(name: str) -> str:
    if name in WINDOWS_FORBIDDEN_NAMES:
        raise ValueError(f"Forbidden name '{name}'")
    escaped = "".join(WINDOWS_ESCAPING_SCHEMA.get(char, char) for char in name)
    return escaped


async def download_medias(client: Client, media_infos: Iterable[MediaFileInfo], target_directory: Path) -> None:
    unknown_files_directory = target_directory / "unknown files"
    media_types_directories: Mapping[FileType, Path] = defaultdict(lambda: unknown_files_directory, {
        file_type: target_directory / f"{file_type.name}s".lower().replace('_', ' ')
        for file_type in FileType
    })
    # unknown_files_directory.mkdir(exist_ok=True)
    # for directory in media_types_directories.values():
    #    directory.mkdir(exist_ok=True)

    for media_info in media_infos:
        directory = media_types_directories.get(media_info.file_type, unknown_files_directory)
        directory.mkdir(exist_ok=True)
        await download_media(client, media_info, directory)


async def download_media(client: Client, media_info: MediaFileInfo, target_directory: Path) -> None:
    file_name = windows_escape_filename(media_info.file_name)
    if (target_directory / file_name).exists():
        logger.info(f"Skip already existed {target_directory.as_posix()}/{file_name}")
    logger.info(f"Start downloading {target_directory.as_posix()}/{file_name}")
    await client.handle_download(
        (media_info.file_id, target_directory, file_name, False, media_info.file_size, None, ())
    )
    logger.info(f"Complete {target_directory.as_posix()}/{file_name}")


async def walk(client: Client, start_channel: Chat, export_dir: Path) -> None:
    known_channels: dict[int, Chat] = {}

    queue: deque[Chat] = deque()
    queue.append(start_channel)

    with ThreadPoolExecutor() as executor:
        while queue:
            channel: Chat = queue.pop()
            new_channels = await step(client=client, channel=channel, export_dir=export_dir, executor=executor)

            for channel in new_channels:
                logger.info("Found referred channel: %s", ChatBrief.from_chat(channel).qualname)
                if channel.id in known_channels:
                    continue

                logger.info("Add new channel in queue: %s", ChatBrief.from_chat(channel).qualname)
                known_channels[channel.id] = channel
                queue.append(channel)

            logger.info("Queue length is %s", len(queue))


def referred_channels(messages: Iterable[Message]) -> Iterator[Chat]:
    for message in messages:
        #if not message.forward_from:
        #    continue
        if not message.forward_from_chat:
            continue
        if not message.forward_from_message_id:
            continue
        yield message.forward_from_chat


async def step(client: Client, channel: Chat, export_dir: Path, executor: Executor) -> Iterable[Chat]:
    channel_brief = ChatBrief.from_chat(channel)
    logger.info("Process channel %s", channel_brief.qualname)

    channel_dir = export_dir / f"{channel.id} {windows_escape_filename(channel_brief.qualname)}"
    channel_avatars_dir = channel_dir / "avatars"
    channnel_medias_dir = channel_dir / "medias"
    messages_json: Path = channel_dir / "messages.json"
    medias_json: Path = channel_dir / "medias.json"
    try:
        channel_dir.mkdir(exist_ok=True)
    except OSError as e:
        logger.warning("Can not create directory for '%s', skipping...", channel_brief.qualname, exc_info=e)
        return []

    try:
        channnel_medias_dir.mkdir(exist_ok=True)
        channel_avatars_dir.mkdir(exist_ok=True)
    except OSError as e:
        logger.warning("Can not create subdirs for '%s', skipping...", channel_brief.qualname, exc_info=e)
        return []

    messages_to_load = 100 if channel.id != -1001961354253 else 200
    messages_aiter: AsyncIterator[Message] = client.get_chat_history(chat_id=channel.id, limit=messages_to_load)
    try:
        messages: list[Message] = [message async for message in messages_aiter]
    except ChannelPrivate:
        logger.info("Private channel '%s', skipping...", channel_brief.qualname)
        return []

    with (
        messages_json.open("w", encoding="utf-8") as messages_file,
        tgobject_list_writer(messages_file, executor=executor) as messages_writer,
    ):
        messages_writer.write_items(messages)

    avatars = await get_chat_avatars(client, chat_id=channel.id)
    avatars_infos = [media_info for media_info in executor.map(MediaFileInfo.from_media, avatars) if media_info if not None]
    for avatar_info in avatars_infos:
        await download_media(client, avatar_info, channel_avatars_dir)

    medias = [media for media in executor.map(get_media, messages) if media is not None]
    with (
        medias_json.open("w", encoding="utf-8") as medias_file,
        tgobject_list_writer(medias_file, executor=executor) as medias_writer
    ):
        medias_writer.write_items(medias)

    # media_infos = [media_info for media_info in executor.map(MediaFileInfo.from_media, medias) if media_info if not None]
    # await download_medias(client=client, media_infos=media_infos, target_directory=channnel_medias_dir)

    return referred_channels(messages)


async def main(client: Client):
    START_CHAT_ID: int = 0

    start_time = dt.now()

    await client.start()

    start_channel: Chat = await client.get_chat(chat_id=START_CHAT_ID)

    export_dir = Path.cwd() / "tmp" / "walks" / start_time.strftime('%Y-%m-%d_%H-%M-%S')
    export_dir.mkdir(exist_ok=True, parents=True)
    logger.info("Walking and writing to %s", export_dir.absolute())
    await walk(client=client, start_channel=start_channel, export_dir=export_dir)
