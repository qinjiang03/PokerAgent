from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from helper_functions import chanceNode
from preflop import lookupProb
from postflop import getScore
import logging
import time


class MiniMaxPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    # =========================================== #
    # EXTRACT ROUND STATE INFO
    # =========================================== #
    commCards = round_state["community_card"]
    potAmt = round_state["pot"]["main"]["amount"]
    currStreet = round_state["street"]

    # logging.info("\n\n")
    # logging.info("Street: {}".format(currStreet))
    # logging.info("Hole cards: {}".format(hole_card))
    # logging.info("Community cards: {}".format(round_state["community_card"]))
    # logging.info("Valid actions: {}".format(valid_actions))


    DEPTH = 1
    idx = 0

    # start = time.time()
    score = getScore(hole_card, commCards)
    # print(score)
    if currStreet == "preflop":
      prob = lookupProb(hole_card)
      if prob >= 0.75 and len(valid_actions) > 2:
        idx = 2
      elif prob >= 0.4:
        idx = 1
    else:
      oppCards = []
      payout = chanceNode(hole_card, commCards, oppCards, potAmt, DEPTH)
      if payout >= 0:
        idx = 1
      
    
    bestAction = valid_actions[idx]["action"]

    # =========================================== #
    # LOG TIME TAKEN
    # =========================================== #
    # end = time.time()
    # duration = end - start
    # minutes = duration // 60
    # seconds = duration - minutes * 60
    # logging.info("Time taken: {:.0f} min {:.3f} s".format(minutes,seconds))
    # logging.info("Payout: {}".format(payout))
    # logging.info("\n\n")

    return bestAction

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
