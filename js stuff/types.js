const suits = {
    HEARTS: 1,
    DIAMONDS: 2,
    SPADES: 3,
    CLUBS: 4
}

const types = {  
    TWO: 2,
    THREE: 3,
    FOUR: 4,
    FIVE: 5,
    SIX: 6,
    SEVEN: 7,
    EIGHT: 8,
    NINE: 9,
    TEN: 10,
    JACK: 11,
    QUEEN: 12,
    KING: 13,
    ACE: 14
};

const hands = {
    HIGH_CARD: 0,
    PAIR: 1,
    TWO_PAIR: 2,
    THREE_OF_A_KIND: 3,
    STRAIGHT: 4,
    FLUSH: 5,
    FULL_HOUSE: 6,
    FOUR_OF_A_KIND: 7,
    STRAIGHT_FLUSH: 8,
    ROYAL_FLUSH: 9
}

const moves = {
    FOLD: 0,
    CALL: 1,
    RAISE: 2
}

class Card {

    constructor(type, suit) {
        this.type = type;
        this.suit = suit;
    }

}

module.exports = {suits, types, hands, moves, Card};