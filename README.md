eztemplate
==========

Simple templating program to generate plain text (like config files) from name-value pairs.

Lets you create text files from templates in a versatile way. It's designed with easy operation from the command line or scripts, Makefiles, etc. in mind. You can make use of several third party templating engines like **mako** or **empy** as well as simple built-in ones.


Installation
------------


### from PyPI into a virtualenv (recommended)

With **virtualenv** you create a separate python environment without affecting the rest of your system, therefore this approach is recommended for playing around.

#### Install virtualenv

##### on Debian-based distributions (such as Ubuntu)

```sh
$ sudo apt-get install virtualenv
```

##### on Fedora

```sh
$ sudo yum install python-virtualenv
```

#### Install eztemplate

```sh
$ virtualenv myvenv                # create a new environment in a subdirectory
$ . myvenv/bin/activate            # switch to virtualenv (important)
$ pip install eztemplate           # install eztemplate from PyPI
$ eztemplate --version             # check if the correct version was installed
```

#### Upgrade eztemplate

```sh
$ . myvenv/bin/activate            # switch to virtualenv (if not there already)
$ pip install --upgrade eztemplate # upgrade eztemplate from PyPI
$ eztemplate --version             # check if the corrent version was installed
```


### from a git repository into a virtualenv

This is a good approach if you work on the repository and want to test the changes.

#### Install eztemplate

```sh
$ git clone https://github.com/blubberdiblub/eztemplate.git
$ cd eztemplate                    # change into the cloned repository
$ virtualenv venv                  # create a new environment in a subdirectory
$ . venv/bin/activate              # switch to virtualenv (important)
$ pip install .                    # just specify the directory to install from
$ eztemplate --version             # check if the correct version was installed
```

#### Upgrade eztemplate

```sh
$ git pull                         # pull latest commits from remote repository
$ . venv/bin/activate              # switch to virtualenv (if not there already)
$ pip install --upgrade --force-reinstall . # force upgrade eztemplate
$ eztemplate --version             # check if the correct version was installed
```


### from PyPI as system command

#### Install eztemplate

```sh
$ pip install eztemplate           # install eztemplate from PyPI
$ eztemplate --version             # check if the correct version was installed
```

#### Upgrade eztemplate

```sh
$ pip install --upgrade eztemplate # upgrade eztemplate from PyPI
$ eztemplate --version             # check if the corrent version was installed
```


Usage
-----

### Getting quick help

Use the help option:

```sh
$ eztemplate --help
```

You can also call the package explictly with Python (and thereby choose which Python installation to use):

```sh
$ python -m eztemplate --help
```


### Running without arguments

When you run `eztemplate` without arguments, it will expect a template on standard input, possibly waiting forever:

```sh
$ eztemplate
Hello, world!
<Ctrl-D>
Hello, world!
$
```

On __*ix__ terminals you can manually cause an end of file by pressing `Ctrl-D`.


### Quick demonstration

You can check that substitution is working by piping a template into the program and specifying a name-value pair (make sure to protect the string with single quotes, otherwise the shell believes you want to substitute a shell variable, replacing it by an empty string):

```sh
$ echo 'Hello, $entity.' | eztemplate entity=world
Hello, world.
$
```

When you're calling `eztemplate` from a script or similar - i. e. non-interactively - you should specify everything as explicitly as possible (in particular all input files or _stdin_ as well as name-value pairs) and refrain from using positional arguments. Everything can be specified using options, which avoids ambiguities:

```sh
$ echo 'Hello, $entity.' | eztemplate --stdin --arg entity=world
Hello, world.
$
```


Templating engines
------------------

**eztemplate** supports several templating engines. You select the one you want to use with the `-e` or `--engine` option. Specifying `help` instead of a name will list all currently available engines:

```sh
$ eztemplate -e help
Available templating engines:
  empy             -  Empy templating engine.
  mako             -  Mako templating engine.
  string.Template  -  String.Template engine.
$
```

Engines missing the required packages, modules or libraries will not be displayed. For instance to be able to use the `mako` or the `empy` engine, you need to have the respective python packages installed and working.

However, **eztemplate** comes with simple built-in engines which are available at all times. The `string.Template` engine is the default when you don't explicitly specify one.


### string.Template engine

This engine is named after the [string.Template class](https://docs.python.org/library/string.html#template-strings) in the Python standard library. It substitutes identifiers beginning with a dollar sign. To resolve ambiguities, you can also enclose the identifier in curly braces. It's similar to shell variable subsitution minus the more sophisticated features. It suffices for simple cases where you just need to insert some values into a text:

```bash
$ eztemplate --stdin \
>   --arg user="$( getent passwd "$USER" | cut -d: -f5 | cut -d, -f1 )" \
>   --arg food=cake --arg vendor=cafeteria --arg price="$RANDOM" \
>   <<\EOF
> Hello, $user.
>
> If you're hungry, get some ${food}s from the $vendor.
> They're only $$$price per piece.
> EOF
Hello, Niels Boehm.

If you're hungry, get some cakes from the cafeteria.
They're only $29993 per piece.
$
```
