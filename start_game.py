from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from honest_player import HonestPlayer
from custom.call_player import CallPlayer
from NovicePlayer import NovicePlayer

import pprint

from custom.logging_functions import startLogging, stopLogging
import os, datetime, logging
import numpy as np
import itertools

#from custom.logging_functions import startLogging, stopLogging
import datetime
import os

#logFile = os.path.join('log', "log_{}.log".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
#logger = startLogging(logFile)

#TODO:config the config as our wish
config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=20)

config.register_player(name="NovicePlayer", algorithm=NovicePlayer())
config.register_player(name="HonestPlayer", algorithm=HonestPlayer())
#config.register_player(name="NovicePlayer", algorithm=NovicePlayer())

game_result = start_poker(config, verbose=0)
