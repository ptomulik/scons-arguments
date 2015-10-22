"""`SConsArguments`

**Intro**

This module implements SCons *Arguments*. An *Argument* is an entity which
correlates up to three *Endpoints*:

- single construction variable in SCons environment (``env['NAME'], env.subst('$NAME')``),
- single SCons command-line variable (``scons variable=value`` in command-line), and
- single SCons command-line option (``scons --option=value`` in command-line).

Some of the above may be missing in *Argument* definition, so we may for
example correlate only a construction variable with command-line option without
involving command-line variable. *Arguments* specify how information shall flow
from command-line to SCons environment.

**Endpoint names and data flow**

Each *Argument* has up to three *Endpoints*: a construction variable in
SCons environment (``ENV`` endpoint), a command line variable (``VAR``
endpoint) and a command line option (``OPT`` endpoint).  *Arguments* use
separate "namespaces" for construction variables, command-line variables and
command-line options; the user defines mappings between these *Endpoints*.
For example, you may create an *Argument* named ``foo`` which correlates a
construction variable named ``ENV_FOO``, command-line variable named
``VAR_FOO`` and command-line option identified by key ``opt_foo`` (we use
``dest`` attribute of command line option as its identifying key, see `option
attributes`_ of python ``optparse``). At certain point you request *Arguments*
to update your SCons environment ``env``, that is to populate environment with
values taken from command-line variables and/or options.  At this point, value
taken from command-line variable ``VAR_FOO`` or value from command-line option
``opt_foo`` is passed to construction variable ``ENV_FOO``. If both,
command-line variable and command-line option are set, then command-line option
takes precedence.

**Substitutions in Arguments**

If a command-line value is a string, it may contain substitutions (e.g.
``VAR_FOO`` may be a string in form ``"bleah bleah ${VAR_BAR}"``).
Placeholders are assumed to be variable/option names in endpoint's namespace.
It means, that if we have a command-line variable, and its value is
a string containing placeholder ``"$VVV"``, then ``VVV`` is assumed to be the
name of another command-line variable (and not, for example, construction
variable). When passing strings from command-line variables and options to an
environment, the placeholders are renamed such that they refer to corresponding
construction variables in SCons environment. This is shown in the example
below.

**Example**

Assume, we have the following three *Arguments* defined::

    .               (1)         (2)         (3)
    Arguments:      foo         bar         geez
    Environment:    ENV_FOO     ENV_BAR     ENV_GEEZ
    Variables:      VAR_FOO     VAR_BAR     VAR_GEEZ
    Options:        opt_foo     opt_bar     opt_geez
    .             --opt-foo   --opt-bar   --opt-geez


and we invoked scons as follows::

    # Command line:
    scons VAR_FOO='${VAR_BAR}' VAR_BAR='${foo}' --opt-geez='${opt_foo}'

then, after updating a SCons environment ``env`` with *Arguments*, the
environment will have the following construction variables set::

    env['ENV_FOO'] = '${ENV_BAR}'   # VAR_FOO -> ENV_FOO,  VAR_BAR -> ENV_BAR
    env['ENV_BAR'] = '${foo}'       # VAR_BAR -> ENV_BAR,  foo -x-> foo
    env['ENV_GEEZ'] = '${ENV_FOO}'  # opt_geez-> ENV_GEEZ, opt_foo -> ENV_FOO

The arrow ``-x->`` denotes the fact, that there was no command-line variable
named ``foo``, so the ``"${foo}"`` placeholder was left unaltered.

**Example**

The following ``SConstruct`` file defines three *Arguments*: ``foo``, ``bar``
and ``geez``. Corresponding construction variables (environment) are named
``ENV_FOO``, ``ENV_BAR`` and ``ENV_GEEZ`` respectively. Corresponding
command-line variables are: ``VAR_FOO``, ``VAR_BAR`` and ``VAR_GEEZ``. Finally,
the command-line options that correspond to our *Arguments* are named
``opt_foo``, ``opt_bar`` and ``opt_geez`` (note: these are actually keys
identifying options within SCons script, they may be different from the option
names that user sees on his screen - here we have key ``opt_foo`` and
command-line option ``--foo``).

.. python::

    from SConsArguments import ArgumentDecls
    env = Environment()
    decls = ArgumentDecls(
       # Argument 'foo'
       foo = (   {'ENV_FOO' : 'ENV_FOO default'},                   # ENV
                 ('VAR_FOO',  'VAR_FOO help'),                      # VAR
                 ('--foo', {'dest' : "opt_foo"})         ),         # OPT
       # Argument 'bar'
       bar = (   {'ENV_BAR' : None},                                # ENV
                 ('VAR_BAR', 'VAR_BAR help', 'VAR_BAR default'),    # VAR
                 ('--bar',  {'dest':"opt_bar", "type":"string"})),  # OPT
       # Argument 'geez'
       geez =(   {'ENV_GEEZ' : None},                               # ENV
                 ('VAR_GEEZ', 'VAR_GEEZ help', 'VAR_GEEZ default'), # VAR
                 ('--geez', {'dest':"opt_geez", "type":"string"}))  # OPT
    )
    variables = Variables()
    args = decls.Commit(env, variables, True)
    args.UpdateEnvironment(env, variables, True)

    print "env['ENV_FOO']: %r" %  env['ENV_FOO']
    print "env['ENV_BAR']: %r" %  env['ENV_BAR']
    print "env['ENV_GEEZ']: %r" %  env['ENV_GEEZ']

Running scons several times for this example, different results may be obtained
depending on command-line variables and options provided. Let's do some
experiments, first show the help message to see available command-line options::

    user@host:$ scons -Q -h
    env['ENV_FOO']: 'ENV_FOO default'
    env['ENV_BAR']: 'VAR_BAR default'
    env['ENV_GEEZ']: 'VAR_GEEZ default'
    usage: scons [OPTION] [TARGET] ...

    SCons Options:
       <.... lot of output here ...>
    Local Options:
      --geez=OPT_GEEZ
      --foo=OPT_FOO
      --bar=OPT_BAR

then play with them a little bit (as well as with command-line variables)::

    user@host:$ scons -Q --foo='OPT FOO'
    env['ENV_FOO']: 'OPT FOO'
    env['ENV_BAR']: 'VAR_BAR default'
    env['ENV_GEEZ']: 'VAR_GEEZ default'
    scons: `.' is up to date.

    user@host:$ scons -Q VAR_FOO='VAR_FOO cmdline'
    env['ENV_FOO']: 'VAR_FOO cmdline'
    env['ENV_BAR']: 'VAR_BAR default'
    env['ENV_GEEZ']: 'VAR_GEEZ default'
    scons: `.' is up to date.

    user@host:$ scons -Q VAR_FOO='VAR_FOO cmdline' --foo='opt_foo cmdline'
    env['ENV_FOO']: 'opt_foo cmdline'
    env['ENV_BAR']: 'VAR_BAR default'
    env['ENV_GEEZ']: 'VAR_GEEZ default'
    scons: `.' is up to date.

    user@host:$ scons -Q VAR_FOO='VAR_FOO and ${VAR_BAR}'
    env['ENV_FOO']: 'VAR_FOO and ${ENV_BAR}'
    env['ENV_BAR']: 'VAR_BAR default'
    env['ENV_GEEZ']: 'VAR_GEEZ default'
    scons: `.' is up to date.

    user@host:$ scons -Q --foo='opt_foo with ${opt_geez}'
    env['ENV_FOO']: 'opt_foo with ${ENV_GEEZ}'
    env['ENV_BAR']: 'VAR_BAR default'
    env['ENV_GEEZ']: 'VAR_GEEZ default'
    scons: `.' is up to date.

You may decide to not create corresponding command-line variable or
command-line option for a particular *Argument*. In following example we
declare two *Arguments* named ``foo`` and ``bar``. Argument ``foo`` has no
corresponding command-line variable and argument ``bar`` has no corresponding
command-line option.

**Example**

Consider following ``SConstruct`` file:

.. python::

    from SConsArguments import ArgumentDecls
    env = Environment()
    decls = ArgumentDecls(
       # Argument 'foo'
       foo =  (   {'ENV_FOO' : 'ENV_FOO default'},                  # ENV
                  None,                                             # no VAR
                  ('--foo',       {'dest' : "opt_foo"})         ),  # OPT
       # Argument 'bar'
       bar = (   {'ENV_BAR' : None},                                # ENV
                 ('VAR_BAR', 'VAR_BAR help', 'VAR_BAR default'),    # VAR
                 None                                           ),  # no OPT
    )
    variables = Variables()
    args = decls.Commit(env, variables, True)
    args.UpdateEnvironment(env, variables, True)

    print "env['ENV_FOO']: %r" %  env['ENV_FOO']
    print "env['ENV_BAR']: %r" %  env['ENV_BAR']

Some experiments with command-line yield following output::

    user@host:$ scons -Q VAR_FOO='VAR_FOO cmdline'
    env['ENV_FOO']: 'ENV_FOO default'
    env['ENV_BAR']: 'VAR_BAR default'
    scons: `.' is up to date.

    user@host:$ scons -Q --bar='opt_bar cmdline'
    env['ENV_FOO']: 'ENV_FOO default'
    env['ENV_BAR']: 'VAR_BAR default'
    usage: scons [OPTION] [TARGET] ...

    SCons error: no such option: --bar

    user@host:$ scons -Q --foo='opt_foo and ${opt_bar}'
    env['ENV_FOO']: 'opt_foo and ${opt_bar}'
    env['ENV_BAR']: 'VAR_BAR default'
    scons: `.' is up to date.

    user@host:$ scons -Q --foo='opt_foo and ${opt_foo}'
    env['ENV_FOO']: 'opt_foo and ${ENV_FOO}'
    env['ENV_BAR']: 'VAR_BAR default'
    scons: `.' is up to date.

    user@host:$ scons -Q VAR_BAR='VAR_BAR and ${VAR_FOO}'
    env['ENV_FOO']: 'ENV_FOO default'
    env['ENV_BAR']: 'VAR_BAR and ${VAR_FOO}'
    scons: `.' is up to date.

    user@host:$ scons -Q VAR_BAR='VAR_BAR and ${VAR_BAR}'
    env['ENV_FOO']: 'ENV_FOO default'
    env['ENV_BAR']: 'VAR_BAR and ${ENV_BAR}'
    scons: `.' is up to date.


For more details go to the documentation of `ArgumentDecls()`,
`ArgumentDecl()`, `DeclareArguments()` and `DeclareArgument()`.
See also `_ArgumentDecls`, `_Arguments`, and `_ArgumentDecl` classes.

.. _option attributes: http://docs.python.org/2/library/optparse.html#option-attributes
"""

#
# Copyright (c) 2015 by Pawel Tomulik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

__docformat__ = "restructuredText"

import SCons.Util
import string

#############################################################################
ENV = 0
"""Represents selection of construction variable corresponding to particular
*Argument*."""

VAR = 1
"""Represents selection of command-line variable corresponding to particular
*Argument* variable."""

OPT = 2
"""Represents selection of command-line option related to particular *Argument*."""

ALL = 3
"""Number of all namespaces (currently there are three: ``ENV``, ``VAR``,
``OPT``)"""
#############################################################################

#############################################################################
class _missing_meta(type):
    "Meta-class for the _missing class"
    def __bool__(self):
        return False
    __nonzero__ = __bool__
    def __repr__(cls):
        return 'MISSING'

#############################################################################
class _missing(object):
    "Represents missing argument to function."
    __metaclass__ = _missing_meta

#############################################################################
MISSING = _missing
"""Represents missing argument to function."""

#############################################################################
class _undef_meta(type):
    """Meta-class for the _undef class"""
    def __bool__(self):
        return False
    __nonzero__ = __bool__
    def __repr__(cls):
        return 'UNDEFINED'

