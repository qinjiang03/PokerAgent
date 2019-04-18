#This is a poker agent that try to model opponent strategy and counter it

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from pypokerengine.engine.poker_constants import PokerConstants as Const
from anytree import Node, Walker, RenderTree, ContStyle, search, LevelOrderIter
from custom import helper_functions
import queue
import random as rand
import pprint
import numpy
import itertools
import copy
import math

class NovicePlayer(BasePokerPlayer):
  def __init__(self):
    #for call and raise only, since you cannot observe opponent hand when his fold
    #opp_model = [low, high, probability within k*standard_deviation, k = sqrt(standard_deviation)]
    self.opp_model = list((0, 0, 0, 0))
    #to observe the action perform in that sequence given the believe EHS at that current state (got opponent hand from showdown, do the same as our hand)
    #assume opponent action depend on his current observance of his own EHS
    #opponent must be consistent at least within 30 - 50 rounds
    self.raiseEHS = list()
    self.raiseEHS.append(0)
    self.callEHS = list()
    self.callEHS.append(0)
    self.action_sequence = str()
    self.action_tree = SequenceActionTree()
    self.action_tree.generate_tree(20)
    self.hole_card = None
    self.player_position = None
    self.player_uuid = None

    #print self.action_tree.no_nodes
    #print(RenderTree(self.action_tree.root, style=ContStyle()).by_attr("name"))
    # for row in RenderTree(self.action_tree.root, style=ContStyle()):
    #   print(row.node.name)
    #   row.node.round_state.print_round()
    #   row.node.round_state.player_state.print_player()
    #   print(" ")
    
  def declare_action(self, valid_actions, hole_card, round_state):    
    #run one to know if we are small blind or big blind
    if round_state['street'] == "preflop" and self.player_position == None:
      if len(round_state['action_histories']['preflop']) > 2:
        self.action_sequence = "r"
        self.player_position = "big_blind"
        self.player_uuid = round_state['action_histories']['preflop'][1]['uuid']
      else: 
        self.action_sequence = "cr" 
        self.player_position = "small_blind"
        self.player_uuid = round_state['action_histories']['preflop'][0]['uuid']

    self.update_lastest_history(round_state)
    current_node = self.action_tree.search_node_by_name(self.action_sequence)
    
    opp_model_action = None
    #fail safe in case tree construction have error
    if current_node == None:
      print "tree construction has error", self.action_sequence
      opp_model_action = None
    else:
      #test method at turn
      opp_model_action = self.action_tree.declare_action(current_node, 1, self.opp_model)

    #there is not enough data to declare action
    #put honest player here
    if opp_model_action == None:
      opp_model_action = "call"

    for i in valid_actions:
      if i["action"] == opp_model_action:
        action = i["action"]
        return action 

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    self.hole_card = hole_card
    
  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    #get opp card from here
    for i in hand_info:
      if i['hand']['card'] != self.hole_card:
        opp_card = i['hand']['card']

        #river
        update_node_action_sequence = self.leaf_node_sequence_at_street(round_state, 3)
        EHS_opp = PlayerUtil.hand_strength(opp_card, round_state['community_card'])
        node = self.action_tree.search_node_by_name(update_node_action_sequence)
        node.history_cell.update_action_frequency_cell(EHS_opp)
        self.update_call_raise_EHS(round_state, 3, EHS_opp)

        #turn
        update_node_action_sequence = self.leaf_node_sequence_at_street(round_state, 2) 
        node = self.action_tree.search_node_by_name(update_node_action_sequence)
        #use precompute method here later
        EHS_opp = 0.457
        node.history_cell.update_action_frequency_cell(EHS_opp)
        self.update_call_raise_EHS(round_state, 2, EHS_opp)

        #flop
        update_node_action_sequence = self.leaf_node_sequence_at_street(round_state, 1) 
        node = self.action_tree.search_node_by_name(update_node_action_sequence)
        #use precompute method here later
        EHS_opp = 0.5
        node.history_cell.update_action_frequency_cell(EHS_opp)
        self.update_call_raise_EHS(round_state, 1, EHS_opp)

        self.update_opp_model()

    #reset variable here
    self.action_sequence = ""

  def setup_ai():
    return NovicePlayer()

  def update_opp_model(self):
    call_mean = PlayerUtil.calculate_mean(self.callEHS)
    call_var = PlayerUtil.calculate_var(self.callEHS)

    raise_mean = PlayerUtil.calculate_mean(self.raiseEHS)
    raise_var = PlayerUtil.calculate_var(self.raiseEHS)
    
    self.opp_model[0] = call_mean - call_var
    self.opp_model[1] = call_mean + call_var
    self.opp_model[2] = raise_mean - raise_var
    self.opp_model[3] = raise_mean + raise_var

  def update_call_raise_EHS(self, round_state, street, EHS_opp):
    no_call_raise = self.number_of_raise_call_at_street(round_state, street)
    threshold = 1500
    forget = 20

    for i in range(no_call_raise[0]):
      self.callEHS.append(EHS_opp)

    for i in range(no_call_raise[1]):
      self.raiseEHS.append(EHS_opp)

    if len(self.callEHS) > threshold:
      for i in range(forget):
        self.callEHS.pop(0)
    
    if len(self.raiseEHS) > threshold:
      for i in range(forget):
        self.raiseEHS.pop(0)        

  def number_of_raise_call_at_street(self, round_state, street):
    c = 0
    r = 0
  
    if street == 0:
      action_list = round_state['action_histories']['preflop']
    elif street == 1:
      action_list = round_state['action_histories']['flop']
    elif street == 2:
      action_list = round_state['action_histories']['turn']
    elif street == 3:
      action_list = round_state['action_histories']['river']
    
    for action in action_list:
      if action['action'] == "RAISE" and action['uuid'] != self.player_uuid:
        r += 1
      elif action['action'] == "CALL" and action['uuid'] != self.player_uuid:
        c += 1
    if r == 2:
      c -= 1
    return (c, r)   

  def leaf_node_sequence_at_street(self, round_state, street):
    if self.player_position == "small_blind":
      street_action_sequence = "cr"
    else:
      street_action_sequence= "r"

    #print current_no_street
    for i in range(street + 1):
      if i == 0:
        action_list = round_state['action_histories']['preflop']
      elif i == 1:
        action_list = round_state['action_histories']['flop']
      elif i == 2:
        action_list = round_state['action_histories']['turn']
      elif i == 3:
        action_list = round_state['action_histories']['river']
      if len(action_list) > 0:
        for action in action_list:
          if action['action'] != "SMALLBLIND" and action['action'] != "BIGBLIND":
             street_action_sequence += self.action_mapping(action['action'])
        street_action_sequence += "|"

    return street_action_sequence

  def update_lastest_history(self, round_state):
    if self.player_position == "small_blind":
      self.action_sequence = "cr"
    else:
      self.action_sequence = "r"

    current_no_street = len(round_state['action_histories'])
    #print current_no_street
    for i in range(current_no_street):
      if i == 0:
        action_list = round_state['action_histories']['preflop']
      elif i == 1:
        action_list = round_state['action_histories']['flop']
      elif i == 2:
        action_list = round_state['action_histories']['turn']
      elif i == 3:
        action_list = round_state['action_histories']['river']
      if len(action_list) > 0:
        for action in action_list:
          if action['action'] != "SMALLBLIND" and action['action'] != "BIGBLIND":
            self.action_sequence += self.action_mapping(action['action'])
        #append at the end of street if action in the lastest street is call that is not double call  
        if i < current_no_street - 1 or (i == current_no_street - 1 and action['action'] == "CALL" and self.action_sequence[len(self.action_sequence) - 2] != "|"):
          self.action_sequence += "|"

  def action_mapping(self, action):
    if action  == "CALL":
      return "c"
    elif action == "RAISE":
      return "r"
    else:
      return "f"


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
    ahead = 0 
    tied = 0
    behind = 0
  
    for opp_cards in oppPossbileCards:
      opp_cards = [Card.from_str(card) for card in opp_cards]
      opprank = HandEvaluator.eval_hand(opp_cards, comm_cards)
      if ourrank > opprank:
          ahead += 1
      elif ourrank == opprank:
          tied += 1
      else:
          behind += 1
    return (ahead + tied / 2.0) / (ahead + tied + behind)

  @staticmethod  
  def positive_potential(hole_cards, comm_cards):
    ahead = 0
    tied = 1
    behind = 2
    HP = list((0,0),(0,0),(0,0))
    HPTotal = list(0, 0, 0)
    deck = PlayerUtil.reduceDeck(PlayerUtil.getNewDeck(), comm_cards)
    deck = PlayerUtil.reduceDeck(deck, hole_cards)
    oppPossbileCards = PlayerUtil.getAllCombins(deck, 2)   
    
    hole_cards = [Card.from_str(card) for card in hole_cards]
    comm_cards = [Card.from_str(card) for card in comm_cards]    
    ourrank = HandEvaluator.eval_hand(hole_cards, comm_cards)
  
    if len(comm_cards) == 3:   
      n = 2
    elif len(comm_cards) == 4: 
      n = 1
    else:                      
      n = 0
  
    for opp_cards in oppPossbileCards:
      possible_board_deck = copy.deepcopy(deck)
      possible_board_deck = PlayerUtil.reduceDeck(possible_board_deck, opp_cards)
      possible_board_cards = PlayerUtil.getAllCombins(possible_board_deck, n)
      
      opp_cards = [Card.from_str(card) for card in opp_cards]
      opprank = HandEvaluator.eval_hand(opp_cards, comm_cards)

      if ourrank > opprank:
          index = 0
      elif ourrank == opprank:
          index = 1
      else:
          index = 2
      HPTotal[index] += 1

      for p_board_card in possible_board_cards:
        p_board_card = [Card.from_str(card) for card in p_board_card]
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
    HS = PlayerUtil.hand_strength(hole_cards, comm_cards)
    PosP = PlayerUtil.positive_potential(hole_cards, comm_cards)
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
  def update_action_frequency_cell(self, EHS):
    #round to 1 decimal, using 10 cell divider
    if EHS == 0.0:
      EHS += 0.01
    self.EHS_frequency_cell[int(math.ceil(EHS*10 - 1))] += 1
    self.total_data_point += 1

  #Probability of opponent having action from the node that contain this cell 
  def pr_EHS_range_call_only(self, opp_model):
    callPr = 0.0
    total = 0.0
    #call probability
    for i in range(int(opp_model[0]*10 - 1), int(math.ceil(opp_model[1]*10 - 1))):
      total += EHS_frequency_cell[i]
    
    callPr = float(total)/self.total_data_point
    return [1 - callPr, callPr]

  def pr_EHS_range(self, opp_model):
    callPr = 0.0
    raisePr = 0.0
    total = 0.0
    #call probability
    for i in range(int(opp_model[0]*10 - 1), int(math.ceil(opp_model[1]*10 - 1))):
      total += EHS_frequency_cell[i]
    
    callPr = float(total)/self.total_data_point
    total = 0.0

    #raise probability
    for i in range(int(opp_model[2]*10 - 1), int(math.ceil(opp_model[3]*10 - 1))):
      total += EHS_frequency_cell[i]
    raisePr = float(total)/self.total_data_point

    return [1 - callPr - raisePr, callPr, raisePr]

