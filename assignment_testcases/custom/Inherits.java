package apple;

public class Inherits {

    public static int foo = 100;
    public int i = 2;
    public int j;

//    public Inherits() { i = 50; }

    public Inherits() {
        i = 13;    
    }

    public int foo(int a) { return 1; }

    public static boolean func() {
        apple.Inherits.foo = 25;
        return true;
    }

    public static int test() {
        if (false || apple.Inherits.func())
        {
            return Inherits.foo;
        }
        return 1;
    }

}
