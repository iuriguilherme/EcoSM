"""Windows Manager"""

from configparser import ConfigParser
import logging
import os
import psutil
import signal
import subprocess
import sys

logger: logging.Logger = logging.getLogger(__name__)

async def run_subprocess(command: list[str], *args, **kwargs) -> str:
  """Run subprocess"""
  try:
    return subprocess.run([command])
  except Exception as e:
    logger.exception(e)

async def send_system(
  command: str,
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Send command to Operational System"""
  exception: Exception | None = None
  try:
    return (True, f"Command sent\n{os.system(command)}")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, 
    f"Failed to send command to system!\n{repr(exception)}")

async def reboot_soft(
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Send reboot signal with one minute timeout to Operational system"""
  try:
    if sys.platform.startswith('win32'):
      return await send_system("shutdown /t 60", *args,
        **kwargs)
    elif sys.platform.startswith('linux'):
      return await send_system("shutdown -r 60", *args,
        **kwargs)
    else:
      return (False, 
        "Couldn't reboot system because I don't know how :(")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, 
    f"Failed to send command to server!\n{repr(exception)}")

async def reboot_hard(
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Send forceful reboot to Operational system"""
  try:
    if sys.platform.startswith('win32'):
      return await send_system(eco, "shutdown /t 0 /f", *args,
        **kwargs)
    elif sys.platform.startswith('linux'):
      return await send_system(eco, "shutdown -r now", *args,
        **kwargs)
    else:
      return (False, 
        "Couldn't reboot system because I don't know how :(")
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, 
    f"Failed to send command to server!\n{repr(exception)}")
