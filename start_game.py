from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from custom.minimax_player import MiniMaxPlayer
from custom.honest_player import HonestPlayer
from custom.honest_player2 import HonestPlayer2
from custom.call_player import CallPlayer
import pprint

from custom.logging_functions import startLogging, stopLogging
import os, datetime, logging
import numpy as np
import itertools


#TODO:config the config as our wish

# logFile = os.path.join('log', "log_{}.log".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
# logger = startLogging(logFile)

# w1s = np.arange(0.3,0.5,0.05)
# w2s = np.arange(0.7,0.85,0.05)
# w3s = np.arange(0.2,0.5,0.05)
# # w2s = [0.75]
# # w3s = [0.3]

# w_list = list(itertools.product(w1s, w2s, w3s))

# results = []
# for w in w_list:
config = setup_config(max_round=100, initial_stack=10000, small_blind_amount=10)
config.register_player(name="RaisePlayer", algorithm=RaisedPlayer())
# config.register_player(name="CallPlayer", algorithm=CallPlayer())
# config.register_player(name="HonestPlayer1", algorithm=HonestPlayer())
config.register_player(name="HonestPlayer2", algorithm=HonestPlayer())
# config.register_player(name="MiniMaxPlayer", algorithm=MiniMaxPlayer())
# config.register_player(name="HonestPlayer2", algorithm=HonestPlayer2(w[0], w[1], w[2]))

game_result = start_poker(config, verbose=0)
print(game_result)

#     result = list(w) + [player["stack"] for player in game_result["players"]]
#     logging.info(result)   
#     results.append(result)

# stopLogging(logger)
