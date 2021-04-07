from pypokerengine.utils.card_utils import gen_cards, gen_deck, estimate_hole_card_win_rate
from pprint import pprint
from random import randint, choice
import numpy as np
from itertools import combinations
from scipy.cluster.vq import vq, kmeans, whiten
import uuid
import pickle
from copy import copy, deepcopy
from nodes import NatureNode, DecisionNode, ValueNode


def build_decision_tree():

    init_state = GameState(2, [0.5, 1], [0, 0], 0, 10)
    root = DecisionNode(None, init_state, 0)

    def build_children(node):
        for n in node.get_children():
            if type(n) != ValueNode and not n.round_over:
                build_children(n)

    build_children(root)
    return root

def collapse(parent, n, copy_children = True): #collapses children of parent into n AbstractNodes based on k-means cluster 

    #kmeans cluster
    wrs = [node.get_wr() for node in parent.get_children()]
    # whitened = whiten(wrs)
    means, _error = kmeans(wrs, n)
    
    abstracted = [AbstractNatureNode(parent, m) for m in means]

    #transfer children to correct abstract node
    for child in parent.get_children():
        a_node = min(abstracted, key= lambda a: abs(child.get_wr() - a.get_wr()) )
        a_node.p += 1
        if copy_children:
            for g_child in child.get_children():
                # print(len(child.get_children()))
                a_node.children.append(g_child)


    #normailze
    s = sum( a.p for a in abstracted )
    for a in abstracted:
        a.p /= s
    
    return abstracted


def build_postflop_tree(hole, flop):

    root = NatureNode(hole=hole, comm=flop, stage='TURN')

    print('Bulding tree')

    for turn in root.get_children():
        turn.get_wr()
        for river in turn.get_children():
            river.get_wr()

    print('Collapsing layer 1')

    a = collapse(root, 10)

    print('Collapsing layer 2')

    for node in a:
        node.children = collapse(node, 10)

    # print(len(a))


def build_flop_tree(prune_level = None, calc_wrs = False):

    root = NatureNode()
    
    print('building holes')

    holes = root.get_children()

    if prune_level:
        prune_low_holes(root, prune_level)

    print('getting flops')
    if calc_wrs:
        print('calculating wrs')

    l = len(root.get_children())
    i = 0
    for hole in root.get_children():
        i += 1
        for flop in hole.get_children():
            if calc_wrs:
                flop.get_wr()    

    return root
            

def prune_low_holes(root, limit):

    print('pruning holes')
    print('start len', len(root.get_children()))

    pruned = []

    for hole in root.get_children():
        # print(hole.get_wr())
        if hole.get_wr() < limit:
            root.children.remove(hole)
            pruned.append(hole)

    print('end len', len(root.get_children()))
    return pruned


def save_tree(root, filename):
    print('saving tree')
    with open(filename, 'wb') as f:
        pickle.dump(root, f)

    
def load_tree(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


