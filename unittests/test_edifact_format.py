from typing import Optional

import pytest

from efoli import EdifactFormat, get_format_of_pruefidentifikator


@pytest.mark.parametrize(
    "pruefi, expected",
    [
        pytest.param("11042", EdifactFormat.UTILMD),
        ("13002", EdifactFormat.MSCONS),
        ("25001", EdifactFormat.UTILTS),
        ("11001", EdifactFormat.UTILMD),
        ("44001", EdifactFormat.UTILMDG),
        ("55001", EdifactFormat.UTILMDS),
    ],
)
def test_pruefi_to_format(pruefi: str, expected: EdifactFormat) -> None:
    """
    Tests that the prüfis can be mapped to an EDIFACT format
    """
    assert get_format_of_pruefidentifikator(pruefi) == expected


@pytest.mark.parametrize(
    "illegal_pruefi",
    [None, "", "asdas", "01234"],
)
def test_illegal_pruefis(illegal_pruefi: Optional[str]) -> None:
    """
    Test that illegal pruefis are not accepted
    :return:
    """
    with pytest.raises(ValueError):
        get_format_of_pruefidentifikator(illegal_pruefi)  # type: ignore[arg-type] # ok, because this raises an error


@pytest.mark.parametrize("pruefi", [pytest.param("10000")])
def test_pruefi_to_format_not_mapped_exception(pruefi: str) -> None:
    """
    Test that pruefis that are not mapped to an edifact format are not accepted
    """
    with pytest.raises(ValueError) as excinfo:
        _ = get_format_of_pruefidentifikator(pruefi)

    assert "No Edifact format was found for pruefidentifikator" in excinfo.value.args[0]


def test_str_representation() -> None:
    assert str(EdifactFormat.UTILMD) == "UTILMD"
