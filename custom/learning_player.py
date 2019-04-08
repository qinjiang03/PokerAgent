from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from pypokerengine.utils.card_utils import *
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card


class LearningPlayer(BasePokerPlayer):

  @staticmethod
  def getHandStrength(holeCards, commCards):
    holeCards = [Card.from_str(card) for card in holeCards]
    commCards = [Card.from_str(card) for card in commCards]
    score = HandEvaluator.eval_hand(holeCards, commCards)
    return score


  def getFeatures(self, hole_card, round_state):
    MAX_HAND_STR = 8429805.0
    STREETS = {"preflop": 1, "flop": 2, "turn": 3, "river": 4}

    potAmt = round_state["pot"]["main"]["amount"]
    stacks = [seat["stack"] for seat in round_state["seats"]]
    TOTAL_STACK = potAmt + sum(stack for stack in stacks)

    potFrac = [potAmt * 1.0 / TOTAL_STACK]
    stackFracs = [stack * 1.0 / TOTAL_STACK for stack in stacks]

    handStr = [self.getHandStrength(hole_card, round_state["community_card"]) / MAX_HAND_STR]
    streetNum = [num for street, num in STREETS.items() if round_state["street"] == street]
    isSmallBlind = [round_state["next_player"] == round_state["small_blind_pos"]]
    numRaiseSelf = [sum(1 if history["action"] == "RAISE" and history["uuid"] == self.uuid else 0 \
                    for history in round_state["action_histories"][street]) / 4.0 \
                    if street in round_state["action_histories"] else 0 \
                    for street in STREETS.keys()]
    numRaiseOpp = [sum(1 if history["action"] == "RAISE" and history["uuid"] != self.uuid else 0 \
                    for history in round_state["action_histories"][street]) / 4.0 \
                    if street in round_state["action_histories"] else 0 \
                    for street in STREETS.keys()]
    totalRaiseSelf = [sum(numRaiseSelf)]
    totalRaiseOpp = [sum(numRaiseOpp)]
    
    features = handStr + streetNum + isSmallBlind \
      + numRaiseSelf + numRaiseOpp + totalRaiseSelf + totalRaiseOpp \
      + potFrac + stackFracs
    
    return features

  
  def declare_action(self, valid_actions, hole_card, round_state):

    ################## Features ################## 
    features = self.getFeatures(hole_card, round_state)
    
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(round_state)
    ################## Actions ##################
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
    pp = pprint.PrettyPrinter(indent=2)
    print("winners")
    pp.pprint(winners)
    print("handinfo")
    pp.pprint(hand_info)
    print("round_state")
    pp.pprint(round_state)
    pass

def setup_ai():
  return LearningPlayer()
