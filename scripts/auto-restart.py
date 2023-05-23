"""Script Auto restarter"""

from configparser import ConfigParser
import logging
import os
from pathlib import Path
import subprocess
from subprocess import Popen
import sys
from time import sleep

logger: logging.Logger = logging.getLogger(__name__)

while True:
  method: str = "venv"
  path: Path = Path.cwd()
  try:
    config: ConfigParser = ConfigParser()
    config.read(os.path.join(path.parents[0], "instance", "config.ini"))
    method = config["script"]["method"]
  except Exception as e:
    logger.exception(e)
    logger.warning("""Couldn't read configuration file. Please make \
sure instance/config.ini exists. Use example.config.ini""")
  try:
    proc: Popen = Popen(
      os.path.join(path, f"start-{method}.bat"),
      cwd = path.parents[0],
      creationflags = subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    proc.communicate()
  except Exception as e:
    logger.exception(e)
  sleep(1e-15)
