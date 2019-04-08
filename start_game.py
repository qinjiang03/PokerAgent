from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from custom.minimax_player import MiniMaxPlayer
from custom.call_player import CallPlayer
from NovicePlayer import NovicePlayer
#from custom.logging_functions import startLogging, stopLogging
import datetime
import os

#logFile = os.path.join('log', "log_{}.log".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
#logger = startLogging(logFile)

#TODO:config the config as our wish
config = setup_config(max_round=1, initial_stack=3000, small_blind_amount=20)

#config.register_player(name="NoviceOpponentModelPlayer", algorithm=NovicePlayer())
config.register_player(name="RaisedPlayer1", algorithm=RaisedPlayer())
config.register_player(name="RaisedPlayer2", algorithm=RaisedePlayer())


game_result = start_poker(config, verbose=1)


#stopLogging(logger)