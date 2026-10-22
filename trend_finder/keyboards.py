"""Inline keyboards for country and provider selection."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from trend_finder.countries import COUNTRIES
from trend_finder.sources import SOURCES


def country_keyboard() -> InlineKeyboardMarkup:
    """Build a compact keyboard containing supported country choices."""
    rows: list[list[InlineKeyboardButton]] = []
    buttons = [
        InlineKeyboardButton(text=f"{name} ({code})", callback_data=f"country:{code}")
        for code, name in COUNTRIES.items()
    ]
    for index in range(0, len(buttons), 2):
        rows.append(buttons[index : index + 2])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def source_keyboard() -> InlineKeyboardMarkup:
    """Build a provider keyboard from the registered source adapters."""
    rows = [
        [InlineKeyboardButton(text=source.label, callback_data=f"source:{key}")]
        for key, source in SOURCES.items()
    ]
    rows.append([InlineKeyboardButton(text="تغییر کشور", callback_data="choose_country")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