#############################################################################
class _undef(object):
    "Represents undefined/inexistent variable. This is not the same as None"
    __metaclass__ = _undef_meta

UNDEFINED = _undef
"""Represents undefined/inexistent variable. This is not the same as None"""

#############################################################################
class _notfound(object):
    "Something that has not been found, a result of failed search."
    pass

#############################################################################
def _resubst(value, resubst_dict = {}):
    """Rename placeholders (substrings like ``$name``) in a string value.

    :Parameters:
        value
            the value to process; if it is string it is passed through
            placeholder renaming procedure; otherwise it is returned unaltered,
        resubst_dict
            a dictionary of the form ``{ "xxx":"${yyy}", "vvv":"${www}", ...}``
            used to rename placeholders within ``value`` string; with the above
            dictionary, all occurrences of ``$xxx`` or ``${xxx}`` within
            `value` string will be replaced with ``${yyy}``, all occurrences of
            ``$vvv`` or ``${vvv}`` with ``${www}`` and so on; see also
            `_build_resubst_dict()`,
    :Returns:
        returns the ``value`` with placeholders renamed.
    """
    if SCons.Util.is_String(value):
        # make substitution in strings only
        return string.Template(value).safe_substitute(**resubst_dict)
    else:
        return value

#############################################################################
def _build_resubst_dict(rename_dict):
    """Build dictionary for later use with `_resubst()`.

    **Example**

    .. python::

        >>> import SConsArguments
        >>> SConsArguments._build_resubst_dict( {"xxx":"yyy", "vvv":"www", "zzz":"zzz" })
        {'vvv': '${www}', 'xxx': '${yyy}'}

    :Parameters:
        rename_dict : dict
            dictionary of the form ``{"xxx":"yyy", "vvv":"www", ...}``
            mapping variable names from one namespace to another,

    :Returns:
        returns dictionary of the form ``{"xxx":"${yyy}", "vvv":"${www}"}``
        created from `rename_dict`; items ``(key, val)`` with ``key==val`` are
        ignored, so the entries of type ``"zzz":"zzz"`` do not enter the
        result.
    """
    return dict(map(lambda (k,v): (k, '${' + v + '}'),
                    filter(lambda (k,v) : k != v, rename_dict.iteritems())))

#############################################################################
def _build_iresubst_dict(rename_dict):
    """Build inversed dictionary for later use with `_resubst()`.

    **Example**

    .. python::

        >>> import SConsArguments
        >>> SConsArguments._build_iresubst_dict( {"xxx":"yyy", "vvv":"www", "zzz":"zzz" })
        {'www': '${vvv}', 'yyy': '${xxx}'}

    :Parameters:
        rename_dict : dict
            dictionary of the form ``{"xxx":"yyy", "vvv":"www", ...}``
            mapping variable names from one namespace to another

    :Returns:
        returns dictionary of the form ``{"yyy":"${xxx}", "www":"${vvv}",
        ...}`` created from inverted dictionary `rename_dict`; items ``(key,
        val)`` with ``key==val`` are ignored, so the entries of type
        ``"zzz":"zzz"`` do not enter the result;
    """
    return dict(map(lambda (k,v): (v, '${' + k + '}'),
                    filter(lambda (k,v) : k != v, rename_dict.iteritems())))

#############################################################################
def _compose_mappings(dict1, dict2):
    """Compose two mappings expressed by dicts ``dict1`` and ``dict2``.

    :Parameters:
        dict1, dict2
            dictionaries to compose

    :Returns:
        returns a dictionary such that for each item ``(k1,v1)`` from `dict1`
        and ``v2 = dict2[v1]`` the corresponding item in returned dictionary is
        ``(k1,v2)``
    """
    return dict(map(lambda (k,v) : (k, dict2[v]), dict1.iteritems()))

#############################################################################
def _invert_dict(_dict):
    return dict(map(lambda (k,v) : (v,k), _dict.iteritems()))

#############################################################################
class _ArgumentsProxy(object):
    #========================================================================
    """Proxy used to access construction variables stored in a **target**
    dictionary while using their *Argument* names.

    This object implements indirect access to variables stored in a **target**
    dictionary, (supposedly a `SCons environment`_ construction variables)
    while using their *Argument* names. The variable names (and placeholders
    found in their values) are translated forth and back from/to *Arguments*
    namespace when accessing the variables. The `_ArgumentsProxy` object
    provides `subst()` method, which handles the renaming in substitution
    strings, the method currently only works with SCons
    ``SubstitutionEnvironment`` object as the **target** dictionary.

    **Example**::

        user@host:$ scons -Q -f -

        from SConsArguments import _ArgumentsProxy
        env = Environment()
        proxy = _ArgumentsProxy(env, { 'foo'     : 'ENV_FOO'     },
                                     { 'foo'     : '${ENV_FOO}'  },
                                     { 'ENV_FOO' : 'foo'         },
                                     { 'ENV_FOO' : '${foo}'      })
        proxy['foo'] = "FOO"
        print "proxy['foo'] is %r" % proxy['foo']
        print "env['ENV_FOO'] is %r" % env['ENV_FOO']
        <Ctl+D>
        proxy['foo'] is 'FOO'
        env['ENV_FOO'] is 'FOO'
        scons: `.' is up to date.

    .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
    """
    #========================================================================
    def __init__(self, tgt, rename={}, resubst={}, irename={}, iresubst={},
                 strict=False):
        # -------------------------------------------------------------------
        """Initializes `_ArgumentsProxy` object.

        :Parameters:
            tgt
                the **target** dictionary to be proxied,
            rename
                dictionary used for mapping variable names from user namespace
                to environment namespace (used by `__setitem__()` and
                `__getitem__()`),
            resubst
                dictionary used by to rename placeholders in values passed
                from user to environment  (used by `__setitem__()` and
                `subst()`)
            irename
                dictionary used for mapping variable names from environment
                to user namespace (used by ``items()``),
            iresubst
                dictionary used by to rename placeholders in values passed
                back from environment to user (used by `__getitem__()` for
                example)
            strict
                if ``True`` only the keys defined in rename/resubst
                dictionaries are allowed, otherwise the original variables
                from ``tgt`` are also accessible via their keys
        """
        # -------------------------------------------------------------------
        self.tgt = tgt
        self.__rename = rename
        self.__resubst = resubst
        self.__irename = irename
        self.__iresubst = iresubst
        self.set_strict(strict)

    #========================================================================
    def is_strict(self):
        """Whether the proxy is in "strict" mode

        A "strict" mode proxy allows to access only these variables for which
        entries exist in rename/resubst dictionaries. If some variable is
        missing from dictionaries, a KeyError is raised.

        A "non-strict" proxy bypasses the rename/resubst dictionaries for
        variables that are not present therein and accesses the corresponding
        variable/option using Argument's name directly (without mapping).

        :Return:
            ``True``, if "strict" mode is enabled or ``False`` otherwise.
        """
        return self.__strict

    #========================================================================
    def set_strict(self, strict):
        """Set the proxy to "strict" or "non-strict" mode

        A "strict" mode proxy allows to access only these variables for which
        entries exist in rename/resubst dictionaries (for which mapping is
        defined). If some variable is not present in dictionaries, a KeyError
        is raised.

        A "non-strict" proxy bypasses the rename/resubst dictionaries for
        variables that are not present therein and accesses the corresponding
        variable/option using Argument's name directly (without mapping).

        :Parameters:
            strict
                determines whether to enable (``True``) or disable (``False``)
                the "strict" mode
        """
        self.__setup_methods(strict)
        self.__strict = strict

    #========================================================================
    def __setup_methods(self, strict):
        # switch between "strict" and "non-strict" mode by replacing certain
        # methods (accessors)
        if strict:
            self.__delitem__impl = self.__delitem__strict
            self.__getitem__impl = self.__getitem__strict
            self.__setitem__impl = self.__setitem__strict
            self.get = self._get_strict
            self.has_key = self._has_key_strict
            self.__contains__impl = self.__contains__strict
            self.items = self._items_strict
        else:
            self.__delitem__impl = self.__delitem__nonstrict
            self.__getitem__impl = self.__getitem__nonstrict
            self.__setitem__impl = self.__setitem__nonstrict
            self.get = self._get_nonstrict
            self.has_key = self._has_key_nonstrict
            self.__contains__impl = self.__contains__nonstrict
            self.items = self._items_nonstrict

    #========================================================================
    def __delitem__(self, key):
        self.__delitem__impl(key)

    #========================================================================
    def __delitem__strict(self, key):
        self.tgt.__delitem__(self.__rename[key])

    #========================================================================
    def __delitem__nonstrict(self, key):
        self.tgt.__delitem__(self.__rename.get(key,key))

    #========================================================================
    def __getitem__(self, key):
        return self.__getitem__impl(key)

    #========================================================================
    def __getitem__strict(self, key):
        tgt_key = self.__rename[key]
        return _resubst(self.tgt[tgt_key], self.__iresubst)

    #========================================================================
    def __getitem__nonstrict(self, key):
        tgt_key = self.__rename.get(key,key)
        return _resubst(self.tgt[tgt_key], self.__iresubst)

    #========================================================================
    def __setitem__(self, key, value):
        return self.__setitem__impl(key, value)

    #========================================================================
    def __setitem__strict(self, key, value):
        # FIXME: What may seem to be irrational is that we actually can't
        # insert to tgt items that are not already covered by __rename hash.
        # Maybe we should provide some default way of extending __rename when
        # setting new items in strict mode?
        tgt_key = self.__rename[key]
        tgt_val = _resubst(value, self.__resubst)
        self.tgt[tgt_key] = tgt_val

    #========================================================================
    def __setitem__nonstrict(self, key, value):
        tgt_key = self.__rename.get(key,key)
        tgt_val = _resubst(value, self.__resubst)
        self.tgt[tgt_key] = tgt_val

    #========================================================================
    def _get_strict(self, key, default=None):
        tgt_key = self.__rename[key]
        return _resubst(self.tgt.get(tgt_key, default), self.__iresubst)

    #========================================================================
    def _get_nonstrict(self, key, default=None):
        tgt_key = self.__rename.get(key,key)
        return _resubst(self.tgt.get(tgt_key, default), self.__iresubst)

    #========================================================================
    def _has_key_strict(self, key):
        return self.__rename.has_key(key) and self.tgt.has_key(self.__rename[key])

    #========================================================================
    def _has_key_nonstrict(self, key):
        return self.tgt.has_key(self.__rename.get(key,key))

    #========================================================================
    def __contains__(self, key):
        return self.__contains__impl(key)

    #========================================================================
    def __contains__strict(self, key):
        return self.__rename.has_key(key) and self.tgt.__contains__(self.__rename[key])

    #========================================================================
    def __contains__nonstrict(self, key):
        return self.tgt.__contains__(self.__rename.get(key,key))

    #========================================================================
    def _items_strict(self):
        iresubst = lambda v : _resubst(v, self.__iresubst)
        return [ (k, self[k]) for k in self.__rename ]

    #========================================================================
    def _items_nonstrict(self):
        iresubst = lambda v : _resubst(v, self.__iresubst)
        irename = lambda k : self.__irename.get(k,k)
        return [ (irename(k), iresubst(v)) for (k,v) in self.tgt.items() ]

    #========================================================================
    def subst(self, string, *args):
        """Interpolates construction variables from the Environment into the
        specific string, returning expanded result.

        This is merely same as

        .. python::

            self.tgt.subst(_resubst(string, self.__resubst), *args)


        The core job of interpolating the variables is left to the ``tgt``.
        What the method does is to replace *Argument* names with their
        construction variable names before substitution is made.
        """
        return self.tgt.subst(_resubst(string, self.__resubst), *args)

