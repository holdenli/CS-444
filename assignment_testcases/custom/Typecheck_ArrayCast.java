public class Typecheck_ArrayCast {

    public Typecheck_ArrayCast() {
        int[] a = new int[];
        Object o = (Object)a;
        a = (int[])o;

        char[] cs = (char[])o;
        // char[] ds = (char[])a;
        int[] es = (int[])cs;
    }
}
