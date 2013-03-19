// Use with reachability to determine if we evaluate const expressions correctly
// (JLS 15.28 Constant Expression)
public class ConstExpr {

    public ConstExpr() {
        while((1+2-3*1/1) > -1) {}
        while((1 >= 1) && (1 <= 1) || false) {}
        while((2 > 1) && (0 < 1) || false) {}
        while((int)1 % (short)1 != (char)50) {}
        while(!true == false) {}
        while("WHAT" == (String)"WHAT") {}
        if(false) {}
    }
}
