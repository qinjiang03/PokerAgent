from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.engine.card import Card

from lib.net import DQN
from lib.buffer import ExperienceBuffer

import csv
import time
import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import collections

Experience = collections.namedtuple('Experience',
                                    field_names=[
                                        'state',
                                        'action',
                                        'new_state'
                                    ])



class LearningPlayer(BasePokerPlayer):

    def __init__(self, training=False, model_path='model.dat', stats_path='stats.csv'):
        self.numGames = 0
        self.numFolds_opp = 0
        self.numActions_opp = 0
        self.numCalls_opp = 0
        self.numRaises_opp = 0

        # Flag to indicate whether our agent is in training mode
        self.training = training
        self.MODEL_PATH = model_path
        self.STATS_PATH = stats_path
        # Initialize our neural net
        self.N_FEAT = 20
        self.N_ACTIONS = 3
        self.N_HIDDEN = round((self.N_FEAT + self.N_ACTIONS) / 2)
        self.N_LAYERS = 1
        self.net = DQN(self.N_FEAT, self.N_HIDDEN, self.N_ACTIONS, self.N_LAYERS)
        # Counter of frames
        self.frame_i = 0

        # Load pre-trained weights?

        if self.training:
            self.GAMMA = 0.99
            # Batch size sampled from the replay buffer
            self.BATCH = 32
            # Maximum capacity of the buffer
            self.REPLAY_SIZE = 10**2
            # Count of frames to wait for before starting training to
            # populate the replay buffer
            self.REPLAY_START_SIZE = 10**2
            self.LEARNING_RATE = 1e-4
            # How frequently we sync model weights from the training model
            # to the target model, which is used to get the next state in
            # the Bellman approximation
            self.SYNC_TARGET_FRAMES = 10**1

            self.EPSILON_DECAY_LAST_FRAME = 10**3
            self.EPSILON_START = 1.0
            self.EPSILON_FINAL = 0.02

            # Target net
            self.tgt_net = DQN(self.N_FEAT, self.N_HIDDEN, self.N_ACTIONS, self.N_LAYERS)
            self.optimizer = optim.Adam(self.net.parameters(),
                                        lr=self.LEARNING_RATE)
            # Initialize experience buffer
            self.exp_buffer = ExperienceBuffer(self.REPLAY_SIZE)

            # Keep track of rewards for each episode
            self.total_rewards = []
            # Best mean reward reached
            self.best_mean_reward = None
            # Stores the prev state
            self.prev_feat_vector = None
            # Stores the prev action
            self.prev_action = None



    def declare_action(self, valid_actions, hole_card, round_state):
        """AI HERE.
        Returns an action, based on the current state.

        Args:
            valid_actions: A list of valid actions, i.e.
                [
                    { "action" : "fold"  },
                    { "action" : "call" },
                    { "action" : "raise" }
                ]
                May not include the "raise" action.

            hole_card: A list of the two hole cards, e.g. ['CA', 'DK'].

            round_state: A dict of all the various round information.

        Returns (str):
            A string indicating the action to take, i.e.
            "fold" / "call" / "raise"
        """
        # Start of frame
        self.frame_i += 1

        valid_actions = [a['action'] for a in valid_actions]

        # Generate feature vector based on current state
        feat_vector = self._gen_feat_vector(hole_card, round_state)

        # Perform training first, based on previous state
        # Don't train during the first round
        if self.training and not self.prev_feat_vector is None:
            # Store the current transition in the buffer
            self._store_buffer(feat_vector)
            self._train_step()

        # An action is then chosen based on our feature vector
        action = self._choose_action(valid_actions, feat_vector)
        # We'll save this action and the state, for the next step
        if self.training:
            self.prev_feat_vector = feat_vector
            self.prev_action = action

        return valid_actions[action]



    ################
    # MAIN METHODS #
    ################
    def _choose_action(self, valid_actions, feat_vector):
        """Chooses an action.
        ACCOUNT FOR WHEN UNABLE TO RAISE

        Args:
            valid_actions: A list of valid actions, i.e.
                ["fold", "call", "raise"]
                May not include the "raise" action.

            feat_vector: A list of numeric features.

        Returns:
            Int corresponding to chosen action, 0 / 1 / 2
        """
        # Check if unable to raise
        can_raise = len(valid_actions) == 3

        # Make a random move
        # if False:
        if random.random() < self._epsilon():
            # print(f'Random move executed w/ prob of {self._epsilon()}')
            action = random.choice([0, 1, 2]) if can_raise else \
                     random.choice([0, 1])

        # Else choose the action that returns the Q value
        else:
            # Compute the Q values for each action
            feat_vector = np.array([feat_vector], copy=False)
            feat_vector = torch.Tensor(feat_vector)
            # Tensor of shape (1, 3)
            q_vals = self.net(feat_vector)
            q_vals = q_vals if can_raise else q_vals[:,:2]

            # Get the action with the max value
            _, act_v = torch.max(q_vals, dim=1)
            action = int(act_v.item())

        return action

    def _store_buffer(self, feat_vector):
        """Stores the current transition in the buffer

        feat_vector: List of numerical values.
        """
        assert self.prev_feat_vector is not None and \
               self.prev_action is not None
        # Store the transition in the buffer
        exp = Experience(self.prev_feat_vector,
                         self.prev_action,
                         feat_vector)

        self.exp_buffer.append(exp)

    def _train_step(self):
        """Performs a training step based on
        the current state and the previous state.
        """
        # Check whether our buffer is large enough for training
        if len(self.exp_buffer) < self.REPLAY_START_SIZE:
            return
        # Sync parameters from our main net to the target net
        if self.frame_i % self.SYNC_TARGET_FRAMES == 0:
            self.tgt_net.load_state_dict(self.net.state_dict())

        # TRAINING
        self.optimizer.zero_grad()
        batch = self.exp_buffer.sample(self.BATCH)
        loss_t = self._calc_loss(batch)
        loss_t.backward()
        self.optimizer.step()

    def _gen_feat_vector(self, hole_card, round_state):
        MAX_HAND_STR = 8429805.0
        STREETS = {"preflop": 1, "flop": 2, "turn": 3, "river": 4}

        potAmt = round_state["pot"]["main"]["amount"]
        stacks = [seat["stack"] for seat in round_state["seats"]]
        TOTAL_STACK = potAmt + sum(stack for stack in stacks)

        potFrac = [potAmt * 1.0 / TOTAL_STACK]
        stackFracs = [stack * 1.0 / TOTAL_STACK for stack in stacks]

        handStr = [self._get_hand_strength(hole_card, round_state["community_card"]) / MAX_HAND_STR]
        streetNum = [num for street, num in STREETS.items() if round_state["street"] == street]
        isSmallBlind = [1] if round_state["next_player"] == round_state["small_blind_pos"] else [0]
        numRaiseSelf = [sum(1 if history["action"] == "RAISE" and history["uuid"] == self.uuid else 0 \
                        for history in round_state["action_histories"][street]) / 4.0 \
                        if street in round_state["action_histories"] else 0 \
                        for street in STREETS.keys()]
        numRaiseOpp = [sum(1 if history["action"] == "RAISE" and history["uuid"] != self.uuid else 0 \
                        for history in round_state["action_histories"][street]) / 4.0 \
                        if street in round_state["action_histories"] else 0 \
                        for street in STREETS.keys()]
        totalRaiseSelf = [sum(numRaiseSelf)]
        totalRaiseOpp = [sum(numRaiseOpp)]

        histFoldOpp = [self.numFolds_opp * 1.0 / self.numGames] if self.numGames != 0 else [0.0]
        histCallOpp = [self.numCalls_opp * 1.0 / self.numActions_opp] if self.numActions_opp != 0 else [0.0]
        histRaiseOpp = [self.numRaises_opp * 1.0 / self.numActions_opp] if self.numActions_opp != 0 else [0.0]

        features = handStr + streetNum + isSmallBlind \
          + numRaiseSelf + numRaiseOpp + totalRaiseSelf + totalRaiseOpp \
          + potFrac + stackFracs \
          + histFoldOpp + histCallOpp + histRaiseOpp

        return features


    ##################
    # HELPER METHODS #
    ##################
    def _epsilon(self):
        """Calculate the probability of making a random move.
        """
        return max(self.EPSILON_FINAL,
                   self.EPSILON_START - self.frame_i / self.EPSILON_DECAY_LAST_FRAME)

    def _calc_loss(self, batch):
        """Receives a batch of data from the experience buffer,
        and calculates the loss value.

        Backpropogation is to be performed thereafter.
        """
        states, actions, next_states = batch

        states_v = torch.Tensor(states)
        next_states_v = torch.Tensor(next_states)
        actions_v = torch.LongTensor(actions)

        # Get Q-value of each state
        state_action_values = self.net(states_v) \
            .gather(1, actions_v.unsqueeze(-1)).squeeze(-1)
        # Get Q-value of each next state
        next_state_values = self.tgt_net(next_states_v).max(1)[0]
        # We prevent gradients from flowing into the net
        next_state_values = next_state_values.detach()

        # Calculate loss here
        expected_state_action_values = next_state_values*self.GAMMA

        return nn.MSELoss()(state_action_values, expected_state_action_values)

    def _get_hand_strength(self, holeCards, commCards):
        holeCards = [Card.from_str(card) for card in holeCards]
        commCards = [Card.from_str(card) for card in commCards]
        score = HandEvaluator.eval_hand(holeCards, commCards)
        return score



    def receive_game_start_message(self, game_info):
        # Track time taken
        self.ts = time.time()
        # Store the stack amount
        self.TOTAL_STACK = game_info['rule']['initial_stack']*2

    def receive_round_start_message(self, round_count, hole_card, seats):
        # Store hole card for end of round
        self.hole_card = hole_card
        # Reset agent
        if self.training:
            self.prev_feat_vector = None
            self.prev_action = None

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        if action["player_uuid"] != self.uuid:
            self.numActions_opp += 1
            if action["action"] == "fold":    self.numFolds_opp += 1
            elif action["action"] == "call":  self.numCalls_opp += 1
            elif action["action"] == "raise": self.numRaises_opp += 1
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        """Perform final episode training step here?
        With the reward being the payoff.
        """
        # Start of the last frame of the episode
        self.frame_i += 1

        ############
        # TRAINING #
        ############

        # Get hole card
        hole_card = self.hole_card

        # Do a final training step for the episode
        feat_vector = self._gen_feat_vector(hole_card, round_state)

        if self.training and not self.prev_feat_vector is None:
            # Store the current transition in the buffer
            self._store_buffer(feat_vector)
            self._train_step()

        ####################
        # CONCLUDE EPISODE #
        ####################

        # Check whether the agent wins the round
        won = self.uuid == winners[0]['uuid']
        # Get the payoff for this round
        reward = round_state['pot']['main']['amount']
        if not won:
            reward = -reward
        # Get current stack
        winner_stack = winners[0]['stack']
        stack = winner_stack if won else self.TOTAL_STACK - winner_stack

        self.total_rewards.append(reward)
        # Calculate mean reward
        mean_reward = np.mean(self.total_rewards[-100:])
        # Calulate time taken for one episode
        time_taken = time.time() - self.ts

        # Log information
        print("%d: done %d games, mean reward %.3f, eps %.2f, time %.2f s" %
              (self.frame_i, len(self.total_rewards), mean_reward,
               self._epsilon(), time_taken))

        ##############################
        # MODEL AND STATS SAVED HERE #
        ##############################

        # Save model if best mean reward so far
        if self.training:
            if self.best_mean_reward is None or \
               self.best_mean_reward < mean_reward:

                torch.save(self.net.state_dict(), self.MODEL_PATH)
                if self.best_mean_reward is not None:
                    print("Best mean reward updated %.3f -> %.3f, model saved" % (self.best_mean_reward, mean_reward))
                self.best_mean_reward = mean_reward

            # Save statistics
            # - frame_i
            # - epsilon
            # - mean_reward
            # - reward
            # - stack
            with open(self.STATS_PATH, mode='w') as stats:
                stats_writer = csv.writer(stats, delimiter=',')
                stats_writer.writerow([self.frame_i, self._epsilon(),
                                       mean_reward, reward, stack])



def setup_ai():
    return LearningPlayer()
