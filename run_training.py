from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from learning_player import LearningPlayer

# How many episodes to train for
NUM_ROUNDS = 10

config = setup_config(max_round=NUM_ROUNDS, initial_stack=10000, small_blind_amount=10)



config.register_player(name="learner", algorithm=LearningPlayer(True))
config.register_player(name="challenger", algorithm=RandomPlayer())

game_result = start_poker(config, verbose=0)
