import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
import itertools



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



def getDeck():
  suits = ['D','C','H','S']
  values = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
  deck = [suit + value for value in values for suit in suits]
  return deck



def chanceNode(holeCards, commCards, oppCards, potAmt, depth):
  deck = getDeck()
  deck = list(set(deck) - set(holeCards + commCards + oppCards))

  if len(commCards) < 3:     n = 3
  elif len(commCards) == 5:  n = 2
  else:                      n = 1
  combins = list(itertools.combinations(deck, n))

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




