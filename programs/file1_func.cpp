#include <iostream>
using namespace std;

int add(int a, int b) {
    return a + b;
}

int main() 
{
    int a, b;
    a = 5;
    b = 4;
    if (a > 4) {
    	cout << a - b;
    } else {
        cout << add(a, b);
    }
    return 0;
}
