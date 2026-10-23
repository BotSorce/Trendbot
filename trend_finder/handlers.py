"""Telegram command and callback handlers."""

from html import escape
from typing import cast

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from trend_finder.countries import COUNTRIES
from trend_finder.domain import TrendItem
from trend_finder.keyboards import country_keyboard, country_page_count, source_keyboard
from trend_finder.services.trend_service import TrendService
from trend_finder.sources import SOURCES
from trend_finder.sources.types import TrendSourceError

router = Router(name="trend-finder")


def render_trends(items: list[TrendItem], source_label: str, country_name: str) -> str:
    """Render a concise Persian list using escaped text and validated HTTP links."""
    lines = [f"<b>{escape(source_label)} — {escape(country_name)}</b>", ""]
    if items and items[0].source == "reddit":
        lines.extend(
            [
                (
                    "<i>این فهرست محبوبیت جامعه است؛ فیلتر منطقه ممکن است "
                    "از سوی Reddit اعمال نشود.</i>"
                ),
                "",
            ]
        )
    for item in items[:10]:
        title = escape(item.title)
        if item.url.startswith(("https://", "http://")):
            title = f'<a href="{escape(item.url, quote=True)}">{title}</a>'
        lines.append(f"<b>{item.position}.</b> {title}")
        if item.metric:
            lines.append(f"<i>{escape(item.metric)}</i>")
        if item.summary:
            summary = escape(" ".join(item.summary.split())[:180])
            if summary:
                lines.append(summary)
        lines.append("")
    lines.append("برای دریافت دادهٔ تازه، دوباره /trends را انتخاب کنید.")
    return "\n".join(lines)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """Welcome the user and begin the country selection flow."""
    await state.clear()
    await message.answer(
        "سلام. برای دیدن ترندها، ابتدا کشور را انتخاب کنید:",
        reply_markup=country_keyboard(),
    )


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Explain the available commands and how source results are labeled."""
    await message.answer(
        "برای دریافت ترندها از /trends استفاده کنید.\n"
        "منابع فعلی: Google Trends و محبوب‌ترین گفتگوهای Reddit.\n"
        "Reddit سیگنال محبوبیت جامعه است، نه حجم جست‌وجو؛ "
        "فیلتر منطقه هم ممکن است نادیده گرفته شود."
    )


@router.message(Command("trends"))
async def trends_handler(message: Message, state: FSMContext) -> None:
    """Start a new country and source selection."""
    await state.clear()
    await message.answer("کشور موردنظر را انتخاب کنید:", reply_markup=country_keyboard())


@router.callback_query(F.data == "choose_country")
async def choose_country_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to country selection."""
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer("کشور را انتخاب کنید:", reply_markup=country_keyboard())


@router.callback_query(F.data.startswith("country_page:"))
async def country_page_handler(callback: CallbackQuery) -> None:
    """Move between pages in the country selector."""
    try:
        _, current_raw, target_raw = str(callback.data).split(":", maxsplit=2)
        current_page = int(current_raw)
        target_page = int(target_raw)
    except ValueError:
        await callback.answer("صفحه نامعتبر است.", show_alert=True)
        return

    if not 0 <= current_page < country_page_count() or not 0 <= target_page < country_page_count():
        await callback.answer("این صفحه وجود ندارد.", show_alert=True)
        return

    await callback.answer(f"صفحه {target_page + 1} از {country_page_count()}")
    if isinstance(callback.message, Message) and target_page != current_page:
        await callback.message.edit_reply_markup(reply_markup=country_keyboard(target_page))


@router.callback_query(F.data.startswith("country:"))
async def country_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Save the selected country and display available sources."""
    country_code = str(callback.data).partition(":")[2].upper()
    if country_code not in COUNTRIES:
        await callback.answer("کشور پشتیبانی نمی‌شود.", show_alert=True)
        return
    await state.update_data(country_code=country_code)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            f"کشور انتخاب‌شده: {COUNTRIES[country_code]}\nمنبع را انتخاب کنید:",
            reply_markup=source_keyboard(),
        )


@router.callback_query(F.data.startswith("source:"))
async def source_handler(
    callback: CallbackQuery,
    state: FSMContext,
    trend_service: TrendService,
) -> None:
    """Fetch, persist, and display the selected source/country trends."""
    source_key = str(callback.data).partition(":")[2]
    source = SOURCES.get(source_key)
    if source is None:
        await callback.answer("منبع ناشناخته است.", show_alert=True)
        return
    selected = await state.get_data()
    country_code = cast(str | None, selected.get("country_code"))
    if not country_code or country_code not in COUNTRIES:
        await callback.answer("ابتدا کشور را انتخاب کنید.", show_alert=True)
        if callback.message:
            await callback.message.answer("کشور را انتخاب کنید:", reply_markup=country_keyboard())
        return

    await callback.answer("در حال دریافت ترندها…")
    if not callback.message:
        return
    try:
        items = await trend_service.get_trends(source_key, country_code)
    except TrendSourceError as exc:
        await callback.message.answer(escape(str(exc)))
        return
    except Exception:
        from loguru import logger

        logger.exception("Trend request failed for source={} country={}", source_key, country_code)
        await callback.message.answer("دریافت ترندها با خطا روبه‌رو شد. کمی بعد دوباره تلاش کنید.")
        return

    await callback.message.answer(
        render_trends(items, source.label, COUNTRIES[country_code]),
        disable_web_page_preview=True,
    )
