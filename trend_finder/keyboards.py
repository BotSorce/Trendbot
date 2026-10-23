"""Inline keyboards for country and provider selection."""

from math import ceil

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from trend_finder.countries import COUNTRIES
from trend_finder.sources import SOURCES

COUNTRY_PAGE_SIZE = 12


def country_page_count() -> int:
    """Return the number of country-selection pages."""
    return max(1, ceil(len(COUNTRIES) / COUNTRY_PAGE_SIZE))


def country_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Build a paginated keyboard containing supported country choices."""
    page_count = country_page_count()
    page = min(max(page, 0), page_count - 1)
    start = page * COUNTRY_PAGE_SIZE
    country_entries = list(COUNTRIES.items())[start : start + COUNTRY_PAGE_SIZE]
    rows: list[list[InlineKeyboardButton]] = []
    buttons = [
        InlineKeyboardButton(text=f"{name} ({code})", callback_data=f"country:{code}")
        for code, name in country_entries
    ]
    for index in range(0, len(buttons), 2):
        rows.append(buttons[index : index + 2])

    if page_count > 1:
        navigation: list[InlineKeyboardButton] = []
        if page > 0:
            navigation.append(
                InlineKeyboardButton(
                    text="« قبلی",
                    callback_data=f"country_page:{page}:{page - 1}",
                )
            )
        page_label = str(page + 1).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
        count_label = str(page_count).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
        navigation.append(
            InlineKeyboardButton(
                text=f"{page_label}/{count_label}",
                callback_data=f"country_page:{page}:{page}",
            )
        )
        if page < page_count - 1:
            navigation.append(
                InlineKeyboardButton(
                    text="بعدی »",
                    callback_data=f"country_page:{page}:{page + 1}",
                )
            )
        rows.append(navigation)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def source_keyboard() -> InlineKeyboardMarkup:
    """Build a provider keyboard from the registered source adapters."""
    rows = [
        [InlineKeyboardButton(text=source.label, callback_data=f"source:{key}")]
        for key, source in SOURCES.items()
    ]
    rows.append([InlineKeyboardButton(text="تغییر کشور", callback_data="choose_country")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
