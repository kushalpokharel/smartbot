from utils import lastPlay, winValue, firstRound, secondRound, playableActions, get_card_info, get_suit, get_suit_cards, get_partner_idx, pick_winning_card_idx, is_high, index, find
import random
import math
import time
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
    
    
    amount = 0
    if(body["playerId"] == body["bidState"]["defenderId"]):
        amount = body["bidState"]["challengerBid"]
    else:
        amount =  body["bidState"]["defenderBid"]+1
    amount = max(amount, 16)
    highestCountSuit = 0
    highestValueSuit = 0
    myCards = body["cards"]
    totalPoints = winValue(myCards)
    total={'S':0,'H':1, 'D':2, 'C':3}
    suitCount = [0,0,0,0]
    suitValue = [0,0,0,0]
    suitHasJ  = [False, False, False, False]
    getSuit = ['S', 'H', 'D', 'C']
    for card in myCards:
        suit = total[card[1]]
        suitCount[suit]+=1
        suitValue[suit]+=get_card_info(card)["points"]
        suitHasJ[suit] = suitHasJ[suit] or card[0] == 'J'
        if( suitCount[suit] > suitCount[highestCountSuit]):
            highestCountSuit = suit
        if(suitValue[suit] > suitValue[highestValueSuit]):
            highestValueSuit = suit
        
    value=0

    if(suitCount[highestCountSuit] >=3):
        if(suitValue[highestCountSuit] >= 4):
            if amount <=19 and totalPoints >=6:
                value = amount
            elif amount <=18:
                value=amount
        else:
            if amount <= 17:
                value=amount
    else:
        if(suitValue[highestValueSuit] >=5):
            if amount <=19 and value >=8:
                value = amount
            elif amount <=18:
                value = amount
        elif suitValue[highestValueSuit] >=4:
            if amount <=17 and value >=7:
                value = amount
            elif amount <=16:
                value=amount

        elif suitValue[highestValueSuit] >=3:
            if amount <=17 :
                value = amount
            

    ####################################
    #     Input your code here.        #
    ####################################

    return {"bid": value}


def get_trump_suit(body):
    """
    Please note: this is bare implementation of the chooseTrump function.
    Do make changes to this function to throw valid card according to the context of the game.
    """
    amount = 0
    for entry in body["bidHistory"]:
        if entry[1] > 0:
            amount = entry[1]
    
    highestCountSuit = 0
    highestValueSuit = 0
    myCards = body["cards"]
    totalPoints = winValue(myCards)
    total={'S':0,'H':1, 'D':2, 'C':3}
    suitCount = [0,0,0,0]
    suitValue = [0,0,0,0]
    suitHasJ  = [False, False, False, False]
    getSuit = ['S', 'H', 'D', 'C']
    for card in myCards:
        suit = total[card[1]]
        suitCount[suit]+=1
        suitValue[suit]+=get_card_info(card)["points"]
        suitHasJ[suit] = suitHasJ[suit] or card[0] == 'J'
        if( suitCount[suit] > suitCount[highestCountSuit]):
            highestCountSuit = suit
        if(suitValue[suit] > suitValue[highestValueSuit]):
            highestValueSuit = suit
        
    value=0

    if(suitCount[highestCountSuit] >=3):
        if(suitValue[highestCountSuit] >= 4):
            if amount <=19 and totalPoints >=6:
                return {"suit" : getSuit[highestCountSuit]}
            elif amount <=18:
                return {"suit" : getSuit[highestCountSuit]}
        else:
            if amount <= 17:
                return {"suit" : getSuit[highestCountSuit]}
    else:
        if(suitValue[highestValueSuit] >=5):
            if amount <=19 and value >=8:
                return {"suit" : getSuit[highestValueSuit]}
            elif amount <=18:
                return {"suit" : getSuit[highestValueSuit]}
        elif suitValue[highestValueSuit] >=4:
            if amount <=17 and value >=7:
                return {"suit" : getSuit[highestValueSuit]}
            elif amount <=16:
                return {"suit" : getSuit[highestValueSuit]}
    
    if(suitValue[highestValueSuit] >=3):
        return {"suit" : getSuit[highestValueSuit]}
    elif suitCount[highestCountSuit] >=2:
        return {"suit" : getSuit[highestCountSuit]}
    else:
        return {"suit" : getSuit[highestValueSuit]}

    
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
        return float('inf')
    else:
        return tree[node]["score"][tree[parent]["playerId"]] / visitCount + math.sqrt(2*math.log(tree[parent]["visitCount"]) / visitCount )  
    

