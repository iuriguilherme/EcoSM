"""Starts Web application"""

from quart import (
  abort,
  # ~ current_app,
  flash,
  flask_patch,
  jsonify,
  Quart,
  render_template,
  request,
  render_template_string,
)
from flask_wtf import FlaskForm

import asyncio
# ~ from asyncio.subprocess import Process
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from configparser import ConfigParser, NoSectionError
from datetime import datetime
from jinja2 import TemplateNotFound
from multiprocessing import Process
import logging
import os
from quart_auth import (
  AuthManager,
  login_required,
  Unauthorized,
  AuthUser,
  login_user,
  logout_user,
  current_user,
)
import secrets
import shutil
import subprocess
from subprocess import Popen
from wtforms import (
  Form,
  # ~ HiddenField,
  # ~ IntegerField,
  PasswordField,
  RadioField,
  # ~ SelectField,
  StringField,
  SubmitField,
  TextAreaField,
)
from .rcon import get_mcr, get_rcon_commands, rcon_send
from .manager import (
  get_path,
  get_subprocess,
  eco_proper_stop,
  eco_restart,
  eco_status,
  eco_start,
  eco_stop,
  send_break,
  send_ctrlc,
)
from . import name, version

logger: logging.Logger = logging.getLogger(__name__)

app: Quart = Quart(__name__)
app.secret_key: str = secrets.token_urlsafe(32)
AuthManager(app)

eco: Popen | None = None

class LoginForm(FlaskForm):
  username_field = StringField("Username", default = "Arend")
  password_field = PasswordField("Password")
  submit = SubmitField("Login")

