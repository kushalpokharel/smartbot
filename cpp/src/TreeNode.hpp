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
    vector<vector<Card>> allCards;
    vector<int> score;
    vector<int> points;
    variant<bool, Suit>           trumpSuit;
    variant<bool, PlayPayload::RevealedObject> trumpRevealed;
    int roundNumber;
    int visitCount;
    vector<string> playerIds;
    int bidAmount;
    int bidPlayer;

    TreeNode(){
        allCards = vector<vector<Card>> (4, vector<Card>());
    }


    TreeNode(TreeNode* parent, int currentPlayer, vector<Card> currentHand, vector<vector<Card>> allCards, variant<bool, Suit> trumpSuit, 
                variant<bool, PlayPayload::RevealedObject> trumpRevealed, int roundNumber, int visitCount, vector<int> points)
    {
        this->parent = parent;
        this->currentPlayer = currentPlayer;
        this->currentHand = currentHand;
        this->allCards = allCards;
        this->trumpSuit = trumpSuit;
        this->trumpRevealed = trumpRevealed;
        this->roundNumber = roundNumber;
        this->visitCount = 0;
        this->score = vector<int>(4,0);
        this->points = points;
        this->allCards = vector<vector<Card>> (4, vector<Card>());
    }

    TreeNode* select(){
        TreeNode* selected = this;
        // cout<<"inside select "<<endl;
        while(selected->children.size() != 0){
            double bestScore = -1;
            TreeNode* bestChild = nullptr;
            for(auto child : selected->children){
                double uctValue = child->calcUCT();
                if(uctValue > bestScore){
                    bestScore = uctValue;
                    bestChild = child;
                }
            }
            selected = bestChild;
        }
        // cout<<"exiting select "<<endl;
        return selected;
    }

    void expand(){
        // cout<<"inside expand "<<endl;
        createChildren();
        srand(time(0));
        // cout<<"exiting expand "<<endl;
        // if(children.size()==0)
            // cout<<"children size is 0"<<endl;
        // return children[rand() % children.size()];
    }

    void createChildren(){
        vector<int> samesuit(4,1);
        vector<PlayAction*> possibleMoves = playableAction(roundNumber, playerIds[currentPlayer], currentHand, 
                                                        trumpRevealed, trumpSuit, allCards[currentPlayer], samesuit );
        for(auto move : possibleMoves){
            // cout<<"here"<<endl;
            TreeNode* child = new TreeNode();
            child->parent = this;
            child->currentPlayer = currentPlayer;
            for(Card c: currentHand){
                child->currentHand.push_back(c);
            }
            child->roundNumber = roundNumber;
            child->trumpRevealed = trumpRevealed;
            child->trumpSuit = trumpSuit;
            child->visitCount = 0;
            child->score = vector<int>(4,0);
            child->playerIds = playerIds;
            child->bidAmount = bidAmount;
            child->bidPlayer = bidPlayer;
            for(int i: points){
                child->points.push_back(i);
            }
            for(int i=0;i<4;i++){
                
                for(Card c: allCards[i]){
                    child->allCards[i].push_back(c);
                }
            }
            if(move->action == PlayAction::PlayCard){
                child->currentPlayer = (currentPlayer + 1) % 4;
                child->currentHand.push_back(move->played_card);
                if(child->currentHand.size() == 4){
                    child->roundNumber = roundNumber + 1;
                    int winner = returnWinner(child->currentHand, child->currentPlayer, playerIds, child->trumpRevealed, child->trumpSuit);
                    child->currentPlayer = winner;
                    int value = winValue(child->currentHand);
                    child->points[winner] += value;
                    child->points[(winner+2)%4] += value;
                    child->currentHand.clear();
                }
                
                child->allCards[currentPlayer].erase(find(child->allCards[currentPlayer].begin(), child->allCards[currentPlayer].end(), move->played_card));
            }
            else if(move->action == PlayAction::RevealTrump){
                if(!holds_alternative<Suit>(trumpSuit)){
                    srand(time(0));
                    child->trumpSuit = Suit(rand() % 4);
                    
                }
                child->trumpRevealed = PlayPayload::RevealedObject {child->roundNumber ,playerIds[currentPlayer]};
            }
            children.push_back(child);
        }
    }

    //simulate the game from this node

    void simulate(){
        // cout<<"inside simulate "<<endl;
        TreeNode* currentNode = this;
        while(currentNode->children.size() != 0){
            // cout<<"round number"<<currentNode->roundNumber<<endl;
            srand(time(0));
            currentNode = currentNode->children[rand() % currentNode->children.size()];
            currentNode->createChildren();
        }
        // cout<<"exiting simulate "<<endl;
        currentNode->backPropagate();
    }

    void backPropagate(){
        // cout<<"inside backpropagate "<<endl;
        TreeNode* currentNode = this;
        vector<int>score(4,1);
        if(holds_alternative<PlayPayload::RevealedObject>(trumpRevealed)){
            if(points[bidPlayer] >= bidAmount){
                score[bidPlayer] = score[(bidPlayer+2)%4] = 1000;
                score[(bidPlayer+1)%4] = score[(bidPlayer+3)%4] = 0;
            }
            else{
                score[bidPlayer] = score[(bidPlayer+2)%4] = 0;
                score[(bidPlayer+1)%4] = score[(bidPlayer+3)%4] = 1000;
            }
        }
        while(currentNode != NULL){
            currentNode->visitCount++;
            for(int i=0;i<4;i++){
                currentNode->score[i] += score[i];
            }
            currentNode = currentNode->parent;
        }
        // cout<<"exiting backpropagate "<<endl;
    }

    double calcUCT(){

        if(visitCount == 0){
            return 100000000;
        }
        return ((score[parent->currentPlayer]*1.0) / visitCount) + sqrt(2 * log(parent->visitCount) / visitCount);
    }
};