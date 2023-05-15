"""Script for production / staging / testing / development"""

import asyncio
from configparser import ConfigParser
import logging
import os
import sys
import uvicorn
from .web import app

logger = logging.getLogger(__name__)

try:
  if (len(sys.argv) > 1 and sys.argv[1] in \
    ["testing", "stage", "staging"]) or \
    os.environ.get("ENV", None) in \
    ["staging", "testing"]\
  :
    app.run()
  else:
    config: ConfigParser = ConfigParser()
    config.read("config.ini")
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
      logger.warning("""Operational system can't handle UNIX sockets, \
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
