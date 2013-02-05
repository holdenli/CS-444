#!/usr/bin/python3
import re
import sys
import pprint

DIGITS=r'(?:0|[1-9][0-9]*)'
ESCAPE_SEQUENCE=r'\\(?:[btnfr"\'\\]|[0-3][0-7]{2}|[0-7]{1,2})'

MULTILINE_PATTERNS = {
    #'LineTerminator': r'(\r|\n)',
    'WhiteSpace': [r'((?:\t|\n|\r|\f| )+)'],
    
    'MultiComment': [r'(\/\*(?:.*?)\*\/)'],  
}

# Commented lines are from spec but unused in Joos.
SINGLELINE_PATTERNS = {
    'SingleComment': [r'(\/\/.*)'],
    
    'Identifier': [r'([a-zA-Z_$][a-zA-Z0-9_$]*)'],
    
    # integer literals
    #'DecimalIntegerLiteral': [r'('+DIGITS+'[lL]?)'],
    'DecimalIntegerLiteral': [r'('+DIGITS+')'], # No Longs in Joos.
    # 'HexIntegerLiteral': [r'(0[xX][0-9abcedfABCDEF]+[lL]?)'],
    # 'OctalIntegerLiteral': [r'(0[0-7]+[lL]?)'],
    
    # floating point literals (unused in Joos):
    #     Digits . Digitsopt ExponentPartopt FloatTypeSuffixopt
    #     . Digits ExponentPartopt FloatTypeSuffixopt
    #     Digits ExponentPart FloatTypeSuffixopt
    #     Digits ExponentPartopt FloatTypeSuffix
    # 'FloatingPointLiteral': [
    #     r'('+DIGITS+'\.'+DIGITS+'?(?:[eE][+-]?'+DIGITS+'+)?[dDfF]?)',
    #     r'(\.'+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)?[dDfF]?)',
    #     r'('+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)[dDfF]?)',
    #     r'('+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)?[dDfF])',
    # ],
    
    'BooleanLiteral': [r'(true|false)'],
    
    # this one was a bit confusing to write:
    #   (?!\\|\') rejects ' and \ and new lines,
    #   while [\x00-\x7F] matches all other ascii
    'CharacterLiteral': [r'(\'(?:(?!\\|\'|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')\')'],
    
    'StringLiteral': [r'("(?:(?!\\|\"|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')*")'],
    
    'NullLiteral': [r'(null)'],
}

# this is a token string -> token label mapping
# Commented lines are specific to Java, but not in Joos.
STRINGS = {
    
    # assignment operators
    # '%=': 'AssignmentOperator',
    # '&=': 'AssignmentOperator',
    # '*=': 'AssignmentOperator',
    # '+=': 'AssignmentOperator',
    # '-=': 'AssignmentOperator',
    # '/=': 'AssignmentOperator',
    # '<<<=': 'AssignmentOperator',
    # '<<=': 'AssignmentOperator',
    '=': 'AssignmentOperator',
    # '>>=': 'AssignmentOperator',
    # '>>>=': 'AssignmentOperator',
    # '^=': 'AssignmentOperator',
    # '|=': 'AssignmentOperator',
    
    # all other expression operators
    '!': 'NotOperator',
    '!=': 'NotEqualOperator',
    '%': 'ModuloOperator',
    # '&': 'BinaryAndOperator',
    '&&': 'AndOperator',
    '*': 'MultiplyOperator',
    '+': 'AddOperator',
    # '++': 'IncrementOperator',
    '-': 'SubtractOperator',
    # '--': 'DecrementOperator',
    '/': 'DivideOperator',
    # ':': 'ColonOperator',
    '<': 'LessThanOperator',
    # '<<': 'LeftShiftOperator',
    '<=': 'LessThanEqualOperator',
    '==': 'EqualOperator',
    '>': 'GreaterThanOperator',
    '>=': 'GreaterThanEqualOperator',
    # '>>': 'RightShiftOperator',
    # '>>>': 'UnsignedRightShiftOperator',
    # '?': 'QuestionOperator',
    # '^': 'InverseOperator',
    # '|': 'BinaryOrOperator',
    '||': 'OrOperator',
    # '~': 'BinaryNotOperator',
    
    # keywords
    'abstract': 'Abstract',
    'boolean': 'Boolean',
    'break': 'Break',
    'byte': 'Byte',
    'case': 'Case',
    'catch': 'Catch',
    'char': 'Char',
    'class': 'Class',
    'const': 'Const', # TODO: Unused in Java, keep in Joos?
    'continue': 'Continue',
    'default': 'Default',
    'do': 'Do',
    'double': 'Double',
    'else': 'Else',
    'extends': 'Extends',
    'final': 'Final',
    'finally': 'Finally',
    'float': 'Float',
    'for': 'For',
    'goto': 'Goto',
    'if': 'If',
    'implements': 'Implements',
    'import': 'Import',
    'instanceof': 'Instanceof',
    'int': 'Int',
    'interface': 'Interface',
    'long': 'Long',
    'native': 'Native',
    'new': 'New',
    'package': 'Package',
    'private': 'Private',
    'protected': 'Protected',
    'public': 'Public',
    'return': 'Return',
    'short': 'Short',
    'static': 'Static',
    'strictfp': 'Strictfp',
    'super': 'Super',
    'switch': 'Switch',
    'synchronized': 'Synchronized',
    'this': 'This',
    'throw': 'Throw',
    'throws': 'Throws',
    'transient': 'Transient',
    'try': 'Try',
    'void': 'Void',
    'volatile': 'Volatile',
    'while': 'While',
    
    # separators
    '{': 'LeftBrace',
    '}': 'RightBrace',
    '[': 'LeftBracket',
    ']': 'RightBracket',
    '(': 'LeftParenthesis',
    ')': 'RightParenthesis',
    ';': 'SemiColon',
    ',': 'Comma',
    '.': 'Dot',
}

