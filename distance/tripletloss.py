import numpy as np

import chainer
from chainer import function
import chainer.functions as F
from chainer.utils import type_check
from chainer import cuda

xp = cuda.cupy


class TripletLoss(function.Function):

    """"""

    def __init__(self, margin=0.2):
        super().__init__()
        self.margin = margin

    def check_type_forward(self, in_types):
        type_check.expect(in_types.size() == 3)
        type_check.expect(
            in_types[0].dtype == np.float32,
            in_types[1].dtype == np.float32,
            in_types[2].dtype == np.float32,
            in_types[0].shape == in_types[1].shape,
            in_types[0].shape == in_types[2].shape
        )

    def forward_cpu(self, inputs):
        a, p, n = inputs  # anchor, positive, negative
        N = a.shape[0]
        # NOTE on using max(0, ...)
        # the loss is < 0 if (a-n) > (a-p)
        # that's what we want -- we don't want it increase the loss (by using
        # abs(), and we don't want it to decrease the sum by leaving it < 0)
        self.Li = np.maximum(0, (a-p)*(a-p) - (a-n)*(a-n) + self.margin)
        return np.array(np.sum(self.Li) / N, dtype=a[0].dtype),

    def forward_gpu(self, inputs):
        a, p, n = inputs  # anchor, positive, negative
        N = a.shape[0]
        # NOTE on using max(0, ...)
        # the loss is < 0 if (a-n) > (a-p)
        # that's what we want -- we don't want it increase the loss (by using
        # abs(), and we don't want it to decrease the sum by leaving it < 0)
        self.Li = xp.maximum(0, (a-p)*(a-p) - (a-n)*(a-n) + self.margin)
        return xp.sum(self.Li) / N,

    def backward(self, inputs, gy):
        # NOTE
        a, p, n = inputs  # anchor, positive, negative
        N = a.shape[0]
        # TODO
        # import pdb; pdb.set_trace()

        coeff = gy[0] * gy[0].dtype.type(2. / self.Li.shape[0])
        gx0 = coeff * self.Li * (n - p)
        gx1 = coeff * self.Li * (p - a)
        gx2 = coeff * self.Li * (a - n)
        return gx0, gx1, gx2


def triplet_loss(x0, x1, x2):
    """Triplet loss function.

    #This function computes mean squared error between two variables. The mean
    #is taken over the minibatch. Note that the error is not scaled by 1/2.

    """
    return TripletLoss()(x0, x1, x2)
