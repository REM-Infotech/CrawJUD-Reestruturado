from pathlib import Path  # noqa: D100
from typing import Self  # noqa: F401

import jpype.imports
from dotenv import load_dotenv
from jpype import JClass

load_dotenv()

classpath = Path(r"C:\Program Files\PJeOffice Pro\pjeoffice-pro.jar").resolve()
jvm_path = jpype.getDefaultJVMPath()
jpype.startJVM(
    classpath=[classpath],
    *(  # noqa: B026
        "--add-modules=jdk.crypto.mscapi",
        "--add-exports=jdk.crypto.mscapi/sun.security.mscapi=ALL-UNNAMED",
    ),
)
from java.util import HashSet, Set  # type: ignore  # noqa: E402, PGH003

try:
    # with suppress(Exception):
    #     jpype.shutdownJVM()
    JavaPath = JClass("java.nio.file.Paths", initialize=True)
    path = JavaPath.get("\\\\fmv.intranet\\NETLOGON\\CERTIFICADO\\44555059204.pfx")
    DeviceManager = JClass("com.github.signer4j.imp.PKCS12DeviceManager")()
    # DeviceManager = JClass("com.github.signer4j.imp.MSCAPIDeviceManager")()
    # Signer4JDeviceManager = JClass("com.github.signer4j.imp.Signer4JDeviceManager")
    JavaDict: Set = HashSet()
    is_loaded = DeviceManager.isLoaded()
    DeviceManager = DeviceManager.install(path)

    device = DeviceManager.getDevices()
    repository = DeviceManager.getRepository()
    is_empty = device.isEmpty()
    list_devices = device.get().getCertificates()
    for item in list_devices:
        print(item)

except Exception as e:
    print(f"Failed to start JVM: {e}")
    raise
