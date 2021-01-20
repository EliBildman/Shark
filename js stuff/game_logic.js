const {suits, types, hands, moves, Card} = require('./types')

const all_cards = () => {

    cards = [];
    for(type in types) {
        for(suit in suits) {
            cards.push(new Card(type, suit))
        }
    }
    return cards;

}


const all_holes = () => {

    const holes = [];
    const cards = all_cards();

    for(a of cards){
        for(b of cards) {
            if(a != b) {
                holes.push( [a, b] );
            }
        }
    }
    return holes;

}


class Action {

    constructor(player, move, scale) {
        this.player = player;
        this.move = move;
        this.scale = scale;
    }

}


class Player {

    constructor(name = 'FishBitch') {
        this.likely_holes = all_holes();
        this.name = name;
        this.position = null;
    }

}


class Game {

    constructor(n_players, blind) {

        this.players = [];
        this.blind = blind;
        this.com = [];
        this.actions = []; //hmmm

        for(let i = 0; i < n_players; i++) {
            this.players.push(new Player());
        }

    }

    add_com(card) {
        this.com.push(card);
    }

    add_action(player, move, scale) {
        actions.push(
            new Action(player, move, scale)
        )
    }

}


const g = new Game(5, 1.0);
console.log(g.players);






