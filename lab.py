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


try:
    # with suppress(Exception):
    #     jpype.shutdownJVM()
    JavaPath = JClass("java.nio.file.Paths", initialize=True)
    # DeviceManager = JClass("com.github.signer4j.imp.PKCS12DeviceManager")()
    DeviceManager = JClass("com.github.signer4j.imp.MSCAPIDeviceManager")()
    # Signer4JDeviceManager = JClass("com.github.signer4j.imp.Signer4JDeviceManager")

    DeviceManager.load()
    device = DeviceManager.firstDevice()
    repository = DeviceManager.getRepository()
    is_empty = device.isEmpty()
    list_devices = device.get()
    for item in list_devices.getCertificates():
        print(item)

except Exception as e:
    print(f"Failed to start JVM: {e}")
    raise
