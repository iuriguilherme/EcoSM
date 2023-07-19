"""Server Manager for Eco https://wiki.play.eco/en/Server"""

from configparser import ConfigParser
import logging
import os
import signal
import subprocess
from subprocess import Popen
import sys
from .config import servers_file

logger: logging.Logger = logging.getLogger(__name__)

async def get_path(server_name: str, *args, **kwargs) -> str | None:
  """Configuration for server manager"""
  try:
    config: ConfigParser = ConfigParser()
    config.read(servers_file)
    return config[server_name].get("path")
  except Exception as e:
    logger.exception(e)
  return None

async def send_signal(
  process: Popen,
  _signal: int,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Send signal to subprocess"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Failed to send signal to server!",
    "exception": None,
  }
  try:
    _return["message"] = f"""Signal sent: \
{_return["process"].send_signal(_signal)}"""
    _return["status"] = True
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def server_status(
  process: Popen,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Returns server status"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Failed to get server status!",
    "exception": None,
  }
  try:
    if _return["process"].poll() is None:
      _return["message"] = "Server seems to be runing AFAIK"
      _return["status"] = True
    else:
      _return["message"] = "Looks like server is not running :("
  except AttributeError as e:
    _return["message"] = "Server is down"
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def server_start(
  process: Popen,
  server_name: str,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Starts server if not started"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Could not start server!",
    "exception": None,
  }
  try:
    _return = await server_status(_return["process"], *args, **kwargs)
    if not _return["status"]:
      path: str = await get_path(server_name, *args, **kwargs)
      if sys.platform.startswith('win32'):
        _return["process"] = Popen(
          [path],
          cwd = os.path.dirname(os.path.realpath(path)),
          creationflags = subprocess.CREATE_NEW_PROCESS_GROUP,
        )
      else:
        _return["process"] = Popen([path])
      _return["status"] = True
      _return["message"] = "Server started!"
    else:
      _return["message"] = """Can't start the server because it is \
already running!"""
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def server_proper_stop(
  process: Popen,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Stops server the proper way (tm)"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Failed to stop server!",
    "exception": None,
  }
  try:
    _return = await send_break(_return["process"], *args, **kwargs)
    _return["message"] = f"""Server stopped: \
{_return["process"].communicate()}"""
    _return["status"] = True
  except AttributeError as e:
    logger.exception(e)
    _return["message"] = """Couldn't stop the server because the \
server was likely not started to begin with."""
    _return["exception"] = e
    _return["status"] = True
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def server_stop(
  process: Popen,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Stops server if started"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Failed to Terminate server!",
    "exception": None,
  }
  try:
    _return["message"] = f"""Server Terminated: \
{_return["process"].terminate()}"""
    _return["status"] = True
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def server_restart(
  process: Popen,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Performs a stop then a start"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Failed to restart server!",
    "exception": None,
  }
  try:
    _return = await server_proper_stop(_return["process"], *args,
      **kwargs)
    if _return["status"]:
      return await server_start(_return["process"], *args, **kwargs)
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def send_ctrlc(
  process: Popen,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Send CTRL+C to subprocess"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Failed to send signal to server!",
    "exception": None,
  }
  try:
    _signal: int = 0
    if sys.platform.startswith("win32"):
      _signal = signal.CTRL_C_EVENT
    else:
      _signal = signal.SIGINT
    return await send_signal(_return["process"], _signal, *args,
      **kwargs)
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def send_break(
  process: Popen,
  *args,
  **kwargs,
) -> dict[str, bool | Popen | str | Exception | None]:
  """Send CTRL+BREAK to subprocess"""
  _return: dict[str, bool | Popen | str | Exception | None] = {
    "status": False,
    "process": process,
    "message": "Failed to send signal to server!",
    "exception": None,
  }
  try:
    _signal: int = 0
    if sys.platform.startswith("win32"):
      _signal = signal.CTRL_BREAK_EVENT
    else:
      _signal = signal.SIGBREAK
    return await send_signal(_return["process"], _signal, *args,
      **kwargs)
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return
