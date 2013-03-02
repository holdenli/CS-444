import a.a.A;
import b.b.B;

public class AST_Class2 extends a.a.A implements Foo, b.Foo {
    public int x;
    public int y = (0 + 1);
    protected a.a.A s;
    protected b.b.B t = null;

    public AST_Class2() {}
    public AST_Class2(int i) {}

    protected void M(a.a.A i) {}
    protected void N(a.a.A j) { return; }
    public int O(int j) { return j; }
    public int[] P(String s) { return null; }

}


