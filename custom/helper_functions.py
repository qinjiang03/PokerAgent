import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card



def evaluateShowdown(holeCards, commCards, oppCards, potAmt):
  # =========================================== #
  # Using PyPokerEngine's HandEvaluator
  # =========================================== #
  holeCards = [Card.from_str(card) for card in holeCards]
  commCards = [Card.from_str(card) for card in commCards]
  oppCards = [Card.from_str(card) for card in oppCards]

  myScore = HandEvaluator.eval_hand(holeCards, commCards)
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




def evaluationFunc(holeCards, commCards, oppCards, potAmt):
  payout = 0
  ######### DEBUG #########
  # logging.info("Terminate: payout: {}".format(payout))
  ######### DEBUG #########
  return payout




def evaluateHand(holeCards, commCards, oppCards, potAmt, depth):
  ######### DEBUG #########
  # logging.info("Evaluate hand: depth: {}".format(depth))
  ######### DEBUG #########

  if len(oppCards) == 2:
    payout = evaluateShowdown(holeCards, commCards, oppCards, potAmt)
  elif depth <= 1:
    payout = evaluationFunc(holeCards, commCards, oppCards, potAmt)

  else:
    # =========================================== #
    # DON'T CONSIDER ACTION
    # =========================================== #
    payout = chanceNode(holeCards, commCards, oppCards, potAmt, depth-1)
  return payout




def chanceNode(holeCards, commCards, oppCards, potAmt, depth):
  suits = ['D','C','H','S']
  values = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']

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
      else:
        newOppCards = newOppCards + [nextCard]
      
      ######### DEBUG #########
      # logging.info("hole: {}; comm: {}; opp: {}".format(holeCards, newCommCards, newOppCards))
      ######### DEBUG #########

      # =========================================== #
      # OPEN MORE CARDS OR EVALUATE HAND
      # =========================================== #
      if (len(newCommCards) < 3) or (len(newCommCards + newOppCards) == 6):
        payout = chanceNode(holeCards, newCommCards, newOppCards, potAmt, depth)
      else:
        payout = evaluateHand(holeCards, newCommCards, newOppCards, potAmt, depth)
      payouts.append(payout)
    
  expectedPayout = sum(payouts) / len(payouts)
  return expectedPayout




