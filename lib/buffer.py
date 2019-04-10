import collections
import numpy as np

class ExperienceBuffer:
    """Stores the transition frames, with a specified max capacity.
    Will store a sequence of Experience tuples.
    """
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)

    def __len__(self):
        return len(self.buffer)

    def append(self, experience):
        """Adds an Experience tuple to the buffer.
        """
        self.buffer.append(experience)

    def sample(self, batch_size):
        """Samples a batch of transitions, with a specified size.

        Returns:
            (
                np.array of states (a feature vector),
                np.array of actions (int, 0 / 1 / 2),
                np.array of next_states (a feature vector)
            )
        """
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)

        states, actions, next_states = \
            zip(*[self.buffer[idx] for idx in indices])

        return np.array(states), np.array(actions), np.array(next_states)
