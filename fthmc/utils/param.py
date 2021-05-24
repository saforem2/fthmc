"""
utils/param.py

Implements `Param` object, a helper class for specifying the parameters of a
model instance.
"""
import os
from dataclasses import dataclass
from functools import reduce
from math import pi as PI
import numpy as np
import torch


@dataclass
class Param:
    beta: float = 6.0       # inverse coupling constant
    #  batch_size: int = 128
    L: int = 64
    tau: float = 2.0        # trajectory length
    nstep: int = 50
    ntraj: int = 256
    nrun: int = 4
    nprint: int = 256
    seed: int = 11 * 13
    randinit: bool = False
    nth: int = int(os.environ.get('OMP_NUM_THREADS', '2'))
    nth_interop: int = 2

    def __post_init__(self):
        self.lat = [self.L, self.L]
        self.nd = len(self.lat)
        self.shape = [self.nd, *self.lat]
        #  self.shape = [self.batch_size, self.nd, *self.lat]
        self.volume = reduce(lambda x, y: x * y, self.lat)
        self.dt = self.tau / self.nstep

    def initializer(self):
        #  if self.randinit:
        #      rand = np.random.uniform(-PI, PI, size=self.shape)
        #      return torch.from_numpy(rand)
        #
        #  return torch.zeros(self.shape)
        if self.randinit:
            return torch.empty([self.nd,] + self.lat).uniform_(-PI, PI)
        else:
            return torch.zeros([self.nd,] + self.lat)

    def __repr__(self):
        status = {k: v for k, v in self.__dict__.items()}
        s = '\n'.join('='.join((str(k), str(v))) for k, v in status.items())
        return '\n'.join(['Param:', 16 * '-', s])

    def to_json(self):
        attrs = {k: v for k, v in self.__dict__.items()}
        return attrs

    def summary(self):
        return self.__repr__

    def uniquestr(self, ext=None):
        lat = "x".join(str(x) for x in self.lat)
        ustr = (
            f'out_t{lat}_b{self.beta}_n{self.ntraj}'
            f'_t{self.tau}_s{self.nstep}'
        )
        if ext is not None:
            ustr = f'{ustr}.ext'

        return ustr



class Param1:
    def __init__(
        self,
        beta: float = 6.0,          # inverse coupling const
        lat: list = [64, 64],       # lattice shape
        tau: float = 2.0,           # trajectory length
        nstep: int = 50,            # number of leapfrog steps
        ntraj: int = 256,           # number of trajectories
        nrun: int = 4,              # number of runs
        nprint: int = 256,          # print freq  ??
        seed: int = 11*13,          # seed
        randinit: bool = False,     # randomly intitialize?
        nth: int = int(os.environ.get('OMP_NUM_THREADS', '2')),  # num threads
        nth_interop: int = 2,       # num interop threads
    ):
        """Parameter object for runing the Field Transformation HMC.

        NOTE: When running HMC, we generate configurations by the following loop:
        -----
        ```python
        field = param.initializer()
        trajectories = []
        for n in range(param.nrum):
            for i in range(param.ntraj):
                field = hmc(param, field)
            trajectories.append(field)
        ```
        """
        self.beta = beta
        self.lat = lat
        self.nd = len(lat)
        self.volume = reduce(lambda x, y: x * y, lat)
        self.tau = tau
        self.nstep = nstep
        self.dt = self.tau / self.nstep
        self.ntraj = ntraj
        self.nrun = nrun
        self.nprint = nprint
        self.seed = seed
        self.randinit = randinit
        self.nth = nth
        self.nth_interop = nth_interop

    def initializer(self):
        if self.randinit:
            return torch.empty((self.nd,) + self.lat).uniform_(-PI, PI)
        else:
            return torch.zeros((self.nd,) + self.lat)

    def summary(self):
        status = {
            'latsize': self.lat,
            'volume': self.volume,
            'beta': self.beta,
            'trajs': self.ntraj,
            'tau': self.tau,
            'steps': self.nstep,
            'seed': self.seed,
            'nth': self.nth,
            'nth_interop': self.nth_interop,
        }

        #  return ', '.join('='.join((str(k), str(v))) for k, v in status.items())
        s = ', '.join('='.join((str(k), str(v))) for k, v in status.items())
        return f'{s}\n'

    def uniquestr(self):
        lat = ".".join(str(x) for x in self.lat)
        return (
            f'out_l{lat}_b{self.beta}_n{self.ntraj}'
            f'_t{self.tau}_s{self.nstep}.out'
        )