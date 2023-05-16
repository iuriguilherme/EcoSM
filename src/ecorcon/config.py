"""System wide variables"""

from configparser import ConfigParser, NoSectionError
from datetime import datetime
import logging
import os
import shutil

logger: logging.Logger = logging.getLogger(__name__)

config_file: str = "config.ini"
servers_file: str = ".servers"
passwords_file: str = ".passwd"

async def edit_server(
  name: str,
  path: str,
  boot: bool,
  active: bool,
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Edit server config on server configuration file"""
  exception: str | None = None
  try:
    config: ConfigParser = ConfigParser()
    if not os.path.exists(os.path.dirname(servers_file)):
      os.makedirs(os.path.dirname(servers_file))
    config.read(servers_file)
    try:
      config.set(name, "active", str(int(active)))
      config.set(name, "boot", str(int(boot)))
      config.set(name, "path", path)
    except NoSectionError as e2:
      logger.exception(e2)
      config.add_section(name)
      config.set(name, "active", str(int(active)))
      config.set(name, "boot", str(int(boot)))
      config.set(name, "path", path)
    try:
      shutil.copy(servers_file,
        f"{servers_file}.backup.{datetime.utcnow().timestamp()}")
      with open(servers_file, "w+") as srv:
        config.write(srv)
      return (True, f"{name} settings updated.")
    except Exception as e1:
      logger.exception(e1)
      exception = e1
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, f"We messed up: {repr(exception)}")

async def edit_user(
  user: str,
  password: str,
  level: str,
  active: bool,
  *args,
  **kwargs,
) -> tuple[bool, str]:
  """Add server config to server configuration file"""
  exception: str | None = None
  try:
    config: ConfigParser = ConfigParser()
    config.read(passwords_file)
    try:
      config.set(user, "password", password)
      config.set(user, "level", level)
      config.set(user, "active", str(int(active)))
    except NoSectionError as e2:
      logger.exception(e2)
      user_id: str = str(len(config.sections()))
      config.add_section(user)
      config.set(user, "password", password)
      config.set(user, "level", level)
      config.set(user, "active", str(int(active)))
      config.set(user, "id", user_id)
    try:
      shutil.copy(passwords_file,
        f"{passwords_file}.backup.{datetime.utcnow().timestamp()}")
      with open(passwords_file, "w+") as pwd:
        config.write(pwd)
      return (True, f"{user} credentials updated. Do try to login.")
    except Exception as e1:
      logger.exception(e1)
      exception = e1
  except Exception as e:
    logger.exception(e)
    exception = e
  return (False, f"We messed up: {repr(exception)}")
