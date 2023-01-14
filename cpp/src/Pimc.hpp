#include <bits/stdc++.h>
#include "./Utility.hpp"
#include "./bot.hpp"
#include "./TreeNode.hpp"

using namespace std;

void mcts(TreeNode* root){
    int startTime = time(0);
    while(time(0)-startTime<15){
        TreeNode* selected = root->select();
        selected->simulate();
    }
}

PlayAction* pimc(PlayPayload payload){

    auto playableActions = playableAction(payload.hand_history.size()+1, payload.player_id,
                            payload.played, payload.trumpRevealed, payload.trumpSuit, payload.cards ); 
    
    int startTime = time(0);
    int iter = 0;
    vector<double> preferred_move(playableActions.size(),0.0);
    while(time(0)-startTime<135){
        iter++;
        vector<vector<Card>> shuffledPlayersCard(4,vector<Card>());
        shuffle(payload.hand_history, payload.cards, payload.played, payload.player_id, payload.player_ids, shuffledPlayersCard);
        TreeNode* root = new TreeNode();    
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
        mcts(root);
        for(int i=0;i<playableActions.size();i++){
            preferred_move[i] += root->children[i]->visitCount/(double)root->visitCount ;
        }
    }
    int bestMove = 0;
    for(int i=1;i<preferred_move.size();i++){
        if(preferred_move[i] > preferred_move[bestMove]){
            bestMove = i;
        }
    }
    return playableActions[bestMove];   
}

