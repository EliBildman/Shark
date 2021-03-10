import numpy
from numpy.random import choice

moves = ['R', 'P', 'S']

def calculate_value(player, opponent):
    r = ((player - opponent + 1) % 3 - 1)
    if player == 1 and r == 1:
        return 10
    return r


def calculate_regret(player, opponent):
    regrets = numpy.zeros(3)
    for move in range(len(moves)):
        regret = calculate_value(move, opponent) - calculate_value(player, opponent)
        regrets[move] = regret
    return regrets

def form_strat(rsum):
    pos_sum = sum( num for num in rsum if num > 0 )
    if pos_sum == 0:
        return list(1 / len(rsum) for _ in range(3))
    else:
        return list((num / pos_sum) if num > 0 else 0 for num in rsum)

def play_rps_round(data):
    
    p1_strat, p2_strat, p1_rsum, p2_rsum = data

    p1_move = choice(3, p= p1_strat)
    p2_move = choice(3, p= p2_strat)

    # print('P1:', moves[p1_move], ', P2:', moves[p2_move], ' -> ', calculate_value(p1_move, p2_move))

    p1_rsum += list(x if x > 0 else 0 for x in calculate_regret(p1_move, p2_move))
    p2_rsum += list(x if x > 0 else 0 for x in calculate_regret(p2_move, p1_move))

    p1_strat = form_strat(p1_rsum)
    p2_strat = form_strat(p2_rsum)

    # print(p1_strat, p2_strat)

    return (p1_strat, p2_strat, p1_rsum, p2_rsum)

def train_rps(rounds, start_strats):

    p1_strat, p2_strat = start_strats
    p1_rsum, p2_rsum = numpy.zeros(3), numpy.zeros(3)

    data = p1_strat, p2_strat, p1_rsum, p2_rsum

    for _ in range(rounds):
        data = play_rps_round(data)

    p1_strat, p2_strat, p1_rsum, p2_rsum = data

    print('Final Strats:')
    print('P1:', p1_strat)
    print('P2:', p2_strat)



train_rps(100000, ( numpy.array([0.33, 0.33, 0.34]) , numpy.array([0.33, 0.33, 0.34]) ))