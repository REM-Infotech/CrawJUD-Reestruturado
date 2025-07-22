from os import environ  # noqa: D100
from pathlib import Path
from platform import system

import jpype as jp

jpype_config = None
jar_pjeoffice = "/root/.local/bin/pjeoffice-pro/pjeoffice-pro.jar"
if system() == "Windows":
    jar_pjeoffice = r"C:\Program Files\PJeOffice Pro\pjeoffice-pro.jar"

parent_path = Path(__file__).parent.resolve()
class_list = [
    str(Path(jar_pjeoffice).resolve()),
    str(parent_path.joinpath("_lib", "bcprov.jar")),
    str(parent_path.joinpath("_lib", "bcpkix.jar")),
    str(parent_path.joinpath("_lib", "bcutil.jar")),
]

if system() == "Windows":
    jpype_config = tuple(environ.get("JPYPE_CONFIG", "").split(","))
    jp.startJVM(classpath=class_list, *jpype_config)  # noqa: B026
elif system() == "Linux":
    jp.startJVM(
        classpath=class_list,
    )
