eztemplate
==========

Simple templating program to generate plain text (like config files) from name-value pairs.

Lets you create text files from templates in a versatile way. It's designed with easy operation from the command line or scripts, Makefiles, etc. in mind. You can make use of several third party templating engines like **mako** or **empy** as well as simple built-in ones.


Usage
-----


### Getting quick help

Make sure `eztemplate.py` is executable (`chmod a+x eztemplate.py`), then fire up the help:

```sh
./eztemplate.py --help
```

If for one reason or another that doesn't work on your system, you can also call it explictly with Python:

```sh
python eztemplate.py --help
```


### Running without arguments

When you run `eztemplate.py` without arguments, it will expect a template on standard input, possibly waiting forever:

```sh
./eztemplate.py
```

On __*ix__ terminals you can manually cause an end of file by pressing `Ctrl-D`.


### Quick demonstration

You can check that substitution is working by piping a template into the program and specifying a name-value pair (make sure to protect the string with single quotes, otherwise the shell believes you want to substitute a shell variable, replacing it by an empty string):

```sh
echo 'Hello, $entity.' | ./eztemplate.py entity=world
```

It should produce this output:

    Hello, world.

When you're calling `eztemplate.py` from a script or similar - i. e. non-interactively - you should specify everything as explicitly as possible (in particular all input files or _stdin_ as well as name-value pairs) and avoid using positional arguments. Everything can be specified using options, which avoids ambiguities:

```sh
echo 'Hello, $entity.' | ./eztemplate.py --stdin --arg entity=world
```
