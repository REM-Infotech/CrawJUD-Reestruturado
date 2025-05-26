"""
Types for socketio_server package.

This module defines type extensions for Socket.IO AsyncServer.
"""

import engineio
import socketio


class ASyncServerType(socketio.AsyncServer):
    """
    Type extension for socketio.AsyncServer with an explicit engineio.AsyncServer attribute.

    Inherits from socketio.AsyncServer and adds a type annotation for the 'eio' attribute,
    which represents the underlying Engine.IO AsyncServer instance.
    """

    eio: engineio.AsyncServer
