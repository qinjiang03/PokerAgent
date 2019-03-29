from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from helper_functions import placeBet, chanceNode, getValidActions, actionNode
from copy import deepcopy
import logging
import time


class MiniMaxPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state_ori):
    # =========================================== #
    # EXTRACT ROUND STATE INFO
    # =========================================== #
    player = round_state_ori["next_player"]
    opp = (player + 1) % 2
    currStreet = round_state_ori["street"]

    logging.info("\n\n")
    logging.info("Street: {}".format(currStreet))
    logging.info("Hole cards: {}".format(hole_card))
    logging.info("Community cards: {}".format(round_state_ori["community_card"]))
    logging.info("Valid actions: {}".format(valid_actions))


    DEPTH = 1

    start = time.time()
    # =========================================== #
    # DON'T CONSIDER ACTION
    # =========================================== #
    round_state = deepcopy(round_state_ori)
    round_state["opp_card"] = []
    payout = chanceNode(hole_card, round_state, DEPTH)
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
