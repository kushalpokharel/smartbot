def get_suit(card):
    """
    This function returns the suit of the given card.
    """

    return card[1]


def get_suit_cards(cards, card_suit):
    """
    This function returns the list of cards of the given suit from the initial list of cards.
    """
    return [card for card in cards if get_suit(card) == card_suit]


def index(sequence, predicate):
    """
    This function returns the index of the first element in the sequence which satisfies the predicate, otherwise -1
    Just like javascript
    """
    return next((i for i, e in enumerate(sequence) if predicate(e)), -1)


def find(sequence, predicate):
    """
    This function returns the first element in the sequence which satisfies the given predicate, None otherwise
    Just like Javascript
    """
    return next((e for i, e in enumerate(sequence) if predicate(e)), None)


def get_partner_idx(my_idx):
    return (my_idx + 2) % 4


def get_rank(card):
    return card[0]


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


def get_card_info(card):
    return CARDS_DICT[get_rank(card)]


def is_high(highest_card, compare_card, trump_suit=None):
    is_highest_card_trump = get_suit(highest_card) == trump_suit
    is_compare_card_trump = get_suit(compare_card) == trump_suit

    if (trump_suit and is_highest_card_trump and not is_compare_card_trump):
        return True
    if (trump_suit and not is_highest_card_trump and is_compare_card_trump):
        return False
    # if both have similar suit, we could just check the points with order
    if (get_suit(highest_card) == get_suit(compare_card)):
        high = get_card_info(highest_card)
        compare = get_card_info(compare_card)

        return high["points"] >= compare["points"] and high["order"] > compare["order"]

    return False


def pick_winning_card_idx(cards, trump_suit):
    winner = 0
    first_card = cards[0]

    for i in range(winner, len(cards)):
        winning_card = cards[winner]
        compare_card = cards[i]

        if (not trump_suit and get_suit(first_card) != get_suit(compare_card)):
            continue
        if (not is_high(winning_card, compare_card, trump_suit)):
            winner = i

    return winner

def findPlayerIndex(playerId, playerIds):
    for i in range(4):
        if playerIds[i] == playerId:
            return i
    
    return -1

def playableActions(body):
    roundNumber = body["roundNumber"]
    currPlayer = body["playerId"]
    if type(currPlayer) == str:
        currPlayer = findPlayerIndex(currPlayer, body["playerIds"])
    currentHand = body["played"]
    trumpRevealed = body["trumpRevealed"]
    trumpSuit = body["trumpSuit"]
    myCards = body["cards"]
    
    possibleActions = []
    if len(currentHand) == 0:
        for card in myCards:
            possibleActions.append({"card":card})
    
    else :
        if not trumpRevealed:
            lead_suit = currentHand[0][1]
            same_suit_cards = get_suit_cards(myCards, lead_suit)
            if len(same_suit_cards) == 0:
                # print("No same suit cards")
                for card in myCards:
                    possibleActions.append({"card":card})
                possibleActions.append({"revealTrump": True})

            else:
                for card in same_suit_cards:
                    possibleActions.append({"card":card})

        else:
            trump = trumpRevealed
            if trump["hand"] == roundNumber and trump["playerId"] == body["playerIds"][currPlayer]:
                # print("I am the trump picker")
                same_suit_cards = get_suit_cards(myCards, trumpSuit)
                if len(same_suit_cards) != 0:
                    toPlay = same_suit_cards[0]
                    for i in range(1, len(same_suit_cards)):
                        if CARDS_DICT[same_suit_cards[i][0]]["order"] > CARDS_DICT[toPlay[0]]["order"]:
                            toPlay = same_suit_cards[i]

                    possibleActions.append({"card": toPlay})
                else:
                    for card in myCards:
                        possibleActions.append({"card":card})
                    
            else:
                lead_suit = currentHand[0][1]
                same_suit_cards = get_suit_cards(myCards, lead_suit)
                if len(same_suit_cards) == 0:
                    for card in myCards:
                        possibleActions.append({"card":card})
                else:
                    for card in same_suit_cards:
                        possibleActions.append({"card":card})
    return possibleActions


def winValue(currentHand):
    value = 0
    for card in currentHand:
        value += get_card_info(card)["points"]
    return value

