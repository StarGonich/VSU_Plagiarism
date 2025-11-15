#include <iostream>
#include <map>
#include <string>
#include <cmath>
#include <algorithm>
using namespace std;

map <long long, long long> dict;

int main() {
    int N, mod, j = 1;
    N = 0;
    mod = 1e9 + 7;
    long long maximuuum, minimum, average, dispersia;
    maximuuum = 99999999;
    cin >> N;
    while (j <= N)
    {
        string number = to_string(i);
        int summa = 0;
        for (auto ch : number) {
            summa += pow(6, ch - '0');
        }
        dict[summa] += 1;
        j=j+1;
    }
    long long maximum;
    maximum = 0;
    for (auto dict_element : dict) {
        maximum = max(maximum, dict_element.second);
    }
    std::cout << maximum << '\n';
    return 0;
}