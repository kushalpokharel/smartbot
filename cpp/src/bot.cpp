#include "./bot.hpp"
#include "./Utility.hpp"
#include <bits/stdc++.h>

#ifdef RANGES_SUPPORT
#undef RANGES_SUPPORT
#endif

#if _HAS_CXX20
#define RANGES_SUPPORT 1
#include <ranges>
#endif

using namespace std;

// Internal
 ostream &operator<<(ostream &os, Card const &card)
{
    return os << Card::ToStr(card) <<  endl;
}

 ostream &operator<<( ostream &os, PlayPayload const &payload)
{
    os << "Player ID : " << payload.player_id <<  endl;
    os << "Player IDs : ";
    for (auto const &player : payload.player_ids)
        os << player << "    ";

    os << "\nCards \n";
    for (auto card : payload.cards)
        os << card << "   ";

    os << "\nPlayed : \n";
    for (auto card : payload.played)
        os << card << "  \n";

    os << "\nBid History : \n";
    for (auto const &entry : payload.bid_history)
    {
        os << "player    : " << entry.player_id << "\n"
           << "Bid value : " << entry.bid_value <<  endl;
    }

    // Hand history
    for (auto const &x : payload.hand_history)
    {
        os << "Initiator : " << x.initiator;
        os << "\nWinner   : " << x.winner;
        os << "\nCards Played : ";
        for (auto card : x.card)
            os << card << "   ";
        os <<  endl;
    }
    return os;
}

static GameState game_instance;

GameState& GetGameInstance()
{
    return game_instance;
}

void InitGameInstance()
{
    // Initialization code of game state goes here, if any
}

//
// Actual gameplay goes here
//
// These three functions are called in response to the http request calls /chooseTrump, /bid and /play respectively. 
// Logic of your code should go inside respective functions
//

 // CLUBS = 0, DIAMONDS, HEARTS, SPADES
pair<int,Suit> evaluate(vector<Card> mycards){
    int total[4]={0};
    for(auto card : mycards){
        total[card.suit]++;
    }
    int maxi=0;
    Suit suit;
    for(int i=0;i<4;i++){
        if(total[i]>maxi){
            maxi=total[i];
            suit=Suit(i);
        }
    }
    return {maxi,suit};
}

int place_bid(PlayerID myid, vector<BidEntry> bid_history, BidState const &bid_state, pair<int,Suit> maximum){
    int amount=0;
    if(myid == bid_state.defender.player_id){
        amount = bid_state.challenger.bid_value;
    }
    else{
        amount = bid_state.defender.bid_value+1;
    }
    // cout<<bid_state.defender.player_id<<" "<<bid_state.challenger.player_id<<endl;
    for(auto entry : bid_history){
        amount= max(amount, entry.bid_value);
    }
    if(maximum.first==1){
        return 0;
    }
    if(maximum.first==2){
        if(amount<= 17){
            return max(amount,16);
        }
        else 
            return 0;
    }
    if(maximum.first==3){
        if(amount<= 18){
            return max(amount,16);
        }
        else 
            return 0;
    }
    if(maximum.first==4){
        if(amount<= 19){
            return max(amount,16);
        }
        else 
            return 0;
    }
}

Suit GameState::ChooseTrump(PlayerID myid,  vector<PlayerID> player_ids,  vector<Card> mycards,
                            int32_t time_remaining,  vector<BidEntry> bid_history)
{
    return evaluate(mycards).second;
}

int GameState::Bid(PlayerID myid,  vector<PlayerID> player_ids,  vector<Card> mycards, int32_t time_remaining,
                    vector<BidEntry> bid_history, BidState const &bid_state)
{
    // Either bid or pass
    pair<int,Suit> maximum = evaluate(mycards);
    // cout<<maximum.first<<" "<<maximum.second<<endl;
    return place_bid(myid, bid_history, bid_state, maximum);

}

void status(PlayPayload payload){
    // aile samma nakheleko taas haru -> vector<Cards> 
    // kun player sanga kun suit chhaina -> vector<vector<bool>> -> 4*4

}

void distributeCard(vector<Card> remaining, vector<vector<bool>> suitPresent ){
    // harek player lai randomly shuffle garna paryo taas 

}

PlayAction GameState::Play(PlayPayload payload)
{

    auto playableActions = playableAction(payload.hand_history.size()+1, payload.player_id,
                            payload.played, payload.trumpRevealed, payload.trumpSuit, payload.cards ); 
    cout<<payload.hand_history.size()<<endl;
    if(payload.hand_history.size()==7){
        vector<vector<Card>> shuffledPlayersCard(4,vector<Card>());
        shuffle(payload.hand_history, payload.cards, payload.played, payload.player_id, payload.player_ids, shuffledPlayersCard);
        for(int i=0;i<shuffledPlayersCard.size();i++){
            cout<<"player "<<payload.player_ids[i]<<endl;
            for(int j=0;j<shuffledPlayersCard[i].size();j++){
                cout<<shuffledPlayersCard[i][j]<<" ";
            }
            cout<<endl;
        }
    }

    int random = rand()%playableActions.size();
    return *playableActions[0];
}
