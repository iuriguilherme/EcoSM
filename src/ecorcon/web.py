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
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from configparser import ConfigParser, NoSectionError
from jinja2 import TemplateNotFound
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
  validators,
)
from .rcon import get_mcr, get_rcon_commands, rcon_send
from .server import (
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
from .system import (
  reboot_hard,
  reboot_soft,
)
from . import name, version
from .config import (
  edit_server,
  edit_user,
  passwords_file,
  servers_file,
)

logger: logging.Logger = logging.getLogger(__name__)

app: Quart = Quart(__name__)
app.secret_key: str = secrets.token_urlsafe(32)
AuthManager(app)

servers: dict[str, Popen | None] = {}
try:
  config: ConfigParser = ConfigParser()
  config.read(servers_file)
  for server in config.sections():
    servers[server] = None
except Exception as e:
  logger.exception(e)

async def start_server(
  server: Popen | None,
  server_name: str,
  *args,
  **kwargs,
) -> tuple[bool, Popen, str]:
  """Starts Eco Server"""
  try:
    return await eco_start(server, server_name)
  except Exception as e:
    return (False, server, repr(e))

@app.before_serving
async def startup() -> None:
  """Startup routine before serving Quart app"""
  global servers
  global config
  try:
    for server_name in config.sections():
      if bool(int(config[server_name].get("boot"))):
        status, server, message = await start(None, server_name)
        if status:
          servers[server_name] = server
  except Exception as e:
    logger.exception(e)

class LoginForm(FlaskForm):
  """Form for login"""
  username_field = StringField("Username", [
    validators.DataRequired()], default = "Arend")
  password_field = PasswordField(
    "Password",
    [
      validators.DataRequired(),
      validators.EqualTo(
        "confirm_field",
        message = "Passwords don't match",
      ),
    ]
  )
  confirm_field = PasswordField("Password again", [
    validators.DataRequired()])
  submit = SubmitField("Login")

class RegisterForm(FlaskForm):
  """Form for register"""
  username_field = StringField("Username", [
    validators.DataRequired()], default = "Arend")
  password_field = PasswordField(
    "Password",
    [
      validators.DataRequired(),
      validators.EqualTo(
        "confirm_field",
        message = "Passwords don't match",
      ),
    ]
  )
  confirm_field = PasswordField("Password again", [
    validators.DataRequired()])
  level_field: RadioField = RadioField(
    "Permission Level (top inherits lower levels)",
    [validators.DataRequired()],
    choices = [
      ("0", "Root (can interact with all pages"),
      ("1", "System admin (Can use the Windows Manager page)"),
      ("2", "Server admin (Can use the Eco Server Manager page)"),
      ("3", "RCON (Can use the Eco Remote Console page)"),
      ("4", "Lurker (Can't do anything)"),
    ],
  )
  active_field: RadioField = RadioField(
    "Account active?",
    [validators.DataRequired()],
    choices = [("0", "Inactive"), ("1", "Active")],
  )
  submit = SubmitField("Update")

@app.route("/", defaults={"page": "index"})
@app.route("/<page>")
async def show(page):
  """Attempt to load template for `page`"""
  try:
    return await render_template(
      f"{page}.html",
      name = name,
      version = version,
      title = name,
    )
  except TemplateNotFound as e:
    logger.warning(f"Template not found for {page}")
    raise
    # ~ await abort(404)
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

## TODO: parse arguments in rcon module (for example, validate 
## arguments separated by comma, get players list with another
## rcon command, etc.
@app.route("/rcon", methods = ['GET', 'POST'])
# ~ @login_required
async def rcon() -> str:
  """Send RCON Command"""
  response: str | None = None
  try:
    class RCONForm(FlaskForm):
      """Remote Console Form"""
      command_field = RadioField(
        "Select Command",
        [validators.DataRequired()],
        choices = [("0", "None")],
      )
      arguments_field = TextAreaField(
        "Command Arguments (optional)",
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
    form: FlaskForm = RCONForm(formdata = await request.form)
    await form.validate_command_field(form.command_field)
    if request.method == "POST":
      try:
        if form["command_field"].data not in [None, '', ' ']:
          command: tuple = await rcon_send(' '.join([
            form["command_field"].data,
            form["arguments_field"].data,
          ]))
        else: 
          command: tuple = await rcon_send(
            form["arguments_field"].data)
        response = command[1]
      except Exception as e2:
        logger.exception(e2)
        response = repr(e2)
  except Exception as e1:
      logger.exception(e1)
      response = repr(e1)
  try:
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

@app.route("/server", methods = ['GET', 'POST'])
# ~ @login_required
async def server() -> str:
  """Manage Eco server"""
  global servers
  status: bool = False
  response: str | None = None
  try:
    config: ConfigParser = ConfigParser()
    config.read(servers_file)
    function_map: dict = {
      "0": ("Eco Server Status", eco_status),
      "1": ("Start Eco Server", eco_start),
      "2": ("Stop Eco Server", eco_proper_stop),
      "3": ("Restart Eco Server", eco_restart),
      "4": ("Advanced - Force Eco Server Stop", eco_stop),
    }
    class ServerForm(FlaskForm):
      """Form for server and action selection"""
      server_field: RadioField = RadioField(
        "Select Eco Server",
        [validators.DataRequired()],
        choices = [("0", "None")],
      )
      action_field: RadioField = RadioField(
        "Select Action",
        [validators.DataRequired()],
        choices = [("0", "None")],
      )
      submit: SubmitField = SubmitField("Send")
      async def validate_server_field(form, field) -> None:
        """Populate server selection list"""
        try:
          field.choices = [(index, server) for index, server in \
            enumerate(config.sections())]
        except Exception as e:
          logger.exception(e)
      async def validate_action_field(form, field) -> None:
        """Populate action selection list"""
        field.choices = [(k, v[0]) for k, v in \
          sorted(function_map.items())]
    form: FlaskForm = ServerForm(formdata = await request.form)
    await form.validate_server_field(form.server_field)
    await form.validate_action_field(form.action_field)
    if request.method == "POST":
      try:
        server_name: str = config.sections()[int(
          form["server_field"].data)]
        server: Popen = servers[server_name]
        status, server, response = await function_map[
          form["action_field"].data][1](server, server_name)
        servers[server_name] = server
      except Exception as e3:
        logger.exception(e3)
        status = False
        response = repr(e3)
    alive: dict[str, bool] = {}
    for server_name, server in servers.items():
      alive[server_name] = False
      try:
        alive[server_name] = (server.poll() is None)
      except (ValueError, AttributeError) as e2:
        logger.exception(e2)
      except Exception as e1:
        logger.exception(e1)
  except Exception as e:
    logger.exception(e)
    status = False
    response = repr(e)
  return await render_template(
    "server.html",
    name = name,
    version = version,
    title = "Eco Server Manager",
    form = form,
    response = response,
    alive = alive,
  )

@app.route("/system", methods = ['GET', 'POST'])
# ~ @login_required
async def system() -> str:
  """Manage operational system"""
  status: bool = False
  response: str | None = None
  try:
    function_map: dict = {
      "0": ("Restart Windows Server", reboot_soft),
      "1": ("Advanced - Force Windows Restart", reboot_hard),
    }
    class SystemForm(FlaskForm):
      command_field = RadioField(
        "Select Command",
        [validators.DataRequired()],
        choices = [(k, v[0]) for k, v in sorted(function_map.items())],
      )
      submit = SubmitField("Send")
    form: FlaskForm = SystemForm(formdata = await request.form)
    if request.method == "POST":
      try:
        status, response = await function_map[
          form["command_field"].data][1]()
      except Exception as e:
        logger.exception(e)
        return jsonify(repr(e))
    return await render_template(
      "system.html",
      name = name,
      version = version,
      title = "Windows Manager",
      form = form,
      response = response,
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
  logger.exception(e)
  response: str | None = None
  try:
    form: FlaskForm = LoginForm(formdata = await request.form)
    if request.method == "POST":
      try:
        hasher: PasswordHasher = PasswordHasher()
        config: ConfigParser = ConfigParser()
        config.read(passwords_file)
        user: dict = config[form["username_field"].data]
        try:
          hasher.verify(
            user.get("password"),
            form['password_field'].data,
          )
          login_user(AuthUser(user.get("id")))
          if current_user.is_authenticated:
            response = f"""Not sure how you did do done it, but \
you happened to did supplied the actual password for user \
{form['username_field'].data}."""
          else:
            response = "Well the password sounds correct but the \
login still didn't work. Go figure."
        except VerifyMismatchError as e5:
          logger.exception(e5)
          response: str = "y u no give the proper password"
      except KeyError as e4:
        logger.exception(e4)
        response = f"""we haz no such user as \
{form['username_field'].data}"""
      except Exception as e3:
        logger.exception(e3)
        response = repr(e3)
  except Exception as e2:
    logger.exception(e2)
    response = repr(e2)
  try:
    return await render_template(
      "login.html",
      name = name,
      version = version,
      title = "Login",
      form = form,
      response = response,
    )
  except Exception as e1:
    logger.exception(e1)
    return jsonify(repr(e1))

@app.route("/register", methods = ['GET', 'POST'])
# ~ @login_required
async def register() -> str:
  """Register Form"""
  try:
    response: str | None = None
    form: FlaskForm = RegisterForm(formdata = await request.form)
    if request.method == "POST":
      try:
        hasher: PasswordHasher = PasswordHasher()
        user: str = form["username_field"].data
        password: str = hasher.hash(form["password_field"].data)
        level: str = form["level_field"].data
        active: str = form["active_field"].data
        try:
          status, response = await edit_user(
            form["username_field"].data,
            hasher.hash(form["password_field"].data),
            form["level_field"].data,
            form["active_field"].data,
          )
        except Exception as e3:
          logger.exception(e3)
          response: str = f"We messed up: {repr(e3)}"
      except Exception as e2:
        logger.exception(e2)
        response: str = f"We messed up: {repr(e2)}"
  except Exception as e1:
    logger.exception(e1)
    response: str = f"We messed up: {repr(e1)}"
  try:
    return await render_template(
      "register.html",
      name = name,
      version = version,
      title = "Register",
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
