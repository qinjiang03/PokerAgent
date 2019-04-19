from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from learning_player import LearningPlayer
from custom.call_player import CallPlayer
from custom.honest_player import HonestPlayer
import pandas as pd

N_LAYERS_LIST = [1,2,3,5]
for N_LAYERS in N_LAYERS_LIST:

    # How many episodes to train for
    NUM_ROUNDS = 200
    # Path to save model weights
    MODEL_PATH = 'model2_random{}_200_new.dat'.format(N_LAYERS)
    # Path to save training stats
    STATS_PATH = 'stats2_random{}_200_new.csv'.format(N_LAYERS)

    NUM_GAMES = 50
    total_rewards = []
    best_mean_reward = None
    learning_player = LearningPlayer(training=True,
                        model_path=MODEL_PATH,
                        stats_path=STATS_PATH,
                        n_layers=N_LAYERS)

    for n in range(NUM_GAMES):
        config = setup_config(max_round=NUM_ROUNDS, initial_stack=10000, small_blind_amount=10)

        config.register_player(name="learner", algorithm=learning_player)
        config.register_player(name="challenger", algorithm=RandomPlayer())

        game_result = start_poker(config, verbose=0)
        print(game_result)
