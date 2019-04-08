#This is a poker agent that try to model opponent strategy and counter it

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from pypokerengine.engine.poker_constants import PokerConstants as Const
from anytree import Node, Walker

import queue
import random as rand
import pprint
import numpy

class NovicePlayer(BasePokerPlayer):
  def __init__(self):
    #for call and raise only, since you cannot observe opponent hand when his fold
    #action_range = [low, high, probability within k*standard_deviation, k = sqrt(standard_deviation)]
    self.action_range = [[0, 0],[0, 0]]
    #to observe the action perform in that sequence given the believe EHS at that current state (got opponent hand from showdown, do the same as our hand)
    #assume opponent action depend on his current observance of his own EHS
    #opponent must be consistent at least within 30 - 50 rounds
    self.raiseEHS = list()
    self.callEHS = list()

    self.current_round_player_action_history = list(list(), list(), list(), list()) #list of 4 lists for each round
    self.current_round_opp_action_history = list(list(), list(), list(), list())
    
    self.action_tree = SequenceActionTree()
    self.action_tree.generate_tree(20)
    self.hole_card = None

  def declare_action(self, valid_actions, hole_card, round_state):
    current_street = action_histories['street']
    c_street = 0
    if current_street == 'preflop'
      c_street = 0
    elif current_street == 'flop'
      c_street = 1
    elif current_street == 'turn'
      c_street = 2
    elif current_street == 'river'
      c_street = 3

    s = size(round_state.action_histories[current_street])
    current_round_opp_action_history[c_street].append(round_state.action_histories[s - 1])

    action = "fold"
    for i in valid_actions:
        if i["action"] == "call":
          action = i["action"]
          return action 
    return action  # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    #get current configuration of small/big blind

  
  def receive_round_start_message(self, round_count, hole_card, seats):
    self.hole_card = hole_card
    
  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    #add to history here

  def receive_round_result_message(self, winners, hand_info, round_state):
    #get opp card from here
    opp_card = hand_info['hand']['card']
    update_after_showdown(opp_card, comm_cards_river)
    
  def update_after_showdown(self, opp_card, comm_cards_river):
    EHS_opp = PlayerUtil.hand_strength(opp_card, comm_cards_river)
    SequenceActionTree.search_node_by_name()

    EHS_opp = PlayerUtil.effective_hand_strength(opp_card, comm_cards_river - comm_cards_river[size(comm_cards_river) - 1])
    SequenceActionTree.search_node_by_name()
    
    EHS_opp = PlayerUtil.effective_hand_strength(opp_card, comm_cards_river - comm_cards_river[size(comm_cards_river) - 1])
    SequenceActionTree.search_node_by_name()
    
  def setup_ai():
    return NovicePlayer()