#############################################################################
class _VariablesWrapper(object):
    """Wrapper class used to overcome several issues with original
    implementation of SCons Variables."""

    #========================================================================
    def __init__(self, variables):
        self.variables = variables

    #========================================================================
    def __getattr__(self, attr):
        return getattr(self.variables, attr)

    #========================================================================
    def Update(self, env, args):
        # One reason why it's reimplemented here is to get rid of env.subst(...)
        # substitutions that are present in the original SCons implementation
        # of Variables.Update(). The other is handling of the special _undef
        # value. If a variable's value is _undef, the corresponding construction
        # variable will not be created (env[varname] will raise keyerror,
        # unless it was created by someone else).
        import os
        import sys

        variables = self.variables
        values = {}

        # first set the defaults:
        for option in variables.options:
            if not option.default is None:
                values[option.key] = option.default

        # next set the value specified in the options file
        for filename in variables.files:
            if os.path.exists(filename):
                dir = os.path.split(os.path.abspath(filename))[0]
                if dir:
                    sys.path.insert(0, dir)
                try:
                    values['__name__'] = filename
                    exec open(filename, 'rU').read() in {}, values
                finally:
                    if dir:
                        del sys.path[0]
                    del values['__name__']

        # set the values specified on the command line
        if args is None:
            args = variables.args

        for arg, value in args.items():
            added = False
            for option in variables.options:
                if arg in list(option.aliases) + [ option.key ]:
                    values[option.key] = value
                    added = True
            if not added:
                variables.unknown[arg] = value

        # put the variables in the environment:
        # (don't copy over variables that are not declared as options)
        for option in variables.options:
            try:
                if values[option.key] is not _undef:
                    env[option.key] = values[option.key]
            except KeyError:
                pass

        # Call the convert functions:
        for option in variables.options:
            if option.converter and option.key in values and values[option.key] is not _undef:
                value = env.get(option.key)
                try:
                    try:
                        env[option.key] = option.converter(value)
                    except TypeError:
                        env[option.key] = option.converter(value, env)
                except ValueError, x:
                    raise SCons.Errors.UserError('Error converting option: %s\n%s'%(option.key, x))


        # Finally validate the values:
        for option in variables.options:
            if option.validator and option.key in values:
                option.validator(option.key, env.get(option.key), env)

