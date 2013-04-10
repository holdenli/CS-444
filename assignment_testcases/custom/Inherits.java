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
        String[] a = new String[5];
        a[4] = "hello";
        System.out.println(a[4]);
        java.io.Serializable o = a;
        Cloneable o2 = a;
        Object o3 = a;
        System.out.println(o3);

        a = (String[])o;
        System.out.println(a[4]);
        a = (String[])o2;
        System.out.println(a[4]);
        a = (String[])o3;
        System.out.println(a[4]);
        return 1;
    }

}
