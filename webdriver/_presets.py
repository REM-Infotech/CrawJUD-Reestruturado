from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeVar, Union

BrowserOptions = Literal["chrome", "gecko", "firefox"]
TExtensionsPath = TypeVar("ExtensionsPath", bound=Union[str, Path])
