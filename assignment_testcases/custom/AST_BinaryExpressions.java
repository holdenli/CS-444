public class AST_BinaryExpressions {

    public AST_BinaryExpressions() {
        int i = 0;
        int j = 0;
        int k = 0;
        i = j + 1;
        k = j + (i - j);
        k = i * j / 2;
        boolean b;
        b = false;
        b = b && true;
        b = !b;
        b = (i == j);
        b = (j != i);
        b = j < i;
        b = k >= j;
        b = k % j;
    }
}

