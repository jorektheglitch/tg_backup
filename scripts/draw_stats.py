from dataclasses import dataclass
from itertools import pairwise
from datetime import (datetime as dt, timedelta as td)
from pathlib import Path
from pyrogram.client import Client
from typing import TypeAlias, TypedDict

from adaptix import Retort
from PIL import Image, ImageDraw


UserID: TypeAlias = int

HOUR = td(hours=1)
retort = Retort(strict_coercion=False)


class Stats(TypedDict):
    users: dict[UserID | str, str]
    stats: dict[dt, dict[UserID | str, int]]


@dataclass
class PreparedStats():
    pass


def add_empty_hours(stats: dict[dt, dict[UserID | str, int]]) -> dict[dt, dict[UserID | str, int]]:
    hours = sorted(stats)
    missed: list[dt] = []
    for prev, next in pairwise(hours):
        delta_hours = (next - prev) // HOUR
        if delta_hours == 1:
            continue

        for delta in range(delta_hours):
            missed.append(prev+td(hours=delta+1))

    stats = stats.copy()
    for missed_hour in missed:
        stats[missed_hour] = {}

    stats = dict(sorted(stats.items()))

    return stats


def prepare_stats(data: Stats) -> tuple[Stats, int]:
    overall_stats: dict[UserID | str, int] = {}
    for hour_stats in data["stats"].values():
        for user_id, hour_count in hour_stats.items():
            overall_stats.setdefault(user_id, 0)
            overall_stats[user_id] += hour_count

    users: dict[UserID | str, str] = {
        user_id: data["users"][user_id] if isinstance(user_id, int) else user_id
        for user_id, count in overall_stats.items()
        if count > 100
    }

    stats = add_empty_hours(data["stats"])
    return {"users": users, "stats": stats}, sum(overall_stats[user_id] for user_id in users)


def draw(data: Stats, image_path: Path) -> None:
    data, total_messages = prepare_stats(data)
    users = data["users"]
    stats = data["stats"]
    rows: list[dict[str, int]] = []
    row = dict.fromkeys(users.values(), 0)
    for _, hour_stats in stats.items():
        row = row.copy()
        for user_id, count in hour_stats.items():
            name = users.get(user_id)
            if name is None:
                continue
            row[name] += count
        rows.append(row)

    ROW_LEN = len(users)
    COLORS: dict[str, tuple[int, int, int]] = {
        users[user_id]: color_by_n(idx, ROW_LEN) for idx, user_id in enumerate(users)
    }
    # for name, (r, g, b) in COLORS.items():
    #    print(f"#{r:02X}{g:02X}{b:02X} - {name}")

    width = len(stats)
    height = (total_messages // 100)+1
    image = Image.new("RGBA", (width, height), color=(255, 255, 255, 255))

    draw = ImageDraw.ImageDraw(image, mode="RGBA")
    for row_idx, row in enumerate(rows):
        y = height*100
        for name, count in row.items():
            if not count:
                continue
            color = COLORS[name]
            end_y = y - count
            draw.line((row_idx, y // 100, row_idx, end_y // 100), fill=color, width=1)
            y = end_y

    days_borders_idxs = []
    weeks_borseds_idxs = []
    month_borders_idxs = []
    for idx, datetime in enumerate(stats.keys()):
        if datetime.hour != 0:
            continue

        days_borders_idxs.append(idx)

        if datetime.weekday() == 0:
            weeks_borseds_idxs.append(idx)

        if datetime.day == 1:
            month_borders_idxs.append(idx)

    tenths_thousands_borders_idxs = [idx for idx in range(0, height, 100)]

    measures_net = Image.new("RGBA", size=(width, height), color=(0, 0, 0, 0))
    measures_draw = ImageDraw.ImageDraw(measures_net, mode="RGBA")

    for day_border_idx in days_borders_idxs:
        measures_draw.line((day_border_idx, 0, day_border_idx, height), fill=(224, 224, 224, 192), width=1)
    for week_border_idx in weeks_borseds_idxs:
        measures_draw.line((week_border_idx, 0, week_border_idx, height), fill=(176, 176, 176, 192), width=1)
    for month_border_idx in month_borders_idxs:
        measures_draw.line((month_border_idx, 0, month_border_idx, height), fill=(128, 128, 128, 192), width=2)

    for tenth_thousands_border_idx in tenths_thousands_borders_idxs:
        measures_draw.line((0, tenth_thousands_border_idx, width, tenth_thousands_border_idx), fill=(128, 128, 128, 192), width=1)

    image.alpha_composite(measures_net)

    image.save(image_path)


def color_by_n(index: int, total_colors: int) -> tuple[int, int, int]:
    norm = round((index / total_colors) * 0x5F9)
    hexant, intensity = divmod(norm, 255)
    match hexant:
        case 0:
            color = (255,           intensity,     0)
        case 1:
            color = (255-intensity, 255,           0)
        case 2:
            color = (0,             255,           intensity)
        case 3:
            color = (0,             255-intensity, 255)
        case 4:
            color = (intensity,     0,             255)
        case 5:
            color = (255,           0,             255-intensity)

    return color


async def main(client: Client):
    from collections.abc import AsyncIterator

    from pyrogram.types import Message, Chat, User

    from tg_backup.tg_interface import get_qualname

    chat: Chat
    messages_iter: AsyncIterator[Message] = client.get_chat_history(
        chat_id=chat.id,
    )

    by_hour: dict[str, dict[int | str, list[Message]]] = {}
    users: dict[int, User] = {}

    async for message in messages_iter:
        author_id: int | str = message.from_user.id if message.from_user else message.author_signature
        by_hour.setdefault(message.date.strftime("%Y-%m-%d_%H"), {}).setdefault(author_id, []).append(message)
        if message.from_user is not None:
            users.setdefault(message.from_user.id, message.from_user)

    stats: dict[str, dict[int | str, int]] = {
        day: {user: len(messages) for user, messages in users_messages.items()}
        for day, users_messages in by_hour.items()
    }
    stats_raw = dict(
        users={id: get_qualname(user) for id, user in users.items()},
        stats={hour: hour_stats for hour, hour_stats in sorted(stats.items())}
    )

    stats = retort.load(stats_raw, Stats)
    stats_image = Path() / "stats.png"
    draw(stats, stats_image)
