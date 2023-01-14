#include<bits/stdc++.h>
#include<chrono>
using namespace std;

int main(){
    uint64_t ms = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    std::cout << ms << " milliseconds since the Epoch\n";
}