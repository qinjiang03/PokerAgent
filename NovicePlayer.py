#This is a poker agent that try to model opponent strategy and counter it

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from pypokerengine.engine.poker_constants import PokerConstants as Const
from anytree import Node, Walker, RenderTree, ContStyle, search
from custom import helper_functions
import queue
import random as rand
import pprint
import numpy
import itertools
import copy

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

    self.opp_action = list() #list of 4 lists for each round
    self.player_action = list()
    
    self.action_tree = SequenceActionTree()
    self.action_tree.generate_tree(20)
    self.hole_card = None

    print self.action_tree.no_nodes
    #print(self.action_tree.search_node_by_name("rrrrc "))
    #print(RenderTree(self.action_tree.root, style=ContStyle()).by_attr("name"))
    # for row in RenderTree(self.action_tree.root, style=ContStyle()):
    #   print(row.node.name)
    #   row.node.round_state.print_round()
    #   row.node.round_state.player_state.print_player()
    #   print(" ")
    
  def declare_action(self, valid_actions, hole_card, round_state):
    #print(round_state)
    # current_round_player_action_history[c_street].append(round_state.action_histories[s - 2]) 
    # current_round_opp_action_history[c_street].append(round_state.action_histories[s - 1])
    action = "fold"
    for i in valid_actions:
      if i["action"] == "call":
        action = i["action"]
        return action 
    action = valid_actions[1]["action"]
    print(round_state)
    return action  # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    pass
  
  def receive_round_start_message(self, round_count, hole_card, seats):
    self.hole_card = hole_card
    print(seats)
    
  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    #add to history here
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    #get opp card from here
    for i in hand_info:
      if i['hand']['card'] != self.hole_card:
        opp_card = i['hand']['card']
        EHS_opp = PlayerUtil.hand_strength(opp_card, round_state['community_card'])

    
  def setup_ai():
    return NovicePlayer()

class PlayerUtil:
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
    deck = PlayerUtil.reduceDeck(PlayerUtil.getNewDeck(), comm_cards)
    deck = PlayerUtil.reduceDeck(deck, hole_cards)
    oppPossbileCards = PlayerUtil.getAllCombins(deck, 2)

    hole_cards = [Card.from_str(card) for card in hole_cards]
    comm_cards = [Card.from_str(card) for card in comm_cards]
    ourrank = HandEvaluator.eval_hand(hole_cards, comm_cards)
    ahead = tied = behind = 0
  
    for opp_cards in oppPossbileCards:
      opp_cards = [Card.from_str(card) for card in opp_cards]
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
    deck = reduceDeck(PlayerUtil.getNewDeck(), comm_cards)
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
    self.min_data_points = 10

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

