"""Starts Web application"""

import logging

from quart import (
  abort,
  # ~ current_app,
  flash,
  flask_patch,
  jsonify,
  Quart,
  render_template,
  request,
)
from flask_wtf import FlaskForm

from jinja2 import TemplateNotFound
import secrets
from wtforms import (
  Form,
  # ~ HiddenField,
  # ~ IntegerField,
  # ~ SelectField,
  # ~ StringField,
  SubmitField,
  RadioField,
  TextAreaField,
)
from .rcon import (
  get_mcr,
  get_rcon_commands,
  rcon_send,
)
from . import name, version

logging.basicConfig(level = "INFO")
logger: logging.Logger = logging.getLogger(__name__)

app: Quart = Quart(__name__)
app.secret_key = secrets.token_urlsafe(32)

@app.route('/', defaults={'page': 'index'})
@app.route('/<page>')
async def show(page):
  try:
    return await render_template(
      '{0}.html'.format(page),
      name = name,
      version = version,
      title = page,
    )
  except TemplateNotFound as e:
    logger.warning(f"Template not found for {page}")
    await abort(404)
  except Exception as e:
    logger.exception(e)
    return jsonify(repr(e))

@app.route("/send", methods = ['GET', 'POST'])
async def send():
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
      "send.html",
      name = name,
      version = version,
      title = "Send Command",
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
