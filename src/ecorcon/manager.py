"""Server Manager for Eco https://wiki.play.eco/en/Server"""

# ~ import asyncio
from configparser import ConfigParser
import logging
# ~ from asyncio.subprocess import Process
from multiprocessing import Process
import os
import signal
import subprocess
from subprocess import Popen

logging.basicConfig(level = "INFO")
logger: logging.Logger = logging.getLogger(__name__)

def get_path(*args, **kwargs) -> str | None:
  """Configuration for server manager"""
  try:
    # ~ config: ConfigParser = ConfigParser()
    # ~ config.read("config.ini")
    # ~ return config["server"].get("path")
    return r"C:\Windows\notepad.exe"
  except Exception as e:
    logger.exception(e)
  return None

def get_subprocess(*args, **kwargs) -> None:
  """Run subprocess"""
  try:
    subprocess.run(get_path())
  except Exception as e:
    logger.exception(e)

def get_process(*args, **kwargs) -> Process:
  """Get Process"""
  # ~ return Process(target = get_subprocess)
  return Process(target = get_path)

async def eco_status(
  # ~ eco_coroutine: object,
  # ~ eco_process: Process,
  eco: Process,
  *args,
  **kwargs,
) -> tuple[bool, str]:
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
  eco: Process,
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Starts server if not started"""
  exception: Exception | None = None
  try:
    ## asyncio.subprocess
    # ~ eco_process: Process = await eco_coroutine
    # ~ await eco_process.wait()
    ## multiprocessing.Process
    # ~ eco.start()
    ## subprocess.Popen
    path: str = get_path()
    eco: Popen = Popen(
      [path],
      creationflags = subprocess.CREATE_NEW_PROCESS_GROUP,
      cwd = os.path.dirname(os.path.realpath(path)),
    )
    return (True, eco, "Server started")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco, f"""Server is probably already started!\n\
{repr(exception)}""")

async def eco_stop(
  # ~ eco_coroutine: object,
  # ~ eco_process: Process,
  eco: Process,
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Stops server if started"""
  exception: Exception | None = None
  try:
    ## asyncio.subprocess
    # ~ await eco_process.terminate()
    ## multiprocessing.Process
    # ~ eco.terminate()
    # ~ eco.join()
    # ~ eco.close()
    # ~ eco: Process = get_process()
    ## subprocess.Popen
    eco.send_signal(signal.CTRL_C_EVENT)
    return (True, eco, f"Server stopped\n{eco.communicate()}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco, f"""Failed to stop server!\n{repr(exception)}""")

async def eco_restart(
  # ~ eco_coroutine: object,
  # ~ eco_process: Process,
  eco: Process,
  *args,
  **kwargs,
) -> tuple[bool, Process, str]:
  """Performs a stop then a start"""
  exception: Exception | None = None
  try:
    return await eco_start(
      (await eco_stop(eco, *args, **kwargs))[1],
      *args,
      **kwargs,
    )
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, eco, f"Failed to restart server!\n{repr(exception)}")
