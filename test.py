import random
import torch
import torch.optim as optim
import numpy as np
import collections

from learning_player import LearningPlayer
from lib.net import DQN
from lib.buffer import ExperienceBuffer

round_count = 2
seats = [
  {'stack': 135, 'state': 'participating', 'name': 'p1', 'uuid': 'ftwdqkystzsqwjrzvludgi'},
  {'stack': 80, 'state': 'participating', 'name': 'p2', 'uuid': 'bbiuvgalrglojvmgggydyt'},
  {'stack': 40, 'state': 'participating', 'name': 'p3', 'uuid': 'zkbpehnazembrxrihzxnmt'}
]

valid_actions = [
                    { "action" : "fold"  },
                    { "action" : "call" },
                    { "action" : "raise" }
                ]
hole_card = ['CA', 'DK']
round_state = {
  'round_count': 2,
  'dealer_btn': 1,
  'small_blind_pos': 2,
  'big_blind_pos': 0,
  'next_player': 0,
  'small_blind_amount': 10,
  'street': 'turn',
  'community_card': ['DJ', 'H6', 'S6', 'H5'],
  'seats': [
    {'stack': 95, 'state': 'participating', 'name': 'p1', 'uuid': 'ftwdqkystzsqwjrzvludgi'},
    {'stack': 20, 'state': 'participating', 'name': 'p2', 'uuid': 'bbiuvgalrglojvmgggydyt'},
    {'stack': 0, 'state': 'allin', 'name': 'p3', 'uuid': 'zkbpehnazembrxrihzxnmt'}
  ],
  'pot': {
    'main': {'amount': 165},
    'side': [{'amount': 20, 'eligibles': ['ftwdqkystzsqwjrzvludgi', 'bbiuvgalrglojvmgggydyt']}]
  },
  'action_histories': {
    'preflop': [
      {'action': 'ANTE', 'amount': 5, 'uuid': 'zkbpehnazembrxrihzxnmt'},
      {'action': 'ANTE', 'amount': 5, 'uuid': 'ftwdqkystzsqwjrzvludgi'},
      {'action': 'ANTE', 'amount': 5, 'uuid': 'bbiuvgalrglojvmgggydyt'},
      {'action': 'SMALLBLIND', 'amount': 10, 'add_amount': 10, 'uuid': 'zkbpehnazembrxrihzxnmt'},
      {'action': 'BIGBLIND', 'amount': 20, 'add_amount': 10, 'uuid': 'ftwdqkystzsqwjrzvludgi'},
      {'action': 'CALL', 'amount': 20, 'uuid': 'bbiuvgalrglojvmgggydyt', 'paid': 20},
      {'action': 'RAISE', 'amount': 30, 'add_amount': 10, 'paid': 20, 'uuid': 'zkbpehnazembrxrihzxnmt'},
      {'action': 'CALL', 'amount': 30, 'uuid': 'ftwdqkystzsqwjrzvludgi', 'paid': 10},
      {'action': 'CALL', 'amount': 30, 'uuid': 'bbiuvgalrglojvmgggydyt', 'paid': 10}
    ],
    'flop': [
      {'action': 'CALL', 'amount': 0, 'uuid': 'zkbpehnazembrxrihzxnmt', 'paid': 0},
      {'action': 'RAISE', 'amount': 30, 'add_amount': 30, 'paid': 30, 'uuid': 'ftwdqkystzsqwjrzvludgi'},
      {'action': 'CALL', 'amount': 30, 'uuid': 'bbiuvgalrglojvmgggydyt', 'paid': 30},
      {'action': 'CALL', 'amount': 20, 'uuid': 'zkbpehnazembrxrihzxnmt', 'paid': 20}
     ],
    'turn': [],
  }
}

winners = [
  {'stack': 300, 'state': 'participating', 'name': 'p1', 'uuid': 'ftwdqkystzsqwjrzvludgi'}
]
hand_info = [ {'hand': {'card': ['HQ', 'HA'],
           'hand': {'high': 12, 'low': 0, 'strength': 'ONEPAIR'},
           'hole': {'high': 14, 'low': 12}},
  'uuid': 'dfaeddzjrhvkmprfwyenkm'},
 {'hand': {'card': ['S9', 'HT'],
           'hand': {'high': 10, 'low': 9, 'strength': 'HIGHCARD'},
           'hole': {'high': 10, 'low': 9}},
  'uuid': 'ftwdqkystzsqwjrzvludgi'}]

Experience = collections.namedtuple('Experience',
                                    field_names=[
                                        'state',
                                        'action',
                                        'new_state'
                                    ])



player = LearningPlayer(True)
player.uuid = 'ftwdqkystzsqwjrzvludgi'

for i in range(player.REPLAY_START_SIZE):
    exp = Experience(list(np.random.rand(17)),
                     random.choice([0, 1, 2]),
                     list(np.random.rand(17)))

    player.exp_buffer.append(exp)


player.receive_round_start_message(round_count, hole_card, seats)
player.declare_action(valid_actions, hole_card, round_state)
player.receive_round_result_message(winners, hand_info, round_state)
