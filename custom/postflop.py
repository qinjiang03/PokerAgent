import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from helper_functions import getNewDeck, reduceDeck, getAllCombins



def getScore(holeCards, commCards):
    # =========================================== #
    # Using PyPokerEngine's HandEvaluator
    # =========================================== #
    holeCards = [Card.from_str(card) for card in holeCards]
    commCards = [Card.from_str(card) for card in commCards]

    myScore = HandEvaluator.eval_hand(holeCards, commCards)
    return myScore


def calcScore():
    deck = getNewDeck()
    n = 2
    combins = getAllCombins(deck, n)
    
    commCards = []
    scores = []
    for combin in combins:
        holeCards = list(combin)
        score = getScore(holeCards, commCards)
        # print("holeCards: {};\tscore: {}".format(newHoleCards, score))
        scores.append([holeCards, score])
    return scores



if __name__ == "__main__":
    holeCards = []
    scores = calcScore()
    
    import pandas as pd
    df = pd.DataFrame(scores)
    print(df)
