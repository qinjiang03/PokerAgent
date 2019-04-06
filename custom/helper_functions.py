import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
import itertools
import csv



def evaluateShowdown(holeCards, commCards, oppCards, potAmt):
  # =========================================== #
  # Using PyPokerEngine's HandEvaluator
  # =========================================== #
  holeCards = [Card.from_str(card) for card in holeCards]
  commCards = [Card.from_str(card) for card in commCards]
  oppCards = [Card.from_str(card) for card in oppCards]

  myScore = HandEvaluator.eval_hand(holeCards, commCards)
  oppScore = HandEvaluator.eval_hand(oppCards, commCards)
  if myScore > oppScore:      payout = potAmt
  elif myScore == oppScore:   payout = potAmt / 2
  else:                       payout = -potAmt
  return payout


def getHandStrength(holeCards, commCards):
  holeCards = [Card.from_str(card) for card in holeCards]
  commCards = [Card.from_str(card) for card in commCards]
  score = HandEvaluator.eval_hand(holeCards, commCards)
  return score


def printFeatures(*args):
  for arg in args:
    print(arg)
  return




def evaluationFunc(holeCards, commCards, oppCards, potAmt):
  payout = 0
  return payout




def evaluateHand(holeCards, commCards, oppCards, potAmt, depth):
  if len(oppCards) == 2:
    payout = evaluateShowdown(holeCards, commCards, oppCards, potAmt)
  elif depth <= 1:
    payout = evaluationFunc(holeCards, commCards, oppCards, potAmt)
  else:
    payout = chanceNode(holeCards, commCards, oppCards, potAmt, depth-1)
  return payout



def getNewDeck():
  suits = ['D','C','H','S']
  values = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
  deck = [suit + value for value in values for suit in suits]
  return deck


def reduceDeck(deck, cardsToReduce):
  deck = list(set(deck) - set(cardsToReduce))
  return deck

def getAllCombins(deck, n):
  combins = list(itertools.combinations(deck, n))
  return combins


def chanceNode(holeCards, commCards, oppCards, potAmt, depth):
  if len(commCards) < 3:     n = 3
  elif len(commCards) == 5:  n = 2
  else:                      n = 1
  
  deck = getNewDeck()
  deck = reduceDeck(deck, holeCards + commCards + oppCards)
  combins = getAllCombins(deck, n)

  payouts = []
  for combin in combins:
    newCommCards = commCards
    newOppCards = oppCards
    if len(newCommCards) < 5:
      newCommCards = newCommCards + list(combin)
    else:
      newOppCards = newOppCards + list(combin)
    payout = evaluateHand(holeCards, newCommCards, newOppCards, potAmt, depth)
    payouts.append(payout)
    
  expectedPayout = sum(payouts) / len(payouts)
  return expectedPayout



def lookupProb(holeCards):
  # =========================================== #
  # Read data as dict (from NatesHoldem)
  # =========================================== #
  filename = "custom/preflopProb.csv"
  with open(filename,'r') as file:
      reader = csv.reader(file)
      table = {rows[0]:rows[1] for rows in reader}
  
  hand = "".join([card[1] for card in holeCards])
  if holeCards[0][0] == holeCards[1][0]:    hand += "s"
  elif holeCards[0][1] != holeCards[1][1]:  hand += "o"
  try:
      prob = float(table[hand])
  except KeyError:
      hand = hand[1] + hand[0] + hand[2:]
      prob = float(table[hand])
  return prob
  



# from pypokerengine.engine.action_checker import ActionChecker
# def getValidActions():
#   raise_amount,raise_limit = ActionChecker.round_raise_amount(sb_amount,street)