def lastPlay(body):
    currentHand = body["played"]
    myCards = body["cards"]
    trumpSuit = body["trumpSuit"]
    trumpRevealed = body["trumpRevealed"]
    total={'S':0,'H':1, 'D':2, 'C':3}
    suitCount = [0,0,0,0]
    suitValue = [0,0,0,0]
    suitHasJ  = [False, False, False, False]
    getSuit = ['S', 'H', 'D', 'C']
    rN = body["roundNumber"]
    for card in myCards:
        suit = total[card[1]]
        suitCount[suit]+=1
        suitValue[suit]+=get_card_info(card)["points"]
        suitHasJ[suit] = suitHasJ[suit] or card[0] == 'J'
    leadSuit = currentHand[0][1]
    winner = pick_winning_card_idx(currentHand, False)
    if trumpRevealed:
        winner = pick_winning_card_idx(currentHand, trumpSuit) 
    leadCards = get_suit_cards(myCards, leadSuit)
    if len(leadCards) == 0:
        if trumpRevealed:
            trumpIndex = total[trumpSuit]
            trumpCards = get_suit_cards(myCards, trumpSuit)
            # print(rN, trumpRevealed["hand"], trumpRevealed["playerId"], body["playerId"], "test ")
            if trumpRevealed["hand"] == rN and trumpRevealed["playerId"] == body["playerId"]:
                # print("I am here ", rN)
                if len(trumpCards) == 0:
                    # print("trump cards not available")
                    leastValue = 4
                    leastCard = ""
                    for card in myCards:
                        suit = total[card[1]] 
                        if suitCount[suit] <= 8:
                            if get_card_info(card)["points"] < leastValue:
                                leastValue = get_card_info(card)["points"]
                                leastCard = card
                            elif get_card_info(card)["points"] == leastValue:
                                if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                    leastCard = card
                    return {"card": leastCard}
                else:
                    # print("Trump cards available ")
                    if currentHand[2][1] == trumpSuit:
        
                        leastCard = ""
                        for card in trumpCards:
                            if get_card_info(card)["order"] > get_card_info(currentHand[2])["order"]:
                                if leastCard == "":
                                    leastCard = card
                                else:
                                    if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                        leastCard = card
                        if leastCard != "":
                            return {"card": leastCard}
                        

                    
                    leastValue = 4
                    leastCard = ""
                    # print(trumpCards)
                    for card in trumpCards:
                        suit = total[card[1]] 
                        if suitCount[suit] <= 8:
                            if get_card_info(card)["points"] < leastValue:
                                leastValue = get_card_info(card)["points"]
                                leastCard = card
                            elif get_card_info(card)["points"] == leastValue:
                                if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                    leastCard = card
                    
                    return {"card": leastCard}

            else:
                if winner == 1:
                    leastSuitIndex = -1
                    for i in range(4):
                        if suitCount[i] != 0:
                            if leastSuitIndex == -1:
                                leastSuitIndex = i
                            elif suitCount[i] < suitCount[leastSuitIndex]:
                                leastSuitIndex = i
                    leastSuitCards = get_suit_cards(myCards, getSuit[leastSuitIndex])
                    maxValue = -1
                    maxCard = ""
                    for card in leastSuitCards:
                        suit = total[card[1]] 
                        if get_card_info(card)["points"] > maxValue:
                            maxValue = get_card_info(card)["points"]
                            maxCard = card
                        elif get_card_info(card)["points"] == maxValue:
                            if get_card_info(card)["order"] > get_card_info(maxCard)["order"]:
                                maxCard = card
                    return {"card": maxCard}
                else:
                    if currentHand[2][1] == trumpSuit:
        
                        leastCard = ""
                        for card in trumpCards:
                            if get_card_info(card)["order"] > get_card_info(currentHand[2])["order"]:
                                if leastCard == "":
                                    leastCard = card
                                else:
                                    if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                        leastCard = card
                        if leastCard != "":
                            return {"card": leastCard}

                    leastValue = 4
                    leastCard = ""
                    for card in myCards:
                        suit = total[card[1]] 
                        if suitCount[suit] <= 8:
                            if get_card_info(card)["points"] < leastValue:
                                leastValue = get_card_info(card)["points"]
                                leastCard = card
                            elif get_card_info(card)["points"] == leastValue:
                                if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                    leastCard = card
                    # print(leastCard)
                    return {"card": leastCard}

                    

        else:
            return {"revealTrump": True}
    else:
        if winner == 1:
            maxValue = -1
            maxCard = ""
            for card in leadCards:
                suit = total[card[1]] 
                if get_card_info(card)["points"] > maxValue:
                    maxValue = get_card_info(card)["points"]
                    maxCard = card
                elif get_card_info(card)["points"] == maxValue:
                    if get_card_info(card)["order"] > get_card_info(maxCard)["order"]:
                        maxCard = card
            return {"card": maxCard}
        else:
            if trumpRevealed and currentHand[2][1] == trumpSuit:
                leastValue = 4
                leastCard = ""
                for card in leadCards:
                    suit = total[card[1]] 
                    if suitCount[suit] <= 8:
                        if get_card_info(card)["points"] < leastValue:
                            leastValue = get_card_info(card)["points"]
                            leastCard = card
                        elif get_card_info(card)["points"] == leastValue:
                            if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                leastCard = card
                return {"card": leastCard}

            else:
                toThrow = ""
                for card in leadCards:
                    if get_card_info(card)["order"] >= get_card_info(currentHand[0])["order"]:
                        if leadSuit == currentHand[2][1]:
                            if get_card_info(card)["order"] > get_card_info(currentHand[2])["order"]:
                                if toThrow == "":
                                    toThrow = card
                                else:
                                    if get_card_info(card)["order"] > get_card_info(toThrow)["order"]:
                                        toThrow = card
                        else:
                                if toThrow == "":
                                    toThrow = card
                                else:
                                    if get_card_info(card)["order"] > get_card_info(toThrow)["order"]:
                                        toThrow = card
                if toThrow == "":
                    leastValue = 4
                    leastCard = ""
                    for card in leadCards:
                        suit = total[card[1]] 
                        if suitCount[suit] <= 8:
                            if get_card_info(card)["points"] < leastValue:
                                leastValue = get_card_info(card)["points"]
                                leastCard = card
                            elif get_card_info(card)["points"] == leastValue:
                                if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                    leastCard = card
                    return {"card": leastCard}

                else:
                    return {"card": toThrow}


