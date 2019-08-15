import logging
import sys
import os
import hjson
import contextlib

from . import mixins
from .common import *
from .bot import NearlyOnTime


os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('config.hjson') as f:
    conf = hjson.load(f, object_hook=Obj, object_pairs_hook=None)

if len(sys.argv) != 2:
    print('Usage: python3 -m nearly_on_time <account>')
    sys.exit(1)

chosen_account = sys.argv[1]

if chosen_account not in conf.tokens:
    print(f'Error: {chosen_account!r} is not a valid account, must be one of {tuple(conf.tokens)!r}.')
    sys.exit(1)

@contextlib.contextmanager
def log(name, level):
    l = logging.getLogger(name)
    l.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[%(asctime)s] (%(levelname)s) %(name)s: %(message)s'))

    l.addHandler(handler)

    yield

    for hdlr in l.handlers[:]:
        l.removeHandler(hdlr)
        hdlr.close()

with log('discord', logging.WARNING), log('bot', logging.INFO):
    bot = NearlyOnTime(conf)
    bot.run(conf.tokens[chosen_account])