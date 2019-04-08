from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from pypokerengine.utils.card_utils import *
from pypokerengine.utils.action_utils import *

class MiniMaxPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    pp = pprint.PrettyPrinter(indent=2)
    print("\n\n")
    pp.pprint(valid_actions)
    pp.pprint(round_state)
    commCards = round_state["community_card"]
    potAmt = round_state["pot"]["main"]["amount"]
    currStreet = round_state["street"]

    payouts = []
    for validAction in valid_actions:
      action = validAction["action"]
      if action == "fold":
        payout = -round_state["pot"]["main"]["amount"]
      else:
        if action == "call":
          pass
        else:
          if currStreet == "preflop": add_amt = 20
          elif currStreet == "river": add_amt = 40
          else:                       add_amt = 10
      payouts.append(payout)
    
    idx = 1
    # raised = [action for action in round_state["action_histories"][currStreet] \
    #           if action["uuid"] == self.uuid and action["action"] == "RAISE"]
    # if not raised and len(valid_actions) > 2: idx = 2
    # idx = payouts.index(max(payouts))

    return valid_actions[idx]["action"]

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