def select(root):
    global tree
    selected = root
    while len(tree[selected]["children"]) != 0:
        bestScore = float('-inf')
        bestChild = 0
        for child in tree[selected]["children"]:
            uctValue = calcUCT(child, selected)
            #print("UCTValue", uctValue)
            if uctValue > bestScore:
                bestScore = uctValue
                bestChild = child
        #print("BestChild",bestChild)
        # print("Select Status)")
        # print(bestScore, bestChild)
        selected = bestChild

    return selected

def returnWinner(currentHand, startPlayer, playerIds, trumpRevealed, trumpSuit):

    max_index = 0
    if trumpRevealed:
        max_index = pick_winning_card_idx(currentHand, trumpSuit)
    else:
        max_index = pick_winning_card_idx(currentHand, False)
        
    return (startPlayer+max_index)%4

def createChildren(root):
    global tree
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
                random.seed()
                child["trumpSuit"] = suits[random.randint(0,3)]    

            child["trumpRevealed"] = {"hand": child["roundNumber"], "playerId": child["playerIds"][child["playerId"]]}  
        for card in child["allCards"][child["playerId"]] :
            child["cards"].append(card)
        tree.append(child)
        tree[root]["children"].append(len(tree)-1)

def backpropagate(root):
    global tree
    score = [0,0,0,0]
    bidPlayer = tree[root]["bidPlayer"]
    bidAmount = tree[root]["bidAmount"]
    trumpRevealed = tree[root]["trumpRevealed"]
    if trumpRevealed:
        if tree[root]["points"][bidPlayer] >= bidAmount:
            score[bidPlayer] = score[(bidPlayer+2)%4] = (tree[root]["points"][bidPlayer])/5
            score[(bidPlayer+1)%4] = score[(bidPlayer+3)%4] = -(tree[root]["points"][bidPlayer])/5
        else:
            score[bidPlayer] = score[(bidPlayer+2)%4] = -(28 - tree[root]["points"][bidPlayer] )/5
            score[(bidPlayer+1)%4] = score[(bidPlayer+3)%4] = (28 - tree[root]["points"][bidPlayer] )/5
    #print("Score is", score)
    while root != -1:
        tree[root]["visitCount"] += 1
        for i in range(4):
            tree[root]["score"][i] += score[i]
        root = tree[root]["parent"]

def simulate(root):
    global tree
    currentNode = root
    createChildren(root)
    while len(tree[currentNode]["children"])!=0:
        random.seed()
        currentNode = tree[currentNode]["children"][random.randint(0, len(tree[currentNode]["children"])-1)]
        createChildren(currentNode)
    backpropagate(currentNode)


def mcts(root, bound):
    
    iter = 0
    while iter < bound:
        #time_before_selection = int(time()*1000)
        iter+=1
        selected = select(root)
        #time_after_selection = int(time()*1000)
        #print("Time taken for selection", time_after_selection - time_before_selection)
        simulate(selected)
        #time_after_simulate= int(time()*1000)
        #print("Time taken for simulation", time_after_simulate - time_after_selection)
        
    #print("Time taken for mcts" , current_time- start_time )

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
    bidPlayer = body["bidPlayer"]
    bidCards = []
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
            if current_turn == bidPlayer:
                bidCards.append(h[1][i])
            remainingCards.remove(h[1][i])
            if h[1][i][1] != lead_suit:
                playerHasSuit[current_turn][total[lead_suit]] = False
    
    if currentHand:
        start = (findPlayerIndex(currentPlayer, playerIds) - len(currentHand)+4)%4
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
        random.seed()
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
    
    i = (my_index+1)%4
    while i != my_index:
        for j in range(len(shuffledPlayersCard[i])):
            if not playerHasSuit[i][total[shuffledPlayersCard[i][j][1]]]:
                found = False
                for k in range(4):
                    if k == my_index or k == i:
                        continue
                    if not playerHasSuit[k][total[shuffledPlayersCard[i][j][1]]]:
                        continue
                    for l in range(len(shuffledPlayersCard[k])):
                        if playerHasSuit[i][total[shuffledPlayersCard[k][l][1]]]:
                            temp = shuffledPlayersCard[i][j]
                            shuffledPlayersCard[i][j] = shuffledPlayersCard[k][l]
                            shuffledPlayersCard[k][l] = temp
                            found = True
                            break
                    
                    if found:
                        break
        i=(i+1)%4

    for card in shuffledPlayersCard[bidPlayer]:
        bidCards.append(card)
    trumpSuit = body["trumpSuit"]
    
    if not trumpSuit:
        total={'S':0,'H':1, 'D':2, 'C':3}
        suitValue = [0,0,0,0]
        getSuit = ['S', 'H', 'D', 'C']
        totalValue = 0
        for card in bidCards:
            suit = total[card[1]]
            suitValue[suit]+=get_card_info(card)["points"]+1
            totalValue = totalValue + get_card_info(card)["points"] + 1
        for i in range(4):
            suitValue[i] = suitValue[i]/totalValue
        random.seed()
        rand = random.random()
        trumpSuit = getSuit[3]
        for i in range(4):
            if rand < suitValue[i]:
                trumpSuit = getSuit[i]
                break
            rand-=suitValue[i]
    return shuffledPlayersCard, trumpSuit
    

