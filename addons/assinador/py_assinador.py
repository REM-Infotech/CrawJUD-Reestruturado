from typing import (
    Protocol,
    Self,  # noqa: F401
)

from dotenv import load_dotenv
from jpype import JClass


class MyClassInterface(Protocol):  # noqa: D101
    def foo(self, x: int) -> str: ...  # noqa: D102
    def bar(self) -> None: ...  # noqa: D102


load_dotenv()


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
