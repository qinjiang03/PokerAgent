from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint

class MyPlayer(BasePokerPlayer):

  def helperfunc(self, valid_actions, hole_card, round_state, pp):
    CARDS_LEFT = {'preflop': 3, 'flop': 2, 'turn': 1, 'river': 0}
    SUITS = ['D','C','H','S']
    keys = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
    VALUES = {keys[value-2]: value for value in range(2,15)}
    
    community_cards = round_state["community_card"]
    curr_street = round_state["street"]
    
    cardsLeft = CARDS_LEFT[curr_street]
    suits = [sum(card[0] == suit for card in hole_card) + sum(card[0] == suit for card in community_cards) for suit in SUITS]
    values = [sum(card[1] == value for card in hole_card) + sum(card[1] == value for card in community_cards) for value in VALUES]
    
    pp.pprint(suits)
    pp.pprint(values)

    flush = max(suits) + cardsLeft >= 5
    twoPairs = sum(value >= 2 for value in values) >= 2
    
    handValue = sum(VALUES[card[1]] for card in hole_card)
    
    veryGoodCards = handValue >= 25
    goodCards = flush or twoPairs or handValue >= 20
    
    if veryGoodCards and len(valid_actions) > 2:
      call_action_info = valid_actions[2]
    elif goodCards:
      call_action_info = valid_actions[1]
    else:
      call_action_info = valid_actions[0]

    action = call_action_info["action"]
    return action


  def declare_action(self, valid_actions, hole_card, round_state):
    # valid_actions format => [raise_action_pp = pprint.PrettyPrinter(indent=2)
    pp = pprint.PrettyPrinter(indent=2)
    # print("")
    # print("")
    # print("------------ROUND_STATE(RANDOM)--------")
    # pp.pprint(round_state)
    print("------------HOLE_CARD----------")
    pp.pprint(hole_card)
    # print("------------VALID_ACTIONS----------")
    # pp.pprint(valid_actions)
    # print("-------------------------------")

    action = self.helperfunc(valid_actions, hole_card, round_state, pp)
    
    return action  # action returned here is sent to the poker engine

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
  return MyPlayer()