#This tree only need to follow normal rule and with these restriction
#1. each player have max 4 number of raise
#2. 2 max raise in a turn
#3. big blind is counted as 1 raise
#set name same to the sequence of action that lead to this point
#the tree expand given this agent as the root or player 0
#if we are small blind, first action is call, and opp first action is raise
#if we are big blind, first action is raise, then act normally
class SequenceActionTree: 
  def __init__(self):
    self.no_nodes = 0
    self.root = None

  #to search for current position
  def search_node_by_name(self, name):
    return search.find_by_attr(self.root, name, name = 'name')

  #To search for all node in the same street from current position
  def return_all_node_in_current_street(self, current_node, current_street):
    return search.findall_by_attr(current_node, current_street, name = 'round_state["player_state"]["player_no"]')

  #To check if the cut_off node have enough data point to use
  #return false if anynode in the subtree need to search don't have enough data points to use for calculation
  def check_opp_model_availability(self, node_list):
    for i in node_list:
      if i.history_cell.total_data_point < i.history_cell.min_data_points:
        return False    
    return True 

  #return the root of the tree
  def generate_tree(self, sb):
    self.no_nodes = 3
    max_street = Const.Street.RIVER
    rr_state = RoundState()
    rp_state = PlayerState()
    rp_state.set(0, [4,4],[2,2],[sb,sb])
    rr_state.set(0, 2*sb, sb, rp_state)
    self.root = Node(name = "root", parent = None, round_state = rr_state, history_cell = None, eva = 0)

    rr_state = RoundState()
    rp_state = PlayerState()
    rp_state.set(0, [4,4],[2,1],[sb,2*sb])
    rr_state.set(0, 3*sb, sb, rp_state)
    small_blind = Node(name = "cr", parent = self.root, round_state = rr_state, history_cell = None, eva = 0)

    rr_state = RoundState()
    rp_state = PlayerState()
    rp_state.set(1, [4,4],[1,2],[2*sb,sb])
    rr_state.set(0, 3*sb, sb, rp_state)
    big_blind = Node(name = "r", parent = self.root, round_state = rr_state, history_cell = None, eva = 0)
    action = ["f", "c", "r"]
    initialize_history_cell = HistoryCell()

    #parent queue
    p_queue = queue.Queue()
    p_queue.put(small_blind)
    p_queue.put(big_blind)

    while p_queue.empty() == False:
      parent = p_queue.get()
      # print parent.name
      # parent.round_state.print_round()
      # parent.round_state.player_state.print_player()
      
      for i in range(3):
        #update this game state from parent then create new node if possible)
        r_state = RoundState()
        p_state = PlayerState()
        #inherit value from parent
        name = copy.deepcopy(parent.name) + action[i]
        player = copy.deepcopy(parent.round_state.player_state.player_no)
        history_cell = copy.deepcopy(initialize_history_cell)
        p_state = copy.deepcopy(parent.round_state.player_state)        
        r_state = copy.deepcopy(parent.round_state)

        #eva depend on who fold
        if action[i] == "f":
          #we fold
          if player == 0:
            eva = 0 - p_state.no_bet[player]
          #opp fold
          elif player == 1:
            eva = r_state.pot - p_state.no_bet[player]
          node = Node(name = name, parent = parent, round_state = r_state, history_cell = None, eva = eva)
          self.no_nodes += 1
        
        #any node here should go to queue
        elif action[i] == "c":
          #level money and move to next turn
          if p_state.no_bet[player] != p_state.no_bet[1-player] and len(name) > 3:
            #raise player bet and change pot
            if  p_state.no_bet[player] > p_state.no_bet[1-player]:
              p_state.no_bet[1-player] = p_state.no_bet[player]
            else:
              p_state.no_bet[player] = p_state.no_bet[1-player]
            r_state.pot = p_state.no_bet[player]*2
            if name[0] == "r":
              player = 1
            elif name[0] == "c":
              player = 0
            r_state.current_street += 1
            name += " "
            p_state.player_no = player
            p_state.no_turn_raise = [2,2]
            r_state.player_state = p_state
            node = Node(name = name, parent = parent, round_state = r_state, history_cell = history_cell, eva = 0)
            if r_state.current_street < (max_street + 1): 
              p_queue.put(node)
          #for first street first action of small blind is call, round continue    
          elif p_state.no_bet[player] != p_state.no_bet[1-player] and len(name) <= 3:
              p_state.player_no = (player + 1)%2            
              r_state.player_state = p_state
              node = Node(name = name, parent = parent, round_state = r_state, history_cell = history_cell, eva = 0) 
              if r_state.current_street < (max_street + 1): 
                p_queue.put(node)
          #double call/start turn call case      
          else: 
            #if previous action is not call --> nothing change, just switch turn
            if name[len(name) - 2] == " ":
              p_state.player_no = (player + 1)%2            
              r_state.player_state = p_state
              node = Node(name = name, parent = parent, round_state = r_state, history_cell = history_cell, eva = 0) 
              if r_state.current_street < (max_street + 1): 
                p_queue.put(node)

            #if previous action is call --> nmove to new street (2 continuous call so no value change)
            elif name[len(name) - 2] == "c":
              if name[0] == "r":
                player = 1
              elif name[0] == "c":
                player = 0
              r_state.current_street += 1
              name += " "
              p_state.player_no = player
              p_state.no_turn_raise = [2,2]
              r_state.player_state = p_state
              node = Node(name = name, parent = parent, round_state = r_state, history_cell = history_cell, eva = 0)
              if r_state.current_street < (max_street + 1): 
                p_queue.put(node)

        #can only raise 2 times in 1 turn and max 4 times
        elif action[i] == "r":
          #if player can raise
          if p_state.no_raise[player] > 0:   
            #if the turn still allow player to raise, perform action and switch turn
            if p_state.no_turn_raise[player] > 0:
              if r_state.current_street > 1:
                p_state.no_bet[player] = p_state.no_bet[1-player] + 4*sb
              else:  
                p_state.no_bet[player] = p_state.no_bet[1-player] + 2*sb
              
              r_state.pot = rp_state.no_bet[player] + rp_state.no_bet[1-player]
              p_state.no_turn_raise[player] -= 1
              p_state.no_raise[player] -= 1
              
              p_state.player_no = (player + 1)%2
              r_state.player_state = p_state
              node = Node(name = name, parent = parent, round_state = r_state, history_cell = None, eva = 0) 
              
              if r_state.current_street < (max_street + 1): 
                p_queue.put(node)
    
class RoundState:

  def __init__(self):
    self.current_street = 0
    self.pot = 0
    self.sb = 20
    self.player_state = PlayerState()

  def set(self, current_street, pot, sb, player_state):
    self.current_street = current_street
    self.pot = pot
    self.sb = sb
    self.player_state = player_state

  def print_round(self):
    print self.current_street, self.pot, self.sb

class PlayerState:
  def __init__(self):
    self.player_no = 0
    self.no_raise = [4,4]
    self.no_turn_raise =[2,2]
    self.no_bet = [0,0]

  def set(self, player_no, no_raise, no_turn_raise, no_bet):
    self.player_no = player_no
    self.no_raise = no_raise
    #this value should only be reseted if current street value increase
    self.no_turn_raise = no_turn_raise
    self.no_bet = no_bet

  def print_player(self):
    print self.player_no, self.no_raise, self.no_turn_raise, self.no_bet
