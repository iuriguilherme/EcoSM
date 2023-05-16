Eco Server Manager and RCON
===

This is a web interface for a remote console to 
[Eco Global Survival Game](https://play.eco).  

This program can also start, stop, restart an Eco server, as well as 
the underlying operational system for that matter.  

This is accomplished through a web interface using the 
[Quart framework](https://quart.palletsprojects.com/en/latest/).  

This script is better used running in the system boot, as it would 
allow remote control over the Eco server through a web interface.  

Currently the way to deploy it is the same as any regular Flask / Quart 
application.  

The software used for remote console communication is the 
[minecraft rcon](https://pypi.org/project/mcrcon/).  

The Eco server manager and the remote console plugins are independent. 
You can use this software strictly for restarting your Eco server (or 
just Windows really), or strictly to control an Eco server through 
remote console, although any game using th minecraft RCON would work 
too.  

Quickstart
---

First of all, copy the file example.config.ini to config.ini and 
edit it to your needs. This program will run in the TCP port specified 
at the **uvicorn** section. In the **rcon** section, those are the 
RCON configurations you must make in the Eco server, and use the same 
values here. The **server** section has the path for your EcoServer.exe 
program.  

This script by default will start the EcoServer.exe configured, so you 
can run it in the system boot to bring up both.  

### pipenv

```
$ pipenv install -e .
$ pipenv run prod
```

### poetry

```
$ poetry install
$ poetry run prod
```

### venv / pip

```
$ python -m venv venv
$ .\venv\Scripts\activate
(venv) $ pip install -e .
(venv) $ python -m ecorcon
```

That's Windows Power Shell. If Unix second line is:

```
$ source venv/bin/activate
```

The program will run in the TCP port specified in the config.ini file.  

License
---

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
