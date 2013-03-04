import a.B;

public class AST_CastExpressions {

    public AST_CastExpressions() {
        int i = 0;

        // Test all 4 cast expressions.
        B b = (B)i;
        B[] bs = (B[])i;
        c.D d = (c.D)i;
        c.D[] ds = (c.D[])i;
        char c = (char)i;
        char[] cs = (char[])i;
    }
}
        