#This tree only need to follow normal rule and with these restriction
#1. each player have max 4 number of raise
#2. 2 max raise in a turn
#3. big blind is counted as 1 raise
#set name same to the sequence of action that lead to this point
#the tree expand given this agent as the root or player 0
#if we are small blind, first action is call, and opp first action is raise
#if we are big blind, first action is raise, then act normally
#only cut_off(end_street node) or terminal(leaf node) should contain history cell
class SequenceActionTree: 
  def __init__(self):
    self.no_nodes = 0
    self.root = None

  #to search for current position
  def search_node_by_name(self, name):
    return search.find_by_attr(self.root, name, name = 'name')

  #To search for all node leaf node at current street given current node and the depth = number of street player
  #bug here
  def all_leaf_node_in_current_street(self, current_node, depth):
    current_street = copy.deepcopy(current_node.round_state.current_street)
    if current_street + depth > Const.Street.RIVER:
      return None
    else:
      return search.findall(current_node, filter_=lambda node: (node.round_state.current_street == current_street + depth) and node.history_cell != None)

  #To check if the cut_off node have enough data point to use
  #return false if anynode in the subtree need to search don't have enough data points to use for calculation
  def check_opp_model_availability(self, node_list):
    for i in node_list:
      if i.history_cell.total_data_point < i.history_cell.min_data_points:
        return False    
    return True 

  def push_eva(self, current_node, node_list, opp_model):
    #compute eva for every leaf node
    for node in node_list:
      if node.name[len(name) - 1] != "f":
        #evaluation function here
        node.eva = 0#Eval()

    #push eva 
    for leaf in node_list:
      parent = leaf.parent
      #level order transverse using parent, then compute eva for each child
      child_list = LevelOrderIter(current_node, maxLevel = 1)

      #remove any already compute from the node_list
      node_list = list(set(node_list) - set(child_list))
      #add the parent to the list if parent is not current node
      if parent != current_node:
        node_list.append(parent)

      #parent is player node
      if parent.round_state.player_state.player_no == 0:
        parent.eva = -100000000.0
        for child in child_list:
          if child.eva > eva:
            eva = child.eva
      
      #parent is opp node
      elif parent.round_state.player_state.player_no == 1: 
        #cannot raise
        parent.eva = 0
        if len(child_list) == 2:
          pr_opp_action = leaf.history_cell.pr_EHS_range_call_only(opp_model)
          for child in child_list:
            if child.name[len(name)-1] == "f":
              parent.eva += child.eva*pr_opp_action[0]
            else:
              parent.eva += child.eva*pr_opp_action[1]
        
        else:
          pr_opp_action = leaf.history_cell.pr_EHS_range(opp_model)
          for child in child_list:
            if child.name[len(name)-1] == "f":
              parent.eva += child.eva*pr_opp_action[0]
            elif child.name[len(name)-1] == "r":
              parent.eva += child.eva*pr_opp_action[2]
            else:
              parent.eva += child.eva*pr_opp_action[1]

  def declare_action(self, current_node, depth, opp_model):
    #max eva of the child using level transverse
    action = None
    cut_off_nodes = self.all_leaf_node_in_current_street(current_node, depth)
    if self.check_opp_model_availability(cut_off_nodes) == False:
      return action
    self.push_eva(current_node, cut_off_nodes, opp_model)

    child_list = LevelOrderIter(current_node, maxLevel = 1)
    eva = -100000000.0
    for child in child_list:
      if child.eva > eva:
        eva = child.eva
        action = action_mapping(child.name[len(child.name) - 1])
    return action

  def action_mapping(self, action_from_name):
    if action_from_name == "r":
      return "raise"
    elif action_from_name == "c":
      return "call"
    else:
      return "fold"  

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
          #for first street first action of small blind is call, round continue    
          if p_state.no_bet[player] != p_state.no_bet[1-player] and r_state.current_street == 0 and (name == "crc" or name == "rc"):
              p_state.player_no = (player + 1)%2            
              r_state.player_state = p_state
              node = Node(name = name, parent = parent, round_state = r_state, history_cell = None, eva = 0) 
              if r_state.current_street < (max_street + 1): 
                p_queue.put(node)
          
          #level money and move to next turn
          elif p_state.no_bet[player] != p_state.no_bet[1-player]:
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
            name += "|"
            p_state.player_no = player
            p_state.no_turn_raise = [2,2]
            r_state.player_state = p_state
            node = Node(name = name, parent = parent, round_state = r_state, history_cell = history_cell, eva = 0)
            if r_state.current_street < (max_street + 1): 
              p_queue.put(node)

          #double call/start turn call case      
          else: 
            #if previous action is not call --> nothing change, just switch turn
            if name[len(name) - 2] == "|":
              p_state.player_no = (player + 1)%2            
              r_state.player_state = p_state
              node = Node(name = name, parent = parent, round_state = r_state, history_cell = None, eva = 0) 
              if r_state.current_street < (max_street + 1): 
                p_queue.put(node)

            #if previous action is call --> nmove to new street (2 continuous call so no value change)
            elif name[len(name) - 2] == "c":
              if name[0] == "r":
                player = 1
              elif name[0] == "c":
                player = 0
              r_state.current_street += 1
              name += "|"
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
