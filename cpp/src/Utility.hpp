#include <bits/stdc++.h>
#include "./bot.hpp"
#ifdef RANGES_SUPPORT
#undef RANGES_SUPPORT
#endif

#if _HAS_CXX20
#define RANGES_SUPPORT 1
#include <ranges>
#endif


using namespace std;

vector<PlayAction*> playableAction(int roundNumber, string cur_player, vector<Card> &currentHand, 
    variant<bool,PlayPayload::RevealedObject> trumpRevealed, variant<bool,Suit> trumpSuit,  vector<Card> &myCards)
{
    // Returns what actions playerIdx can play from this position 

    vector<PlayAction*> possibleActions;

    if(currentHand.size()==0)
    {
        // When you are starting the hand you can throw all cards
        for(Card c: myCards)
        {
            possibleActions.push_back(new PlayAction(PlayAction::PlayCard, c)); 
        }
        
    } 

    else
    {
        // When this is the middle hand

        if( holds_alternative<PlayPayload::RevealedObject>(trumpRevealed)) 
        {
            // If trump has already been revealed before 

            auto trump = get<PlayPayload::RevealedObject>(trumpRevealed);

            if(trump.hand == roundNumber && trump.player_id.compare(cur_player) == 0 )
            {
                // If you just revealed the trump this round

                // Must play highest card of Trump Suit if he has one

                Suit lead_suit= get<Suit>(trumpSuit);
                auto same_suit_filter = [=](Card card) { return card.suit == lead_suit; };
                #if defined(RANGES_SUPPORT)
                    auto same_suit_cards =  views::filter(myCards, same_suit_filter);
                #else
                    vector<Card> same_suit_cards;
                    copy_if(myCards.begin(), myCards.end(),  back_inserter(same_suit_cards), same_suit_filter);
                #endif

                if (!same_suit_cards.empty())
                {
                    Card toPlay = same_suit_cards[0];
                    for(int i=1;i<same_suit_cards.size();i++){
                        if( CardValue(same_suit_cards[i].rank) > CardValue(toPlay.rank))
                        {
                            toPlay=same_suit_cards[i];
                        }
                        else if(CardValue(same_suit_cards[i].rank) == CardValue(toPlay.rank))
                        {
                            if(same_suit_cards[i].rank > toPlay.rank)
                            {
                                toPlay=same_suit_cards[i];
                            }
                        }
                    }
                    possibleActions.push_back(new PlayAction(PlayAction::PlayCard, toPlay));

                }
                else
                {
                    // Can play any card if no card of trump suit
                    for(Card c: myCards)
                    {
                        possibleActions.push_back(new PlayAction(PlayAction::PlayCard, c)); 
                    }
                }

            }
            else
            {

                // Trump revealed beforehand
                Suit lead_suit = currentHand[0].suit;
                auto same_suit_filter = [=](Card card) { return card.suit == lead_suit; };

                #if defined(RANGES_SUPPORT)
                    auto same_suit_cards =  views::filter(myCards, same_suit_filter);
                #else
                    vector<Card> same_suit_cards;
                    copy_if(myCards.begin(), myCards.end(),  back_inserter(same_suit_cards), same_suit_filter);
                #endif

                if(same_suit_cards.empty())
                {
                    for(Card c: myCards)
                    {
                        possibleActions.push_back(new PlayAction(PlayAction::PlayCard, c)); 
                    }
                }
                else
                {
                    for(Card c: same_suit_cards)
                    {
                        possibleActions.push_back(new PlayAction(PlayAction::PlayCard, c)); 
                    }
                }


            }
            
        }
        else
        {
            // Trump has not been revealed yet

            Suit lead_suit = currentHand[0].suit;
            auto same_suit_filter = [=](Card card) { return card.suit == lead_suit; };

            #if defined(RANGES_SUPPORT)
                auto same_suit_cards =  views::filter(myCards, same_suit_filter);
            #else
                vector<Card> same_suit_cards;
                copy_if(myCards.begin(), myCards.end(),  back_inserter(same_suit_cards), same_suit_filter);
            #endif

            if(same_suit_cards.empty())
            {
                for(Card c: myCards)
                {
                    possibleActions.push_back(new PlayAction(PlayAction::PlayCard, c)); 
                }
                possibleActions.push_back(new PlayAction(PlayAction::RevealTrump, myCards[0])); 

            }
            else
            {
                for(Card c: same_suit_cards)
                {
                    possibleActions.push_back(new PlayAction(PlayAction::PlayCard, c)); 
                }
            }
        
        }
    }

     return possibleActions;
    
}

int findPlayerIndex(string player_id, vector<string>& playerIds)
{
    for(int i=0;i<playerIds.size();i++)
    {
        if(playerIds[i].compare(player_id) == 0)
        {
            return i;
        }
    }
    return -1;
}

