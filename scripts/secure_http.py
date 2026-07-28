from __future__ import annotations

from collections.abc import Collection
from urllib.parse import urlsplit


class UnsafeUrlError(ValueError):
    """Indica URL incompatível com a política de comunicação externa."""


def require_https_url(
    url: str,
    *,
    allowed_hosts: Collection[str] | None = None,
) -> str:
    """Valida HTTPS, host, porta e ausência de credenciais embutidas.

    A função devolve a própria URL para facilitar seu uso imediatamente antes
    da criação de ``urllib.request.Request``. Quando ``allowed_hosts`` é
    informado, subdomínios não são aceitos por aproximação: o hostname precisa
    coincidir exatamente com um item da coleção.
    """

    parsed = urlsplit(url)
    if parsed.scheme.casefold() != "https":
        raise UnsafeUrlError("A comunicação externa exige URL HTTPS.")
    if not parsed.hostname:
        raise UnsafeUrlError("A URL externa deve possuir hostname.")
    if parsed.username or parsed.password:
        raise UnsafeUrlError("Credenciais não podem ser embutidas na URL.")
    if parsed.port not in (None, 443):
        raise UnsafeUrlError("Somente a porta HTTPS padrão é permitida.")

    hostname = parsed.hostname.casefold()
    if allowed_hosts is not None:
        normalized = {host.casefold() for host in allowed_hosts}
        if hostname not in normalized:
            raise UnsafeUrlError(f"Host externo não autorizado: {hostname}.")
    return url
