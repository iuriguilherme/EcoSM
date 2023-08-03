"""Configuration callbacks"""

from configparser import ConfigParser, NoSectionError
from datetime import datetime
import logging
import os
import shutil

logger: logging.Logger = logging.getLogger(__name__)

config_file: str = os.path.join("instance", "config.ini")
servers_file: str = os.path.join("instance", "servers.ini")
users_file: str = os.path.join("instance", "users.ini")

async def edit_server(
  name: str,
  path: str,
  password: str,
  boot: bool,
  *args,
  **kwargs,
) -> dict[str, bool | str | Exception | None]:
  """Edit server config on server configuration file"""
  _return: dict[str, bool | str | Exception | None] = {
    "status": False,
    "message": "Could not edit server configuration!",
    "exception": None,
  }
  try:
    config: ConfigParser = ConfigParser()
    if not os.path.exists(os.path.dirname(servers_file)):
      os.makedirs(os.path.dirname(servers_file))
    config.read(servers_file)
    try:
      config.set(name, "boot", str(int(boot)))
      config.set(name, "password", password)
      config.set(name, "path", path)
    except NoSectionError as e2:
      # ~ logger.exception(e2)
      config.add_section(name)
      config.set(name, "boot", str(int(boot)))
      config.set(name, "password", password)
      config.set(name, "path", path)
    try:
      shutil.copy(servers_file,
        f"{servers_file}.backup.{datetime.utcnow().timestamp()}")
    except FileNotFoundError:
      pass
    try:
      with open(servers_file, "w+") as srv:
        config.write(srv)
      _return["message"] = f"{name} settings updated."
      _return["status"] = True
    except Exception as e1:
      logger.exception(e1)
      _return["exception"] = e1
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def edit_user(
  user: str,
  password: str,
  level: str,
  active: bool,
  *args,
  **kwargs,
) -> dict[str, bool | str | Exception | None]:
  """Add server config to server configuration file"""
  _return: dict[str, bool | str | Exception | None] = {
    "status": False,
    "message": "Could not edit user configuration!",
    "exception": None,
  }
  try:
    config: ConfigParser = ConfigParser()
    config.read(users_file)
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
      shutil.copy(users_file,
        f"{users_file}.backup.{datetime.utcnow().timestamp()}")
    except FileNotFoundError:
      pass
    try:
      with open(users_file, "w+") as pwd:
        config.write(pwd)
      _return["message"] = f"""{user} credentials updated. Do try to \
login."""
      _return["status"] = True
    except Exception as e1:
      logger.exception(e1)
      _return["exception"] = e1
  except Exception as e:
    logger.exception(e)
    _return["exception"] = e
  return _return

async def get_servers(*args, **kwargs) -> dict[str, dict[str, str]]:
  """Get list of servers"""
  config: ConfigParser = ConfigParser()
  config.read(servers_file)
  return {section:dict(config.items(section)) for section in \
    config.sections()}

async def get_users(*args, **kwargs) -> dict[str, dict[str, str]]:
  """Get list of users"""
  config: ConfigParser = ConfigParser()
  config.read(users_file)
  return {section:dict(config.items(section)) for section in \
    config.sections()}
