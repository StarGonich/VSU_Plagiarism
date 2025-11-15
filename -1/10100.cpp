#include <iostream>
#include <map>
#include <string>
#include <cmath>
#include <algorithm>
using namespace std;

map <int, int> dictionary;

int main() {
    int N;
    std::cin >> N;
    for (int j = 1; j < N + 1; j++)
    {
        string number = to_string(j);
        int summa = 0;
        for (char ch : number) {
            summa += pow(6, ch - '0');
        }
        dictionary[summa]++;
    }
    int maximum = 0;
    for (auto dict_element : dictionary) {
        maximum = max(maximum, dict_element.second);
    }
    cout << maximum << endl;

    return 0;
}