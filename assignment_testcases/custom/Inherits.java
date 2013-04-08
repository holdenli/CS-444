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
        int[] i = new int[5];
        i[4] = 4; 
        return i[4];
    }

}
