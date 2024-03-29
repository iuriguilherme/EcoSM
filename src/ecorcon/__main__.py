"""
Eco Server Manager and RCON

Copyright 2023 Iuri Guilherme <https://iuri.neocities.org/>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""

import asyncio
from configparser import ConfigParser
import logging
import os
import sys
import uvicorn
from .web import app
from . import name

logger = logging.getLogger(name)

try:
  if (len(sys.argv) > 1 and sys.argv[1] in \
    ["testing", "stage", "staging"]) or \
    os.environ.get("ENV", None) in \
    ["staging", "testing"]\
  :
    app.run()
  else:
    config: ConfigParser = ConfigParser()
    config_file: str = os.path.join("instance", "config.ini")
    if not os.path.exists(config_file):
      logger.warning("""Could not find configuration file, please \
create directory `instance` and copy example.config.ini to config.ini\
""")
      config_file = "example.config.ini"
    config.read(config_file)
    try:
      uvicorn.run(
        app,
        uds = config["uvicorn"].get("socket"),
        forwarded_allow_ips = '*',
        proxy_headers = True,
        timeout_keep_alive = 0,
        log_level = "info",
      )
    except (OSError, NotImplementedError,
      asyncio.exceptions.CancelledError):
      logger.info("""Operational system can't handle UNIX sockets, \
using TCP/IP (Hint: You're most likely using Windows)...""")
      uvicorn.run(
        app,
        host = config["uvicorn"].get("host"),
        port = int(config["uvicorn"].get("port")),
        forwarded_allow_ips = '*',
        proxy_headers = True,
        timeout_keep_alive = 0,
        log_level = "info",
      )
except Exception as e:
  logger.exception(e)