void shuffle(vector<PlayPayload::HandHistoryEntry>& hand_history, vector<Card>& myCards, 
                    vector<Card>& currentHand, string currentPlayer, vector<string>& playerIds, vector<vector<Card>>& shuffledPlayersCard){
            
    vector<vector<bool>> playerHasSuit(4, vector<bool>(4, true));
    vector<Card> remainingCards;
    vector<Card> shuffled;
    for(int i=7;i<=14;i++){
        for(int j=0;j<4;j++){
            remainingCards.push_back(Card(Rank(i), Suit(j)));
        }
    }

    for(auto h: hand_history){
        int start = findPlayerIndex(h.initiator, playerIds);
        Suit lead_suit = h.card[0].suit;
        for(int i=0;i<4;i++){
            int current_turn = (start+i)%4;
            auto itr = find(remainingCards.begin(),remainingCards.end(), h.card[i]);
            remainingCards.erase(itr);
            if(h.card[i].suit != lead_suit){
                playerHasSuit[current_turn][lead_suit] = false;
            }
        }
    }
    if(!currentHand.empty()){
        int start = (findPlayerIndex(currentPlayer, playerIds) - currentHand.size()+4)%4;
        Suit lead_suit = currentHand[0].suit;
        for(int i=0;i<currentHand.size();i++){
            int current_turn = (start+i)%4;
            auto itr = find(remainingCards.begin(),remainingCards.end(), currentHand[i]);
            remainingCards.erase(itr);
            if(currentHand[i].suit != lead_suit){
                playerHasSuit[current_turn][lead_suit] = false;
            }
        }
    }
    
    for(auto c: myCards){
        auto itr = find(remainingCards.begin(),remainingCards.end(), c);
            remainingCards.erase(itr);
        shuffled.push_back(c);
    }
    cout<<hand_history.size()+1<<" "<<remainingCards.size()<<endl;
    while(!remainingCards.empty()){
        srand(time(0));
        int random = rand()%remainingCards.size();
        Card c = remainingCards[random];
        remainingCards.erase(remainingCards.begin()+random);
        shuffled.push_back(c);
    }
    
    int my_index = findPlayerIndex(currentPlayer, playerIds);
    int remaining_number = myCards.size();
    int index = 0;
    for(int i=0;i<4;i++){
        if(i+currentHand.size() == 4){
            remaining_number--;
        }
        for(int j=0;j<remaining_number;j++){
            shuffledPlayersCard[(my_index+i)%4].push_back(shuffled[index++]);
        }
    }

    // for(int i=(my_index+1)%4;i!=my_index;i=(i+1)%4){
    //     for(int j=0;j<shuffledPlayersCard[i].size();j++){
    //         if(!playerHasSuit[i][shuffledPlayersCard[i][j].suit]){
    //             bool found = false; 
    //             for(int k=0;k<4;k++){
    //                 if(k==my_index || k==i){
    //                     continue;
    //                 }
    //                 if(!playerHasSuit[k][shuffledPlayersCard[i][j].suit]){
    //                     continue;
    //                 }
    //                 for(int l=0;l<shuffledPlayersCard[k].size();l++){
    //                     if(playerHasSuit[i][shuffledPlayersCard[k][l].suit]){
    //                         Card temp = shuffledPlayersCard[i][j];
    //                         shuffledPlayersCard[i][j] = shuffledPlayersCard[k][l];
    //                         shuffledPlayersCard[k][l] = temp;
    //                         found=true;
    //                         break;
    //                     }
    //                 }
    //                 if(found)
    //                     break;
    //             }
    //         }
    //     }
    // }
}

int returnWinner(vector<Card>& currentHand, int startPlayer, vector<string>& playerIds,
                  variant<bool,PlayPayload::RevealedObject> trumpRevealed, variant<bool,Suit> trumpSuit){
    
    Suit lead_suit = currentHand[0].suit;
    int max_rank = currentHand[0].rank;
    int max_index = 0;
    for(int i=1;i<currentHand.size();i++){
        if(currentHand[i].suit == lead_suit){
            if( CardValue(currentHand[i].rank) > CardValue(Rank(max_rank)))
            {
                max_rank=currentHand[i].rank;
                max_index=i;
            }
            else if(CardValue(currentHand[i].rank) == CardValue(Rank(max_rank)))
            {
                if(currentHand[i].rank > max_rank)
                {
                    max_rank=currentHand[i].rank;
                    max_index=i;
                }
            }
        }
    }

    if(holds_alternative<PlayPayload::RevealedObject>(trumpRevealed)){
        Suit trump = get<Suit>(trumpSuit);
        bool trumpFound = false;
        for(int i=1;i<currentHand.size() && trump!=lead_suit;i++){
            if(currentHand[i].suit == trump){
                if(!trumpFound){
                    trumpFound = true;
                    max_rank=currentHand[i].rank;
                    max_index=i;
                }
                else{
                    if( CardValue(currentHand[i].rank) > CardValue(Rank(max_rank)))
                    {
                        max_rank=currentHand[i].rank;
                        max_index=i;
                    }
                    else if(CardValue(currentHand[i].rank) == CardValue(Rank(max_rank)))
                    {
                        if(currentHand[i].rank > max_rank)
                        {
                            max_rank=currentHand[i].rank;
                            max_index=i;
                        }
                    }
                }
            }
        }
        
    }
        
    return (startPlayer+max_index)%4;

}

int winValue(vector<Card>& currentHand){
    int value = 0;
    for(auto c: currentHand){
        value += CardValue(c.rank);
    }
    return value;
}