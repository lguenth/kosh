from functools import partial
from inspect import getmodule, stack
from logging import Logger, getLevelName, getLogger
from re import search
from typing import Any, Callable, Dict, Union, get_type_hints

from graphene import Boolean, Float, Int, String


def concretemethod(method: Callable) -> Callable:
  '''
  ``concretemethod`` annotation with typechecking.

  This inheritance helper throws an error when an annotated concretemethod does
  not correctly inherit its base methods signature.

  Param ``method<Callable>``:
    The annotated method.
  Return``<Callable>``:
    The passed in method.
  '''
  name = search(r'class[^(]+\((\w+)\)\:', stack()[2][4][0]).group(1)
  base = getattr(stack()[2][0].f_locals[name], method.__name__)

  if get_type_hints(method) != get_type_hints(base):
    raise(TypeError('Invalid concretisation'))

  return(method)

class dotdict(dict):
  '''
  ``dict`` wrapper class to allow dot-operator access to values.

  See:
    https://stackoverflow.com/a/23689767
  And:
    https://stackoverflow.com/a/13520518
  '''
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

  def __init__(self, *args, **kwargs):
    for key, value in dict(*args, **kwargs).items():
      if hasattr(value, 'keys'): value = dotdict(value)
      self[key] = value

def defaultconfig() -> Dict[str, Dict[str, str]]:
  '''
  ``defaultconfig`` method, returning the default kosh configuration as dotdict.
  Should be passed to ``ConfigParser.read_dict`` to define sane default values.

  Return``<Dict[str, Dict[str, str]]>``:
    A dotdict containing the default configuration.
  '''
  return dotdict({
    'DEFAULT': {
      'name': 'kosh'
    },
    'api': {
      'ipv4': '0.0.0.0',
      'ipv6': '::/0',
      'port': 5000,
      'root': '/api'
    },
    'data': {
      'host': 'localhost',
      'root': '/var/lib/%(name)s',
      'spec': '.%(name)s'
    },
    'info': {
      'desc': '%(name)s - APIs for Dictionaries',
      'link': 'https://kosh.uni-koeln.de',
      'mail': 'info@cceh.uni-koeln.de',
      'repo': 'https://github.com/cceh/kosh'
    },
    'logs': {
      'elvl': 'INFO'
    }
  })

def graphenemap() -> Dict[str, Union[Boolean, Float, Int, String]]:
  '''
  ``graphenemap`` method, returning the Elastic to Graphene type mapping as
  dotdict, containing Elastic types as string keys and Graphene types as values.

  Return``<Dict[str, Union[Boolean, Float, Int, String]]>``:
    A dotdict containing the Elastic to Graphene type mapping.
  '''
  return dotdict({
    'keyword': String,
    'text': String,
    'short': Int,
    'integer': Int,
    'float': Float,
    'boolean': Boolean
  })

def namespaces() -> Dict[str, str]:
  '''
  todo: docs
  '''
  return dotdict({
    'tei': 'http://www.tei-c.org/ns/1.0'
  })

class instance():
  '''
  ``instance`` class, containing a dotdict sigleton. This singleton data
  storage, shared throughout kosh, is the runtime-storage for all components.
  '''

  __data = dotdict()

  @classmethod
  def __delattr__(cls, attr: str) -> None:
    '''
    ``__delattr__`` method, removing a key and its associated value from the
    dotdict data storage singleton.

    Param ``attr<str>``:
      The key to be removed.
    '''
    del cls.__data[attr]

  @classmethod
  def __getattr__(cls, attr: str) -> Any:
    '''
    ``__getattr__`` method, returning the associated value for the passed in
    key from the dotdict data storage singleton.

    Param ``attr<str>``:
      The key whos associated value shall be returned.
    '''
    return cls.__data[attr]

  @classmethod
  def __setattr__(cls, attr: str, value: Any) -> None:
    '''
    ``__setattr__`` method, setting the value for the passed in key on the
    dotdict data storage singleton.

    Param ``attr<str>``:
      The key to be set.
    Param ``value<Any>``:
      The value to be associated with the passed in key.
    '''
    cls.__data[attr] = value

def logger() -> Logger:
  '''
  ``logger`` method, returning a Logger instance for the caller with the current
  loglevel set. The preferred logging functionality throughout this application.

  Return<``Logger``>:
    A Logger instence for the caller.
  '''
  item = getLogger(getmodule(stack()[1].frame).__name__)
  item.setLevel(getLevelName(instance.config.get('logs', 'elvl')))
  return item
