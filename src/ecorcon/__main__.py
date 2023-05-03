"""Script for production / testing"""

import logging

logging.basicConfig(level = "INFO")
logger = logging.getLogger(__name__)

try:
  from .web import app
  app.run()
except Exception as e:
  logger.exception(e)
