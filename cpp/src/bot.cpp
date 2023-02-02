#include "./bot.hpp"
#include "./TreeNode.hpp"
#include <bits/stdc++.h>

#ifdef RANGES_SUPPORT
#undef RANGES_SUPPORT
#endif

#if _HAS_CXX20
#define RANGES_SUPPORT 1
#include <ranges>
#endif

using namespace std;
using namespace std::chrono;

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
    if(maximum.first<=1){
        return 0;
    }
    if(maximum.first<=2){
        if(amount<= 16){
            return max(amount,16);
        }
        else 
            return 0;
    }
    if(maximum.first<=4){
        if(amount<= 18){
            return max(amount,16);
        }
        else 
            return 0;
    }
    return 0+0;
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

void mcts(TreeNode* root, int bound){
    // cout<<"bid " <<root->bidAmount<<endl;
    int startTime = time(0);
    int iter = 0;
    while(iter<bound){
        iter++;
        TreeNode* selected = root->select();
        selected->expand();
        selected->simulate();
    }
    // cout<<root->children.size()<<endl;
}

PlayAction* pimc(PlayPayload& payload){
    // cout<<"here"<<endl;
    vector<PlayAction*> playableActions;
    vector<int> isSuitPlayed = getPlayed(payload.hand_history);
    playableActions = playableAction(payload.hand_history.size()+1, payload.player_id,
                            payload.played, payload.trumpRevealed, payload.trumpSuit, payload.cards, isSuitPlayed ); 
    
    int startTime = time(0);
    int iter = 0;
    vector<double> preferred_move(playableActions.size(),0.0);
    int round = payload.hand_history.size()+1;
    int pimcbound = 300;
    if(round>2){
        pimcbound = 120;
    }
    uint64_t start_time = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    uint64_t current_time = start_time;
    
    while(current_time - start_time<pimcbound){
        iter++;
        vector<vector<Card>> shuffledPlayersCard(4,vector<Card>());
        shuffle(payload.hand_history, payload.cards, payload.played, payload.player_id, payload.player_ids, shuffledPlayersCard);
        TreeNode* root = new TreeNode();  
        root->parent = NULL;  
        root->currentPlayer = findPlayerIndex(payload.player_id, payload.player_ids);
        root->currentHand = payload.played;
        root->allCards = shuffledPlayersCard;
        root->trumpSuit = payload.trumpSuit;
        root->trumpRevealed = payload.trumpRevealed;
        root->roundNumber = payload.hand_history.size()+1;
        root->visitCount = 0;
        root->score = vector<int>(4,0);
        root->points = vector<int>(4,0);
        for(int i=0;i<4;i++){
            for(int j=0;j<2;j++){
                if(payload.teams[j].players[0] == payload.player_ids[i] || payload.teams[j].players[1] == payload.player_ids[i]){
                    root->points[i] = payload.teams[j].won;
                }
            }
        }
        root->playerIds = payload.player_ids;
        for(auto entry : payload.bid_history){
            if(entry.bid_value > 0){
                root->bidAmount = entry.bid_value;
                root->bidPlayer = findPlayerIndex(entry.player_id, payload.player_ids);
            }
        }
        // cout<<"before"<<endl;
        int siz = 10*playableActions.size();
        int bound = max(siz,30);
        // if(bound>30)
        //     cout<<"bound "<<bound<<endl;
        mcts(root, bound);
        // cout<<"p: "<<playableActions.size()<<endl;
        // cout<<"r: "<<root->children.size()<<endl;
        // cout<<"visit count" << root->visitCount<<endl;
        for(int i=0;i<playableActions.size();i++){
            preferred_move[i] += root->children[i]->visitCount/(double)root->visitCount ;
        }
        current_time = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    }
    // cout<<"iter pimc " <<iter<<endl;
    int bestMove = 0;
    for(int i=1;i<preferred_move.size();i++){
        if(preferred_move[i] > preferred_move[bestMove]){
            bestMove = i;
        }
    }
    // cout<<bestMove<<endl;
    return playableActions[bestMove];   
}


PlayAction GameState::Play(PlayPayload payload)
{
    auto playcard = pimc(payload);
    return *playcard;
    // return *(pimc(payload));
}
