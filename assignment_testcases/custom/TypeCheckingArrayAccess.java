public class TypeCheckingArrayAccess {

    public int[] ints;
    public TypeCheckingArrayAccess() {
        this.ints = new int[3];
        int i = ints[3];
    }
}
