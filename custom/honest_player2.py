from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from pypokerengine.utils.card_utils import *
from helper_functions import mapCardsToKey
import numpy as np
import csv

class HonestPlayer2(BasePokerPlayer):

  def __init__(self):
    filename = "custom/prob.csv"
    with open(filename,'r') as file:
        reader = csv.reader(file)
        self.TABLE = {rows[0]:rows[1] for rows in reader}
    self.THRESHOLDS = [[1, 0], [0.75, 0.3], [0.75, 0.3], [0.75, 0.3]]
  
  
  def lookupProb(self, holeCards, commCards):
    key = mapCardsToKey(holeCards, [])
    if len(commCards) > 0: key += "_" + mapCardsToKey(holeCards, commCards)
    return float(self.TABLE[key])


  def declare_action(self, valid_actions, hole_card, round_state):
    isStreet = [True if round_state["street"] == street else False for street in ["preflop", "flop", "turn", "river"]]
    thresholds = np.dot(isStreet, self.THRESHOLDS)

    if round_state["street"] == "preflop" or round_state["street"] == "flop":
      win_rate = self.lookupProb(hole_card, round_state["community_card"])
    else:
      win_rate = estimate_hole_card_win_rate(
        nb_simulation=100,
        nb_player=2,
        hole_card = gen_cards(hole_card),
        community_card = gen_cards(round_state["community_card"]))
      
    if win_rate >= thresholds[0] and len(valid_actions) == 3:     action = valid_actions[2]
    elif win_rate >= thresholds[1]:                               action = valid_actions[1]
    else:                                                         action = valid_actions[0]

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
  return HonestPlayer2()
