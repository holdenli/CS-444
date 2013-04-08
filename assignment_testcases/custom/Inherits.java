package apple;

public class Inherits {

    public static int foo = 41;
    public int i = 2;
    public int j;

    public Inherits() {}

    public int foo(int a) { return 1; }

    public static int func(int i) {
        return i;
    }

    public static int test() {
        return 201; //apple.Inherits.func(700);
    }

}
