# noqa: D104
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from browsermobproxy import Client as ProxyClient
from browsermobproxy import Server
from dotenv import dotenv_values

environ = dotenv_values()


def configure_proxy() -> ProxyClient:  # noqa: D103
    server = Server(environ["BROWSERMOB_PATH"])
    server.start()
    return server.create_proxy()


@dataclass(frozen=True)
class CreatorInfo:  # noqa: D101
    name: str = "BrowserMob Proxy"
    version: str = "2.1.4"
    comment: str = ""


@dataclass(frozen=True)
class HARProxy:  # noqa: D101
    creator: CreatorInfo
    version: str = ""
    pages: list[Page] = field(default_factory=list)
    entries: list[EntryRequest] = field(default_factory=list)
    comment: str = ""


@dataclass(frozen=True)
class EntryRequest:  # noqa: D101
    pageref: str = "default"
    startedDateTime: str = "2025-07-29T12:15:00.626-04:00"  # noqa: N815
    request: RequestData = field(default_factory=dict)
    response: ResponseData = field(default_factory=dict)
    cache: dict[str, str] = field(default_factory=dict)
    timings: dict[str, str | int] = field(default_factory=dict)
    serverIPAddress: str = ""  # noqa: N815
    comment: str = ""
    time: int = 0


@dataclass(frozen=True)
class RequestData:  # noqa: D101
    method: str
    httpVersion: str  # noqa: N815
    url: str
    headersSize: int  # noqa: N815
    bodySize: int  # noqa: N815
    comment: str
    cookies: list[Cookie] = field(default_factory=list)
    headers: list[Header] = field(default_factory=list)
    queryString: list[str] = field(default_factory=list)  # noqa: N815


@dataclass(frozen=True)
class ResponseData:  # noqa: D101
    status: int
    statusText: str  # noqa: N815
    httpVersion: str  # noqa: N815
    content: ContentData
    redirectURL: str  # noqa: N815
    headersSize: int  # noqa: N815
    bodySize: int  # noqa: N815
    comment: str
    cookies: list[Cookie] = field(default_factory=list)
    headers: list[Header] = field(default_factory=list)


@dataclass(frozen=True)
class ContentData(TypedDict):  # noqa: D101
    size: int
    mimeType: str  # noqa: N815
    comment: str
    text: str = ""


class Header(TypedDict):  # noqa: D101
    name: str = ""
    value: str = ""


class Cookie(TypedDict):  # noqa: D101
    name: str = ""
    value: str = ""
    path: str = ""
    domain: str = ""
    secure: bool = False
    httpOnly: bool = False
    expiry: int = 0
    sameSite: str = ""


class Page(TypedDict):  # noqa: D101
    id: str = "default"
    startedDateTime: str = "2025-07-29T12:15:00.124-04:00"
    title: str = "default"
    pageTimings: dict[str, str | int] = {}
    comment: str = ""


class DictHARProxy(TypedDict):  # noqa: D101
    version: str = ""
    creator: CreatorInfo
    pages: list[Page] = []
    entries: list[EntryRequest] = []
    comment: str = ""
