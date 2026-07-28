from __future__ import annotations

import pytest

from scripts.secure_http import UnsafeUrlError, require_https_url


def test_require_https_url_accepts_exact_allowed_host() -> None:
    url = "https://firebase.googleapis.com/v1/projects/example"

    assert require_https_url(
        url, allowed_hosts={"firebase.googleapis.com"}
    ) == url


@pytest.mark.parametrize(
    "url",
    [
        "http://firebase.googleapis.com/v1/projects/example",
        "https://user:password@firebase.googleapis.com/v1/projects/example",
        "https://firebase.googleapis.com:8443/v1/projects/example",
        "file:///tmp/report.xml",
    ],
)
def test_require_https_url_rejects_unsafe_forms(url: str) -> None:
    with pytest.raises(UnsafeUrlError):
        require_https_url(url, allowed_hosts={"firebase.googleapis.com"})


def test_require_https_url_rejects_subdomain_approximation() -> None:
    with pytest.raises(UnsafeUrlError):
        require_https_url(
            "https://firebase.googleapis.com.evil.example/v1/projects/example",
            allowed_hosts={"firebase.googleapis.com"},
        )


def test_require_https_url_can_validate_arbitrary_public_https_without_allowlist() -> None:
    url = "https://brasildesconto.com.br/"

    assert require_https_url(url) == url
