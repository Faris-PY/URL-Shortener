#import environ

#env = environ.Env()
#environ.Env.read_env()
import os
from dotenv import load_dotenv
from os.path import dirname

LOC = dirname(dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(LOC, ".env"))

Env = os.getenv('ENVIRONMENT')
if Env == 'PRODUCTION':
    from .conf.production.setting import *
else:
    from .conf.development.setting import *