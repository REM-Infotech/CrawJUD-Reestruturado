"""Main file for Windows service."""

# import asyncio
# import importlib
# import socket

# import servicemanager  # type: ignore #noqa: PGH003
# import win32event  # type: ignore #noqa: PGH003
# import win32service  # type: ignore #noqa: PGH003
# import win32serviceutil  # type: ignore #noqa: PGH003


# class AppServerSvc(win32serviceutil.ServiceFramework):
#     """NT Service."""

#     _svc_name_ = "CrawJUD"
#     _svc_display_name_ = "CrawJUD-Bots Service"

#     def __init__(self, args: any) -> None:
#         """Init for service."""
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#         socket.setdefaulttimeout(60)

#     def SvcStop(self) -> None:  # noqa: N802
#         """Stop the service."""
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.hWaitStop)

#     def SvcDoRun(self) -> None:  # noqa: N802
#         """Run the service."""
#         servicemanager.LogMsg(
#             servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, "")
#         )
#         self.main()

#     def main(self) -> None:
#         """Start application."""
#         from threading import Thread

#         from crawjud.api.beat import run_beat  # noqa: PGH001
#         from crawjud.api.worker import run_worker  # noqa: PGH001

#         def run_worker_thread() -> None:
#             """Run the worker."""
#             asyncio.run(run_worker())

#         def run_beat_thread() -> None:
#             """Run the beat scheduler."""
#             asyncio.run(run_beat())

#         worker_thread = Thread(target=run_worker_thread)
#         beat_thread = Thread(target=run_beat_thread)

#         worker_thread.start()
#         beat_thread.start()

#         importlib.import_module("app.asgi", __package__)


# if __name__ == "__main__":
#     win32serviceutil.HandleCommandLine(AppServerSvc)
