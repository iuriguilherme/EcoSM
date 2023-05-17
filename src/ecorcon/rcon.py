"""Remote Console for Eco https://wiki.play.eco/en/RCON"""

## TODO: Add "password" to the config.py module and use the same server 
## list for RCON.

from configparser import ConfigParser
import logging
from mcrcon import MCRcon
from .config import config_file

logger: logging.Logger = logging.getLogger(__name__)

async def get_mcr(*args, **kwargs) -> MCRcon | None:
  """Connects to remote console Eco server"""
  server: str = "127.0.0.1"
  port: int = 3002
  password: str = "ididntchangethepassword"
  try:
    config: ConfigParser = ConfigParser()
    config.read(config_file)
    server = config.get("rcon")["server"]
    password = config.get("rcon")["password"]
    port: int(config.get("rcon")["port"])
    mcr: MCRcon = MCRcon(server, password, port = port)
    return mcr
  except Exception as e:
    logger.exception(e)
  return None

async def rcon_send(command: str, *args, **kwargs) -> tuple[bool, str]:
  """Send raw RCON command"""
  exception: str | None = None
  try:
    mcr: MCRcon = await get_mcr()
    try:
      mcr.connect()
      response: str = mcr.command(command)
      return (True, response)
    except Exception as e:
      logger.exception(e)
      exception = e
    finally:
      mcr.disconnect()
  except Exception as e:
    logger.exception(e)
    exception = e
  return (
    False,
    f"Failed to connect to remote Eco server: {repr(exception)}",
  )

async def get_rcon_commands(*args, **kwargs
) -> tuple[bool, list[tuple]]:
  """Get RCON Commands"""
  return (True, [
    ("", """<EMPTY COMMAND> (send a RAW Commmand in the arguments \
textbox below"""),
    ("/help", """/help (/?) -- Displays all the commands available \
with hidden subcommands. Accepts a string to filter commands to a \
search string."""),
    # ~ ("/helpful",
      # ~ "/helpful -- Shows all help, including sub commands."),
    # ~ ("/chat", "/chat -- Shows Commands related to chat."),
    # ~ ("/districts", """/districts -- Shows commands related to \
# ~ user-defined districts."""),
    ("/performance", """/performance -- Runs server performance \
reports and dump to files. Optionally pass duration in seconds, \
defaults to 60 seconds."""),
    ("/profiler", """/profiler -- Shows commands to profile the server \
and generate diagnostic data."""),
    ("/teleport", """/teleport -- List of different teleportation \
commands"""),
    ("/teleport atob", """/teleport atob -- Teleports player A to \
player B"""),
    ("/teleport targetto", """/teleport targetto -- Teleports \
otherPlayer to an xyz coordinate"""),
  ])