THROWAWAY_TOKENS = {'WhiteSpace', 'SingleComment', 'MultiComment'}

def find_prefix(string: "body of text we are matching prefixes of",
                prefixes: "list/iterable of prefixes",
                pos: "an offset of string") -> "prefix":
    for prefix in prefixes:
        if string.startswith(prefix, pos):
            return prefix
    
    return None

def scan(program: "Joos program as a string") -> "list of tokens":
    """
    - First, match the STRINGS
    - Then, the single and multiline patterns
    """
    
    # tuple of (TOKEN LABEL, token value, position, line)
    tokens = []
    pos = 0
    line = 0
    
    # get the list of tokens to match for, sorted by length of token (desc)
    strings = sorted(STRINGS, reverse=True, key=len)
    
    # compile the regex and merge them into one `patterns` dict
    patterns = {k: [re.compile(p, re.ASCII)
                    for p in SINGLELINE_PATTERNS[k]]
                    for k in SINGLELINE_PATTERNS}

    patterns.update({k: [re.compile(p, re.ASCII | re.DOTALL)
                        for p in MULTILINE_PATTERNS[k]]
                        for k in MULTILINE_PATTERNS})

    while pos != len(program):
        is_identifier = False
        
        # In the event we have more than 1 regex that matches, we keep a list
        # of matches and pick the greediest match
        matches = []
        
        # first, we try to match string tokens from STRINGS dict.
        # this is pretty inefficient.  TODO:  use a trie
        prefix = find_prefix(program, strings, pos)
        if prefix != None:
            matches.append((STRINGS[prefix], prefix))
    
        # now, we match regex patterns.
        for token_label in patterns:
            for pattern in patterns[token_label]:
                match = pattern.match(program, pos)
                if match != None:
                    if token_label == 'Identifier':
                        is_identifier = True 
                    matches.append((token_label, match.group(1)))
        
        if len(matches) > 0:
            # if we have a match for an Identifier and a different token type,
            # the different token type trumps it!
            if is_identifier and len(matches) >= 2:
                # find and remove the identifier
                found = 0
                for (n, (token_type,_)) in enumerate(matches):
                    if token_type == 'Identifier':
                        found = n
                        break
                matches.pop(found)

            # find the match that consumes the most characters in program
            (token_label, token_value) = max(matches, key=lambda x: len(x[1]))
            line += token_value.count('\n')
            pos += len(token_value)
            
            # ignore whitespace and comments
            if token_label not in THROWAWAY_TOKENS:
                tokens.append((token_label, token_value, pos, line))
        else:
            pprint.pprint(tokens)
            print("LEXER FAILURE: pos = %d, line = %d; next few chars:\n%s"
                % (pos, line, program[pos:pos+20].replace("\n", "\\n")))
            sys.exit(42)
    
    return tokens

if __name__ == "__main__":
    import test
    def test_work(path):
        try:
            with open(path, 'r') as f:
                scan(f.read())
            return 0
        except SystemExit as e:
            return 1

    ts = test.TestRunner("Scanner", test_work)
    ts.assignment = "a1"
    ts.re_expected = "LEXER_EXCEPTION"
    #ts.verbose = True

    ts.run()

