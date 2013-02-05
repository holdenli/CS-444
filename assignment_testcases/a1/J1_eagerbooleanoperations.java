// PARSER_WEEDER
// JOOSW:LEXER_EXCEPTION
public class J1_eagerbooleanoperations {
  public J1_eagerbooleanoperations() {}
  public static int test() {
      boolean x = false;
      boolean b = (x & true) | !x;
      return 123;
  }
}
