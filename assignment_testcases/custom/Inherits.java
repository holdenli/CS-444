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

    public static int func(int i) {
        return i;
    }

    public static int test() {
        Inherits s = new Inherits2();
        Object t = (Object)"hello";
        if ("hello" == "hello")
        {
            return 25;
        }
        return 1;
    }

}
