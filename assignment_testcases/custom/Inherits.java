package apple;

public class Inherits {

    public int i;
    public int j;

    public Inherits() {}

    public int foo(int a) { return 1; }
    public static int test() {
        Inherits i = new Inherits();
        return 1;
    }

}
