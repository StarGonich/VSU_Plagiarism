// Магазин

#include <iostream>
using namespace std;

int n, q;
int money;

const int NMAX = 10000;
int arrN[NMAX];
int arrQ[NMAX];

int main() {
    ios_base::sync_with_stdio(0);
    cin.tie(0);

    cin >> n >> q;

    for (int i = 0; i < n; i++) {
        cin >> arrN[i];
    }

    for (int buyer = 0; buyer < q; buyer++) {
        cin >> money;
        money--;
        int i = 0, j = 0;
        int s = arrN[0];
        int mx = 0;
        if (s <= money) {
            mx = s;
        }
        bool go = true;
        while (go) {
            if (s == money) {
                go = false;
            } else if (s < money) {
                if (j == n - 1) {
                    go = false;
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

    for (int i = 0; i < q; i++) {
        cout << arrQ[i] << " ";
    }

    return 0;
}