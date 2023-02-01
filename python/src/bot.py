from utils import playableActions, get_suit, get_suit_cards, get_partner_idx, pick_winning_card_idx, is_high, index, find
import random
# pair<int,Suit> evaluate(vector<Card> mycards){
#     int total[4]={0};
#     for(auto card : mycards){
#         total[card.suit]++;
#     }
#     int maxi=0;
#     Suit suit;
#     for(int i=0;i<4;i++){
#         if(total[i]>maxi){
#             maxi=total[i];
#             suit=Suit(i);
#         }
#     }
#     return {maxi,suit};
# }

tree = []

def get_bid(body):
    """
    Please note: this is bare implementation of the bid function.
    Do make changes to this function to throw valid bid according to the context of the game.
    """
    myCards = body["cards"]
    total={'S':0,'H':0, 'D':0, 'C':0}
    for card in myCards:
        total[card[1]]+=1
    maxi = 0
    suit = ''
    for i in total.keys():
        if total[i]>maxi :
            maxi = total[i]
            suit = i
    
    amount = 0
    if(body["playerId"] == body["bidState"]["defenderId"]):
        amount = body["bidState"]["challengerBid"]
    else:
        amount =  body["bidState"]["defenderBid"]+1
    
    for entry in body["bidHistory"]:
        amount = max(amount, entry[1])
    value = 0
    if maxi<=1:
        value = 0

    elif maxi <=2:
        if amount <= 16:
            value = max(amount, 16)
        else :
            value = 0
    
    elif maxi <=4:
        if amount <= 18:
            value = max(amount, 16)
        else :
            value = 0

    ####################################
    #     Input your code here.        #
    ####################################

    return {"bid": value}


def get_trump_suit(body):
    """
    Please note: this is bare implementation of the chooseTrump function.
    Do make changes to this function to throw valid card according to the context of the game.
    """
    myCards = body["cards"]
    total={'S':0,'H':0, 'D':0, 'C':0}
    for card in myCards:
        total[card[1]]+=1
    maxi = 0
    suit = ''
    for i in total.keys():
        if total[i]>maxi :
            maxi = total[i]
            suit = i
    ####################################
    #     Input your code here.        #
    ####################################

    return {"suit": suit}

def calcUCT(node, parent):
    #  if(visitCount == 0){
    #         return 100000000;
    #     }
    #     return ((score[parent->currentPlayer]*1.0) / visitCount) + sqrt(2 * log(parent->visitCount) / visitCount);
    visitCount = tree[node]["visitCount"]
    if tree[node]["visitCount"] == 0:
        return 100000000
    else:
        return tree[node]["score"][tree[parent]["player"]] / visitCount + sqrt(2*log(tree[parent]["visitCount"]) / visitCount )  
    

def select(root):
    selected = root
    while len(tree[selected]["children"]) != 0:
        bestScore = -1.0
        bestChild = 0
        for child in tree[selected]["children"]:
            uctValue = calcUCT(child, selected)
            if uctValue > bestScore:
                bestScore = uctValue
                bestChild = child
        selected = bestChild

    return selected

def createChildren(root):
    possibleMoves = playableActions(tree[root])
    for move in possibleMoves:
        child = {}
        child["parent"] = root
        child["playerId"] = tree[root]["playerId"]
        child["played"] = []
        for card in tree[root]["played"]:
            child["played"].append(card)
        child["roundNumber"] = tree[root]["roundNumber"]
        child["trumpRevealed"] = tree[root]["trumpRevealed"]
        child["trumpSuit"] = tree[root]["trumpSuit"]
        child["visitCount"] = 0
        child["score"] = [0,0,0,0]
        child["playerIds"] = tree[root]["playerIds"]
        child["bidAmount"] = tree[root]["bidAmount"]
        child["bidPlayer"] = tree[root]["bidPlayer"]
        child["points"] = []
        for point in tree[root]["points"]:
            child["points"].append(point)
        child["allCards"] = []
        for i in range(4):
            child["allCards"].append([])
            for card in tree[root]["allCards"][i]:
                child["allCards"][i].append(card)

        if "card" in move.keys():
            child["playerId"] = (child["playerId"] + 1) % 4
            child["played"].append(move["card"])
            if len(child["played"]) == 4:
                child["roundNumber"] = child["roundNumber"] + 1
                winner = returnWinner(child["played"], child["playerId"], child["playerIds"], child["trumpRevealed"], child["trumpSuit"])
                child["playerId"] = winner
                value = winValue(child["played"])
                child["points"][winner] += value
                child["points"][(winner+2)%4] += value
                child["played"] = []
            child["allCards"][child["playerId"]].remove(move["card"])
            
        else:
            if not child["trumpSuit"]:
                suits = ['S','H', 'D', 'C']
                child["trumpSuit"] = suits[random.randint(0,3)]    

            child["trumpRevealed"] = {"hand": child["roundNumber"], "playerId": child["playerId"]}     
        tree.append(child)
        tree[root]["children"].append(len(tree)-1)
    #     else if(move->action == PlayAction::RevealTrump){
    #         if(!holds_alternative<Suit>(trumpSuit)){
    #             srand(time(0));
    #             child->trumpSuit = Suit(rand() % 4);
                
    #         }
    #         child->trumpRevealed = PlayPayload::RevealedObject {child->roundNumber ,playerIds[currentPlayer]};
    #     }
    #     children.push_back(child);
    # }