class PlayerUtil:
  @staticmethod
  def set_up():
    self.alway_full_deck = getNewDeck()

  @staticmethod
  def getNewDeck():
    suits = ['D','C','H','S']
    values = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
    deck = [suit + value for value in values for suit in suits]
    return deck

  @staticmethod
  def reduceDeck(deck, cardsToReduce):
    deck = list(set(deck) - set(cardsToReduce))
    return deck

  @staticmethod
  def getAllCombins(deck, n):
    combins = list(itertools.combinations(deck, n))
    return combins

  @staticmethod  
  #Caculate immediate win rate against opponent
  def hand_strength(hole_cards, comm_cards):
    ourrank = HandEvaluator.eval_hand(holeCards, comm_cards)
    ahead = tied = behind = 0
    deck = reduceDeck(self.alway_full_deck, comm_cards)
    deck = reduceDeck(deck, hole_cards)
    oppPossbileCards = getAllCombins(deck, 2)
    
    for opp_cards in oppPossbileCards:
      opprank = HandEvaluator.eval_hand(opp_cards, comm_cards)
      if ourrank > opprank:
          ahead += 1
      elif ourrank == opprank:
          tied += 1
      else:
          behind += 1
    return (ahead + tied / 2) / (ahead + tied + behind)

  @staticmethod  
  def positive_potential(hole_cards, comm_cards):
    HP = [(0,0),(0,0),(0,0)]
    HPTotal = [0, 0, 0]
    ourrank = HandEvaluator.eval_hand(hole_cards, comm_cards)
    deck = reduceDeck(self.always_full_deck, comm_cards)
    deck = reduceDeck(deck, hole_cards)
    oppPossbileCards = getAllCombins(deck, 2)     
    if len(comm_cards) == 3:   
      n = 2
    elif len(comm_cards) == 4: 
      n = 1
    else:                      
      n = 0
  
    for opp_cards in oppPossbileCards:
      opprank = HandEvaluator.eval_hand(opp_cards, comm_cards)
      possible_board_deck = deck
      possible_board_deck = reduceDeck(possible_boards, opp_cards)
      possible_board_cards = getAllCombins(possible_board_deck, n)

      if ourrank > opprank:
          index = 0
      elif ourrank == opprank:
          index = 1
      else:
          index = 2
      HPTotal[index] += 1

      for p_board_card in possible_board_cards:
        ourbest = HandEvaluator.eval_hand(hole_cards, comm_cards + p_board_card)
        oppbest = HandEvaluator.eval_hand(opp_cards, comm_cards + p_board_card)
        if ourbest > oppbest:
            HP[index][ahead] += 1
        elif ourbest == oppbest:
          HP[index][tied] += 1
        else: 
          HP[index][behind] += 1 
      PPot = (HP[behind][ahead] + HP[behind][tied]/2 + HP[tied][ahed]/2) / (HPTotal[behind]+HPTotal[tied]/2)
    return PPot

  @staticmethod
  #Caculate possible change that benefit the current hand win rate
  def effective_hand_strength(hole_cards, comm_cards):
    HS = hand_strength(hole_cards, comm_cards)
    PosP = positive_potential(hole_cards, comm_cards)
    return  HS + (1 - HS)*PosP

  @staticmethod  
  def calculate_mean(data):
    return numpy.mean(data)

  @staticmethod 
  def calculate_var(data):
    return numpy.var(data)

  @staticmethod
  def calculate_range(mean, var):
    return [int(mean - var), int(mean + var)]  
  # @staticmethod
  # def calculate_standard_deviation(data):
  #   return numpy.std(data)

class HistoryCell:
  def __init__(self):
    self.EHS_frequency_cell = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    self.total_data_point = 0

  #update the frequency
  def update_action_frequency_cell(self, hole_cards, comm_cards):
    #round to 1 decimal, using 10 cell divider
    EHS = effective_hand_strength(hole_cards, comm_cards)
    self.EHS_frequency_cell[int(EHS*10 - 1)] += 1
    self.total_data_point += 1

  #Probability of opponent having action from the node that contain this cell 
  def pr_EHS_range(self, action_range):
    callPr = 0.0
    raisePr = 0.0
    total = 0
    #call probability
    for i in range(int(action_range[0][0]*10 - 1), int(action_range[0][1]*10), 1):
      total += EHS_frequency_cell[i]
    
    callPr = total/self.total_data_point
    total = 0

    #raise probability
    for i in range(int(action_range[1][0]*10 - 1), int(action_range[1][1]*10), 1):
      total += EHS_frequency_cell[i]
    raisePr = total/self.total_data_point

    return [1 - callPr - raisePr, callPr, raisePr]

#Some attribute only insert/define when necessary
#this tree only need to follow normal rule and with these restriction
#1. each player have max 4 number of raise
#2. 2 max raise in a turn
#3. big blind is counted as 1 raise
#library provide iterate and search that need to update eva
#to know which action, take last letter from name
#turn end == need a history cell
#set name same to the sequence of action that lead to this point
#the tree expand given this agent as the root or player 0
#To make the tree become symmetric for action, we start with the same money and number of raise
  #if we are small blind, first action is call, and opp first action is raise
  #if we are big blind, first action is raise, then act normally
