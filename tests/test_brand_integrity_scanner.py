from pathlib import Path

from scripts.check_brand_integrity import (
    fragment_targets_brand_art,
    references_in,
    style_fragments,
)


def test_markdown_code_reference_does_not_include_trailing_backtick() -> None:
    assert references_in(
        "**Ativo oficial:** `assets/brand/all-in-one-logo-official.png`"
    ) == {"assets/brand/all-in-one-logo-official.png"}


def test_minified_css_is_split_into_independent_rule_blocks() -> None:
    css = (
        ".brand__logo{width:44px;height:44px;object-fit:contain}"
        ".sidebar{backdrop-filter:blur(18px)}"
    )

    fragments = style_fragments(Path("styles.css"), css)

    assert fragments == [
        (1, ".brand__logo{width:44px;height:44px;object-fit:contain"),
        (1, ".sidebar{backdrop-filter:blur(18px)"),
        (1, ""),
    ]


def test_brand_color_variable_does_not_turn_unrelated_rule_into_logo_art() -> None:
    assert not fragment_targets_brand_art(
        ".primary-button{border-color:var(--brand);border-radius:11px"
    )
    assert fragment_targets_brand_art(
        ".brand__logo{width:44px;height:44px;object-fit:contain"
    )