def pimc(body):
    global tree
    rN= body["roundNumber"]
    playableMoves = playableActions(body)
    # print(playableMoves)
    if(len(playableMoves) == 1):
        return playableMoves[0]
    if(body["timeRemaining"] <=200):
        print("time remaining is less than 200")
        random.seed()
        return playableMoves[random.randint(0,len(playableMoves)-1)]
    iter = 0
    preferred_move = [0.0]*len(playableMoves)
    pimcbound = 4
    # if rN<=6:
    #     pimcbound= 5

    # else:
    #     pimcbound = 2
    body["bidAmount"] = 0
    body["bidPlayer"] = -1
    for entry in body["bidHistory"]:
        if entry[1] > 0:
            body["bidAmount"] = entry[1]
            body["bidPlayer"] = findPlayerIndex(entry[0], body["playerIds"])
    while iter < pimcbound:
        tree = []
        iter+=1
        # print(shuffledPlayersCard)
        root = {}
        root["allCards"], root["trumpSuit"] = shuffle(body)
        root["parent"] = -1
        root["playerId"] = findPlayerIndex(body["playerId"], body["playerIds"])
        root["played"] = body["played"]
        root["trumpRevealed"] = body["trumpRevealed"]
        root["roundNumber"] = body["roundNumber"]
        root["visitCount"] = 0
        root["score"] = [0,0,0,0]
        root["points"] = [0,0,0,0]
        root["children"] = []
        root["cards"] = body["cards"]
        root["bidAmount"] = body["bidAmount"]
        root["bidPlayer"] = body["bidPlayer"]
        for i in range(4):
            for j in range(2):
                if body["teams"][j]["players"][0] == body["playerIds"][i] or body["teams"][j]["players"][1] == body["playerIds"][i]:
                   root["points"][i] = body["teams"][j]["won"]
                    

        root["playerIds"] = body["playerIds"]
        
        tree.append(root)
        bound = 10
        if(rN <= 4):
            bound = 30
        elif(rN ==5):
            bound = 20
        elif rN == 6:
            bound = 10
        else:
            bound = 5

        mcts(0, bound)
        for i in range(len(playableMoves)):
            preferred_move[i] += tree[tree[0]["children"][i]]["visitCount"]/tree[0]["visitCount"]
            
    bestMove = 0
    
    for i in range(1,len(preferred_move)):
        if preferred_move[i] > preferred_move[bestMove]:
            bestMove = i
    
    return playableMoves[bestMove]

def createChildren2(root):
    global tree
    tree[root]["children"] = []
    #print("Inside Create Children")
    if tree[root]["parent"]!=-1:
        if tree[root]["roundNumber"] != tree[tree[root]["parent"]]["roundNumber"]:
            return
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
                winner = pick_winning_card_idx(child["played"], False)
                if child["trumpRevealed"]:
                    winner = pick_winning_card_idx(child["played"], child["trumpSuit"])
                winner = (child["playerId"] + winner) % 4               
                child["playerId"] = winner
                value = winValue(child["played"])
            child["allCards"][tree[child["parent"]]["playerId"]].remove(move["card"])
            
        else:
            if not child["trumpSuit"]:
                suits = ['S','H', 'D', 'C']
                random.seed()
                child["trumpSuit"] = suits[random.randint(0,3)]    

            child["trumpRevealed"] = {"hand": child["roundNumber"], "playerId": child["playerIds"][child["playerId"]]}  
        for card in child["allCards"][child["playerId"]] :
            child["cards"].append(card)
        tree.append(child)
        tree[root]["children"].append(len(tree)-1)


