from pypokerengine.players import BasePokerPlayer
from time import sleep
#from preflop import lookupProb
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import pprint

class HonestPlayer(BasePokerPlayer):

    #action 0,1,2 = fold, call, raise
    #street = preflop -> flop -> turn -> river -- (showdown)!
    def declare_action(self, valid_actions, hole_card, round_state):
        if round_state["street"] == "preflop":
            return valid_actions[1]['action']

        curStreet = round_state["action_histories"][round_state["street"]]
        if not curStreet:
            previousAction = None
        elif curStreet[-1]["action"] == 'CALL':
            previousAction = 'CALL'
        else:
            previousAction = 'RAISE'

        win_rate = estimate_hole_card_win_rate(
            nb_simulation=200,
            nb_player=2,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(round_state['community_card'])
        )
        if (win_rate >= 0.8 or (win_rate >= 0.7 and previousAction == 'CALL')) and len(valid_actions) == 3:
            action = valid_actions[2]
        elif previousAction != 'RAISE' or win_rate >= 0.3:
            action = valid_actions[1]
        else:
            action = valid_actions[0]

        return action['action']

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def setup_ai():
      return RandomPlayer()
