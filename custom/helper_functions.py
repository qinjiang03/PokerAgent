import logging
from copy import deepcopy
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card

def placeBet(roundState, player, amt):
  roundState["pot"]["main"]["amount"] += amt
  roundState["seats"][player]["stack"] -= amt
  return roundState



def getValidActions(roundState, player, numRaiseLeft):
  opp = (player + 1) % 2
  playerStack = roundState["seats"][player]["stack"]
  oppStack = roundState["seats"][opp]["stack"]
  
  validActions = [{'action': 'fold'}, {'action': 'call'}]
  if numRaiseLeft > 0 and playerStack >= 20 and oppStack >= 10:
    validActions.append({'action': 'raise'})

  return validActions



def evaluateShowdown(holeCards, roundState):
  # =========================================== #
  # Using PyPokerEngine's HandEvaluator
  # =========================================== #
  potAmt = roundState["pot"]["main"]["amount"]
  myCards = [Card.from_str(card) for card in holeCards]
  commCards = [Card.from_str(card) for card in roundState["community_card"]]
  oppCards = [Card.from_str(card) for card in roundState["opp_card"]]

  myScore = HandEvaluator.eval_hand(myCards, commCards)
  oppScore = HandEvaluator.eval_hand(oppCards, commCards)
  if myScore > oppScore:
    payout = potAmt
  elif myScore == oppScore:
    payout = potAmt / 2
  else:
    payout = -potAmt

  ######### DEBUG #########
  # logging.info("Showdown: myScore: {}; oppScore: {}; payout: {}".format(myScore, oppScore, payout))
  ######### DEBUG #########
  return payout




def evaluationFunc(holeCards, roundState):
  payout = 0
  ######### DEBUG #########
  # logging.info("Terminate: payout: {}".format(payout))
  ######### DEBUG #########
  return payout




def evaluateHand(holeCards, roundState, depth):
  ######### DEBUG #########
  # logging.info("Evaluate hand: depth: {}".format(depth))
  ######### DEBUG #########

  if len(roundState["opp_card"]) == 2:
    payout = evaluateShowdown(holeCards, roundState)
  elif depth <= 1:
    payout = evaluationFunc(holeCards, roundState)

  else:
    # =========================================== #
    # DON'T CONSIDER ACTION
    # =========================================== #
    payout = chanceNode(holeCards, roundState, depth-1)
  return payout




def openCards(holeCards, roundState, depth):
  suits = ['D','C','H','S']
  values = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
  
  commCards = roundState["community_card"]
  oppCards = roundState["opp_card"]

  payouts = []
  for suit in suits:
    for value in values:
      nextCard = suit + value
      if nextCard in holeCards + commCards + oppCards: continue     # Skip card if already seen
      newCommCards = commCards
      newOppCards = oppCards
      
      # =========================================== #
      # APPEND CARD
      # =========================================== #
      if len(commCards) < 5:
        newCommCards = newCommCards + [nextCard]
        roundState["community_card"] = newCommCards
      else:
        newOppCards = newOppCards + [nextCard]
        roundState["opp_card"] = newOppCards
      
      ######### DEBUG #########
      # logging.info("hole: {}; comm: {}; opp: {}".format(holeCards + newCommCards + newOppCards))
      ######### DEBUG #########

      # =========================================== #
      # OPEN MORE CARDS OR EVALUATE HAND
      # =========================================== #
      if (len(newCommCards) < 3) or (len(newCommCards + newOppCards) == 6):
        payout = openCards(holeCards, roundState, depth)
      else:
        payout = evaluateHand(holeCards, roundState, depth)
      payouts.append(payout)
    
  expectedPayout = sum(payouts) / len(payouts)
  return expectedPayout




def chanceNode(holeCards, roundState, depth):
  payout = openCards(holeCards, roundState, depth)

  ######### DEBUG #########
  logging.info("Chance payout: {}".format(payout))
  ######### DEBUG #########
  return payout



