from utils import playableActions, get_card_info, get_suit, get_suit_cards, get_partner_idx, pick_winning_card_idx, is_high, index, find
import random
import math
from time import time
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
        return tree[node]["score"][tree[parent]["playerId"]] / visitCount + math.sqrt(2*math.log(tree[parent]["visitCount"]) / visitCount )  
    

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

def returnWinner(currentHand, startPlayer, playerIds, trumpRevealed, trumpSuit):

    max_index = 0
    if trumpRevealed:
        max_index = pick_winning_card_idx(currentHand, trumpSuit)
    else:
        max_index = pick_winning_card_idx(currentHand, False)
        
    return (startPlayer+max_index)%4

def winValue(currentHand):
    value = 0
    for card in currentHand:
        value += get_card_info(card)["points"]
    return value

def createChildren(root):
    tree[root]["children"] = []
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
        child["cards"]  = []
        child["children"] = []
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
            child["allCards"][tree[child["parent"]]["playerId"]].remove(move["card"])
            
        else:
            if not child["trumpSuit"]:
                suits = ['S','H', 'D', 'C']
                child["trumpSuit"] = suits[random.randint(0,3)]    

            child["trumpRevealed"] = {"hand": child["roundNumber"], "playerId": child["playerId"]}  
        child["cards"] = child["allCards"][child["playerId"]]
        tree.append(child)
        tree[root]["children"].append(len(tree)-1)

def backpropagate(root):
    score = [1,1,1,1]
    bidPlayer = tree[root]["bidPlayer"]
    bidAmount = tree[root]["bidAmount"]
    trumpRevealed = tree[root]["trumpRevealed"]
    if trumpRevealed:
        if tree[root]["points"][bidPlayer] >= bidAmount:
            score[bidPlayer] = score[(bidPlayer+2)%4] = 1000
            score[(bidPlayer+1)%4] = score[(bidPlayer+3)%4] = 0
        else:
            score[bidPlayer] = score[(bidPlayer+2)%4] = 0
            score[(bidPlayer+1)%4] = score[(bidPlayer+3)%4] = 1000
    while root != -1:
        tree[root]["visitCount"] += 1
        for i in range(4):
            tree[root]["score"][i] += score[i]
        root = tree[root]["parent"]


def simulate(root):
    currentNode = root
    createChildren(root)
    while len(tree[currentNode]["children"])!=0 :
        currentNode = tree[currentNode]["children"][random.randint(0, len(tree[currentNode]["children"])-1)]
        createChildren(currentNode)
    backpropagate(currentNode)


def mcts(root, bound):
    iter = 0
    start_time = int(time()*1000)
    current_time = start_time
    while current_time - start_time < bound:
        selected = select(root)
        simulate(selected)
        iter+=1
        current_time = int(time()*1000)
    # print(f"mcts iter {iter}")

def findPlayerIndex(playerId, playerIds):
    for i in range(4):
        if playerIds[i] == playerId:
            return i
    
    return -1

def shuffle(body):
    currentHand = body["played"]
    handsHistory = body["handsHistory"]
    playerIds = body["playerIds"]
    myCards = body["cards"]
    currentPlayer = body["playerId"]
    playerHasSuit = [[True for i in range(4)] for j in range(4)]
    remainingCards = []
    shuffled = []
    CARDS_DICT = {
        "J": {"points": 3, "order": 8},
        "9": {"points": 2, "order": 7},
        "1": {"points": 1, "order": 6},
        "T": {"points": 1, "order": 5},
        "K": {"points": 0, "order": 4},
        "Q": {"points": 0, "order": 3},
        "8": {"points": 0, "order": 2},
        "7": {"points": 0, "order": 1},
    }
    total={'S':0,'H':1, 'D':2, 'C':3}

    for i in CARDS_DICT:
        for j in total:
            remainingCards.append(i+j)

    for h in handsHistory:
        start = findPlayerIndex(h[0], playerIds)
        lead_suit = h[1][0][1]
        for i in range(4):
            current_turn = (start+i)%4
            remainingCards.remove(h[1][i])
            if h[1][i][1] != lead_suit:
                playerHasSuit[current_turn][total[lead_suit]] = False
    
    if currentHand:
        start = findPlayerIndex(currentPlayer, playerIds)
        lead_suit = currentHand[0][1]
        for i in range(len(currentHand)):
            current_turn = (start+i)%4
            remainingCards.remove(currentHand[i])
            if currentHand[i][1] != lead_suit:
                playerHasSuit[current_turn][total[lead_suit]] = False
    
    for c in myCards:
        remainingCards.remove(c)
        shuffled.append(c)
    
    while remainingCards:
        rand = random.randint(0,len(remainingCards)-1)
        c = remainingCards[rand]
        remainingCards.remove(c)
        shuffled.append(c)
    
    shuffledPlayersCard = [[],[],[],[]]
    my_index = findPlayerIndex(currentPlayer, playerIds)
    remaining_number = len(myCards)
    index = 0
    for i in range(4):
        if i+len(currentHand) == 4:
            remaining_number-=1
        for j in range(remaining_number):
            shuffledPlayersCard[(my_index+i)%4].append(shuffled[index])
            index+=1
    return shuffledPlayersCard
    

def pimc(body):
    global tree
    body["roundNumber"] = len(body["handsHistory"])+1
    playableMoves = playableActions(body)
    iter = 0
    preferred_move = [0.0]*len(playableMoves)
    start_time = int(time()*1000)
    current_time = start_time
    while current_time-start_time < 135:
        tree = []
        iter+=1
        shuffledPlayersCard = shuffle(body)
        # print(shuffledPlayersCard)
        root = {}
        root["parent"] = -1
        root["playerId"] = findPlayerIndex(body["playerId"], body["playerIds"])
        root["played"] = body["played"]
        root["allCards"] = shuffledPlayersCard
        root["trumpSuit"] = body["trumpSuit"]
        root["trumpRevealed"] = body["trumpRevealed"]
        root["roundNumber"] = body["roundNumber"]
        root["visitCount"] = 0
        root["score"] = [0,0,0,0]
        root["points"] = [0,0,0,0]
        root["children"] = []
        root["cards"] = body["cards"]

        for i in range(4):
            for j in range(2):
                if body["teams"][j]["players"][0] == body["playerIds"][i] or body["teams"][j]["players"][1] == body["playerIds"][i]:
                   root["points"][i] = body["teams"][j]["won"]
                    

        root["playerIds"] = body["playerIds"]
        root["bidAmount"] = 0
        root["bidPlayer"] = -1
        for entry in body["bidHistory"]:
            if entry[1] > 0:
                root["bidAmount"] = entry[1]
                root["bidPlayer"] = findPlayerIndex(entry[0], body["playerIds"])
  
        tree.append(root)
        siz = 3*len(playableMoves)
        bound = 40

        mcts(0, bound)
        for i in range(len(playableMoves)):
            preferred_move[i] += tree[tree[0]["children"][i]]["visitCount"]/tree[0]["visitCount"]
        current_time = int(time()*1000)
    # print(f"mcts iter {iter}")

    bestMove = 0
    for i in range(1,len(preferred_move)):
        if preferred_move[i] > preferred_move[bestMove]:
            bestMove = i
    return playableMoves[bestMove]

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
    return pimc(body)


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
