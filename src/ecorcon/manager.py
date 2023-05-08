"""Server Manager for Eco https://wiki.play.eco/en/Server"""

# ~ import asyncio
from configparser import ConfigParser
import logging
# ~ from asyncio.subprocess import Process
# ~ from multiprocessing import Process
import os
import signal
import subprocess
from subprocess import Popen
import sys

# ~ logging.basicConfig(level = "INFO")
logger: logging.Logger = logging.getLogger(__name__)

def get_path(*args, **kwargs) -> str | None:
  """Configuration for server manager"""
  try:
    config: ConfigParser = ConfigParser()
    config.read("config.ini")
    return config["server"].get("path")
    # ~ return r"C:\Windows\notepad.exe"
  except Exception as e:
    logger.exception(e)
  return None

def get_subprocess(*args, **kwargs) -> None:
  """Run subprocess"""
  try:
    subprocess.run(get_path())
  except Exception as e:
    logger.exception(e)

# ~ def get_process(*args, **kwargs) -> Process | None:
  # ~ """Get Process"""
  # ~ try:
    # ~ return Process(target = get_path)
  # ~ except Exception as e:
    # ~ logger.exception(e)
  # ~ return None

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

async def eco_status(
  # ~ eco_coroutine: object,
  # ~ eco_process: Process,
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Returns server status"""
  exception: Exception | None = None
  try:
    ## multiprocessing.Process
    # ~ if eco.is_alive():
    if eco.poll() is None:
      return (True, eco, "Server seems to be runing AFAIK")
    else:
      return (True, eco, "Looks like server is not running :(")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Failed to get server status!\n{repr(exception)}")

async def eco_start(
  # ~ eco_coroutine: object,
  # ~ eco_process: Process,
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Starts server if not started"""
  exception: Exception | None = None
  try:
    path: str = get_path()
    if sys.platform.startswith('win32'):
      eco: Popen = Popen(
        [path],
        cwd = os.path.dirname(os.path.realpath(path)),
        creationflags = \
          subprocess.CREATE_NEW_CONSOLE | \
          subprocess.CREATE_NEW_PROCESS_GROUP \
        ,
      )
    else:
      eco: Popen = Popen([path])
    return (True, eco, f"Server started!\n{repr(eco)}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco,
    f"Server is probably already started!\n{repr(exception)}")

async def eco_wait_stop(
  eco: Popen,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Stops server if started"""
  exception: Exception | None = None
  try:
    await eco_stop(eco, *args, **kwargs)
    return (True, eco, f"Server stopped\n{eco.communicate()}")
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
      (await eco_wait_stop(eco, *args, **kwargs))[1],
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
