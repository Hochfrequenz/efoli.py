import warnings
from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest

from efoli import (
    EdifactFormatVersion,
    get_current_edifact_format_version,
    get_edifact_format_version,
    get_edifact_format_version_valid_from,
)
from efoli.edifact_format_version import _format_version_thresholds, _latest_format_version


@pytest.mark.parametrize(
    "key_date,expected_result",
    [
        pytest.param(
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            EdifactFormatVersion.FV2104,
            id="Anything before 2021-04-01 (datetime)",
        ),
        pytest.param(
            date(2021, 1, 1),
            EdifactFormatVersion.FV2104,
            id="Anything before 2021-04-01 (date)",
        ),
        pytest.param(datetime(2021, 5, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2104),
        pytest.param(datetime(2021, 10, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2110),
        pytest.param(datetime(2022, 7, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2110),
        pytest.param(datetime(2022, 10, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2210),
        pytest.param(datetime(2022, 10, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2210),
        pytest.param(datetime(2023, 12, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2310),
        pytest.param(datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2310),
        pytest.param(
            datetime(2024, 4, 1, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2310
        ),  # 2404 is valid form 2024-04-03 onwards
        pytest.param(datetime(2024, 4, 2, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2404),
        pytest.param(datetime(2024, 9, 30, 21, 59, 59, tzinfo=timezone.utc), EdifactFormatVersion.FV2404),
        pytest.param(datetime(2024, 9, 30, 22, 0, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2410),
        pytest.param(datetime(2025, 3, 31, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2410),
        pytest.param(datetime(2025, 4, 3, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2410),
        pytest.param(datetime(2025, 6, 5, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2504),
        pytest.param(date(2025, 4, 3), EdifactFormatVersion.FV2410),
        pytest.param(date(2025, 4, 4), EdifactFormatVersion.FV2410),
        pytest.param(date(2025, 6, 6), EdifactFormatVersion.FV2504),
        pytest.param(datetime(2025, 9, 30, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2510),
        pytest.param(datetime(2025, 10, 1, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2510),
        pytest.param(datetime(2026, 3, 31, 21, 59, 59, tzinfo=timezone.utc), EdifactFormatVersion.FV2510),
        pytest.param(datetime(2026, 3, 31, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2604),
        pytest.param(datetime(2026, 9, 30, 22, 0, 0, tzinfo=timezone.utc), EdifactFormatVersion.FV2610),
    ],
)
def test_format_version_from_keydate(key_date: datetime, expected_result: EdifactFormatVersion) -> None:
    actual = get_edifact_format_version(key_date)
    assert actual == expected_result


def test_key_date_beyond_last_threshold_returns_newest_format_version() -> None:
    """Dates beyond the last known threshold saturate to the newest format version.

    Deliberately expressed via list(EdifactFormatVersion)[-1] instead of a literal: with a literal
    this assertion keeps passing after a new format version is added, while
    get_edifact_format_version would then wrongly return the second newest version for all
    future dates.
    """
    newest_format_version = list(EdifactFormatVersion)[-1]
    assert get_edifact_format_version(datetime(2050, 10, 1, 0, 0, 0, tzinfo=timezone.utc)) == newest_format_version
    assert get_edifact_format_version(date(2050, 10, 1)) == newest_format_version


def test_key_date_beyond_last_threshold_reads_the_derived_value() -> None:
    """get_edifact_format_version has to *read* _latest_format_version, not repeat its current value.

    Without this test, replacing the return value with the literal that _latest_format_version happens
    to equal today passes every other test, and the bug only surfaces one format version later - which
    is exactly the failure mode this module is supposed to prevent.
    """
    not_the_newest_version = next(iter(EdifactFormatVersion))
    far_future = datetime(2050, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    with patch("efoli.edifact_format_version._latest_format_version", not_the_newest_version):
        assert get_edifact_format_version(far_future) is not_the_newest_version


def test_get_current_format_version() -> None:
    actual = get_current_edifact_format_version()
    assert isinstance(actual, EdifactFormatVersion) is True


def test_get_current_format_version_is_free_of_deprecation_warnings() -> None:
    """pins the timezone aware datetime.now(utc); datetime.utcnow() is deprecated since 3.12

    Only bites on Python 3.12+, where utcnow() started warning; on the 3.9-3.11 legs of the CI
    matrix this passes either way.
    """
    with warnings.catch_warnings(record=True) as caught_warnings:
        # "always" never consults the per-module warning registry, so this neither depends on nor
        # manipulates whether an earlier test already triggered the same warning
        warnings.simplefilter("always")
        assert isinstance(get_current_edifact_format_version(), EdifactFormatVersion)
    assert [w for w in caught_warnings if issubclass(w.category, DeprecationWarning)] == []


def test_str_representation() -> None:
    assert str(EdifactFormatVersion.FV2504) == "FV2504"


@pytest.mark.parametrize(
    "version,expected_date",
    [
        pytest.param(EdifactFormatVersion.FV2110, date(2021, 10, 1), id="FV2110"),
        pytest.param(EdifactFormatVersion.FV2210, date(2022, 10, 1), id="FV2210"),
        pytest.param(EdifactFormatVersion.FV2304, date(2023, 4, 1), id="FV2304"),
        pytest.param(EdifactFormatVersion.FV2310, date(2023, 10, 1), id="FV2310"),
        pytest.param(EdifactFormatVersion.FV2404, date(2024, 4, 3), id="FV2404"),
        pytest.param(EdifactFormatVersion.FV2410, date(2024, 10, 1), id="FV2410"),
        pytest.param(EdifactFormatVersion.FV2504, date(2025, 6, 6), id="FV2504"),
        pytest.param(EdifactFormatVersion.FV2510, date(2025, 10, 1), id="FV2510"),
        pytest.param(EdifactFormatVersion.FV2604, date(2026, 4, 1), id="FV2604"),
        pytest.param(EdifactFormatVersion.FV2610, date(2026, 10, 1), id="FV2610"),
    ],
)
def test_format_version_valid_from(version: EdifactFormatVersion, expected_date: date) -> None:
    actual = get_edifact_format_version_valid_from(version)
    assert actual == expected_date


def test_format_version_valid_from_unknown_raises() -> None:
    with pytest.raises(KeyError):
        get_edifact_format_version_valid_from(EdifactFormatVersion.FV2104)


def test_format_versions_are_declared_in_chronological_order() -> None:
    """The enum's declaration order has to match the chronological order.

    Both _latest_format_version (the last member) and _build_valid_from_map rely on it.
    """
    valid_from_dates = []
    for fv in list(EdifactFormatVersion)[1:]:  # FV2104 has no known start date
        try:
            valid_from_dates.append(get_edifact_format_version_valid_from(fv))
        except KeyError:
            # a missing start date is reported by test_all_format_versions_except_first_have_valid_from;
            # swallowing it here keeps this test's failure about the *order*, as its name promises
            continue
    assert valid_from_dates == sorted(valid_from_dates)
    assert len(set(valid_from_dates)) == len(valid_from_dates), "two format versions share a start date"


def test_thresholds_are_in_chronological_order() -> None:
    """get_edifact_format_version returns the first threshold the key date falls below.

    That is only the *closest* threshold if the list is ordered, so the order is part of the
    contract. _format_version_thresholds is sorted at its point of definition; this fails if that
    sorting is removed and an entry is written out of order.
    """
    threshold_dates = [threshold_date for threshold_date, _ in _format_version_thresholds]
    assert threshold_dates == sorted(threshold_dates)
    assert len(set(threshold_dates)) == len(threshold_dates), "two format versions share a threshold"


def test_latest_format_version_is_the_newest_enum_member() -> None:
    """The newest format version must be the only member without an upper threshold.

    This is the invariant that lets _latest_format_version simply be the last enum member. It fails
    if a format version is added to the enum without giving its predecessor a threshold, or if a
    threshold is added for the newest version without adding its successor to the enum.
    """
    bounded_versions = {version for _, version in _format_version_thresholds}
    assert _latest_format_version not in bounded_versions
    assert bounded_versions == set(EdifactFormatVersion) - {_latest_format_version}


def test_all_format_versions_except_first_have_valid_from() -> None:
    """Every FV except the very first (FV2104) must have a known start date.
    This test fails if a new FV is added to the enum but not to the thresholds list."""
    all_fvs = list(EdifactFormatVersion)
    first_fv = all_fvs[0]
    for fv in all_fvs[1:]:
        result = get_edifact_format_version_valid_from(fv)
        assert isinstance(result, date), f"{fv} should have a valid_from date"
    # First FV has no start date
    with pytest.raises(KeyError):
        get_edifact_format_version_valid_from(first_fv)
