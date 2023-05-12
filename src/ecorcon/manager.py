"""Server Manager for Eco https://wiki.play.eco/en/Server"""

from configparser import ConfigParser
import logging
import os
import signal
import subprocess
from subprocess import Popen
import sys

logger: logging.Logger = logging.getLogger(__name__)

def get_path(*args, **kwargs) -> str | None:
  """Configuration for server manager"""
  try:
    config: ConfigParser = ConfigParser()
    config.read("config.ini")
    return config["server"].get("path")
  except Exception as e:
    logger.exception(e)
  return None

def get_subprocess(*args, **kwargs) -> None:
  """Run subprocess"""
  try:
    subprocess.run(get_path())
  except Exception as e:
    logger.exception(e)

async def send_signal(
  eco: Popen,
  _signal: int,
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Send signal to subprocess"""
  exception: Exception | None = None
  try:
    return (True, eco, f"Signal sent\n{eco.send_signal(_signal)}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to send signal to server!\n{repr(exception)}")

async def send_system(
  eco: Popen,
  command: str,
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Send command to Operational System"""
  exception: Exception | None = None
  try:
    return (True, eco, f"Command sent\n{os.system(command)}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to send command to system!\n{repr(exception)}")

async def eco_status(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Returns server status"""
  exception: Exception | None = None
  try:
    if eco.poll() is None:
      return (True, eco, "Server seems to be runing AFAIK")
    else:
      return (False, eco, "Looks like server is not running :(")
  except AttributeError:
    return (False, eco, f"Server is down\n{repr(e)}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to get server status!\n{repr(exception)}")

async def eco_start(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Starts server if not started"""
  exception: Exception | None = None
  try:
    if not (await eco_status(eco, *args, **kwargs))[0]:
      path: str = get_path()
      if sys.platform.startswith('win32'):
        eco: Popen = Popen(
          [path],
          cwd = os.path.dirname(os.path.realpath(path)),
          creationflags = \
            # ~ subprocess.CREATE_NEW_CONSOLE | \
            # ~ subprocess.DETACHED_PROCESS | \
            subprocess.CREATE_NEW_PROCESS_GROUP \
          ,
        )
      else:
        eco: Popen = Popen([path])
      return (True, eco, f"Server started!\n{repr(eco)}")
    else:
      return (False, eco,
        "Can't start the server because it is already running!")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Server is probably already started!\n{repr(exception)}")

async def eco_proper_stop(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Stops server the proper way (tm)"""
  exception: Exception | None = None
  try:
    response: tuple[bool, Popen, str] = await send_break(
      eco, *args, **kwargs)
    return (response[0], response[1],
      f"Server stopped\n{response[1].communicate()}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to stop server!\n{repr(exception)}")

async def eco_stop(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Stops server if started"""
  exception: Exception | None = None
  try:
    return (True, eco, f"Server Terminated\n{eco.terminate()}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to Terminate server!\n{repr(exception)}")

async def eco_restart(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Performs a stop then a start"""
  exception: Exception | None = None
  try:
    return await eco_start(
      (await eco_proper_stop(eco, *args, **kwargs))[1],
      *args,
      **kwargs,
    )
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to restart server!\n{repr(exception)}")

async def send_ctrlc(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Send CTRL+C to subprocess"""
  exception: Exception | None = None
  try:
    _signal: int = 0
    if sys.platform.startswith("win32"):
      _signal = signal.CTRL_C_EVENT
    else:
      _signal = signal.SIGINT
    return await send_signal(eco, _signal, *args, **kwargs)
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to send signal to server!\n{repr(exception)}")

async def send_break(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Send CTRL+BREAK to subprocess"""
  exception: Exception | None = None
  try:
    _signal: int = 0
    if sys.platform.startswith("win32"):
      _signal = signal.CTRL_BREAK_EVENT
    else:
      _signal = signal.SIGBREAK
    return await send_signal(eco, _signal, *args, **kwargs)
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to send signal to server!\n{repr(exception)}")

async def reboot_soft(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Send reboot signal with one minute timeout to Operational system"""
  try:
      if sys.platform.startswith('win32'):
        return await send_system(eco, "shutdown /t 60", *args,
          **kwargs)
      elif sys.platform.startswith('linux'):
        return await send_system(eco, "shutdown -r 60", *args,
          **kwargs)
      else:
        return (False, eco,
          "Couldn't reboot system because I don't know how :(")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to send command to server!\n{repr(exception)}")

async def reboot_hard(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Send forceful reboot to Operational system"""
  try:
      if sys.platform.startswith('win32'):
        return await send_system(eco, "shutdown /t 0 /f", *args,
          **kwargs)
      elif sys.platform.startswith('linux'):
        return await send_system(eco, "shutdown -r now", *args,
          **kwargs)
      else:
        return (False, eco,
          "Couldn't reboot system because I don't know how :(")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to send command to server!\n{repr(exception)}")
