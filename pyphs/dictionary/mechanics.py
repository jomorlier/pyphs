# -*- coding: utf-8 -*-
"""
Created on Sat May 21 16:29:43 2016

@author: Falaize
"""

from __future__ import absolute_import, division, print_function
from .edges import (PHSPort,
                    PHSDissipativeLinear,
                    PHSStorageLinear, PHSStorageNonLinear)
from pyphs.dictionary.tools import symbols


class Source(PHSPort):
    """
    Voltage or current source

    Parameters
    -----------

    label : str, port label.

    nodes: tuple of nodes labels

        if a single label in nodes, port edge is "datum -> node"; \
else, the edge corresponds to "nodes[0] -> nodes[1]".

    kwargs: dic with following "keys:values"

        * 'type' : source type in ('force', 'velocity').
        * 'const': if not None, the input will be replaced by the value (subs).
    """
    def __init__(self, label, nodes, **kwargs):
        type_ = kwargs['type']
        type_ = type_.lower()
        assert type_ in ('force', 'velocity')
        if type_ == 'force':
            ctrl = 'f'
        elif type_ == 'velocity':
            ctrl = 'e'
        kwargs.update({'ctrl': ctrl})
        PHSPort.__init__(self, label, nodes, **kwargs)


class Stiffness(PHSStorageLinear):
    """
    Linear stiffness

    Parameters
    -----------

    label : str, port label.

    nodes: tuple of nodes labels

        Edge is "nodes[0] -> nodes[1]".

    kwargs: dic with following "keys:values"

        * 'K' : stiffness value or symbol label or tuple (label, value).
    """
    def __init__(self, label, nodes, **kwargs):
        par_name = 'K'
        par_val = kwargs[par_name]
        kwargs = {'name': par_name,
                  'value': par_val,
                  'inv_coeff': False,
                  'ctrl': 'f'}
        PHSStorageLinear.__init__(self, label, nodes, **kwargs)


class Mass(PHSStorageLinear):
    """
    Mass moving in 1D space

    Parameters
    -----------

    label : str, port label.

    nodes: tuple of nodes labels

        Edge is "nodes[0] -> nodes[1]".

    kwargs: dic with following "keys:values"

        * 'M' : Mass value or symbol label or tuple (label, value).
    """
    def __init__(self, label, nodes, **kwargs):
        par_name = 'M'
        par_val = kwargs[par_name]
        kwargs = {'name': par_name,
                  'value': par_val,
                  'inv_coeff': True,
                  'ctrl': 'e'}
        PHSStorageLinear.__init__(self, label, nodes, **kwargs)


class Damper(PHSDissipativeLinear):
    """
    Linear damper (unconstrained control)

    Parameters
    -----------

    label : str, port label.

    nodes: tuple of nodes labels

        Edge is "nodes[0] -> nodes[1]".

    kwargs: dic with following "keys:values"

        * 'A' : Damping coefficient or symbol label (string) or tuple \
(label, value).
    """
    def __init__(self, label, nodes, **kwargs):
        if kwargs['A'] is None:
            coeff = 0.
        else:
            coeff = kwargs['A']
        PHSDissipativeLinear.__init__(self, label, nodes, coeff=coeff)


class Springcubic(PHSStorageNonLinear):
    """
    Spring with cubic nonlinearity F(q)=K0*(q + K2*q**3)

    Usage
    -----

    mechanics.springcubic label nodes: **kwargs

    Parameters:
    -----------

    nodes : (N1, N2)
        tuple of nodes labels (int or string). The edge (ie. the velocity \
'v') is directed from N1 to N2.

    kwargs : dictionary with following "key: value"

         * 'K0': Stiffness (N/m)
         * 'K2': Nonlinear contribution (dimensionless unit)
    """
    def __init__(self, label, nodes, **kwargs):
        # parameters
        pars = ['K0', 'K2']
        for par in pars:
            assert par in kwargs.keys()
        K0, K2 = symbols(pars)
        # state  variable
        x = symbols("x"+label)
        # storage funcion
        H = K0*x*(x + x**3/2)/2
        N1, N2 = nodes

        # edge data
        data = {'label': x,
                'type': 'storage',
                'ctrl': 'f',
                'link': None}

        # edge
        edge = (N1, N2, data)

        # init component
        PHSStorageNonLinear.__init__(self, label, [edge],
                                     x, H, **kwargs)
