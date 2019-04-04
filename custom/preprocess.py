import logging
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card
from pypokerengine.utils.card_utils import *
from helper_functions import getNewDeck, reduceDeck, getAllCombins
import pandas as pd
import datetime
import random
from ast import literal_eval
import csv


# =========================================== #
# Generate Combinations
# =========================================== #
def mapCardsToKey(holeCards, commCards):
    SUITS = ['D','C','H','S']
    VALUES = ['A','K','Q','J','T'] + [str(i) for i in range(9,1,-1)]
    suitCount = [sum(card[0] == suit for card in holeCards) + sum(card[0] == suit for card in commCards) for suit in SUITS]
    valueCount = [sum(card[1] == value for card in holeCards) + sum(card[1] == value for card in commCards) for value in VALUES]
    
    suitCount.sort(reverse=True)
    suitKey = "".join([str(i) for i in suitCount])
    valueKey = "".join([str(value) * valueCount[i] for i,value in enumerate(VALUES) if valueCount[i] != 0])
    key = suitKey + "_" + valueKey
    return key



def genUniqCombins(nCommCards):
    deck = getNewDeck()
    holeCardCombins = getAllCombins(deck, 2)

    data = []
    table = {}
    n = 0
    for holeCards in holeCardCombins:
        deck2 = reduceDeck(deck, holeCards)
        commCardCombins = getAllCombins(deck2, nCommCards)
        for commCards in commCardCombins:
            n += 1
            key = mapCardsToKey(holeCards, [])
            if nCommCards > 0: 
                key = key + "_" + mapCardsToKey(holeCards, commCards)
            if key not in table.keys():
                table[key] = 0
                data.append([list(holeCards), list(commCards), key, 0])
                # print("{}: {}, {}; {}; table: {} keys".format(n, holeCards, commCards, key, len(table)))
        
    df = pd.DataFrame(data, columns=["holeCards", "commCards", "Key", "Value"])
    df.to_csv("flopCombins_n{}.csv".format(nCommCards), index=False)
    return




def genUniqCombins2(nCommCards):
    deck = getNewDeck()
    holeCardCombins = getAllCombins(deck, 2)

    data = []
    table = {}
    n = 0
    for holeCards in holeCardCombins:
        n += 1
        holeKey = mapCardsToKey(holeCards, [])        
        if holeKey not in table.keys():
            deck2 = reduceDeck(deck, holeCards)
            commCardCombins = getAllCombins(deck2, nCommCards)

            table2 = {}
            n2 = 0
            for commCards in commCardCombins:
                n2 += 1
                if nCommCards > 0: 
                    key = holeKey + "_" + mapCardsToKey(holeCards, commCards)
                if key not in table2.keys():
                    table2[key] = 0
                    data.append([list(holeCards), list(commCards), key, 0])
                    # print("{}_{}: {}, {}; {}; table: {} keys".format(n, n2, holeCards, commCards, key, len(table2)))
            
            table[holeKey] = table2
            print("{}: {}; {}; table: {}; table2: {}".format(n, holeCards, holeKey, len(table), len(table2)))

    df = pd.DataFrame(data, columns=["holeCards", "commCards", "Key", "Value"])
    df.to_csv("flopCombins_n{}.csv".format(nCommCards), index=False)
    return


def monteCarloSimulation(file, nSims):
    df = pd.read_csv(file)
    
    exportFile = "flopCombinsMC_n3_sim1000.csv"
    with open(exportFile, 'w') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(df.columns)
        for i, row in df.iterrows():
            if i < 5700: continue
            holeCards = literal_eval(row["holeCards"])
            commCards = literal_eval(row["commCards"])
            win_rate = estimate_hole_card_win_rate(
                nb_simulation=nSims,
                nb_player=2,
                hole_card=gen_cards(holeCards),
                community_card=gen_cards(commCards))
            print("{} of {}: {}, {}, {}".format(i, df.shape[0], holeCards, commCards, win_rate))
            writer.writerow([holeCards, commCards, row["Key"], win_rate])
    return




if __name__ == "__main__":
    # genUniqCombins2(3)
    
    import time
    t0 = time.time()
    monteCarloSimulation(file="flopCombins_n3.csv", nSims=1000)
    t1 = time.time()
    print(t1 - t0)
