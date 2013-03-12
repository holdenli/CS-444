import a.b.c.d;

public class AST_FieldAccess {
    public AST_FieldAccess() {
        a.b.c.d = 3; // Assignment, not a field access.
        this.a.b.c.d = 3; // Assignment, not a field access.
        a.b = this.a.b.c;
    }
}

