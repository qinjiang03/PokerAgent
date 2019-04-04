from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from pypokerengine.utils.card_utils import *
from pypokerengine.utils.action_utils import *

class MiniMaxPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    commCards = round_state["community_card"]
    potAmt = round_state["pot"]["main"]["amount"]
    currStreet = round_state["street"]

    DEPTH = 1
    
    
    

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
    # print("\n\nHAND INFO")
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(hand_info)
    pass

def setup_ai():
  return MiniMaxPlayer()
