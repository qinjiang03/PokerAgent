# =========================================== #
# FILE: minimax_player.py
# =========================================== #
class MiniMaxPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state_ori):
    # =========================================== #
    # EXTRACT ROUND STATE INFO
    # =========================================== #
    player = round_state_ori["next_player"]
    opp = (player + 1) % 2
    currStreet = round_state_ori["street"]

    logging.info("\n\n")
    logging.info("Street: {}".format(currStreet))
    logging.info("Hole cards: {}".format(hole_card))
    logging.info("Community cards: {}".format(round_state_ori["community_card"]))
    logging.info("Valid actions: {}".format(valid_actions))


    DEPTH = 1

    start = time.time()
    # =========================================== #
    # CONSIDER ACTION (takes too long)
    # =========================================== #
    payouts = []
    for validAction in valid_actions:
      action = validAction["action"]
      if action == "fold":
        payout = -round_state_ori["pot"]["main"]["amount"]
      elif action == "call":
        round_state = deepcopy(round_state_ori)
        round_state["opp_card"] = []
        round_state = placeBet(round_state, player, amt=10)
        payout = chanceNode(hole_card, round_state, DEPTH)
      else:
        round_state = deepcopy(round_state_ori)
        round_state["opp_card"] = []
        round_state = placeBet(round_state, player, amt=20)
        oppValidActions = getValidActions(round_state, opp, numRaiseLeft=3)
        payout = actionNode(hole_card, round_state, oppValidActions, opp, DEPTH, numRaiseLeft=3)
      payouts.append(payout)

    idx = payouts.index(max(payouts))
    
    bestAction = valid_actions[idx]["action"]

    # =========================================== #
    # LOG TIME TAKEN
    # =========================================== #
    end = time.time()
    duration = end - start
    minutes = duration // 60
    seconds = duration - minutes * 60
    logging.info("Time taken: {:.0f} min {:.3f} s".format(minutes,seconds))
    logging.info("Payout: {}".format(payout))
    logging.info("\n\n")

    return bestAction










# =========================================== #
# FILE: helper_functions.py
# =========================================== #
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
    # CONSIDER ACTION
    # =========================================== #
    startPlayer = roundState["small_blind_pos"]
    validActions = getValidActions(roundState, startPlayer, numRaiseLeft=4)
    payout = actionNode(holeCards, roundState, validActions, startPlayer, depth-1, numRaiseLeft=4)
  return payout




def actionNode(holeCards, roundStateOri, validActions, player, depth, numRaiseLeft):
  opp = (player + 1) % 2

  payouts = []
  for validAction in validActions:
    action = validAction["action"]
    
    if action == "fold":
      payout = -roundStateOri["pot"]["main"]["amount"]

    elif action == "call":
      ######### DEBUG #########
      # logging.info("Call: player: {};  numRaiseLeft: {}".format(player, numRaiseLeft))
      ######### DEBUG #########
      
      roundState = deepcopy(roundStateOri)
      roundState = placeBet(roundState, player, amt=10)
      payout = chanceNode(holeCards, roundState, depth)

    else:
      ######### DEBUG #########
      # logging.info("Raise: player: {};  numRaiseLeft: {}".format(player, numRaiseLeft))
      ######### DEBUG #########

      roundState = deepcopy(roundStateOri)
      roundState = placeBet(roundState, player, amt=20)
      numRaiseLeft -= 1
      oppValidActions = getValidActions(roundState, opp, numRaiseLeft)
      payout = actionNode(holeCards, roundState, oppValidActions, opp, depth, numRaiseLeft)
    payouts.append(payout)

  if player == roundState["next_player"]:
    bestPayout = max(payouts)
  else:
    bestPayout = min(payouts)

  return bestPayout