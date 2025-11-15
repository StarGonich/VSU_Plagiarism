// Тет системы на проверку плагиата

#include <iostream>
#include <string>
#include <algorithm>
#include <unordered_map>
using namespace std;

int main() {
    int n;
    cin >> n;

    unordered_map<string, int> ump;
    int mxcount = 0;

    for (int number = 1; number <= n; number++) {
        string digits = to_string(number);
        sort(digits.begin(), digits.end());
        ump[digits]++;
        mxcount = max(mxcount, ump[digits]);
    }

    cout << mxcount << endl;

    return 0;
}