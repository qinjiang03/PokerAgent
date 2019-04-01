import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from logging_functions import startLogging, stopLogging
from helper_functions import getNewDeck, reduceDeck
from datetime import datetime
import random
import csv



def evaluateShowdown(holeCards, commCards, oppCards):
    # =========================================== #
    # Using PyPokerEngine's HandEvaluator
    # =========================================== #
    holeCards = [Card.from_str(card) for card in holeCards]
    commCards = [Card.from_str(card) for card in commCards]
    oppCards = [Card.from_str(card) for card in oppCards]

    myScore = HandEvaluator.eval_hand(holeCards, commCards)
    oppScore = HandEvaluator.eval_hand(oppCards, commCards)

    if myScore > oppScore:        return 1
    elif myScore == oppScore:     return 0
    else:                         return -1



def calcProb(holeCards):
    deck = getNewDeck()
    outcomes = []
    numIters = 10000
    for i in range(0,numIters):
        commCards = random.sample(deck, 5)
        deck = reduceDeck(deck, commCards)
        oppCards = random.sample(deck, 2)
        deck = reduceDeck(deck, oppCards)

        outcome = evaluateShowdown(holeCards, commCards, oppCards)
        outcomes.append(outcome)
        deck = deck + commCards + oppCards

    numWins = outcomes.count(1)
    winProb = numWins * 1.0 /numIters * 100
    print("holeCards: {}".format(holeCards))
    print("numWins: {}; winProb: {:.3f}".format(numWins, winProb))
    return



def lookupProb(holeCards):
    # =========================================== #
    # Read data as dict (from NatesHoldem)
    # =========================================== #
    filename = "custom/preflopProb.csv"
    with open(filename,'r') as file:
        reader = csv.reader(file)
        table = {rows[0]:rows[1] for rows in reader}
    
    hand = "".join([card[1] for card in holeCards])
    if holeCards[0][0] == holeCards[1][0]:
        hand += "s"
    elif holeCards[0][1] != holeCards[1][1]:
        hand += "o"
    try:
        prob = float(table[hand])
    except KeyError:
        hand = hand[1] + hand[0] + hand[2:]
        prob = float(table[hand])
    return prob



if __name__ == "__main__":

    # logFile = "preflop_{}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    # logger = startLogging(logFile)
    
    holeCards = ['SA', 'HA']
    # calcProb(holeCards)
    # lookupProb(holeCards)
    
    # stopLogging(logger)
