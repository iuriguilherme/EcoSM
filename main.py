"""Eco RCON"""

import logging
import configparser
from mcrcon import MCRcon

logging.basicConfig(level = "INFO")
logger: logging.Logger = logging.getLogger(__name__)

try:
  config: configparser.ConfigParser = configparser.ConfigParser()
  config.read("config.ini")
  args: list = [
    config["eco"]["server"],
    config["eco"]["password"],
  ]
  kwargs: dict = {
    "port": int(config["eco"]["port"]),
  }
  with MCRcon(*args, **kwargs) as mcr:
    resp = mcr.command("/manage setreputation iggy,60")
    print(resp)
except Exception as e:
  logger.exception(e)

