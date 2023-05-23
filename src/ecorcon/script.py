"""Script Manager"""

from configparser import ConfigParser
import logging
import os
import subprocess
import sys
from . import name

logger: logging.Logger = logging.getLogger(__name__)

async def run_subprocess(
  script: list[str],
  message_sucess: str,
  message_failure: str,
  *args,
  **kwargs,
) -> dict[str, bool | str | Exception | None]:
  """Run subprocess"""
  _return: dict[str, bool | str | Exception | None] = {
    "status": False,
    "message": message_failure,
    "exception": None,
  }
  try:
    process_result: str = subprocess.run(os.path.join("scripts", 
      *script))
    _return["message"] = f"{message_sucess}: {process_result}"
    _return["status"] = True
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def update_git(*args, **kwargs) -> dict:
  """Update script to latest git commit"""
  return await run_subprocess(
    ["update-git.bat"],
    f"""Updated {name} to latest git commit. Will take effect at next \
restart.""",
    "Failed to update script with git. Is this a git repository?",
    *args,
    **kwargs,
  )

async def update_pipenv(*args, **kwargs) -> dict:
  """Update virtual environment using pipenv"""
  return await run_subprocess(
    ["update-pipenv.bat"],
    "Updated virtual environment through pipenv",
    """Failed to update virtual environment with pipenv. Is pipenv \
properly installed?""",
    *args,
    **kwargs,
  )

async def update_venv(*args, **kwargs) -> dict:
  """Update virtual environment using venv and pip"""
  return await run_subprocess(
    ["update-venv.bat"],
    "Updated virtual environment through venv",
    """Failed to update virtual environment with venv. Is python \
properly installed?""",
    *args,
    **kwargs,
  )

async def update_reinstall(*args, **kwargs) -> dict:
  """Reinstall this script, removing the virtual environments and \
pulling from last git commit"""
  return await run_subprocess(
    ["reinstall.bat"],
    """Reinstalled system, removed virtual environments and pulled \
from last git commit. Use one of the update scripts before restarting \
(pipenv or venv).""",
    """Failed to reinstall system. This script may not restart \
properly without manual fix now.""",
    *args,
    **kwargs,
  )

async def update_restart(*args, **kwargs) -> None:
  """Terminates program"""
  sys.exit(*args, **kwargs)

