from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from custom.minimax_player import MiniMaxPlayer
from custom.call_player import CallPlayer
from custom.logging_functions import startLogging, stopLogging
import datetime
import os

logFile = os.path.join('log', "log_{}.log".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
logger = startLogging(logFile)

#TODO:config the config as our wish
config = setup_config(max_round=2, initial_stack=10000, small_blind_amount=10)



config.register_player(name="MiniMaxPlayer", algorithm=MiniMaxPlayer())
config.register_player(name="CallPlayer", algorithm=CallPlayer())


game_result = start_poker(config, verbose=1)


stopLogging(logger)