def backpropagate2(root):
    global tree
    score = [0,0,0,0]
    winner = tree[root]["playerId"]
    # if tree[root]["trumpRevealed"]:
    #     winner = pick_winning_card_idx(tree[root]["played"], tree[root]["trumpSuit"])
    # winner = (winner + tree[root]["playerId"])%4
    amount = winValue(tree[root]["played"])
    score[winner] = score[(winner+2)%4] = amount
    score[(winner+1)%4] = score[(winner+3)%4] = -amount
    while root != -1:
        tree[root]["visitCount"] += 1
        for i in range(4):
            tree[root]["score"][i] += score[i]
        root = tree[root]["parent"]

def select2(node):
    return select(node)

def simulate2(root):
    global tree
    currentNode = root
    createChildren2(root)
    while len(tree[currentNode]["children"])!=0:
        random.seed()
        currentNode = tree[currentNode]["children"][random.randint(0, len(tree[currentNode]["children"])-1)]
        createChildren2(currentNode)
    backpropagate2(currentNode)

def mcts2(root, bound):
    iter = 0
    while iter < bound:
        iter+=1
        selected = select2(root)
        simulate2(selected)

def pimc2(body):
    global tree
    rN= body["roundNumber"]
    playableMoves = playableActions(body)
    # print(playableMoves)
    if(len(playableMoves) == 1):
        return playableMoves[0]
    # if(body["timeRemaining"] <=100):
    #     print(f"rN {rN}")
    #     random.seed() 
    #     return playableMoves[random.randint(0,len(playableMoves)-1)]
    body["bidAmount"] = 0
    body["bidPlayer"] = -1
    for entry in body["bidHistory"]:
        if entry[1] > 0:
            body["bidAmount"] = entry[1]
            body["bidPlayer"] = findPlayerIndex(entry[0], body["playerIds"])
    iter = 0
    preferred_move = [0.0]*len(playableMoves)
    pimcbound = 5
    
    while iter < pimcbound:
        tree = []
        iter+=1
        # print(shuffledPlayersCard)
        root = {}
        root["parent"] = -1
        root["playerId"] = findPlayerIndex(body["playerId"], body["playerIds"])
        root["allCards"], root["trumpSuit"] = shuffle(body)
        root["played"] = body["played"]
        root["trumpRevealed"] = body["trumpRevealed"]
        root["roundNumber"] = body["roundNumber"]
        root["visitCount"] = 0
        root["score"] = [0,0,0,0]
        root["points"] = [0,0,0,0]
        root["children"] = []
        root["cards"] = body["cards"]
        # for i in range(4):
        #     for j in range(2):
        #         if body["teams"][j]["players"][0] == body["playerIds"][i] or body["teams"][j]["players"][1] == body["playerIds"][i]:
        #            root["points"][i] = body["teams"][j]["won"]
                    

        root["playerIds"] = body["playerIds"]
        # root["bidAmount"] = 0
        root["bidPlayer"] = (root["playerId"] - len(root["cards"])+4)%4
        
        # for entry in body["bidHistory"]:
        #     if entry[1] > 0:
        #         root["bidAmount"] = entry[1]
        #         root["bidPlayer"] = findPlayerIndex(entry[0], body["playerIds"])
        tree.append(root)
        bound = 40

        mcts2(0, bound)
        for i in range(len(playableMoves)):
            preferred_move[i] += tree[tree[0]["children"][i]]["visitCount"]/tree[0]["visitCount"]
            
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
   
    ####################################
    #     Input your code here.        #
    ####################################
    body["roundNumber"] = len(body["handsHistory"])+1
    # currentHand = body["played"]
    # rN = body["roundNumber"]
    # print(rN, body["playerId"], body["timeRemaining"])
    # if  not body["trumpRevealed"] and rN <= 3:
    #     return pimc2(body)
    return pimc(body)


   