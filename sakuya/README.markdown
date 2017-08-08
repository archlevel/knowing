Knowing - New Monitoring System
===============================

Knowing intends to replace the PyFisheyes system, which provides the charting monitor function for our OPS team.

It is inspired by many other famous projects, such as [twitter bootstrap][1], [compass][2], [sass][3].

Code Name
---------

Since the project name was not determined when the coding work started, I named it with a code name `sakuya`. You can find out who she is [here][4]:)


HOW TO RUN
----------

This project is written in python, so the first thing you need is a python at least 2.7. We recommend using [pythonbrew](https://github.com/utahta/pythonbrew/).

**about pythonbrew installation, please reference [here][5]**

### Create python virtual environment

Assuming you have `virtualenv` installed.

```
$ virtualenv venv --distribute
$ source venv/bin/activate
```

### Setup the project in developing mode.

```
$ python setup.py develop
```

You may meet with some dependency issues. Try installing the following packages using yum / apt-get:

* mysql server and client-side packages, with development files (headers).
* freetype and libpng with headers, required by `matplotlib`, the charting library.

### Install Ruby, rake, and compass.

The style of this project is made by awesome `compass`, which is built by ruby.

So you should first setup a ruby development enviroment, such as `rvm`, `bundler`

**about rvm install requirements, please reference [here][6]**

Then, run

```
bundle install
```

and the following commands are available:

```
$ rake -T
rake db:console[conn]  # run the db console
rake db:init           # initiate database
rake sass:compile      # compile the sass to css
rake sass:watch        # compile the sass to css and keep watching
rake serve             # run development server
```

### Create MySQL database and user accounts.

```
$ mysql -uroot -p
mysql> create database OPS_Monitor;
mysql> grant all on OPS_Monitor.* to 'ops_monitor'@'%' identified by 'ops_monitor';
mysql> grant all on OPS_Monitor.* to 'ops_monitor'@'localhost' identified by 'ops_monitor';
```

### Start the project.

```
$ rake db:init
$ rake sass:compile
$ rake serve
venv/bin/python -m bottle --bind 127.0.0.1:9075 --debug --reload sakuya:app
Bottle v0.11.3 server starting up (using WSGIRefServer())...
Listening on http://127.0.0.1:9075/
Hit Ctrl-C to quit.
```

### Jobs

Knowing uses seperate alert job for alerting function. You can use
`jobs/alert_wrapper.sh` to start it, or use supervisor

```
# modify `wd` alert_wrapper to locate the real alert.py
bash jobs/alert_wrapper.sh ${YOUR_PYTHON_VENV_EXECUTABLE}
```

TODO
---------------
* category management
* chart management, cooperation with Storm
* follow charts
* maybe more?


[1]: http://twitter.github.com/bootstrap
[2]: http://compass-style.org/
[3]: http://sass-lang.com/
[4]: http://en.touhouwiki.net/wiki/Sakuya_Izayoi
[5]: http://wiki.areverie.org/pythonbrew
[6]: http://wiki.areverie.org/rvm

