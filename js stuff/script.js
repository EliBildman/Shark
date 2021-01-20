const { get_label, sort_hand, compare_hands } = require('./hand_evaluation');
const { suits, types, hands, moves, Card } = require('./types');

const deck = [];

for(suit in suits) {
    for(type in types) {
        deck.push({type: types[type], suit: suits[suit]});
    }
}



const shuffle = () => {
    for(i in deck) {
        let rand_ind = Math.floor(Math.random() * deck.length);
        let temp = deck[i];
        deck[i] = deck[rand_ind];
        deck[rand_ind] = temp;
    }
}

shuffle();


hand1 = [];

for(let i = 0; i < 5; i++) {
    hand1.push(deck.pop())
}


hand2 = [];

for(let i = 0; i < 5; i++) {
    hand2.push(deck.pop())
}


// console.log(hand1)
console.log(get_label(hand1))

// console.log(hand2)
console.log(get_label(hand2))

console.log(compare_hands(hand1, hand2))


// let n = 0;

// for(a of deck) {
//     for(b of deck) {
//         if(b != a) for(c of deck) {
//             if(c != b && c != a) for(d of deck) {
//                 if(d != c && d != b && d != a) for (e of deck) {
//                     if(e != d && e != c && e != b && e != a) {
//                         hand = [a, b, c, d, e];
//                         // n += 1;
//                         if(get_label(hand).label == hands.PAIR) n += 1
//                     }
//                 }
//             }
//         }
//     }
// }
