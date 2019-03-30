import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card



def getScore(holeCards, commCards):
    # =========================================== #
    # Using PyPokerEngine's HandEvaluator
    # =========================================== #
    holeCards = [Card.from_str(card) for card in holeCards]
    commCards = [Card.from_str(card) for card in commCards]

    myScore = HandEvaluator.eval_hand(holeCards, commCards)
    return myScore


def dealCard(holeCards):
    suits = ['D','C','H','S']
    values = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
    
    scores = []
    commCards = []
    for suit in suits:
        for value in values:
            card = suit + value
            if card in holeCards + commCards: continue
            newHoleCards = holeCards + [card]
            if len(newHoleCards) < 2:
                score = dealCard(newHoleCards)
            else:
                score = getScore(newHoleCards, commCards)
                # print("holeCards: {};\tscore: {}".format(newHoleCards, score))
            
            scores.append([newHoleCards, score])

    return scores



if __name__ == "__main__":
    holeCards = []
    scores = dealCard(holeCards)
    
    import pandas as pd
    df = pd.DataFrame(scores)
    print(df)
