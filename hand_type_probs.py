from pypokerengine.utils.card_utils import gen_cards, gen_deck
from pypokerengine.engine.hand_evaluator import HandEvaluator

#gives probabilty of hand types given some comm and hole
#only really works post-flop
def hole_probs(hole, comm):
    totals = {}
    deck = gen_deck(exclude_cards=hole).deck

    def calc(_comm):
        if len(_comm) < 5:
            for card in deck:
                if card not in _comm:
                    calc(_comm + [card])
        else:
            rank = HandEvaluator.gen_hand_rank_info(hole, _comm)['hand']['strength']
            if rank in totals:
                totals[rank] += 1
            else:
                totals[rank] = 1
        # s = sum(totals.values())
        # if s % 10000 == 0:
        #     print(s)

    calc(comm)

    all_sum = sum(totals.values())

    for rank in totals:
        totals[rank] /= all_sum

    return totals

#gets probability of hand types overall for some comm
#for now ignores the comm cards to come, only evaulates those showing, TODO: change this
def overall_probs(comm):
    totals = {}
    deck = gen_deck(exclude_cards=comm).deck

    for card_a in deck:
        for card_b in deck:
            if card_a is not card_b:
                rank = HandEvaluator.gen_hand_rank_info([card_a, card_b], comm)['hand']['strength']
                if rank in totals:
                    totals[rank] += 1
                else:
                    totals[rank] = 1

    
    all_sum = sum(totals.values())

    for rank in totals:
        totals[rank] /= all_sum

    return totals


def prob_winning(hole, comm):
    h_probs = hole_probs(hole, comm)
    o_probs = overall_probs(comm)
    ranks = {'HIGHCARD': 0, 'ONEPAIR': 1, 'TWOPAIR': 2, 'THREECARD': 3, 'STRAIGHT': 4, 'FLASH': 5, 'FULLHOUSE': 6, 'FOURCARD': 7, 'STRAIGHTFLASH': 8}

    winning = 0.0
    # losing = 0.0

    print(h_probs)
    print(o_probs)

    for my_type in h_probs:
        for opp_type in o_probs:
            if ranks[my_type] > ranks[opp_type]:
                winning += h_probs[my_type] * o_probs[opp_type]
            elif ranks[my_type] == ranks[opp_type]:
                winning += (h_probs[my_type] * o_probs[opp_type]) / 2
            # else:
            #     losing += h_probs[my_type] * o_probs[opp_type]

    return winning
    
    


# hole = gen_cards(['HK', 'SQ'])
# comm = gen_cards(['H2', 'C3', 'S4', 'H5'])

# # print(HandEvaluator.gen_hand_rank_info(hole, comm))
# # print( overall_probs(comm) )
# print(prob_winning(hole, comm))
