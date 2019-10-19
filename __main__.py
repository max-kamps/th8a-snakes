import logging
import sys
import os
import contextlib
import json
from pathlib import Path

from . import mixins
from .common import *
from .bot import NearlyOnTime
from . import persistence


os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('credentials.json') as f:
    credentials = json.load(f, object_hook=Obj)

if len(sys.argv) != 2:
    print('Usage: python3 -m nearly_on_time <account>')
    sys.exit(1)

chosen_account = sys.argv[1]

if chosen_account not in credentials:
    print(f'Error: {chosen_account!r} is not a valid account, must be one of {tuple(credentials)!r}.')
    sys.exit(1)

config_dir = (Path(__file__).parent / '.config' / chosen_account).resolve()
os.makedirs(config_dir, exist_ok=True)
persistence.config_dir = config_dir

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
try:
    with log('discord', logging.WARNING), log('bot', logging.INFO):
        bot = NearlyOnTime()
        bot.run(credentials[chosen_account])

except:
    persistence.close_all_shelves()
    raise