@app.route("/", defaults={"page": "index"})
@app.route("/<page>")
async def show(page):
  """Attempt to load template for `page`"""
  try:
    return await render_template(
      f"{page}.html",
      name = name,
      version = version,
      title = page,
    )
  except TemplateNotFound as e:
    logger.warning(f"Template not found for {page}")
    raise
    # ~ await abort(404)
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/rcon", methods = ['GET', 'POST'])
# ~ @login_required
async def rcon() -> str:
  """Send RCON Command"""
  try:
    class CommandForm(FlaskForm):
      command_field = RadioField(
        "select command",
        choices = [("0", "None")],
      )
      arguments_field = TextAreaField(
        "command arguments",
        default = "",
      )
      submit = SubmitField("Send")
      async def validate_command_field(form, field) -> None:
        """Populate command selection list"""
        commands = await get_rcon_commands()
        if commands[0]:
          field.choices = commands[1]
        else:
          raise Exception(commands[1])
    response: str | None = None
    form: FlaskForm = CommandForm(formdata = await request.form)
    await form.validate_command_field(form.command_field)
    if request.method == "POST":
      try:
        ## TODO: parse arguments in rcon module (for example, validate 
        ## arguments separated by comma, get players list with another
        ## rcon command, etc.
        command: tuple = await rcon_send(' '.join([
          form['command_field'].data,
          form['arguments_field'].data,
        ]))
        response = command[1]
      except Exception as e:
        logger.exception(e)
        return jsonify(repr(e))
    return await render_template(
      "rcon.html",
      name = name,
      version = version,
      title = "Remote Console",
      form = form,
      response = response,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/manager", methods = ['GET', 'POST'])
# ~ @login_required
async def manager() -> str:
  """Manage server process"""
  global eco
  try:
    function_map: dict = {
      "0": eco_status,
      "1": eco_start,
      "2": send_ctrlc,
      "3": send_break,
      "4": eco_proper_stop,
      "5": eco_stop,
      "6": eco_restart,
    }
    class ManagerForm(FlaskForm):
      command_field = RadioField(
        "select command",
        choices = [
          ("0", "Eco Server Status"),
          ("1", "Start Eco Server"),
          ("4", "Stop Eco Server"),
          ("6", "Restart Eco Server - the proper way(tm)"),
          ("5", """Advanced - Forcefully Hard Stop (may mess up and \
require windows server restart)"""),
          ("2", "Advanced - Send CTRL+C to Server"),
          ("3", "Advanced - Send CTRL+BREAK to Server"),
        ],
      )
      submit = SubmitField("Send")
    response: str | None = None
    form: FlaskForm = ManagerForm(formdata = await request.form)
    if request.method == "POST":
      try:
        status, eco, response = await function_map[
          form['command_field'].data](
            # ~ eco_coroutine,
            # ~ eco_process,
            eco,
          )
      except Exception as e:
        logger.exception(e)
        return jsonify(repr(e))
    alive: bool = False
    try:
      alive: bool = (eco.poll() is None)
    except (ValueError, AttributeError):
      pass
    except Exception as e:
      logger.exception(e)
      # ~ pass
    return await render_template(
      "manager.html",
      name = name,
      version = version,
      title = "Server Manager",
      form = form,
      response = response,
      alive = alive,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/logout")
async def logout() -> str:
  """Logout route"""
  try:
    while (await current_user.is_authenticated):
      logout_user()
    return await render_template_string("""<p>BYE</p>\
<p><a href='{{url_for("show", page="index")}}'>back</a></p>""")
  except Exception as e:
    return jsonify(repr(e))

@app.errorhandler(TemplateNotFound)
@app.errorhandler(404)
@app.route("/not_found")
async def not_found(*e: Exception) -> str:
  """404"""
  logger.warning(e)
  return await render_template_string("""<p>Someone probably sent you \
the wrong link on purpose, but there's a tiny chance that you messed \
up.</p><p><a href='{{url_for("show", page="index")}}'>back</a></p>\
"""), 404

@app.errorhandler(Unauthorized)
@app.route("/login", methods = ['GET', 'POST'])
async def login(*e: Exception) -> str:
  """Login Form"""
  logger.warning(e)
  try:
    response: str | None = None
    form: FlaskForm = LoginForm(formdata = await request.form)
    if request.method == "POST":
      try:
        hasher: PasswordHasher = PasswordHasher()
        config: ConfigParser = ConfigParser()
        config.read(".passwd")
        user: dict = config[form['username_field'].data]
        try:
          hasher.verify(
            user.get("password"),
            form['password_field'].data,
          )
          login_user(AuthUser(user.get("id")))
          if current_user.is_authenticated:
            response: str = f"""Not sure how you did do done it, but \
you happened to did supplied the actual password for user \
{form['username_field'].data}."""
          else:
            response: str = "Well the password sounds correct but the \
login still didn't work. Go figure."
        except VerifyMismatchError as e:
          response: str = "y u no give the proper password"
      except KeyError as e:
        logger.exception(e)
        response: str = f"""we haz no such user as \
{form['username_field'].data}"""
      except Exception as e:
        logger.exception(e)
        return jsonify(repr(e))
    return await render_template(
      "login.html",
      name = name,
      version = version,
      title = "Login",
      form = form,
      response = response,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/register", methods = ['GET', 'POST'])
# ~ @login_required
async def register() -> str:
  """Register Form"""
  try:
    response: str | None = None
    form: FlaskForm = LoginForm(formdata = await request.form)
    if request.method == "POST":
      try:
        hasher: PasswordHasher = PasswordHasher()
        config: ConfigParser = ConfigParser()
        pwd_file: str = ".passwd"
        if not os.path.exists(os.path.dirname(pwd_file)):
          os.mkdirs(os.path.dirname(pwd_file))  
        config.read(pwd_file)
        user: str = form['username_field'].data
        password: str = hasher.hash(form['password_field'].data)
        try:
          config.set(user, "password", password)
        except NoSectionError as e:
          logger.exception(e)
          user_id: str = str(len(config.sections()))
          config.add_section(user)
          config.set(user, "password", password)
          config.set(user, "id", user_id)
        try:
          shutil.copy(pwd_file,
            f"{pwd_file}.backup.{datetime.utcnow().timestamp()}")
          with open(pwd_file, "w") as pwd:
            config.write(pwd)
          response: str = f"""{form['username_field'].data} password \
updated. Do try to login."""
        except Exception as e:
          logger.exception(e)
          response: str = f"we messed up: {repr(e)}"
      except Exception as e:
        logger.exception(e)
        return jsonify(repr(e))
    return await render_template(
      "login.html",
      name = name,
      version = version,
      title = "Login",
      form = form,
      response = response,
    )
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

def run() -> None:
  """Blocking default Quart run"""
  app.run()

if __name__ == "__main__":
  run()