def firstRound(body):
    currentHand = body["played"]
    myCards = body["cards"]
    print(myCards)
    trumpSuit = body["trumpSuit"]
    trumpRevealed = body["trumpRevealed"]
    turn = len(currentHand)
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
    #first turn
    if turn == 0:
        #if I know trump suit
        if trumpSuit:
            trumpIndex = total[trumpSuit]
            trumpCards = get_suit_cards(myCards, trumpSuit)
            trumpCount = len(trumpCards)
            trumpValue = winValue(trumpCards)
            remainingValue = totalPoints - trumpValue
            for i in range(4):
                if suitCount[i] <= 2 and suitHasJ[i] and getSuit[i]!=trumpSuit:
                    return {"card": "J"+getSuit[i]}
            for i in range(4):
                if suitValue[i]==0 and suitCount[i]>0 and getSuit[i]!=trumpSuit: 
                    suitCard = get_suit_cards(myCards, getSuit[i])
                    return {"card": suitCard[0]}

            #if I have 3 or less trump cards
            if trumpCount <= 3:
                #if I don't have trump J
                if not suitHasJ[trumpIndex]:
                    for card in myCards:
                        suit = total[card[1]] 
                        if suitCount[suit] == 3 and suitHasJ[suit]:
                            return {"card": 'J'+getSuit[suit]}
                    leastValue = 4
                    leastCard = ""
                    for card in myCards:
                        suit = total[card[1]] 
                        if suitCount[suit] <= 8 and suit!=trumpIndex:
                            if get_card_info(card)["points"] < leastValue:
                                leastValue = get_card_info(card)["points"]
                                leastCard = card
                            elif get_card_info(card)["points"] == leastValue:
                                if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                    leastCard = card
                    return {"card": leastCard}
                else :
                    return {"card": 'J'+trumpSuit}
            else:
                if not suitHasJ[trumpIndex]:
                    leastValue = 4
                    leastCard = ""
                    for card in trumpCards:
                        suit = total[card[1]] 
                        if suitCount[suit] <= 8:
                            if get_card_info(card)["points"] < leastValue:
                                leastValue = get_card_info(card)["points"]
                                leastCard = card
                            elif get_card_info(card)["points"] == leastValue:
                                if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                    leastCard = card
                    return {"card": leastCard}
                else :
                    return {"card": 'J'+trumpSuit}

        else:
            for i in range(4):
                if suitCount[i] <= 2 and suitHasJ[i]:
                    return {"card": "J"+getSuit[i]}
            for i in range(4):
                if suitValue[i]==0 and suitCount[i]>0:
                    suitCard = get_suit_cards(myCards, getSuit[i])
                    return {"card": suitCard[0]}
            leastValue = 4
            leastCard = ""
            for card in myCards:
                suit = total[card[1]] 
                if suitCount[suit] <= 2:

                    if get_card_info(card)["points"] < leastValue:
                        leastValue = get_card_info(card)["points"]
                        leastCard = card
                    elif get_card_info(card)["points"] == leastValue:
                        if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                            leastCard = card

            if leastValue<4:
                return {"card": leastCard}

            for card in myCards:
                suit = total[card[1]] 
                if suitCount[suit] == 3 and suitHasJ[suit]:
                    return {"card": 'J'+getSuit[suit]}

            leastValue = 4
            leastCard = ""
            for card in myCards:
                suit = total[card[1]] 
                if suitCount[suit] <= 8:
                    if get_card_info(card)["points"] < leastValue:
                        leastValue = get_card_info(card)["points"]
                        leastCard = card
                    elif get_card_info(card)["points"] == leastValue:
                        if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                            leastCard = card
            return {"card": leastCard}

    elif turn == 1:
        #second turn
        leadSuit = currentHand[0][1]
        leadCards = get_suit_cards(myCards, leadSuit)
        leadIndex = total[leadSuit]
        #if no lead suit card
        if len(leadCards) == 0:
            if trumpRevealed:
                trumpIndex = total[trumpSuit]
                trumpCard = get_suit_cards(myCards, trumpSuit)
                #if I revealed trump
                if trumpRevealed["playerId"] == body["playerId"]:
                    #if I don't have trump card
                    if len(trumpCard) == 0:
                        leastValue = 4
                        leastCard = ""
                        for card in myCards:
                            suit = total[card[1]] 
                            if suitCount[suit] <= 8:
                                if get_card_info(card)["points"] < leastValue:
                                    leastValue = get_card_info(card)["points"]
                                    leastCard = card
                                elif get_card_info(card)["points"] == leastValue:
                                    if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                        leastCard = card
                        return {"card": leastCard}
                    else:
                        leastValue = 4
                        leastCard = ""
                        for card in trumpCard:
                            suit = total[card[1]] 
                            if suitCount[suit] <= 8:
                                if get_card_info(card)["points"] < leastValue:
                                    leastValue = get_card_info(card)["points"]
                                    leastCard = card
                                elif get_card_info(card)["points"] == leastValue:
                                    if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                        leastCard = card
                        return {"card": leastCard}
            else:
                return {"revealTrump": True}
                #do something
            
        else:
            if suitHasJ[leadIndex]:
                return {"card": 'J'+leadSuit}
            else:
                leastValue = 4
                leastCard = ""
                for card in leadCards:
                    suit = total[card[1]] 
                    if suitCount[suit] <= 8:
                        if get_card_info(card)["points"] < leastValue:
                            leastValue = get_card_info(card)["points"]
                            leastCard = card
                        elif get_card_info(card)["points"] == leastValue:
                            if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                leastCard = card
                return {"card": leastCard}

    elif turn == 2:
        #third turn
        leadSuit = currentHand[0][1]
        leadCards = get_suit_cards(myCards, leadSuit)
        leadIndex = total[leadSuit]
        #if no lead suit card
        if len(leadCards) == 0:
            #if revealed trump
            if trumpRevealed:
                trumpIndex = total[trumpSuit]
                trumpCard = get_suit_cards(myCards, trumpSuit)
                #if I revealed trump
                if trumpRevealed["playerId"] == body["playerId"]:
                    #if I don't have trump card
                    if len(trumpCard) == 0:
                        leastValue = 4
                        leastCard = ""
                        for card in myCards:
                            suit = total[card[1]] 
                            if suitCount[suit] <= 8:
                                if get_card_info(card)["points"] < leastValue:
                                    leastValue = get_card_info(card)["points"]
                                    leastCard = card
                                elif get_card_info(card)["points"] == leastValue:
                                    if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                        leastCard = card
                        return {"card": leastCard}
                    else:
                        leastValue = 4
                        leastCard = ""
                        for card in trumpCard:
                            suit = total[card[1]] 
                            if suitCount[suit] <= 8:
                                if get_card_info(card)["points"] < leastValue:
                                    leastValue = get_card_info(card)["points"]
                                    leastCard = card
                                elif get_card_info(card)["points"] == leastValue:
                                    if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                        leastCard = card
                        return {"card": leastCard}
                else:
                    opponentCard = currentHand[1]
                    myCard = ""
                    foundCard = False
                    for card in trumpCard:
                        if get_card_info(card)["order"] > get_card_info(opponentCard)["order"]:
                            if not foundCard:
                                myCard = card
                                foundCard = True
                            else:
                                if get_card_info(card)["order"] < get_card_info(myCard)["order"]:
                                    myCard = card
                    #if we have a card that is lower than opponent's card
                    if not foundCard:
                        leastValue = 4
                        leastCard = ""
                        for card in myCards:
                            suit = total[card[1]] 
                            if suit == trumpIndex:
                                continue
                            if get_card_info(card)["points"] < leastValue:
                                leastValue = get_card_info(card)["points"]
                                leastCard = card
                            elif get_card_info(card)["points"] == leastValue:
                                if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                    leastCard = card
                        return {"card": leastCard}
                    else:
                        return {"card": myCard}
            else:
                return {"revealTrump": True}
                #do something

        else:
            #if second person reveals trump, throw least card
            if trumpRevealed:
                leastValue = 4
                leastCard = ""
                for card in leadCards:
                    suit = total[card[1]] 
                    if suitCount[suit] <= 8:
                        if get_card_info(card)["points"] < leastValue:
                            leastValue = get_card_info(card)["points"]
                            leastCard = card
                        elif get_card_info(card)["points"] == leastValue:
                            if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                leastCard = card
                return {"card": leastCard}
            else:
                # if I have J of the lead suit, throw it
                if suitHasJ[leadIndex]:
                    return {"card": 'J'+leadSuit}
                else:
                    #if friend has thrown J of the lead suit, throw accordingly
                    if currentHand[0][0] == 'J':
                        #throw least card, if I have 5 or more of the lead suit, throw max otherwise
                        if suitCount[leadIndex] >= 5:
                            leastValue = 4
                            leastCard = ""
                            for card in leadCards:
                                suit = total[card[1]] 
                                if suitCount[suit] <= 8:
                                    if get_card_info(card)["points"] < leastValue:
                                        leastValue = get_card_info(card)["points"]
                                        leastCard = card
                                    elif get_card_info(card)["points"] == leastValue:
                                        if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                            leastCard = card
                            return {"card": leastCard}
                        else:
                            maxValue = -1
                            maxCard = ""
                            for card in leadCards:
                                suit = total[card[1]] 
                                if get_card_info(card)["points"] > maxValue:
                                    maxValue = get_card_info(card)["points"]
                                    maxCard = card
                                elif get_card_info(card)["points"] == maxValue:
                                    if get_card_info(card)["order"] > get_card_info(maxCard)["order"]:
                                        maxCard = card
                            return {"card": maxCard}
                    else:
                        leastValue = 4
                        leastCard = ""
                        for card in leadCards:
                            suit = total[card[1]] 
                            if suitCount[suit] <= 8:
                                if get_card_info(card)["points"] < leastValue:
                                    leastValue = get_card_info(card)["points"]
                                    leastCard = card
                                elif get_card_info(card)["points"] == leastValue:
                                    if get_card_info(card)["order"] < get_card_info(leastCard)["order"]:
                                        leastCard = card
                        return {"card": leastCard}
                            
            
    else:
        #last turn
        return lastPlay(body)

def secondRound(body):
    pass
