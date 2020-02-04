import numpy as np

from pymanopt.manifolds.manifold import Manifold
from pymanopt.tools import ndarraySequenceMixin


class Product(Manifold):
    """Product manifold, i.e., the cartesian product of multiple manifolds."""

    class _TangentVector(list, ndarraySequenceMixin):
        def __repr__(self):
            return "{:s}: {}".format(
                self.__class__.__name__, super().__repr__())

        def __add__(self, other):
            assert len(self) == len(other)
            return self.__class__(
                [v + other[k] for k, v in enumerate(self)])

        def __sub__(self, other):
            assert len(self) == len(other)
            return self.__class__(
                [v - other[k] for k, v in enumerate(self)])

        def __mul__(self, other):
            return self.__class__([other * val for val in self])

        __rmul__ = __mul__

        def __div__(self, other):
            return self.__class__([val / other for val in self])

        def __neg__(self):
            return self.__class__([-val for val in self])

    def __init__(self, *manifolds):
        if len(manifolds) == 0:
            raise ValueError("At least one manifold required")
        for manifold in manifolds:
            if not isinstance(manifold, Manifold):
                raise ValueError(
                    "Unsupport manifold of type '{}'".format(type(manifold)))
            if isinstance(manifold, Product):
                raise ValueError("Nested product manifolds are not supported")
        self._manifolds = tuple(manifolds)
        name = ("Product manifold: {:s}".format(
                " x ".join([str(man) for man in manifolds])))
        dimension = np.sum([man.dim for man in manifolds])
        point_layout = tuple(manifold.point_layout for manifold in manifolds)
        super().__init__(name, dimension, point_layout=point_layout)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            if key == "manifolds":
                raise AttributeError("Cannot override 'manifolds' attribute")
        super().__setattr__(key, value)

    @property
    def typicaldist(self):
        return np.sqrt(np.sum([man.typicaldist ** 2
                               for man in self._manifolds]))

    def inner(self, X, G, H):
        return np.sum([man.inner(X[k], G[k], H[k])
                       for k, man in enumerate(self._manifolds)])

    def norm(self, X, G):
        return np.sqrt(self.inner(X, G, G))

    def dist(self, X, Y):
        return np.sqrt(np.sum([man.dist(X[k], Y[k]) ** 2
                               for k, man in enumerate(self._manifolds)]))

    def proj(self, X, U):
        return self._TangentVector(
            [man.proj(X[k], U[k]) for k, man in enumerate(self._manifolds)])

    def egrad2rgrad(self, X, U):
        return self._TangentVector(
            [man.egrad2rgrad(X[k], U[k])
             for k, man in enumerate(self._manifolds)])

    def ehess2rhess(self, X, egrad, ehess, H):
        return self._TangentVector(
            [man.ehess2rhess(X[k], egrad[k], ehess[k], H[k])
             for k, man in enumerate(self._manifolds)])

    def exp(self, X, U):
        return [man.exp(X[k], U[k]) for k, man in enumerate(self._manifolds)]

    def retr(self, X, U):
        return [man.retr(X[k], U[k]) for k, man in enumerate(self._manifolds)]

    def log(self, X, U):
        return self._TangentVector(
            [man.log(X[k], U[k]) for k, man in enumerate(self._manifolds)])

    def rand(self):
        return [man.rand() for man in self._manifolds]

    def randvec(self, X):
        scale = len(self._manifolds) ** (-1/2)
        return self._TangentVector(
            [scale * man.randvec(X[k])
             for k, man in enumerate(self._manifolds)])

    def transp(self, X1, X2, G):
        return self._TangentVector(
            [man.transp(X1[k], X2[k], G[k])
             for k, man in enumerate(self._manifolds)])

    def pairmean(self, X, Y):
        return [man.pairmean(X[k], Y[k])
                for k, man in enumerate(self._manifolds)]

    def zerovec(self, X):
        return self._TangentVector(
            [man.zerovec(X[k]) for k, man in enumerate(self._manifolds)])
