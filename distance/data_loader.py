import os
import numpy as np
from scipy.misc import imread

class DataLoader(object):
    """A helper class for loading data from the gpds synthetic dataset"""

    def __init__(self, data_dir, array_module):
        self.data_dir = data_dir
        self.xp = array_module

    def get_signature_path(self, person, sign_num):
        directory = os.path.join(self.data_dir, "{:03d}".format(person))
        if sign_num > 24:  # a forgery
            prefix = "cf"
            sign_num -= 24
        else:
            prefix = "c"
        fname = "{}-{:03d}-{:02d}.jpg".format(prefix, person, sign_num)
        return os.path.join(directory, fname)

    def load_image(self, person, sign_num):
        path = self.get_signature_path(person, sign_num)
        return imread(path).astype(self.xp.float32)[self.xp.newaxis, ...]

    def get_batch(self, anchor_id, num_triplets):
        """Make a batch using person <anchor_id> as anchor."""
        anchor_samples = list(range(1, 25))
        np.random.shuffle(anchor_samples)

        # pop anchor_sample, REMOVING it from the remaining anchor_samples
        anchor_sample = anchor_samples.pop()

        neg_ids = list(range(1, 4001))
        neg_ids.remove(anchor_id)
        # allow use of 24 signatures and 30 forgeries of the negatives
        neg_samples = [(np.random.choice(neg_ids),
                        np.random.choice(list(range(1, 55))))
                       for i in range(num_triplets)]

        # repeat anchor sample
        a = self.xp.array([self.load_image(anchor_id, anchor_sample)] * num_triplets,
                          dtype=self.xp.float32)
        # generate <num_triplets> p's randomly sampled from remaining anchor_samples
        p = self.xp.array([self.load_image(anchor_id, np.random.choice(anchor_samples))
                           for _ in range(num_triplets)],
                          dtype=self.xp.float32)
        # negative samples from remaining neg_ids
        n = self.xp.array([self.load_image(np.random.choice(neg_ids), np.random.choice(list(range(1, 55))))
                           for _ in range(num_triplets)],
                          dtype=self.xp.float32)
        return self.xp.concatenate([a, p, n])
