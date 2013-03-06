public class AST_ForStatements {

    public AST_ForStatements() {
        for (i = 0; i < 10; i = i + 1) {

        }

        for (B b = new B(); b.foo(); )
            if (b.bar(new Test()))
                i = i + 1;

        for (;;)
            ;
    }
}
