// Тет системы на проверку плагиата

#include <iostream>
#include <string>
#include <algorithm>
#include <unordered_map>
using namespace std;

int main() {
    int N;
    cin >> N;

    unordered_map<string, int> group_count;
    int max_count = 0;

    for (int num = 1; num <= N; num++) {
        string digits = to_string(num);
        sort(digits.begin(), digits.end());
        group_count[digits]++;
        max_count = max(max_count, group_count[digits]);
    }

    cout << max_count << endl;

    return 0;
}