from pypokerengine.api.game import setup_config, start_poker
from custom.learning_player import LearningPlayer
import pprint


#TODO:config the config as our wish

config = setup_config(max_round=1, initial_stack=10000, small_blind_amount=10)

config.register_player(name="LearningPlayer1", algorithm=LearningPlayer())
config.register_player(name="LearningPlayer2", algorithm=LearningPlayer())

game_result = start_poker(config, verbose=1)
print(game_result)