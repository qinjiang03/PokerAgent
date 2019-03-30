import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from logging_functions import startLogging, stopLogging
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


def getDeck():
    suits = ['D','C','H','S']
    values = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
    deck = []
    deck = [suit + value for value in values for suit in suits]
    return deck


def dealCards(deck, n):
    dealtCards = random.sample(deck, n)
    deck = list(set(deck) - set(dealtCards))
    return dealtCards, deck


def exportProb(holeCards, winProb):
    return



def calcProb(holeCards):
    deck = getDeck()
    outcomes = []
    numIters = 10000
    for i in range(0,numIters):
        commCards, deck = dealCards(deck, n=5)
        oppCards, deck = dealCards(deck, n=2)
        outcome = evaluateShowdown(holeCards, commCards, oppCards)
        outcomes.append(outcome)
        deck = deck + commCards + oppCards

    numWins = outcomes.count(1)
    winProb = numWins * 1.0 /numIters * 100
    print("holeCards: {}".format(holeCards))
    print("numWins: {}; winProb: {:.3f}".format(numWins, winProb))
    exportProb(holeCards, winProb)
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
