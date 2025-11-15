#include <iostream>
#include <map>
#include <string>
#include <cmath>
#include <algorithm>
using namespace std;

map <int, int> mp;

int main() {
    int n, sum = 0, mx = 0;
    std::cin >> n;
    for (int i = 1; i < n + 1; i++)
    {
        string num = to_string(i);
        for (char c : num) {
            sum += pow(6, c - '0');
        }
        mp[sum]++;
    }
    for (auto p : mp) {
        mx = max(mx, p.second);
    }
    cout << mx << endl;

    return 0;
}