class SequenceActionTree: 
  def __init__(self):
    self.no_nodes = 0
    self.root = None

  def search_node_by_name(self, opp_sequence, player_sequence):
    for i in range(max(len(opp_sequence), len(player_sequence))):
      name += player_sequence[i]
      name += opp_sequence[i]
    return anytree.search.find_by_attr(self.root, name, name = 'name')

  #need to test this method 
  def return_all_node_in_current_street(self, current_node, current_street):
    return anytree.search.findall_by_attr(current_node, current_street, name = 'round_state["player_state"]["player_no"]')

  #naming scheme to walk
  #return the root of the tree
  def generate_tree(self, sb):
    self.no_nodes = 4
    rp_state = player_state()
    rp_state.set(0, [4,4],[2,2],[sb,sb])
    rr_state = round_state()
    rr_state.set(0, 2*sb, sb, rp_state)
    self.root = Node("root", parent = None, round_state = rr_state, history_cell = None, eva = 0)

    rp_state.set(1, [4,4],[2,2],[sb,sb])
    opp_turn_small_blind = Node("c", parent = self.root, round_state = rr_state, history_cell = None, eva = 0)

    rp_state.set(0, [4,4],[2,1],[sb,2*sb])
    rr_state.set(0, 3*sb, sb, rp_state)
    small_blind = Node("cr", parent = opp_turn_small_blind, round_state = rr_state, history_cell = None, eva = 0)

    rp_state.set(1, [4,4],[1,2],[2*sb,sb])
    rr_state.set(0, 3*sb, sb, rp_state)
    big_blind = Node("r", parent = self.root, round_state = rr_state, history_cell = None, eva = 0)
    action = ["f", "c", "r"]
    player = 0

    #parent queue
    p_queue = queue.Queue()
    p_queue.put(small_blind, big_blind)

    while ~p_queue.empty():
      parent = p_queue.get()
      #update player
      player = (parent.round_state.player_state.player_no + 1)%2 #switch player

      for i in range(3):
        #update this game state from parent then create new node if possible
        r_state = parent.round_state
        p_state = r_state.player_state
        p_state.player_no = player
        name = parent.name + action[i]
        eva = 0
        history_cell_flag = 0

        if action[i] == "f":
          eva = r_state.pot - p_state.no_bet[player]
        
        elif action[i] == "c":
          if p_state.no_bet[player] != p_state.no_bet[1-player]:
            #raise player bet and change pot
            p_state.no_bet[player] = p_state.no_bet[1-player]
            r_state.pot = p_state.no_raise[player]*2
            #end the round
            r_state.current_street += 1
            p_state.player_no = 0
            history_cell_flag = 1

          #to check if the call can not result in another call but end that turn
          #will create the same node with different player_no bzut the same round state if it not end the turn 
          #check parent of parent, if parent of parent current street is smaller then end the turn
          else: 
            if parent.parent.round_state.current_street < parent.round_state.current_street:
              r_state.current_street += 1
              p_state.player_no = 0
              history_cell_flag = 1
            

        #can only raise 2 times in 1 turn and 
        elif action[i] == "r":
          #if player can raise
          if p_state.no_raise[player] > 0:   
            #if the turn still allow player to raise
            if p_state.no_turn_raise[player] > 0:
              if r_state.current_street == 3:
                p_state.no_bet[player] = p_state.no_bet[1-player] + 2*sb
              else:  
                p_state.no_bet[player] = p_state.no_bet[1-player] + sb
              r_state.pot = p_state.no_bet[player] + p_state.no_bet[1-player]
              p_state.no_turn_raise[player] -= 1
              p_state.no_raise[player] -= 1

          #when can not raise in turn, change to call action
          else:
            name = parent.name + action[1]
            #raise player bet and change pot
            p_state.no_bet[player] = p_state.no_bet[1-player]
            r_state.pot = p_state.no_raise[player]*2
            #end the round and refill number of raise in that turn
            r_state.current_street += 1
            p_state.player_no = 0
            p_state.no_turn_raise[player] = 2
            history_cell_flag = 1
        
        if history_cell_flag == 1:
          history_cell = HistoryCell()
        else:
          history_cell = None
        #add new player state to round state
        r_state.player_state = p_state

        node = Node(name = name, parent = parent, round_state = round_state, history_cell = history_cell, eva = eva)
        self.no_nodes += 1
        
        #only add new node as parent if that node have round_street state before RIVER
        if r_state.current_street < 3:
          p_queue.put(node)
    return root 

class round_state:
  def __init__(self):
    self.current_street = None
    self.pot = None
    self.sb = None
    self.player_state = player_state()

  def set(self, current_street, pot, sb, player_states):
    self.current_street = current_street
    self.pot = pot
    self.sb = sb
    self.player_state = player_states

class player_state:
  def __init__(self):
    self.player_no = None
    self.no_raise = None
    self.no_turn_raise = None
    self.no_bet = None

  def set(self, player_no, no_raise, no_turn_raise, no_bet):
    self.player_no = player_no
    self.no_raise = no_raise
    #this value should only be reseted if current street value increase
    self.no_turn_raise = no_turn_raise
    self.no_bet = no_bet
