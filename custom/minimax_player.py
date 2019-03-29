from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from helper_functions import chanceNode
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

    logging.info("\n\n")
    logging.info("Street: {}".format(currStreet))
    logging.info("Hole cards: {}".format(hole_card))
    logging.info("Community cards: {}".format(round_state["community_card"]))
    logging.info("Valid actions: {}".format(valid_actions))


    DEPTH = 1

    start = time.time()
    # =========================================== #
    # DON'T CONSIDER ACTION
    # =========================================== #
    oppCards = []
    payout = chanceNode(hole_card, commCards, oppCards, potAmt, DEPTH)
    if payout < 0:
      idx = 0
    else:
      idx = 1
    
    bestAction = valid_actions[idx]["action"]

    # =========================================== #
    # LOG TIME TAKEN
    # =========================================== #
    end = time.time()
    duration = end - start
    minutes = duration // 60
    seconds = duration - minutes * 60
    logging.info("Time taken: {:.0f} min {:.3f} s".format(minutes,seconds))
    logging.info("Payout: {}".format(payout))
    logging.info("\n\n")

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
    pass

def setup_ai():
  return MiniMaxPlayer()
