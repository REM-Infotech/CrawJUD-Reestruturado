from os import environ  # noqa: D100
from pathlib import Path
from platform import system

import jpype as jp

jpype_config = tuple(environ["JPYPE_CONFIG"].split(","))
jar_pjeoffice = "/root/.local/bin/pjeoffice-pro/pjeoffice-pro.jar"
if system() == "windows":
    jar_pjeoffice = r"C:\Program Files\PJeOffice Pro\pjeoffice-pro.jar"

classpath = Path(jar_pjeoffice).resolve()
jp.startJVM(
    classpath=[classpath],
)