def expand(root):
    createChildren(root)


    # TreeNode* selected = this;
    #     // cout<<"inside select "<<endl;
    #     while(selected->children.size() != 0){
    #         double bestScore = -1;
    #         for(auto child : selected->children){
    #             double uctValue = child->calcUCT();
    #             if(uctValue > bestScore){
    #                 bestScore = uctValue;
    #                 selected = child;
    #             }
    #         }
    #     }
    #     // cout<<"exiting select "<<endl;
    #     return selected;

def mcts(root, bound):
    iter = 0
    while iter<bound :
        selected = select(root)
        expand(selected)
        simulate(selected)
        iter+=1

def pimc(body):
    pass

def get_play_card(body):
    """
    Please note: this is bare implemenation of the play function.
    It just returns the last card that we have.
    Do make changes to the function to throw valid card according to the context of the game.
    """
    # print(body)
    ####################################
    #     Input your code here.        #
    ####################################
    return playableActions(body)[0]


    # own_cards = body["cards"]
    # first_card = None if len(body["played"]) == 0 else body["played"][0]
    # trump_suit = body["trumpSuit"]
    # trump_revealed = body["trumpRevealed"]
    # hand_history = body["handsHistory"]
    # own_id = body["playerId"]
    # played = body["played"]
    # player_ids = body["playerIds"]
    # my_idx = player_ids.index(own_id)
    # my_idx = index(
    #     player_ids, lambda id: id == own_id)
    # my_partner_idx = get_partner_idx(my_idx)
    # first_turn = (my_idx + 4 - len(played)) % 4
    # is_bidder = trump_suit and not trump_revealed

    # # if we are the one to throw the first card in the hands
    # if (not first_card):
    #     return {"card": own_cards[-1]}

    # first_card_suit = get_suit(first_card)
    # own_suit_cards = get_suit_cards(own_cards, first_card_suit)

    # # if we have the suit with respect to the first card, we throw it
    # if len(own_suit_cards) > 0:
    #     return {"card": own_suit_cards[-1]}

    # # if we don't have cards that follow the suit
    # # @example
    # # the first player played "7H" (7 of hearts)
    # #
    # # we could either
    # #
    # # 1. throw any card
    # # 2. reveal the trump

    # # trump has not been revealed yet, and we don't know what the trump is
    # # let's reveal the trump
    # if (not trump_suit and not trump_revealed):
    #     return {"revealTrump": True}

    # # we don't have any trump suit cards, throw random
    # own_trump_suit_cards = get_suit_cards(own_cards, trump_suit)
    # if (len(own_trump_suit_cards) == 0):
    #     return {"card": own_cards[-1]}

    # did_reveal_the_trump_in_this_hand = trump_revealed and trump_revealed["playerId"] == own_id and trump_revealed["hand"] == (
    #     len(hand_history) + 1)

    # # trump was revealed by me in this hand
    # # or
    # # I am going to reveal the trump, since I am the bidder

    # if (is_bidder or did_reveal_the_trump_in_this_hand):
    #     response = {}
    #     if (is_bidder):
    #         response["revealTrump"] = True

    #     # if there are no trumps in the played
    #     if (len(get_suit_cards(played, trump_suit)) == 0):
    #         response["card"] = own_trump_suit_cards[-1]
    #         return response

    #     winning_trump_card_idx = pick_winning_card_idx(played, trump_suit)
    #     winning_card_player_idx = (first_turn + winning_trump_card_idx) % 4

    #     # if we revealed the trump in this round and the winning card is trump, there are two cases
    #     # 1. If the opponent is winning the hand, then you must throw the winning card of the trump suit against your opponent's card.
    #     # 2. If your partner is winning the hand, then you could throw any card of trump suit since your team is only winning the hand.
    #     if (winning_card_player_idx == my_partner_idx):
    #         response["card"] = own_trump_suit_cards[-1]
    #         return response

    #     winning_trump_card = played[winning_trump_card_idx]
    #     winning_card = find(own_trump_suit_cards, lambda card: is_high(
    #         card, winning_trump_card)) or own_trump_suit_cards[-1]

    #     # player who revealed the trump should throw the trump suit card
    #     return {"card": winning_card}

    # return {"card": own_cards[-1]}
