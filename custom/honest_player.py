from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from pypokerengine.utils.card_utils import *


class HonestPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    if round_state["street"] == "preflop":
      action = valid_actions[1]
    else:
      win_rate = estimate_hole_card_win_rate(
        nb_simulation=250,
        nb_player=2,
        hole_card = gen_cards(hole_card),
        community_card = gen_cards(round_state["community_card"]))
      
      if win_rate >= 0.75 and len(valid_actions) == 3:
        action = valid_actions[2]
      elif win_rate >= 0.3:
        action = valid_actions[1]
      else:
        action = valid_actions[0]

    return action["action"]

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    print("\n\nHAND INFO")
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(hand_info)
    pass

def setup_ai():
  return HonestPlayer()
