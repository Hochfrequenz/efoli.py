"""contains the EdifactFormatVersion enum"""

import datetime
from typing import Union

import pytz

from .strenum import StrEnum

_berlin = pytz.timezone("Europe/Berlin")
_utc = datetime.timezone.utc


class EdifactFormatVersion(StrEnum):
    """
    One format version refers to the period in which an AHB is valid.
    """

    FV2104 = "FV2104"  #: valid from 2021-04-01 until 2021-10-01
    FV2110 = "FV2110"  #: valid from 2021-10-01 until 2022-04-01
    FV2210 = "FV2210"  #: valid from 2022-10-01 onwards ("MaKo 2022", was 2204 previously)
    FV2304 = "FV2304"  #: valid from 2023-04-01 onwards
    FV2310 = "FV2310"  #: valid from 2023-10-01 onwards
    FV2404 = "FV2404"  #: valid from 2024-04-01 onwards
    FV2410 = "FV2410"  #: valid from 2024-10-01 onwards
    FV2504 = "FV2504"  #: valid from 2025-06-06 onwards (was originally planned for 2025-04-04)
    FV2510 = "FV2510"  #: valid from 2025-10-01 onwards
    FV2604 = "FV2604"  #: valid from 2026-04-01 onwards
    FV2610 = "FV2610"  #: valid from 2026-10-01 onwards
    # Whenever you add another value here, add the upper threshold of its *predecessor* to
    # _format_version_thresholds below. The values have to stay in chronological order;
    # test_format_versions_are_declared_in_chronological_order guards that.

    def __str__(self) -> str:
        return self.value


# Maps the exclusive upper threshold (UTC) to the version valid until that threshold.
# When adding a new FV, add a new entry here; the newest version is the one that is intentionally
# absent from this list, because it has no upper threshold (yet).
# Sorted once, here, so that every reader can rely on chronological order: get_edifact_format_version
# returns the first threshold the key date falls below, which is only the *closest* one if the list is
# ordered. Sorting at the single point of definition means a new entry written in the wrong place
# cannot produce wrong format versions.
_format_version_thresholds: list[tuple[datetime.datetime, EdifactFormatVersion]] = sorted(
    [
        (datetime.datetime(2021, 9, 30, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2104),
        (datetime.datetime(2022, 9, 30, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2110),
        (datetime.datetime(2023, 3, 31, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2210),
        (datetime.datetime(2023, 9, 30, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2304),
        (datetime.datetime(2024, 4, 2, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2310),
        (datetime.datetime(2024, 9, 30, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2404),
        (datetime.datetime(2025, 6, 5, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2410),
        (datetime.datetime(2025, 9, 30, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2504),
        (datetime.datetime(2026, 3, 31, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2510),
        (datetime.datetime(2026, 9, 30, 22, 0, 0, 0, tzinfo=_utc), EdifactFormatVersion.FV2604),
    ],
    key=lambda threshold: threshold[0],
)


# The newest format version: the only member without an upper threshold in
# _format_version_thresholds, because nobody knows yet when it will be superseded. Derived from the
# enum instead of hardcoded, so that adding a format version stays a single edit. A hardcoded value
# silently makes get_edifact_format_version return the *previous* version for every date beyond the
# last threshold. test_latest_format_version_is_the_newest_enum_member pins the relationship between
# the enum and the thresholds list, so a mismatch fails one named test instead of breaking `import
# efoli` for everyone.
_latest_format_version = list(EdifactFormatVersion)[-1]


def _build_valid_from_map() -> dict[EdifactFormatVersion, datetime.date]:
    """Derive inclusive start dates from the thresholds list.

    Each threshold is the exclusive upper bound of a version — meaning the NEXT version
    starts at that threshold. Converting to Europe/Berlin gives the local inclusive start date.
    _format_version_thresholds is sorted at its point of definition, so no local sorting here.
    """
    result: dict[EdifactFormatVersion, datetime.date] = {}
    versions_in_order = [version for _, version in _format_version_thresholds]
    # For each threshold at index i, the version at index i+1 starts at that threshold
    for i, (threshold_dt, _) in enumerate(_format_version_thresholds):
        if i + 1 < len(versions_in_order):
            next_version = versions_in_order[i + 1]
            result[next_version] = threshold_dt.astimezone(_berlin).date()
    # The newest version has no upper threshold of its own, so it is not covered by the loop above.
    # It starts where the latest bounded version ends.
    result[_latest_format_version] = _format_version_thresholds[-1][0].astimezone(_berlin).date()
    return result


_valid_from_map = _build_valid_from_map()


def get_edifact_format_version_valid_from(version: EdifactFormatVersion) -> datetime.date:
    """
    Returns the date from which a format version is valid (in Europe/Berlin timezone).

    :param version: The format version to look up.
    :return: The first day on which this format version is active.
    :raises KeyError: If the start date is not known (only FV2104, the earliest version).
    """
    if version not in _valid_from_map:
        raise KeyError(
            f"Start date for {version} is not known. "
            f"Known versions: {', '.join(str(v) for v in sorted(_valid_from_map.keys(), key=lambda x: x.value))}"
        )
    return _valid_from_map[version]


def get_edifact_format_version(key_date: Union[datetime.datetime, datetime.date]) -> EdifactFormatVersion:
    """
    Retrieves the appropriate Edifact format version applicable for the given key date.

    This function determines the correct Edifact format version by comparing the provided key date
    against a series of predefined datetime thresholds. Each threshold corresponds to a specific
    version of the Edifact format.

    Note that any key date beyond the last known threshold returns the newest format version this
    library knows about, because the date at which that version will be superseded is not known yet.
    This means an outdated efoli release reports its own newest version for key dates that actually
    belong to a format version released after it. Update efoli to resolve such dates correctly.

    :param key_date: The date for which the Edifact format version is to be determined.
    :return: The Edifact format version valid for the specified key date.
    """
    if not isinstance(key_date, datetime.datetime) and isinstance(key_date, datetime.date):
        key_date = _berlin.localize(datetime.datetime.combine(key_date, datetime.time(0, 0, 0, 0)))

    for threshold_date, version in _format_version_thresholds:
        if key_date < threshold_date:
            return version

    return _latest_format_version


def get_current_edifact_format_version() -> EdifactFormatVersion:
    """
    returns the edifact_format_version that is valid as of now
    """
    # datetime.datetime.now(_utc) instead of utcnow(): the latter returns a naive datetime and is
    # deprecated since 3.12. datetime.UTC is not used because efoli supports Python 3.9.
    return get_edifact_format_version(datetime.datetime.now(_utc))