#############################################################################
class _Arguments(object):
    #========================================================================
    """A dict-like object which correlates construction variables from SCons
    environment with command-line variables (``variable=value``) and
    command-line options (``--option=value``).

    **Note**:

        In several places we use ``ns`` as placeholder for one of the ``ENV``,
        ``VAR`` or ``OPT`` constants which represent selection of
        "corresponding Environment construction variable", "corresponding SCons
        command-line variable" or "corresponding SCons command-line option"
        respectively.  So, for example the call ``args.get_key(ENV,"foo")``
        returns the key of construction variable in SCons environment (``ENV``)
        which is "bound" to our *Argument* ``foo``.

    In fact, the only internal data the object holds is a list of supplementary
    dictionaries to map the names of variables from one namespace (e.g ``ENV``)
    to another (e.g. ``OPT``).
    """
    #========================================================================

    #========================================================================
    def __init__(self, decls):
        # -------------------------------------------------------------------
        """Initializes `_Arguments` object from *Argument* Declarations `decls`.

        :Parameters:
            decls : `_ArgumentDecls`
                declarations of *Arguments*,
        """
        # -------------------------------------------------------------------
        self.__keys = decls.keys()
        self.__init_supp_dicts(decls)

    #========================================================================
    def __reset_supp_dicts(self):
        """Initialize empty supplementary dictionaries to empty state"""
        self.__rename = [{} for n in range(0,ALL)]
        self.__irename = [{} for n in range(0,ALL)]
        self.__resubst = [{} for n in range(0,ALL)]
        self.__iresubst = [{} for n in range(0,ALL)]

    #========================================================================
    def __init_supp_dicts(self, decls):
        """Initialize supplementary dictionaries according to variable
        declarations."""
        self.__reset_supp_dicts()
        if decls is not None:
            for ns in range(0,ALL):
                self.__rename[ns] = decls.get_rename_dict(ns)
                self.__irename[ns] = decls.get_irename_dict(ns)
                self.__resubst[ns] = decls.get_resubst_dict(ns)
                self.__iresubst[ns] = decls.get_iresubst_dict(ns)

    #========================================================================
    def VarEnvProxy(self, env, *args, **kw):
        """Return proxy to SCons environment `env` which uses keys from
        `VAR` namespace to access corresponding environment construction
        variables"""
        rename = _compose_mappings(self.__irename[VAR], self.__rename[ENV])
        irename = _invert_dict(rename)
        resubst = _build_resubst_dict(rename)
        iresubst = _build_resubst_dict(irename)
        return _ArgumentsProxy(env, rename, resubst, irename, iresubst, *args, **kw)

    #========================================================================
    def OptEnvProxy(self, env, *args, **kw):
        """Return proxy to SCons environment `env` which uses keys from
        `OPT` namespace to access corresponding environment construction
        variables"""
        rename = _compose_mappings(self.__irename[OPT], self.__rename[ENV])
        irename = _invert_dict(rename)
        resubst = _build_resubst_dict(rename)
        iresubst = _build_resubst_dict(irename)
        return _ArgumentsProxy(env, rename, resubst, irename, iresubst, *args, **kw)

    #========================================================================
    def EnvProxy(self, env, *args, **kw):
        """Return proxy to SCons environment `env` which uses original keys
        identifying *Arguments* to access construction variables"""
        return _ArgumentsProxy(env, self.__rename[ENV], self.__resubst[ENV],
                                  self.__irename[ENV], self.__iresubst[ENV],
                                  *args, **kw)

    #========================================================================
    def get_keys(self):
        """Return the list of keys identifying *Arguments* defined in
        this object (list of *Argument* names)."""
        return self.__keys[:]

    #========================================================================
    def get_key(self, ns, key):
        #--------------------------------------------------------------------
        """Map *Argument* to a variable from `ENV`, `VAR` or `OPT` namespace.
        Maps only names (keys), not values.

        :Parameters:
            ns : int
                namespace identifier, one of `ENV`, `VAR` or `OPT`,
            key : string
                the input key (*Argument* name) to be mapped.

        :Return:
            The name of mapped variable (resultant key) from namespace ``ns``.

        **Example**::

            import SConsArguments
            decls = SConsArguments.DeclareArguments(
                foo = { 'env_key' : 'ENV_FOO',
                        'var_key' : 'VAR_FOO',
                        'opt_key' : 'OPT_FOO', 'option' : '--foo' },
                bar = { 'env_key' : 'ENV_BAR',
                        'var_key' : 'VAR_BAR',
                        'opt_key' : 'OPT_BAR', 'option' : '--bar' }
            )
            args = decls.Commit()
            assert(args.get_key(SConsArguments.ENV, 'foo') == 'ENV_FOO')
            assert(args.get_key(SConsArguments.VAR, 'foo') == 'VAR_FOO')
            assert(args.get_key(SConsArguments.OPT, 'foo') == 'OPT_FOO')
            assert(args.get_key(SConsArguments.ENV, 'bar') == 'ENV_BAR')
            assert(args.get_key(SConsArguments.VAR, 'bar') == 'VAR_BAR')
            assert(args.get_key(SConsArguments.OPT, 'bar') == 'OPT_BAR')
        """
        #--------------------------------------------------------------------
        return self.__rename[ns][key]

    #========================================================================
    def env_key(self, key):
        return self.__rename[ENV][key]

    #========================================================================
    def var_key(self, key):
        return self.__rename[VAR][key]

    #========================================================================
    def opt_key(self, key):
        return self.__rename[OPT][key]

    #========================================================================
    def update_env_from_vars(self, env, variables, args=None):
        #--------------------------------------------------------------------
        """Update construction variables in SCons environment
        (``env["VARIABLE"]=VALUE``) according to values stored in their
        corresponding command-line variables (``variable=value``).

        **Note**:

            This function calls the `variables.Update(proxy[,args])`_ method
            passing `env` proxy (see `_ArgumentsProxy`) to the method in
            order to enable mappings between ``ENV`` and ``VAR`` namespaces.

        :Parameters:
            env
                `SCons environment`_ object to be updated,
            variables
                `SCons variables`_ object to take values from

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        .. _SCons variables: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        .. _variables.Update(proxy[,args]): http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html#Update
        """
        #--------------------------------------------------------------------
        proxy = self.VarEnvProxy(env)
        _VariablesWrapper(variables).Update(proxy,args)


    #========================================================================
    def update_env_from_opts(self, env):
        #--------------------------------------------------------------------
        """Update construction variables in SCons environment
        (``env["VARIABLE"]=VALUE``) according to values stored in their
        corresponding `command-line options`_ (``--option=value``).

        :Parameters:
            env
                `SCons environment`_ object to be updated

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        .. _command-line options: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-options
        """
        #--------------------------------------------------------------------
        from SCons.Script.Main import GetOption
        proxy = self.OptEnvProxy(env)
        for opt_key in self.__irename[OPT]:
            opt_value = GetOption(opt_key)
            # FIXME: why not pass None to environment (currently it's skipped)?
            if opt_value is not None and opt_value is not _undef:
                proxy[opt_key] = opt_value

    #========================================================================
    def UpdateEnvironment(self, env, variables=None, use_options=False, args=None):
        #--------------------------------------------------------------------
        """Update construction variables in SCons environment
        (``env["VARIABLE"]=VALUE``) according to values stored in their
        corresponding `command-line variables`_ (``variable=value``) and/or
        `command-line options`_ (``--option=value``).

        :Parameters:
            env
                `SCons environment`_ object to update,
            variables : ``SCons.Variables.Variables`` | None
                if not ``None``, it should be a `SCons.Variables.Variables`_
                object with `SCons variables`_ to retrieve values from,
            use_options : boolean
                if ``True``, `command-line options`_ are taken into account
                when updating `env`.
            args
                if not ``None``, passed verbatim to `update_env_from_vars()`.

        .. _SCons.Variables.Variables: http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html
        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        .. _command-line variables: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        .. _SCons variables: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        .. _command-line options: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-options
        """
        #--------------------------------------------------------------------
        # TODO: implement priority?
        if variables is not None:
            self.update_env_from_vars(env, variables, args)
        if use_options:
            self.update_env_from_opts(env)

    def SaveVariables(self, variables, filename, env):
        #--------------------------------------------------------------------
        """Save the `variables` to file mapping appropriately their names.

        :Parameters:
            variables : ``SCons.Variables.Variables``
                if not ``None``, it should be an instance of
                `SCons.Variables.Variables`_; this object is used to save
                SCons variables,
            filename : string
                name of the file to save into
            env
                `SCons environment`_ object to update,

        .. _SCons.Variables.Variables: http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html
        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        proxy = self.VarEnvProxy(env)
        _VariablesWrapper(variables).Save(filename, proxy)

    def GenerateVariablesHelpText(self, variables, env, *args, **kw):
        #--------------------------------------------------------------------
        """Generate help text for `variables` using
        ``variables.GenerateHelpText()``.

        Note:
            this function handles properly mapping names between namespaces
            where SCons command line variables and construction variables live.

        :Parameters:
            variables : ``SCons.Variables.Variables``
                if not ``None``, it should be an instance of
                `SCons.Variables.Variables`_; this object is used to save
                SCons variables,
            env
                `SCons environment`_ object to update,
            args
                other arguments passed verbatim to ``GenerateHelpText()``

        .. _SCons.Variables.Variables: http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html
        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        proxy = self.VarEnvProxy(env)
        return _VariablesWrapper(variables).GenerateHelpText(proxy, *args, **kw)

    def GetCurrentValues(self, env):
        #--------------------------------------------------------------------
        """Get current values of *Arguments* stored in environment

        :Parameters:
            env
                `SCons environment`_ object to update,
        :Return:
            Dict containing current values.

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        res = {}
        proxy1 = self.EnvProxy(env, strict = True)
        proxy2 = self.EnvProxy(res, strict = True)
        for k in self.__keys:
            try:
                v = proxy1[k]
            except KeyError:
                # note: KeyError can be triggered by env.
                pass
            else:
                proxy2[k] = v
        return res

    @staticmethod
    def _is_unaltered(cur, org, v):
        #--------------------------------------------------------------------
        """Whether variable ``cur[v]`` has changed its value w.r.t. ``org[v]``.

        :Parameters:
            cur
                *Argument* proxy to `SCons Environment`_ or simply to a
                dictionary which holds current values of variables. An
                `_ArgumentsProxy` object.
            org
                *Argument* proxy to a dictionary containig original values of
                *Arguments*.
            v
                *Argument* name to be verified.

        :Return:
            ``True`` or ``False``

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        result = False
        try:
            curval = cur[v]
        except KeyError:
            try:
                org[v]
            except KeyError:
                result = True
        else:
            try:
                orgval = org[v]
            except KeyError:
                # cur[v] has been created in the meantime
                pass
            else:
                if curval == orgval:
                    result = True
        return result

    def GetUnaltered(self, env, org):
        #--------------------------------------------------------------------
        """Return *Arguments* which are not changed with respect to **org**.

        :Parameters:
            env
                `SCons environment`_ object or simply a dictionary which holds
                current values of *Arguments*.
            org
                Dict containing orginal (default) values of variables.

        :Return:
            Dictionary with *Arguments* that didn't change their value. The
            keys are in ENV namespace (i.e. they're same as keys in **env**).

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        res = {}
        envp = self.EnvProxy(env, strict = True)
        orgp = self.EnvProxy(org, strict = True)
        resp = self.EnvProxy(res, strict = True)
        for k in self.__keys:
            if _Arguments._is_unaltered(envp, orgp, k):
                resp[k] = envp[k]
        return res

    def GetAltered(self, env, org):
        #--------------------------------------------------------------------
        """Return *Arguments* which have changed with respect to orig.

        :Parameters:
            env
                `SCons environment`_ object or simply a dictionary which holds
                current values of *Arguments*.
            org
                Dict containing original (default) values of variables.

        :Return:
            Dictionary with *Arguments* that changed their value. The keys are
            in ENV namespace (i.e. they're same as keys in **env**).

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        res = {}
        envp = self.EnvProxy(env, strict = True)
        orgp = self.EnvProxy(org, strict = True)
        resp = self.EnvProxy(res, strict = True)
        for k in self.__keys:
            if not _Arguments._is_unaltered(envp, orgp, k):
                resp[k] = envp[k]
        return res

    def ReplaceUnaltered(self, env, org, new):
        #--------------------------------------------------------------------
        """Replace values of unaltered *Arguments* in **env** with
        corresponding values from **new**.

        For every *Argument* stored in **env**, if its value is same as
        corresponding value in **org** the value in **env** gets replaced with
        corresponding value in **new**.

        :Parameters:
            env
                `SCons environment`_ object or simply a dict which holds
                curreng values of *Arguments*. It's also being updated with new
                values,
            org
                Dict containing orginal (default) values of variables
            new
                Dict with new values to be used to update entries in **env**.

        :Return:
            A dictionary containing only the values from **new** that were
            assigned to **env**.

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        chg = {}
        envp = self.EnvProxy(env, strict = True)
        orgp = self.EnvProxy(org, strict = True)
        chgp = self.EnvProxy(chg, strict = True)
        for k in self.__keys:
            if _Arguments._is_unaltered(envp, orgp, k):
                try:
                    envp[k] = new[k]
                    chgp[k] = new[k] # Backup the values we've changed.
                except KeyError:
                    pass
        return chg

    def WithUnalteredReplaced(self, env, org, new):
        #--------------------------------------------------------------------
        """Return result of replacing *Arguments* stored in **env** with
        corresponding values from **new**, replacing only unaltered values.

        :Parameters:
            env
                `SCons environment`_ object or simply a dict which holds
                current values of *Arguments*.
            org
                Dict containing orginal (default) values of variables
            new
                Dict with new values to be used instead of those from **env**.

        :Return:
            New dictionary with values taken from **env** with some of them
            overwriten by corresponding values from **new**.

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        res = {}
        envp = self.EnvProxy(env, strict = True)
        orgp = self.EnvProxy(org, strict = True)
        resp = self.EnvProxy(res, strict = True)
        for k in self.__keys:
            if _Arguments._is_unaltered(envp, orgp, k):
                try:
                    resp[k] = new[k]
                except KeyError:
                    resp[k] = envp[k]
            else:
                resp[k] = envp[k]
        return res

    def Postprocess(self, env, variables=None, options=False, ose={},
                    args=None, filename=None):
        #--------------------------------------------------------------------
        """Postprocess **variables** and **options** updating variables in
        **env** and optionally saving them to file.

        This method gathers values from **variables**, **options** and
        writes them to **env**. After that it optionally saves the variables
        to file (if **filename** is given) and updates variables with values
        from **ose** (only those that were not changed by **variables** nor the
        **options**).

        The effect of this method is the following:

        - command line **variables** are handled,
        - command line **options** are handled,
        - command line **variables** are saved to filename if requested,
        - additional source **ose** (usually ``os.environ``) handled,

        The values from **ose** are not written to file. Also, they influence
        only variables that were not set by **variables** nor the **options**.
        The intent is to not let the variables from OS environment to overwrite
        these provided by commandline (or retrieved from file).

        **Example**::

            # SConstruct
            import os
            from SConsArguments import DeclareArguments

            env = Environment()
            var = Variables('.scons.variables')
            gds = DeclareArguments( foo = { 'env_key' : 'foo', 'var_key' : 'foo' } )
            gvs = gds.Commit(env, var, False)
            gvs.Postprocess(env, var, False, os.environ, filename = '.scons.variables')

            print "env['foo']: %r" % env['foo']

        Sample session (the sequence order of the following commands is
        important)::

            ptomulik@tea:$ rm -f .scons.variables

            ptomulik@tea:$ scons -Q
            env['foo']: None
            scons: `.' is up to date.

            ptomulik@tea:$ foo=ose scons -Q
            env['foo']: 'ose'
            scons: `.' is up to date.

            ptomulik@tea:$ scons -Q
            env['foo']: None
            scons: `.' is up to date.

            ptomulik@tea:$ foo=ose scons -Q foo=var
            env['foo']: 'var'
            scons: `.' is up to date.

            ptomulik@tea:$ cat .scons.variables
            foo = 'var'

            ptomulik@tea:$ scons -Q
            env['foo']: 'var'
            scons: `.' is up to date.

            ptomulik@tea:$ foo=ose scons -Q
            env['foo']: 'var'
            scons: `.' is up to date.

            ptomulik@tea:$ rm -f .scons.variables
            ptomulik@tea:$ foo=ose scons -Q
            env['foo']: 'ose'
            scons: `.' is up to date.

        :Parameters:
            env
                `SCons environment`_ object which holds current values of
                *Arguments*.
            variables : ``SCons.Variables.Variables`` | None
                if not ``None``, it should be a `SCons.Variables.Variables`_
                object with `SCons variables`_ to retrieve values from,
            options : boolean
                if ``True``, `command-line options`_ are taken into account
                when updating `env`.
            ose : dict
                third source of data, usually taken from ``os.environ``
            args
                passed as **args** to `UpdateEnvironment()`.
            filename : str|None
                Name of the file to save current values of **variables**.
                By default (``None``) variables are not saved.

        :Return:
            New dictionary with only entries updated by either of the data
            sources (variables, options or ose).

        :Note:
            Often you will have to preprocess ``os.environ`` before passing it
            as **ose**. This is necessary especially when your *Argument* use
            ``converter``. In that case you have to pass values from
            ``os.environ`` through a similar converter too.

        .. _SCons.Variables.Variables: http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html
        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        .. _SCons variables: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        .. _command-line options: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-options
        """
        #--------------------------------------------------------------------
        org = self.GetCurrentValues(env)
        self.UpdateEnvironment(env, variables, options, args)
        alt = self.GetAltered(env, org)
        if filename:
            self.SaveVariables(variables, filename, env)
        chg = self.ReplaceUnaltered(env, org, ose)
        alt.update(chg)
        return alt

    def Unmangle(self, env):
        #--------------------------------------------------------------------
        """Return dictionary containing variable values with original names.

        It is possible, that names of *Arguments* are not same as names of
        their associated construction variables in **env**. This function
        returns a new dictionary having original *Argument* names as keys.

        **Example**::

            # SConstruct
            from SConsArguments import DeclareArguments

            env = Environment()
            gds = DeclareArguments( foo = { 'env_key' : 'env_foo' } )
            gvs = gds.Commit(env)
            var = gvs.Unmangle(env)

            try:
                print "env['foo']: %r" % env['foo']
            except KeyError:
                print "env['foo'] is missing"

            try:
                print "env['env_foo']: %r" % env['env_foo']
            except KeyError:
                print "env['foo'] is missing"

            try:
                print "var['foo']: %r" % var['foo']
            except KeyError:
                print "var['foo'] is missing"

        The result of running the above SCons script is::

            ptomulik@tea:$ scons -Q
            env['foo'] is missing
            env['env_foo']: None
            var['foo']: None
            scons: `.' is up to date.

        :Parameters:
            env
                `SCons environment`_ object or simply a dict which holds
                current values of *Arguments*.

        :Return:
            New dictionary with keys transformed back to *Argument* namespace.

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        proxy = self.EnvProxy(env, strict=True)
        res = {}
        for k in self.__keys:
            try:
                res[k] = proxy[k]
            except KeyError:
                pass
        return res

#############################################################################
class _ArgumentDecl(object):
    #========================================================================
    """Declaration of single *Argument*.

    This object holds information necessary to create construction variable in
    SCons Environment, SCons command-line variable (``variable=value``) and
    SCons command-line option (``--option=value``) corresponding to a given
    *Argument* (it for example holds the names and default values of
    these variables/options before they get created).

    **Note**:

        In several places we use ``ns`` as placeholder for one of the ``ENV``,
        ``VAR`` or ``OPT`` constants which represent selection of
        "corresponding Environment construction variable", "corresponding SCons
        command-line variable" or "corresponding SCons command-line option"
        respectively.  So, for example the call ``decl.set_decl(ENV,decl)``
        stores the declaration of corresponding construction variable in a
        SCons environment (``ENV``).
    """
    #========================================================================


    #========================================================================
    def __init__(self, env_decl=None, var_decl=None, opt_decl=None):
        #--------------------------------------------------------------------
        """Constructor for _ArgumentDecl object

        :Parameters:
            env_decl
                parameters used later to create related construction variable
                in `SCons environment`_, same as ``decl`` argument to
                `set_env_decl()`,
            var_decl
                parameters used later to create related `SCons command-line
                variable`_, same as ``decl`` argument to `set_var_decl()`,
            opt_decl
                parameters used later to create related `SCons command-line
                option`_, same as  ``decl`` argument to `set_opt_decl()`.

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        .. _SCons command-line option: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-options
        .. _SCons command-line variable: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        """
        #--------------------------------------------------------------------
        # __decl_tab is an internal 3-element list and holds argument info
        #            for ENV, VAR and OPT endpoints.
        self.__decl_tab = [None,None,None]
        if env_decl: self.set_env_decl(env_decl)
        if var_decl: self.set_var_decl(var_decl)
        if opt_decl: self.set_opt_decl(opt_decl)

    #========================================================================
    def set_decl(self, ns, decl):
        #--------------------------------------------------------------------
        """Set declaration of related *endpoint* variable in `ns` namespace,
        where `ns` is one of `ENV`, `VAR` or `OPT`.

        This functions just dispatches the job between `set_env_decl()`,
        `set_var_decl()` and `set_opt_decl()` according to `ns` argument.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`,
            decl
                declaration parameters passed to particular setter function.
        """
        #--------------------------------------------------------------------
        if ns == ENV:     self.set_env_decl(decl)
        elif ns == VAR:   self.set_var_decl(decl)
        elif ns == OPT:   self.set_opt_decl(decl)
        else:               raise IndexError("index out of range")

    #========================================================================
    def set_env_decl(self, decl):
        #--------------------------------------------------------------------
        """Set parameters for later creation of the related construction
        variable in `SCons environment`_.

        :Parameters:
            decl : tuple | dict | str
                may be a tuple in form ``("name", default)``, one-entry
                dictionary ``{"name": default}`` or just a string ``"name"``;
                later, when requested, this data is used to create construction
                variable for user-provided `SCons environment`_ ``env`` with
                ``env.SetDefault(name = default)``

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        if SCons.Util.is_Tuple(decl):
            if not len(decl) == 2:
                raise ValueError("tuple 'decl' must have 2 elements but " \
                                 "has %d" % len(decl))
            decl = { 'key' : decl[0], 'default' : decl[1] }
        elif SCons.Util.is_Dict(decl):
            if not len(decl) == 1:
                raise ValueError("dictionary 'decl' must have 1 item but " \
                                 "has %d" % len(decl))
            first = decl.items()[0]
            decl = { 'key' : first[0], 'default' : first[1] }
        elif SCons.Util.is_String(decl):
            decl = { 'key' : decl,  'default' : _undef }
        else:
            raise TypeError("'decl' must be tuple, dictionary or string, %r " \
                            "is not allowed" % type(decl).__name__)
        self.__decl_tab[ENV] = decl

    #========================================================================
    def set_var_decl(self, decl):
        #--------------------------------------------------------------------
        """Set parameters for later creation of the related `SCons command-line
        variable`_.

        :Parameters:
            decl : tuple | dict
                declaration parameters used later to add the related `SCons
                command-line variable`_; if `decl` is a tuple, it must have
                the form::

                    ( key [, help, default, validator, converter, kw] ),

                where entries in square brackets are optional; the consecutive
                elements  are interpreted in order shown above as ``key``,
                ``help``, ``default``, ``validator``, ``converter``, ``kw``;
                the meaning of these arguments is same as for
                `SCons.Variables.Variables.Add()`_; the ``kw``, if present,
                must be a dictionary;

                if `decl` is a dictionary, it should have the form::

                    { 'key'         : "file_name",
                      'help'        : "File name to read", ...  }

                the ``'kw'`` entry, if present, must be a dictionary; the
                arguments enclosed in the dictionary are later passed verbatim
                to `SCons.Variables.Variables.Add()`_.

        .. _SCons.Variables.Variables.Add(): http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html#Add
        .. _SCons command-line variable: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        """
        #--------------------------------------------------------------------
        if SCons.Util.is_Tuple(decl) or SCons.Util.is_List(decl):
            keys = [ 'key', 'help', 'default', 'validator', 'converter', 'kw' ]
            if len(decl) > len(keys):
                raise ValueError('len(decl) should be less or greater than ' \
                                 '%d, but is %d' % (len(keys),len(decl) ))
            args = dict(zip(keys, decl))
        elif SCons.Util.is_Dict(decl):
            args = decl.copy()
        else:
            raise TypeError("'decl' must be a list, tuple or dict, %r " \
                            "is not allowed" % type(decl).__name__)
        try:
            kw = args['kw']
            del args['kw']
        except KeyError:
            kw = {}
        if not SCons.Util.is_Dict(kw):
            raise TypeError("decl['kw'] must be a dictionary, %r is not " \
                            "allowed" % type(kw).__name__)
        kw.update(args)
        self.__decl_tab[VAR] = kw

    #========================================================================
    def set_opt_decl(self, decl):
        #--------------------------------------------------------------------
        """Set parameters for later creation of the related `SCons command-line
        option`_.

        :Parameters:
            decl : tuple | list | dict
                declaration parameters used later when creating the related
                `SCons command-line option`_; if it is a tuple or list, it
                should have the form::

                        (names, args) or [names, args]

                where ``names`` is a string or tuple of option names (e.g.
                ``"-f --file"`` or ``('-f', '--file')``) and ``args`` is a
                dictionary defining the remaining `option attributes`_; the
                entire `decl` may be for example::

                    ( ('-f','--file-name'),
                      { 'action'         : "store",
                        'dest'           : "file_name" } )

                if `decl` is a dictionary, it should have following form
                (keys are important, values are just examples)::

                    { 'names'          : ("-f", "--file-name")
                      'action'         : "store",
                      'type'           : "string",
                      'dest'           : "file_name", ... }

                or::

                    { 'names'          : ("-f", "--file-name")
                      'kw' : { 'action'         : "store",
                               'type'           : "string",
                               'dest'           : "file_name", ... } }

                the parameters enclosed in ``decl`` dictionary are later
                passed verbatim to `SCons.Script.Main.AddOption()`_.
                Note, that we require the ``dest`` parameter.

        .. _SCons.Script.Main.AddOption(): http://www.scons.org/doc/latest/HTML/scons-api/SCons.Script.Main-module.html#AddOption
        .. _SCons command-line option: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-options
        .. _option attributes: http://docs.python.org/2/library/optparse.html#option-attributes
        """
        #--------------------------------------------------------------------
        if SCons.Util.is_Tuple(decl) or SCons.Util.is_List(decl):
            try:
                if SCons.Util.is_String(decl[0]):
                    names = tuple(decl[0].split())
                elif SCons.Util.is_Tuple(decl[0]):
                    names = decl[0]
                elif SCons.Util.is_List(decl[0]):
                    names = tuple(decl[0])
                else:
                    raise TypeError("decl[0] must be a string, tuple or list, %s "\
                                    "is not allowed" % type(decl[0]).__name__)
            except IndexError:
                raise ValueError("'decl' must not be empty, got %(decl)r" % locals())
            try:
                kw  = decl[1]
            except IndexError:
                kw = {}
        elif SCons.Util.is_Dict(decl):
            if SCons.Util.is_String(decl['names']):
                names = tuple(decl['names'].split())
            elif SCons.Util.is_Tuple(decl['names']):
                names = decl['names']
            elif SCons.Util.is_List(decl['names']):
                names = tuple(decl['names'])
            else:
                raise TypeError("decl['names'] must be a string, tuple or list, %s "\
                                "is not allowed" % type(decl['names']).__name__)
            try:
                kw = decl['kw']
            except KeyError:
                kw = decl.copy()
                del(kw['names'])
        else:
            raise TypeError("'decl' must be a tuple list or dictionary, %s " \
                            "is not allowed" % type(decl).__name__)
        if 'dest' not in kw:
            raise ValueError("'dest' parameter is missing")
        self.__decl_tab[OPT] = (names, kw)

    #========================================================================
    def has_decl(self, ns):
        #--------------------------------------------------------------------
        """Test if declaration of corresponding `ns` variable was provided,
        where `ns` is one of `ENV`, `VAR` or `OPT`.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`
        :Returns:
            ``True`` if the declaration exists, or ``False`` otherwise.
        """
        #--------------------------------------------------------------------
        return self.__decl_tab[ns] is not None

    #========================================================================
    def has_env_decl(self):
        """Same as `has_decl(ENV)`"""
        return self.has_decl(ENV)

    #========================================================================
    def has_var_decl(self):
        """Same as `has_decl(VAR)`"""
        return self.has_decl(VAR)

    #========================================================================
    def has_opt_decl(self):
        """Same as `has_decl(OPT)`"""
        return self.has_decl(OPT)

    #========================================================================
    def get_decl(self, ns):
        #--------------------------------------------------------------------
        """Return internal representation of declaration for *Endpoint*
        variable from `ns` namespace.

        If the corresponding `ns` declaration does not exist, or `ns` is out of
        range, the method throws an IndexError.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`
        :Returns:
            The corresponding declaration
        """
        #--------------------------------------------------------------------
        if (ns < 0) or ns > ALL:
            raise IndexError("index out of range")
        elif not self.has_decl(ns):
            nsstr = [ 'ENV', 'VAR', 'OPT' ]
            raise IndexError("there is no %s declaration in this _ArgumentDecl" % nsstr[ns])
        return self.__decl_tab[ns]

    #========================================================================
    def get_env_decl(self):
        """Same as `get_decl(ENV)`"""
        return self.get_decl(ENV)

    #========================================================================
    def get_var_decl(self):
        """Same as `get_decl(VAR)`"""
        return self.get_decl(VAR)

    #========================================================================
    def get_opt_decl(self):
        """Same as `get_decl(OPT)`"""
        return self.get_decl(OPT)

    #========================================================================
    def get_key(self, ns):
        #--------------------------------------------------------------------
        """Returns the key (variable name) identifying *endpoint* variable in
        namespace `ns`, where `ns` is one of `ENV`, `VAR` or `OPT`.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`
        :Returns:
            ``decl`` parameters stored by last call `set_decl(ns,decl)`.
        """
        #--------------------------------------------------------------------
        decl = self.get_decl(ns)
        if ns == ENV:
            return decl['key']
        elif ns == VAR:
            return decl['key']
        elif ns == OPT:
            return decl[1]['dest']
        else:
            raise IndexError("index out of range")

    #========================================================================
    def get_env_key(self):
        """Same as `get_key(ENV)`"""
        return self.get_key(ENV)

    #========================================================================
    def get_var_key(self):
        """Same as `get_key(VAR)`"""
        return self.get_key(VAR)

    #========================================================================
    def get_opt_key(self):
        """Same as `get_key(OPT)`"""
        return self.get_key(OPT)

    #========================================================================
    def set_key(self, ns, key):
        #--------------------------------------------------------------------
        """Define the identifying key of corresponding `ns` variable, where
        `ns` is one of `ENV`, `VAR` or `OPT`.

        The corresponding declaration must exists, that is ``has_decl(ns)``
        must be ``True``. Otherwise, ``IndexError`` will be raised.

        **Warning**
            This function should not be used by users. To change the key of
            corresponding `ns` variable, use `_ArgumentDecls.set_key()`.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`
            key : string
                new key for the corresponding variable.
        """
        #--------------------------------------------------------------------
        decl = self.get_decl(ns)
        if ns == ENV:
            decl['key'] = key
        elif ns == VAR:
            decl['key'] = key
        elif ns == OPT:
            decl[1]['dest'] = key
        else:
            raise IndexError("index out of range")

    #========================================================================
    def set_env_key(self, key):
        """Same as `set_key(ENV, key)`"""
        self.set_key(ENV,key)

    #========================================================================
    def set_var_key(self, key):
        """Same as `set_key(VAR, key)`"""
        self.set_key(VAR,key)

    #========================================================================
    def set_opt_key(self, key):
        """Same as `set_key(OPT, key)`"""
        self.set_key(OPT,key)

    #========================================================================
    def get_default(self, ns):
        #--------------------------------------------------------------------
        """Get the default value of corresponding `ns` variable, where `ns`
        is one of `ENV`, `VAR`, `OPT`.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`
        """
        #--------------------------------------------------------------------
        decl = self.get_decl(ns)
        if ns == ENV:
            return decl.get('default', _undef)
        elif ns == VAR:
            return decl.get('default', _undef)
        elif ns == OPT:
            return decl[1].get('default', _undef)
        else:
            raise IndexError("index out of range")

    #========================================================================
    def get_env_default(self):
        """Same as `get_default(ENV)`"""
        return self.get_default(ENV)

    #========================================================================
    def get_var_default(self):
        """Same as `get_default(VAR)`"""
        return self.get_default(VAR)

    #========================================================================
    def get_opt_default(self):
        """Same as `get_default(OPT)`"""
        return self.get_default(OPT)

    #========================================================================
    def set_default(self, ns, default):
        #--------------------------------------------------------------------
        """Define the default value of corresponding `ns` variable, where
        `ns` is one of `ENV`, `VAR`, `OPT`.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`
            default
                the new default value
        """
        #--------------------------------------------------------------------
        decl = self.get_decl(ns)
        if ns == ENV:
            decl['default'] = default
        elif ns == VAR:
            decl['default'] = default
        elif ns == OPT:
            decl[1]['default'] = default
        else:
            raise IndexError("index out of range")

    #========================================================================
    def set_env_default(self, default):
        """Same as `set_default(ENV, default)`"""
        self.set_default(ENV,default)

    #========================================================================
    def set_var_default(self, default):
        """Same as `set_default(VAR, default)`"""
        self.set_default(VAR,default)

    #========================================================================
    def set_opt_default(self, default):
        """Same as `set_default(OPT, default)`"""
        self.set_default(OPT,default)

    #========================================================================
    def add_to(self, ns, *args, **kw):
        #--------------------------------------------------------------------
        """Add new corresponding construction variable, command-line variable
        or command-line option depending on the `ns` variable. The `ns` is one
        of `ENV`, `VAR` or `OPT`.

        The method actually dispatches the job between `add_to_env()`,
        `add_to_var()` and `add_to_opt()`.

        The method raises ``IndexError`` if there is no declaration for the
        given *endpoint* indicated with `ns`.

        **Examples**:

            - ``decl.add_to(ENV,env)`` creates new construction variable
              in `SCons environment`_ ``env``,
            - ``decl.add_to(VAR,vars)`` creates new command-line variable
              in `SCons variables`_ ``vars``
            - ``decl.add_to(OPT)`` creates a corresponding SCons
              `command-line option`_.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`
            args, kw
                additional arguments and keywords, depend on `ns`:

                - if ``ns == ENV``, then ``env=args[0]`` is assumed to be
                  a `SCons environment`_ to create construction variable for,
                - if ``ns == VAR`, then ``vars=args[0]`` is assumed to be
                  a SCons `Variables`_ object, ``*args[1:]`` are used as
                  positional arguments to `vars.Add()`_ and ``**kw`` are
                  passed to `vars.Add()`_ as additional keywords,
                - if ``ns == OPT``, the arguments and keywords are not used.

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        .. _SCons variables: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        .. _Variables: http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html
        .. _vars.Add(): http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html#Add
        .. _command-line option: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-options
        """
        #--------------------------------------------------------------------
        if ns == ENV:
            self.add_to_env(args[0])
        elif ns == VAR:
            self.add_to_var(args[0],*args[1:],**kw)
        elif ns == OPT:
            self.add_to_opt()
        else:
            raise IndexError("index out of range")

    #========================================================================
    def add_to_env(self, env):
        #--------------------------------------------------------------------
        """Add construction variable to `SCons environment`_ corresponding to
        this *Argument* and set it do default value.

        The method raises ``IndexError`` if there is no declaration for
        construction variable in this `_ArgumentDecl` object.

        **Remarks**:
            
            - the construction variable is "created" with ``env.SetDefault()``;
              existing construction variables are NOT overwritten by this call,
            - the construction variable is not created if the default value
              of this *Argument* for construction variable is `_undef`.

        :Parameters:
            env
                  a `SCons environment`_ to create construction variable for,

        .. _SCons environment:  http://www.scons.org/doc/HTML/scons-user.html#chap-environments
        """
        #--------------------------------------------------------------------
        decl = self.get_decl(ENV)
        default = decl.get('default', _undef)
        if default is not _undef:
            env.SetDefault(**{decl['key'] : default})

    #========================================================================
    def add_to_var(self, variables, *args, **kw):
        #--------------------------------------------------------------------
        """Add new SCons `command-line variable`_ corresponding to this *Argument*.

        The method raises ``IndexError`` if there is no declaration for the
        corresponding command-line variable in this `_ArgumentDecl` object.

        :Parameters:
            variables
                SCons `Variables`_ object,
                
            args, kw
                additional arguments and keywords, ``*args`` are used as
                positional arguments to `variables.Add()`_ and ``**kw`` are
                passed to `variables.Add()`_ as additional keywords

        .. _command-line variable: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-variables
        .. _Variables: http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html
        .. _variables.Add(): http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html#Add
        """
        #--------------------------------------------------------------------
        decl = self.get_decl(VAR)
        kw2 = decl.copy()
        kw2.update(kw)
        return variables.Add(*args,**kw2)

    #========================================================================
    def add_to_opt(self):
        #--------------------------------------------------------------------
        """Add new SCons `command-line option`_ corresponding to this *Argument*.

        The method raises ``IndexError`` if there is no declaration for the
        command-line option in this `_ArgumentDecl` object.

        .. _command-line option: http://www.scons.org/doc/HTML/scons-user.html#sect-command-line-options
        """
        #--------------------------------------------------------------------
        from SCons.Script.Main import AddOption
        decl = self.get_decl(OPT)
        AddOption(*decl[0], **decl[1])

    #========================================================================
    def safe_add_to(self, ns, *args):
        #--------------------------------------------------------------------
        """Same as `add_to()`, but does not raise exceptions when the
        corresponding `ns` variable is not declared in this `_ArgumentDecl`
        object.

        :Parameters:
            ns : int
                one of `ENV`, `VAR` or `OPT`

        :Returns:
            returns ``True`` is new variable has been created or ``False`` if
            there is no declaration for corresponding `ns` variable in this
            object.
        """
        #--------------------------------------------------------------------
        if self.has_decl(ns):
            self.add_to(ns, *args)
            return True
        else:
            return False

#############################################################################
def ArgumentDecl(*args, **kw):
    #------------------------------------------------------------------------
    """Convert input arguments to `_ArgumentDecl` instance.

   :Returns:
        - if ``args[0]`` is an instance of `_ArgumentDecl`, then returns
          ``args[0]`` unaltered,
        - otherwise returns result of `_ArgumentDecl(*args,**kw)`
    """
    #------------------------------------------------------------------------
    if len(args) > 0 and isinstance(args[0], _ArgumentDecl):
        return args[0]
    else:
        return _ArgumentDecl(*args, **kw)

#############################################################################
def DeclareArgument(env_key=None, var_key=None, opt_key=None, default=_undef,
              help=None, validator=None, converter=None, option=None,
              type=None, opt_default=None, metavar=None, nargs=None,
              choices=None, action=None, const=None, callback=None,
              callback_args=None, callback_kwargs=None):
    #------------------------------------------------------------------------
    """Convert unified set of arguments to `_ArgumentDecl` instance.

    This function accepts minimal set of parameters to declare consistently an
    *Argument* and its corresponding `ENV`, `VAR` and `OPT` counterparts.  If
    the first argument named `env_key` is an instance of `_ArgumentDecl`, then
    it is returned unaltered. Otherwise the arguments are mapped onto following
    attributes of corresponding `ENV`, `VAR` and `OPT` variables/options::

        ARG                 ENV         VAR         OPT
        ----------------+-----------------------------------------
        env_key         |   key         -           -
        var_key         |   -           key         -
        opt_key         |   -           -           dest
        default         |   default     default     -
        help            |   -           help        help
        validator       |   -           validator   -
        converter       |   -           converter   -
        option          |   -           -           option strings
        type            |   -           -           type
        opt_default     |   -           -           default
        metavar         |   -           -           metavar
        nargs           |   -           -           nargs
        choices         |   -           -           choices
        action          |   -           -           action
        const           |   -           -           const
        callback        |   -           -           callback
        callback_args   |   -           -           callback_args
        callback_kwargs |   -           -           callback_kwargs
        ----------------+------------------------------------------

    :Parameters:
        env_key : `_ArgumentDecl` | string | None
            if an instance of `_ArgumentDecl`, then this object is returned to the
            caller, key used to identify corresponding construction variable
            (`ENV`); if ``None`` the *Argument* has no corresponding
            construction variable,
        var_key : string | None
            key used to identify corresponding command-line variable (`VAR`);
            if ``None``, the *Argument* has no corresponding command-line
            variable,
        opt_key : string | None
            key used to identify corresponding command-line option (`OPT`);
            if ``None`` the *Argument* variable  has no corresponding
            command-line option,
        default
            default value used to initialize corresponding construction
            variable (`ENV`) and command-line variable (`VAR`);
            note that there is separate `opt_default` argument for command-line
            option,
        help : string | None
            message used to initialize help in corresponding command-line
            variable (`VAR`) and command-line option (`OPT`),
        validator
            same as for `SCons.Variables.Variables.Add()`_,
        converter
            same as for `SCons.Variables.Variables.Add()`_,
        option
            option string, e.g. ``"--option"`` used for corresponding
            command-line option,
        type
            same as `type` in `optparse option attributes`_,
        opt_default
            same as `default` in `optparse option attributes`_,
        metavar
            same as `metavar` in `optparse option attributes`_,
        nargs
            same as `nargs` in `optparse option attributes`_,
        choices
            same as `choices` in `optparse option attributes`_,
        action
            same as `action` in `optparse option attributes`_,
        const
            same as `const` in `optparse option attributes`_,
        callback
            same as `callback` in `optparse option attributes`_,
        callback_args
            same as `callback_args` in `optparse option attributes`_,
        callback_kwargs
            same as `callback_kwargs` in `optparse option attributes`_,

    :Returns:
        - if `env_key` is present and it is an instance of `_ArgumentDecl`, then it
          is returned unaltered,
        - otherwise returns new `_ArgumentDecl` object initialized according to
          rules given above.

    .. _SCons.Variables.Variables.Add(): http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html#Add
    .. _optparse option attributes: http://docs.python.org/2/library/optparse.html#option-attributes
    """
    #------------------------------------------------------------------------
    if isinstance(env_key, _ArgumentDecl):
        return env_key
    else:
        # --- ENV ---
        if env_key is not None:
            env_decl = { env_key : default }
        else:
            env_decl = None
        # --- VAR ---
        if var_key is not None:
            items = [ (var_key, 'key'), (default, 'default'), (help, 'help'),
                      (validator, 'validator'), (converter, 'converter') ]
            var_decl = dict([ (k, v) for (v,k) in items if v is not None ])
        else:
            var_decl = None
        # --- OPT ---
        if opt_key and option is not None:
            items = [   (opt_key, 'dest'), (opt_default, 'default'),
                        (help, 'help'), (type, 'type'), (metavar, 'metavar'),
                        (nargs, 'nargs'), (choices, 'choices'),
                        (action, 'action'), (const, 'const'),
                        (callback, 'callback'),
                        (callback_args, 'callback_args'),
                        (callback_kwargs, 'callback_kwargs') ]
            opt_decl = (option, dict( [(k, v) for (v,k) in items if v is not None] ))
        else:
            opt_decl = None
        return _ArgumentDecl(env_decl, var_decl, opt_decl)

#############################################################################
class _ArgumentDecls(dict):
    #========================================================================
    """Dictionary-like object with *Argument* declarations as values.

    The `_ArgumentDecls` object is a subclass of ``dict`` with keys being
    strings identifying declared *Arguments* and values being instances of
    `_ArgumentDecl` objects. The `_ArgumentDecls` dictionary also maintains
    *supplementary dictionaries* used internally to map names of registered
    variables between four namespaces: `ENV` (construction variables in SCons
    environment), `VAR` (command-line variables ``variable=value``), `OPT`
    (command-line options ``--option=value``) and *Argument* (the keys used to
    identify the *Arguments* declared within `_ArgumentDecls` dictionary).

    The usage of `_ArgumentDecls` may be split into three stages:

        - declaring *Arguments*; this may be done during object
          creation, see `__init__()`; further declarations may be added or
          existing ones may be modified via dictionary interface, see
          `__setitem__()`, `update()` and others,
        - committing declared variables, see `commit()`; after commit, the
          contents of `_ArgumentDecls` is "frozen" and any attempts to
          modifications end-up with a `RuntimeError` exception being raised,
        - creating related construction variables (``env["VARIABLE"]=VALUE``),
          command-line variables (``variable=value``) and command-line options
          (``--option=value``) according to committed `_ArgumentDecls`
          declarations, see `add_to()`; this may be performed by `commit()` as
          well.

    After that, an instance of `_Arguments` should be created from `_ArgumentDecls` to
    keep track of created *Arguments* (and corresponding construction
    variables, command-line variables and command-line options). The dictionary
    `_ArgumentDecls` may be then disposed.

    **Note**:

        In several places we use ``ns`` as placeholder for one of the ``ENV``,
        ``VAR`` or ``OPT`` constants which represent selection of
        "corresponding Environment construction variable", "corresponding SCons
        command line variable" or "corresponding SCons command line option"
        respectively.  So, for example the call
        ``decls.set_key(ENV,"foo","ENV_FOO")`` defines the name
        ``"ENV_FOO"`` to be used for construction variable in SCons environment
        (``ENV``) that will correspond to our *Argument* named ``foo``.
    """
    #========================================================================



    #========================================================================
    def __init__(self, *args, **kw):
        #--------------------------------------------------------------------
        """Constructor for `_ArgumentDecls`.

        ``__init__()`` initializes an empty `_ArgumentDecls` dictionary,

        ``__init__(mapping)`` initializes `_ArgumentDecls` dictionary from a
        mapping object's ``(key,value)`` pairs, each ``value`` must be
        instance of `_ArgumentDecl`,

        ``__init__(iterable)`` initializes the `_ArgumentDecls` dictionary as if
        via ``d = { }`` followed by ``for k, v in iterable: d[k] = v``.
        Each value ``v`` from ``iterable`` must be an instance of `_ArgumentDecl`,

        ``__init__(**kw)`` initializes the `_ArgumentDecls` dictionary with
        ``name=value`` pairs in the keyword argument list ``**kw``, each
        ``value`` must be an instance of `_ArgumentDecl`,
        """
        #--------------------------------------------------------------------
        self.__committed = False
        _ArgumentDecls.__validate_values(*args,**kw)
        super(_ArgumentDecls, self).__init__(*args,**kw)
        self.__update_supp_dicts()

    #========================================================================
    def __reset_supp_dicts(self):
        """Reset supplementary dictionaries to empty state"""
        self.__rename = [{} for n in range(0,ALL)]
        self.__irename = [{} for n in range(0,ALL)]
        self.__resubst = [{} for n in range(0,ALL)]
        self.__iresubst = [{} for n in range(0,ALL)]

    #========================================================================
    def __update_supp_dicts(self):
        """Update supplementary dictionaries to be in sync with the
        declarations contained in main dictionary"""
        self.__reset_supp_dicts()
        for x in self.iteritems(): self.__append_decl_to_supp_dicts(*x)

    #========================================================================
    def __replace_key_in_supp_dicts(self, ns, key, ns_key):
        #--------------------------------------------------------------------
        """Replace in the supplementary dicts the key identifying corresponding
        `ns` variable (where `ns` is one of `ENV`, `VAR` or `OPT`).

        If the corresponding `ns` variable identified by ``ns_key`` already
        exists in the supplementary dictionaries, the supplementary
        dictionaries are left unaltered.

        :Parameters:
            ns : int
                selector of the corresponding variable being renamed; one of
                `ENV`, `VAR` or `OPT`,
            key : string
                the key identifying *Argument* declared within this
                `_ArgumentDecls` dictionary, which subject to modification,
            ns_key : string
                new name for the corresponding `ns` variable.
        """
        #--------------------------------------------------------------------
        try: old_key = self.__rename[ns][key]
        except KeyError: old_key = _notfound
        if ns_key != old_key:
            self.__append_key_to_supp_dicts(ns, key, ns_key)
            try: del self.__irename[ns][old_key]
            except KeyError: pass

    #========================================================================
    def __append_key_to_supp_dicts(self, ns, key, ns_key):
        #--------------------------------------------------------------------
        """Add to supplementary dictionaries the new `ns` variable
        corresponding to *Argument* identified by `key`.

        If the corresponding `ns` variable identified by ``ns_key`` already
        exists in the supplementary dictionaries, a ``RuntimeError`` is raised.

        :Parameters:
            ns : int
                selector of the corresponding variable being renamed; one of
                `ENV`, `VAR` or `OPT`,
            key : string
                the key identifying *Argument* within this `_ArgumentDecls`
                dictionary, which subject to modification,
            ns_key : string
                new name for the corresponding `ns` variable.
        """
        #--------------------------------------------------------------------
        if ns_key in self.__irename[ns]:
            raise RuntimeError("variable %r is already declared" % ns_key)
        self.__rename[ns][key] = ns_key
        self.__irename[ns][ns_key] = key

    #========================================================================
    def __append_decl_to_supp_dicts(self, key, decl):
        for ns in range(0,ALL):
            if decl.has_decl(ns):
                ns_key = decl.get_key(ns)
                self.__append_key_to_supp_dicts(ns, key, ns_key)
        return decl

    #========================================================================
    def __del_from_supp_dicts(self, key):
        for ns in range(0,ALL):
            if key in self.__rename[ns]:
                ns_key = self.__rename[ns][key]
                del self.__rename[ns][key]
                del self.__irename[ns][ns_key]

    #========================================================================
    @staticmethod
    def __validate_values(initializer=_missing,**kw):
        if initializer is not _missing:
            try: keys = initializer.keys()
            except AttributeError:
                for (k,v) in iter(initializer): _ArgumentDecls.__validate_value(v)
            else:
                for k in keys: _ArgumentDecls.__validate_value(initializer[k])
        for k in kw: _ArgumentDecls.__validate_value(kw[k])

    #========================================================================
    @staticmethod
    def __validate_value(value):
        if not isinstance(value, _ArgumentDecl):
            raise TypeError("value must be an instance of _ArgumentDecl, %r is not allowed"  % value)

    #========================================================================
    def setdefault(self, key, value = _missing):
        if value is _missing:
            return super(_ArgumentDecls,self).setdefault(key)
        else:
            self.__ensure_not_committed()
            _ArgumentDecls.__validate_value(value)
            return super(_ArgumentDecls,self).setdefault(key, value)

    #========================================================================
    def update(self, *args, **kw):
        self.__ensure_not_committed()
        _ArgumentDecls.__validate_values(*args,**kw)
        super(_ArgumentDecls,self).update(*args,**kw)
        self.__update_supp_dicts()

    #========================================================================
    def clear(self, *args, **kw):
        self.__ensure_not_committed()
        super(_ArgumentDecls,self).clear(*args,**kw)
        self.__update_supp_dicts()

    #========================================================================
    def pop(self, key, *args, **kw):
        self.__ensure_not_committed()
        self.__del_from_supp_dicts(key)
        return super(_ArgumentDecls,self).pop(key,*args,**kw)

    #========================================================================
    def popitem(self, *args, **kw):
        self.__ensure_not_committed()
        (k,v) = super(_ArgumentDecls,self).popitem(*args,**kw)
        self.__del_from_supp_dicts(k)
        return (k,v)

    #========================================================================
    def copy(self):
        return _ArgumentDecls(self)

    #========================================================================
    def __setitem__(self, key, value):
        self.__ensure_not_committed()
        _ArgumentDecls.__validate_value(value)
        self.__append_decl_to_supp_dicts(key, value)
        return super(_ArgumentDecls,self).__setitem__(key, value)

    #========================================================================
    def __delitem__(self, key):
        self.__ensure_not_committed()
        self.__del_from_supp_dicts(key)
        return super(_ArgumentDecls,self).__delitem__(key)

    #========================================================================
    def get_rename_dict(self, ns):
        #--------------------------------------------------------------------
        """Get the dictionary mapping variable names from *Argument* namespace
        to `ns` (where `ns` is one of `ENV`, `VAR` or `OPT`).

        :Parameters:
            ns : int
                selector of the corresponding namespace; one of `ENV`, `VAR` or
                `OPT`,
        :Returns:
            dictionary with items ``(key, ns_key)``, where ``key`` is the key
            from *Argument* namespace and ``ns_key`` is variable name in the
            `ns` (`ENV`, `VAR` or `OPT`) namespace
        """
        #--------------------------------------------------------------------
        return self.__rename[ns].copy()

    #========================================================================
    def get_irename_dict(self, ns):
        #--------------------------------------------------------------------
        """Get the dictionary mapping variable names from `ns` namespace to
        *Argument* namespace (where `ns` is one of `ENV`, `VAR` or `OPT`).

        :Parameters:
            ns : int
                selector of the corresponding namespace; one of `ENV`, `VAR` or
                `OPT`,
        :Returns:
            dictionary with items ``(ns_key, key)``, where ``key`` is the key
            from *Argument* namespace and ``ns_key`` is variable name in the
            `ns` (`ENV`, `VAR` or `OPT`) namespace

        """
        #--------------------------------------------------------------------
        return self.__irename[ns].copy()

    #========================================================================
    def get_resubst_dict(self,ns):
        #--------------------------------------------------------------------
        """Get the dictionary mapping variable names from *Argument* namespace
        to placeholders for variable values from `ns` namespace (where `ns`
        is one of `ENV`, `VAR` or `OPT`).

        **Note**:

            The declarations must be committed before this function may be
            called.

        :Parameters:
            ns : int
                selector of the corresponding namespace; one of `ENV`, `VAR` or
                `OPT`,
        :Returns:
            dictionary with items ``(key, "${" + ns_key + "}")``, where
            ``key`` is the key from *Argument* namespace and ``ns_key`` is
            variable name in the `ns` (`ENV`, `VAR` or `OPT`) namespace

        """
        #--------------------------------------------------------------------
        self.__ensure_committed()
        return self.__resubst[ns].copy()

    #========================================================================
    def get_iresubst_dict(self, ns):
        #--------------------------------------------------------------------
        """Get the dictionary mapping variable names from `ns` namespace to
        placeholders for variable values from *Argument* namespace (where `ns`
        is one of `ENV`, `VAR` or `OPT`).

        **Note**:

            The declarations must be committed before this function may be
            called.

        :Parameters:
            ns : int
                selector of the corresponding namespace; one of `ENV`, `VAR` or
                `OPT`,
        :Returns:
            dictionary with items ``(ns_key, "${" + key + "}")``, where
            ``key`` is the key from *Argument* namespace and ``ns_key`` is
            variable name in the `ns` (`ENV`, `VAR` or `OPT`) namespace

        """
        #--------------------------------------------------------------------
        self.__ensure_committed()
        return self.__iresubst[ns].copy()

    #========================================================================
    def get_key(self, ns, key):
        #--------------------------------------------------------------------
        """Get the key identifying corresponding `ns` variable  (where `ns`
        is one of `ENV`, `VAR` or `OPT`).

        If the corresponding `ns` variable is not declared, the function
        raises an exception.

        :Parameters:
            ns : int
                selector of the corresponding namespace; one of `ENV`, `VAR` or
                `OPT`,
            key : string
                key identifying an already declared *Argument* variable to which
                the queried `ns` variable corresponds,

        :Returns:
            the key (name) identifying `ns` variable corresponding to our
            *Argument* identified by `key`

        """
        #--------------------------------------------------------------------
        return self[key].get_key(ns)

    #========================================================================
    def set_key(self, ns, key, ns_key):
        #--------------------------------------------------------------------
        """Change the key identifying a corresponding `ns` variable (where
        `ns` is one of `ENV`, `VAR` or `OPT`).

        If the corresponding `ns` variable is not declared, the function
        raises an exception.

        :Parameters:
            ns : int
                selector of the corresponding namespace; one of `ENV`, `VAR` or
                `OPT`,
            key : string
                key identifying an already declared *Argument* to which
                the queried `ns` variable corresponds,

        :Returns:
            the key (name) identifying `ns` variable corresponding to our
            *Argument* identified by `key`

        """
        #--------------------------------------------------------------------
        self.__ensure_not_committed()
        self[key].set_key(ns, ns_key)
        self.__replace_key_in_supp_dicts(ns, key, ns_key)

    #========================================================================
    def _add_to(self, ns, *args):
        """Invoke `_ArgumentDecl.add_to()` for each *Argument* declared
        in this dictionary."""
        for (k,v) in self.iteritems(): v.add_to(ns,*args)

    #========================================================================
    def _safe_add_to(self, ns, *args):
        """Invoke `_ArgumentDecl.safe_add_to()` for each *Argument*
        declared in this dictionary."""
        for (k,v) in self.iteritems(): v.safe_add_to(ns, *args)

    #========================================================================
    def _build_resubst_dicts(self):
        """Build supplementary dictionaries used to rename placeholders in
        values (forward, from *Argument* namespace to ``ns`` namespaces)"""
        for ns in range(0,ALL):
            self.__resubst[ns] = _build_resubst_dict(self.__rename[ns])

    #========================================================================
    def _build_iresubst_dicts(self):
        """Build supplementary dictionaries used to rename placeholders in
        values (inverse, from ``ns`` namespaces to *Argument* namespace)"""
        for ns in range(0,ALL):
            self.__iresubst[ns] = _build_iresubst_dict(self.__rename[ns])

    #========================================================================
    def _resubst_decl_defaults(self, decl):
        """Rename placeholders found in the declarations of default values of
        ``ns`` corresponding variables for the given declaration ``decl``.

        :Parameters:
            decl : _ArgumentDecl
                the *Argument* declaration to modify
        """
        for ns in range(0,ALL):
            if decl.has_decl(ns):
                val = _resubst(decl.get_default(ns), self.__resubst[ns])
                decl.set_default(ns,val)

    #========================================================================
    def __resubst_defaults(self):
        """Rename placeholders found in the declarations of default values of
        ``ns`` corresponding variables for all declared *Arguments*.
        """
        for (k,v) in self.iteritems():
            self._resubst_decl_defaults(v)

    #========================================================================
    def __ensure_not_committed(self):
        """Raise exception if the object was already committed"""
        if self.__committed:
            raise RuntimeError("declarations are already committed, can't " \
                               "be modified")
    #========================================================================
    def __ensure_committed(self):
        """Raise exception if the object was not jet committed"""
        if not self.__committed:
            raise RuntimeError("declarations must be committed before " \
                               "performing this operation")

    #========================================================================
    def commit(self, *args):
        #--------------------------------------------------------------------
        """Commit the declaration and optionally add appropriate variables to a
        SCons construction environment, command-line variables and command-line
        options.

        The function finishes declaration stage, freezes the dictionary and
        makes call to `add_to()` with ``*args`` passed verbatim to it.

        :Parameters:
            args
                positional arguments passed verbatim do `add_to()`.
        """
        #--------------------------------------------------------------------
        if not self.__committed:
            self._build_resubst_dicts()
            self._build_iresubst_dicts()
            self.__resubst_defaults()
            self.__committed = True
            self.add_to(*args)

    #========================================================================
    def add_to(self, *args):
        #--------------------------------------------------------------------
        """Create and initialize the corresponding ``ns`` variables (where
        ``ns`` is one of `ENV`, `VAR` or `OPT`).

        This function calls `safe_add_to()` for each ``ns`` from ``(ENV,
        VAR, OPT)``.

        :Parameters:
            args
                positional arguments interpreted in order as ``env``,
                ``variables``, ``options`` where:

                    - ``env`` is a SCons environment object to be updated with
                      *Arguments* defined here and their defaults,
                    - ``variables`` is a SCons Variables object for which new
                      command-line variables will be defined,
                    - ``options`` is a Boolean deciding whether the
                      corresponding command-line options should be created or
                      not (default ``False`` means 'do not create').

                All the arguments are optional. ``None`` may be used to
                represent missing argument and skip the creation of certain
                variables/options.
        """
        #--------------------------------------------------------------------
        self.__ensure_committed()
        for ns in range(0,min(len(args),ALL)):
            if args[ns]: self._safe_add_to(ns, args[ns])

    #========================================================================
    def Commit(self, env=None, variables=None, create_options=False, create_args=True, *args):
        """User interface to `commit()`, optionally returns newly created
        `_Arguments` object.

        :Parameters:
            env
                a SCons environment object to be populated with default values
                of construction variables defined by *Arguments* declared here,
            variables
                a `SCons.Variables.Variables`_ object to be populated with new
                variables defined by *Arguments* declared here,
            create_options : Boolean
                if ``True``, the command-line create_options declared by *Arguments*
                are created,
            create_args
                if ``True`` (default) create and return a `_Arguments` object for
                further operation on variables and their values,

        :Returns:
            if `create_args` is ``True``, returns newly created `_Arguments` object,
            otherwise returns ``None``.

        .. _SCons.Variables.Variables: http://www.scons.org/doc/latest/HTML/scons-api/SCons.Variables.Variables-class.html
        """
        self.commit(env, variables, create_options, *args)
        if create_args:   return _Arguments(self)
        else:       return None

#############################################################################
def __dict_converted(convert, initializer=_missing, **kw):
    """Generic algorithm for dict initialization while converting the values
    provided within initializers"""
    if initializer is _missing:
        decls = {}
    else:
        try: keys = initializer.keys()
        except AttributeError:
            decls = dict([ (k, convert(v)) for (k,v) in iter(initializer) ])
        else:
            decls = dict([ (k, convert(initializer[k])) for k in keys ])
    decls.update(dict([ (k, convert(kw[k])) for k in kw ]))
    return decls

#############################################################################
def ArgumentDecls(*args, **kw):
    """Create `_ArgumentDecls` dictionary with *Argument* declarations.

    The function supports several forms of invocation, see the section
    **Returns** to find systematic description. Here we give just a couple of
    examples.

    If the first positional argument is a mapping (a dictionary for example)
    then values from the dictionary are passed through `ArgumentDecl()` and the
    resultant dictionary is used as initializer to `ArgumentDecl`. You may for
    example pass a dictionary of the form ``{ 'foo' : (env, var, opt)}``,
    where ``env``, ``var`` and ``opt`` are parameters accepted by
    `_ArgumentDecl.set_env_decl()`, `_ArgumentDecl.set_var_decl()` and
    `_ArgumentDecl.set_opt_decl()` respectively.

    **Example**

    .. python::

        decls = {
           # Argument 'foo'
          'foo' : (   {'ENV_FOO' : 'default ENV_FOO'},                  # ENV
                      ('VAR_FOO', 'VAR_FOO help', ),                    # VAR
                      ('--foo', {'dest' : "opt_foo"})               ),  # OPT

           # Argument 'bar'
          'bar' : (   {'ENV_BAR' : None},                               # ENV
                      ('VAR_BAR', 'VAR_BAR help', 'default VAR_BAR'),   # VAR
                      ('--bar', {'dest':"opt_bar", "type":"string"}))   # OPT
        }
        decls = ArgumentDecls(decls)

    The first positional argument may be iterable as well, in which case it
    should yield tuples in form ``(key, value)``, where ``value`` is any value
    convertible to `_ArgumentDecl`.

    **Example**

    .. python::

        decls = [
           # Argument 'foo'
          'foo' , (   {'ENV_FOO' : 'default ENV_FOO'},                  # ENV
                      ('VAR_FOO', 'VAR_FOO help', ),                    # VAR
                      ('--foo', {'dest' : "opt_foo"})               ),  # OPT

           # Argument 'bar'
          'bar' , (   {'ENV_BAR' : None},                               # ENV
                      ('VAR_BAR', 'VAR_BAR help', 'default VAR_BAR'),   # VAR
                      ('--bar', {'dest':"opt_bar", "type":"string"}))   # OPT
        ]
        decls = ArgumentDecls(decls)

    You may also define variables via keyword arguments to `ArgumentDecls()`.

    **Example**

    .. python::

        decls = ArgumentDecls(
           # Argument 'foo'
           foo  = (   {'ENV_FOO' : 'ENV default FOO'},                  # ENV
                      ('FOO',         'FOO variable help', ),           # VAR
                      ('--foo',       {'dest' : "opt_foo"})         ),  # OPT

           # Argument 'bar'
           bar  = (   {'ENV_BAR' : None},                               # ENV
                      ('BAR', 'BAR variable help', 'VAR default BAR'),  # VAR
                      ('--bar', {'dest':"opt_bar", "type":"string"}))   # OPT
        )

    You may of course append keyword arguments to normal arguments to pass
    extra declarations.

    **Example**

    .. python::

        decls = ArgumentDecls(
           # Argument 'foo'
           [('foo',(   {'ENV_FOO' : 'ENV default FOO'},                 # ENV
                      ('FOO',         'FOO variable help', ),           # VAR
                      ('--foo',       {'dest' : "opt_foo"})         ))],# OPT
           # Argument 'geez'
           geez  = (   {'ENV_GEEZ' : None},                             # ENV
                      ('GEEZ', 'GEEZ variable help', 'VAR default GEEZ'),# VAR
                      ('--geez', {'dest':"opt_geez", "type":"string"})) # OPT
        )

    or

    **Example**

    .. python::

        decls = ArgumentDecls(
           # Argument 'bar'
           {'bar':(   {'ENV_BAR' : None},                               # ENV
                      ('BAR', 'BAR variable help', 'VAR default BAR'),  # VAR
                      ('--bar', {'dest':"opt_bar", "type":"string"}))}, # OPT
           # Argument 'geez'
           geez  = (   {'ENV_GEEZ' : None},                             # ENV
                      ('GEEZ', 'GEEZ variable help', 'VAR default GEEZ'),# VAR
                      ('--geez', {'dest':"opt_geez", "type":"string"})) # OPT
        )

    This function

    :Returns:

        - `ArgumentDecls()` returns an empty `_ArgumentDecls` dictionary ``{}``,
        - `ArgumentDecls(mapping)` returns `_ArgumentDecls` dictionary initialized
          with ``{k : ArgumentDecl(mapping[k]) for k in mapping.keys()}``
        - `ArgumentDecls(iterable)` returns `_ArgumentDecls` dictionary initialized
          with ``{k : ArgumentDecl(v) for (k,v) in iter(initializer)}``

        In any case, the keyword arguments ``**kw`` are appended to the
        initializer.

    """
    convert = lambda x : x if isinstance(x, _ArgumentDecl)  \
                           else ArgumentDecl(**x) if hasattr(x, 'keys') \
                           else ArgumentDecl(*tuple(x))
    return _ArgumentDecls(__dict_converted(convert, *args, **kw))

#############################################################################
def DeclareArguments(*args, **kw):
    """Declare multiple *Arguments* at once

    This function may be used to declare multiple *Arguments* at once while
    using same parameters as `DeclareArgument()` for each individual
    *Argument*.

    **Example**

    .. python::

        decls = DeclareArguments(
            foo = ('ENV_FOO', 'VAR_FOO', 'OPT_FOO', 'default foo', 'help for argument foo'),
            bar = ('ENV_BAR', 'VAR_BAR', 'OPT_BAR', 'default bar', 'help for argument bar'),
            gez = {'env_key' : 'ENV_GEZ', 'var_key' : 'VAR_GEZ', 'default' : 'default GEEZ' }
        )

    """
    convert = lambda x : x if isinstance(x, _ArgumentDecl) \
                           else DeclareArgument(**x) if hasattr(x, 'keys') \
                           else DeclareArgument(*tuple(x))
    return _ArgumentDecls(__dict_converted(convert, *args, **kw))


# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4: