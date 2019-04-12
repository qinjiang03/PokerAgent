from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from learning_player import LearningPlayer

# How many episodes to train for
NUM_ROUNDS = 200
# Path to save model weights
MODEL_PATH = 'model.dat'
# Path to save training stats
STATS_PATH = 'stats.csv'

config = setup_config(max_round=NUM_ROUNDS, initial_stack=10000, small_blind_amount=10)

config.register_player(name="learner",
                       algorithm=LearningPlayer(training=True,
                                                model_path=MODEL_PATH,
                                                stats_path=STATS_PATH))
config.register_player(name="challenger", algorithm=RandomPlayer())

game_result = start_poker(config, verbose=0)
