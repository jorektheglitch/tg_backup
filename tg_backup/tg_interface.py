from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator, Callable, Mapping
from logging import Logger, getLogger
from operator import attrgetter

from pyrogram.client import Client
from pyrogram.enums import ChatType
from pyrogram.errors import UserIdInvalid, FloodWait
from pyrogram.types import Chat, Dialog, Message
from pyrogram.types import User
from pyrogram.types import Photo, Animation
from tqdm.asyncio import tqdm

from tg_backup.utils.batching import batched


logger = getLogger(__name__)


class TG:
    def __init__(self, client: Client, logger: Logger = logger) -> None:
        self._client = client
        self._logger = logger
        self.track = True
        self.backoff_time = 30

    async def get_chats(self) -> list[Chat]:
        self._logger.info("Start grabbbing chats.")

        dialogs_iter: AsyncIterator[Dialog] = self._client.get_dialogs()  # type: ignore
        if self.track:
            dialogs_count = await self._client.get_dialogs_count()
            dialogs_iter = tqdm(dialogs_iter, desc="Fetching chats list", total=dialogs_count, unit="ob")

        dialogs: list[Dialog] = [
            dialog
            async for dialog in dialogs_iter
        ]

        chats = [dialog.chat for dialog in dialogs if dialog]
        return chats

        chats_by_type: dict[ChatType, list[Chat]] = {type: [] for type in ChatType}
        for chat in chats:
            chats_by_type[chat.type].append(chat)

        self._logger.info("Collected chats info stats:\n  %s",
                          "\n  ".join(f"{type.name.lower()}: {len(items)}" for type, items in chats_by_type.items()),
                          )
        return chats

    async def get_chat_avatars(self, chat: Chat) -> list[Photo | Animation] | None:
        avatars: list[Photo | Animation] | None = None

        retry = True
        while retry:
            retry = False

            try:
                avatars = [
                    avatar async for avatar in
                    self._client.get_chat_photos(chat.id)  # type: ignore
                ]
            except UserIdInvalid:
                self._logger.warning("Failed to get chat avatars (UserIdInvalid).")
                return None
            except FloodWait as flood:
                retry = True
                self._logger.warning("Got floodwait from Telegram", exc_info=flood)
                await asyncio.sleep(self.backoff_time)

        return avatars

    async def get_chat_messages(self, chat: Chat) -> AsyncIterator[Message]:
        if chat.id is None:
            raise ValueError(f"'id' is None in Chat object {chat}")

        chat_name = get_log_phrase(chat)
        messages_iter: AsyncIterator[Message] = self._client.get_chat_history(
            chat_id=chat.id, reverse=True,
        )
        if self.track:
            self._logger.info(f"Get messages count for {chat_name}")
            messages_count = await self._client.get_chat_history_count(chat.id)
            self._logger.info(f"Got messages count for {chat_name}: {messages_count}")
            messages_iter = tqdm(
                messages_iter,
                desc=f"Grabbing messages from {chat_name}",
                total=messages_count,
                unit="msg"
            )

        async for message in messages_iter:
            if message is None:
                continue
            yield message
            if isinstance(messages_iter, tqdm):
                messages_iter.unpause()

        if isinstance(messages_iter, tqdm):
            messages_iter.close()

        self._logger.info(f"Got all messages from {chat_name}")

    async def get_chat_messages_batches(self, chat: Chat, batch_size: int = 1000) -> AsyncIterator[list[Message]]:
        if chat.id is None:
            raise ValueError(f"'id' is None in Chat object {chat}")

        chat_name = get_log_phrase(chat)
        messages_iter: AsyncIterator[Message] = self._client.get_chat_history(
            chat_id=chat.id, reverse=True,
        )
        if self.track:
            self._logger.info(f"Get messages count for {chat_name}")
            messages_count = await self._client.get_chat_history_count(chat.id)
            self._logger.info(f"Got messages count for {chat_name}: {messages_count}")
            messages_iter = tqdm(
                messages_iter,
                desc=f"Grabbing messages from {chat_name}",
                total=messages_count,
                unit="msg"
            )

        async for batch in batched(messages_iter, batch_size=batch_size):
            clean_batch = [message for message in batch if message is not None]
            yield clean_batch
            if isinstance(messages_iter, tqdm):
                messages_iter.unpause()

        if isinstance(messages_iter, tqdm):
            messages_iter.close()

        self._logger.info(f"Got all messages from {chat_name}")


def get_log_phrase(chat: Chat) -> str:
    qualname = get_qualname(chat)
    match chat.type:
        case ChatType.PRIVATE:
            return f"chat with '{qualname}' (id {chat.id})"
        case ChatType.BOT:
            return f"chat with bot '{qualname}' (id {chat.id})"
        case ChatType.GROUP:
            return f"chat '{qualname}' (id {chat.id})"
        case ChatType.SUPERGROUP:
            return f"superchat '{qualname}' (id {chat.id})"
        case ChatType.CHANNEL:
            return f"channel '{qualname}' (id {chat.id})"
        case ChatType.FORUM:
            return f"forum '{qualname}' (id {chat.id})"
        case ChatType.DIRECT:
            return f"DMs with '{qualname}' (id {chat.id})"
        case _:
            return f"'{qualname}' (id {chat.id})"


def get_qualname(chat: Chat) -> str:
    return _QUALNAME_GETTERS[chat.type](chat)


def _user_chat_qualname(chat: Chat | User) -> str:
    if chat.first_name and chat.last_name:
        return f"{chat.first_name} {chat.last_name}"
    elif chat.first_name:
        return chat.first_name
    else:
        return f"Deleted User #{chat.id}"


_QUALNAME_GETTERS: Mapping[ChatType | None, Callable[[Chat], str]] = {
    ChatType.PRIVATE: _user_chat_qualname,
    ChatType.BOT: _user_chat_qualname,
    ChatType.GROUP: attrgetter('title'),
    ChatType.SUPERGROUP: attrgetter('title'),
    ChatType.CHANNEL: attrgetter('title'),
    ChatType.FORUM: attrgetter('title'),
    ChatType.DIRECT: attrgetter('title'),
}
_QUALNAME_GETTERS = defaultdict(lambda: lambda _: 'unknown', _QUALNAME_GETTERS)
