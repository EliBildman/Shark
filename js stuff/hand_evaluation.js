const {suits, types, hands} = require('./types')

//helpers

const n_of = (hand, type) => {
    let n = 0;
    for(_card of hand) {
        if(_card.type == type) n += 1;
    }
    return n;
}

const sort_hand = (hand) => {
    return [...hand].sort( compare_cards );
}

//evaluators

const is_straight = (hand) => {
    const sorted = sort_hand(hand);
    for( let i = 0; i < sorted.length - 1; i++ ) {
        if(sorted[i + 1].type != sorted[i].type + 1) return false;
    }
    return {rank: sorted.reverse()};
}

const is_flush = (hand) => {
    for(card of hand) {
        if(card.suit != hand[0].suit) return false;
    }
    return {rank: sort_hand(hand)}
}

const is_pair = (hand) => {
    for(card of hand) {
        if(n_of(hand, card.type) == 2) return {rank: [card].concat( sort_hand(hand).reverse() )}; //a little hacky maybe revisit
    }
    return false;
}

const is_three_of = (hand) => {
    for(card of hand) {
        if(n_of(hand, card.type) == 3) return {rank: [card].concat( sort_hand(hand).reverse() )};
    }
    return false;
}

const is_four_of = (hand) => {
    for(card of hand) {
        if(n_of(hand, card.type) == 4) return {rank: [card].concat( sort_hand(hand).reverse() )};
    }
    return false;
}

const is_two_pair = (hand) => {
    let first_pair = null;
    for(card of hand) {
        if(n_of(hand, card.type) == 2) {
            if(first_pair == null) {
                first_pair = card
            } else if(first_pair.type != card.type) {
                let last = hand.find((el) => el.type != first_pair.type && el.type != card.type);
                return {rank: sort_hand([first_pair, card]).concat([last])};
            }
        }
    }
    return false;
}

const is_full_house = (hand) => {
    const three = is_three_of(hand).rank;
    const two = is_pair(hand).rank;
    if(three && two) {
        return {rank: [three[0], two[0]]};
    }
    return false;
}

const is_high = (hand) => {
    const sorted = sort_hand(hand).reverse();
    return {rank: sorted};
}

const is_straight_flush = (hand) => {
    const straight = is_straight(hand);
    const flush = is_flush(hand);
    if(straight && flush) {
        return straight;
    }
    return false;
}

const is_royal_flush = (hand) => {
    const sflush = is_straight_flush(hand);
    if(sflush && sflush.rank[0] == types.ACE) {
        return sflush;
    }
    return false
}

//export

const get_label = (hand) => {
    let ret = null;
    if ( ret = is_royal_flush(hand) ) {
        return { label: hands.ROYAL_FLUSH, rank: ret.rank }
    } else if ( ret = is_straight_flush(hand) ) {
        return { label: hands.STRAIGHT_FLUSH, rank: ret.rank }
    } else if ( ret = is_four_of(hand) ) {
        return { label: hands.FOUR_OF_A_KIND, rank: ret.rank }
    } else if ( ret = is_full_house(hand) ) {
        return { label: hands.FULL_HOUSE, rank: ret.rank }
    } else if ( ret = is_flush(hand) ) {
        return { label: hands.FLUSH, rank: ret.rank }
    } else if ( ret = is_straight(hand) ) {
        return { label: hands.STRAIGHT, rank: ret.rank }
    } else if ( ret = is_three_of(hand) ) {
        return { label: hands.THREE_OF_A_KIND, rank: ret.rank }
    } else if ( ret = is_two_pair(hand) ) {
        return { label: hands.TWO_PAIR, rank: ret.rank }
    } else if ( ret = is_pair(hand) ) {
        return { label: hands.PAIR, rank: ret.rank }
    } else if ( ret = is_high(hand) ) {
        return { label: hands.HIGH_CARD, rank: ret.rank }
    } else {
        throw('somethings fucked');
    }

}

const compare_cards = (a, b) => {
    // if(a.type != b.type) {
    //     return a.type - b.type;
    // } else {
    //     return a.suit - b.suit;
    // }
    // console.log(a.type, b.type)
    return a.type - b.type;
}

//takes {label, rank}
const compare_hands = (a, b) => {
    a_lab = get_label(a);
    b_lab = get_label(b)
    if(a_lab.label != b_lab.label) {
        return a_lab.label - b_lab.label;
    } else {
        for(_i in a_lab.rank) {
            // console.log(_i)
            let comp = compare_cards(a_lab.rank[_i], b_lab.rank[_i]);
            // console.log(comp)
            if(comp != 0) return comp;
        }
        return 0;
    }
}

module.exports = { 
    get_label,
    sort_hand,
    compare_hands,
}
