int main() {
    int x = 10;
    cout << goodfunc(x);
}

int * goodfunc(int x) {
    return &x;
}