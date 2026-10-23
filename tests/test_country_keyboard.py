"""Tests for the paginated country-selection keyboard."""

from trend_finder.countries import COUNTRIES
from trend_finder.keyboards import COUNTRY_PAGE_SIZE, country_keyboard, country_page_count


def test_country_keyboard_pages_contain_each_country_once() -> None:
    """Every supported country is reachable from exactly one page."""
    country_callbacks: list[str] = []
    for page in range(country_page_count()):
        keyboard = country_keyboard(page)
        country_callbacks.extend(
            button.callback_data or ""
            for row in keyboard.inline_keyboard
            for button in row
            if (button.callback_data or "").startswith("country:")
        )

    assert len(country_callbacks) == len(COUNTRIES)
    assert {value.partition(":")[2] for value in country_callbacks} == set(COUNTRIES)


def test_country_keyboard_has_bounded_pages_and_navigation() -> None:
    """Each page stays compact and navigation points to adjacent pages."""
    first_page = country_keyboard(0)
    last_page_index = country_page_count() - 1
    last_page = country_keyboard(last_page_index)

    first_country_buttons = [
        button
        for row in first_page.inline_keyboard
        for button in row
        if (button.callback_data or "").startswith("country:")
    ]
    last_navigation = [
        button.callback_data
        for button in last_page.inline_keyboard[-1]
        if (button.callback_data or "").startswith("country_page:")
    ]

    assert len(first_country_buttons) == COUNTRY_PAGE_SIZE
    assert len(last_page.inline_keyboard[-1]) == 2
    assert last_navigation == [
        f"country_page:{last_page_index}:{last_page_index - 1}",
        f"country_page:{last_page_index}:{last_page_index}",
    ]


def test_country_keyboard_clamps_out_of_range_page() -> None:
    """Invalid page indexes do not generate an empty selector."""
    assert country_keyboard(-10) == country_keyboard(0)
    assert country_keyboard(10_000) == country_keyboard(country_page_count() - 1)
