#include <iostream>

int main() {
    int n, q;
    int money;

    const int NMAX = 10000;
    int arrN[NMAX];
    int arrQ[NMAX];

    std::cin >> n >> q;

    int i = 0;
    while (i < n) {
        std::cin >> arrN[i];
        i = i + 1;
    }

    for (int buyer = 0; buyer < q; buyer++) {
        std::cin >> money;
        money = money - 1;
        int i = 0, j = 0;
        int s = arrN[0];
        int mx = 0;
        if (s <= money) {
            mx = s;
        }
        bool boolean = true;
        while (boolean) {
            if (s == money) {
                boolean = false;
            } else if (s < money) {
                if (j == n - 1) {
                    boolean = false;
                } else {
                    j += 1;
                    s += arrN[j];
                }
            } else {
                s -= arrN[i];
                i += 1;
            }
            if (mx < s && s <= money) {
                mx = s;
            }
        }
        arrQ[buyer] = money + 1 - mx;
    }

    i = 0;
    while (i < q) {
        std::cout << arrQ[i] << " ";
        i = i + 1;
    }
}