#include <iostream>
#include <map>
#include <string>
#include <cmath>
#include <algorithm>
using namespace std;

map<long long, long long> mp;

int main() {
    int n, i = 1;
    cin >> n;
    while (i <= n)
    {
        string num = to_string(i);
        int sum = 0;
        for (auto c : num) {
            sum += pow(6, c - '0');
        }
        mp[sum]++;
        i++;
    }
    long long mx = 0;
    for (auto p : mp) {
        mx = max(mx, p.second);
    }
    std::cout << mx << '\n';

    return 0;
}