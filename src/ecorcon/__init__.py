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

import logging

name: str = 'ecorcon'
description: str = "Remote Console for Eco"
version: str = '0.0.0'

__name__: str = name

logging.basicConfig(level = "INFO")
logger = logging.getLogger(__name__)

try:
  from . import _version
  version: str = _version.__version__
except Exception as e:
  logger.exception(e)
  logger.debug(f"""Unable to get version from _version file, using \
{version}""")

__version__: str = version
__description__: str = description

__all__: list = [
  __name__,
  __version__,
  __description__,
  'manager',
  'rcon',
  'web',
]

logger.info(f"Starting {name} v{version}")
