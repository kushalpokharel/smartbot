#include <bits/stdc++.h>
#include "./Utility.hpp"
#include "./bot.hpp"

using namespace std;

class TreeNode{
public:
    vector<TreeNode*> children;
    TreeNode* parent;
    int currentPlayer;
    vector<Card> currentHand;
    vector<Card> myCards;
    vector<int> score;
    variant<bool, Suit>           trumpSuit;
    variant<bool, PlayPayload::RevealedObject> trumpRevealed;
    int roundNumber;
    int visitCount;

    TreeNode(TreeNode* parent, int currentPlayer, vector<Card> currentHand, vector<Card> myCards, variant<bool, Suit> trumpSuit, 
                variant<bool, PlayPayload::RevealedObject> trumpRevealed, int roundNumber, int visitCount)
    {
        this->parent = parent;
        this->currentPlayer = currentPlayer;
        this->currentHand = currentHand;
        this->myCards = myCards;
        this->trumpSuit = trumpSuit;
        this->trumpRevealed = trumpRevealed;
        this->roundNumber = roundNumber;
        this->visitCount = 0;
        this->score = vector<4>(0);
    }

    TreeNode* select(){
        TreeNode* selected = this;
        while(selected->children.size() != 0){
            double bestScore = -1;
            for(auto child : selected->children){
                double uctValue = child->calcUCT();
                if(uctValue > bestScore){
                    bestScore = uctValue;
                    selected = child;
                }
            }
        }
        return selected;
    }

    TreeNode* expand(vector<string> playerIds){
        vector<PlayAction*> = playableAction(roundNumber, playerIds[currentPlayer], currentHand, trumpRevealed, trumpSuit, myCards );
        for(auto move : possibleMoves){
            TreeNode* child = new TreeNode(this, (currentPlayer + 1) % 4, currentHand, myCards, trumpSuit, trumpRevealed, roundNumber, 0);
            child->currentHand.push_back(move);
            children.push_back(child);
        }
        return children[rand() % children.size()];
    }

    double calcUCT(){
        if(visitCount == 0){
            return 100000000;
        }
        return ((score[parent->currentPlayer]*1.0) / visitCount) + sqrt(2 * log(parent->visitCount) / visitCount);
    }
}