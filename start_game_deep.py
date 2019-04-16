from pypokerengine.api.game import setup_config, start_poker
from custom.learning_player import LearningPlayer
from raise_player import RaisedPlayer
import pprint


#TODO:config the config as our wish

config = setup_config(max_round=1, initial_stack=10000, small_blind_amount=10)

config.register_player(name="RaisedPlayer1", algorithm=RaisedPlayer())
config.register_player(name="RaisedPlayer2", algorithm=RaisedPlayer())

game_result = start_poker(config, verbose=1)
print(game_result)