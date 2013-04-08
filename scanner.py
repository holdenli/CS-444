#!/usr/bin/python3

import re
import sys
import pprint
from collections import namedtuple

from utils import logging

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
    'DecimalIntegerLiteral': [r'('+DIGITS+')'],
    #'DecimalIntegerLiteral': [r'('+DIGITS+'[lL]?)'],
    #'DecimalIntegerLiteral': [r'('+DIGITS+')'], # No Longs in Joos.
    #'HexIntegerLiteral': [r'(0[xX][0-9abcedfABCDEF]+[lL]?)'],
    #'OctalIntegerLiteral': [r'(0[0-7]+[lL]?)'],
    
    # floating point literals (unused in Joos):
    #     Digits . Digitsopt ExponentPartopt FloatTypeSuffixopt
    #     . Digits ExponentPartopt FloatTypeSuffixopt
    #     Digits ExponentPart FloatTypeSuffixopt
    #     Digits ExponentPartopt FloatTypeSuffix
    'FloatingPointLiteral': [
        r'('+DIGITS+'\.'+DIGITS+'?(?:[eE][+-]?'+DIGITS+'+)?[dDfF]?)',
        r'(\.'+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)?[dDfF]?)',
        r'('+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)[dDfF]?)',
        r'('+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)?[dDfF])',
    ],
    
    # this one was a bit confusing to write:
    #   (?!\\|\') rejects ' and \ and new lines,
    #   while [\x00-\x7F] matches all other ascii
    'CharacterLiteral': [r'(\'(?:(?!\\|\'|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')\')'],
    
    'StringLiteral': [r'("(?:(?!\\|\"|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')*")'],
}

def unescape_str(s):
    def unescape_chr(seq):
        sequences = {
            '\\b': "\b",
            '\\t': "\t",
            '\\n': "\n",
            '\\f': "\f",
            '\\r': "\r",
            '\\"': "\"",
            "\\'": "'",
            '\\\\': "\\",
        }

        if seq in sequences:
            return sequences[seq]

        # octal escapes:
        return chr(int(seq[1:], 8))

    seq_re = re.compile("(%s)" % ESCAPE_SEQUENCE)

    consumed = 0
    new_s = ''
    while consumed < len(s):
        matches = seq_re.match(s, consumed)
        if matches != None:
            new_s += unescape_chr(matches.group(0))
            consumed += len(matches.group(0))
        else:
            new_s += s[consumed]
            consumed += 1

    return new_s

# this is a token string -> token label mapping
# Commented lines are specific to Java, but not in Joos.
STRINGS = {

    # literals
    'true': 'BooleanLiteral',
    'false': 'BooleanLiteral',
    'null': 'NullLiteral',
    
    # assignment operators
    '%=': 'ModuloAssignmentOperator',
    '&=': 'BinaryAndAssignmentOperator',
    '*=': 'MultiplyAssignmentOperator',
    '+=': 'AddAssignmentOperator',
    '-=': 'SubtractAssignmentOperator',
    '/=': 'DivideAssignmentOperator',
    '<<=': 'LeftShiftAssignmentOperator',
    '=': 'DirectAssignmentOperator',
    '>>=': 'RightShiftAssignmentOperator',
    '>>>=': 'UnsignedRightShiftAssignmentOperator',
    '^=': 'InverseAssignmentOperator',
    '|=': 'BinaryOrAssignmentOperator',
    
    # all other expression operators
    '!': 'NotOperator',
    '!=': 'NotEqualOperator',
    '%': 'ModuloOperator',
    '&': 'BinaryAndOperator',
    '&&': 'AndOperator',
    '*': 'MultiplyOperator',
    '+': 'AddOperator',
    '++': 'IncrementOperator',
    '-': 'SubtractOperator',
    '--': 'DecrementOperator',
    '/': 'DivideOperator',
    ':': 'ColonOperator',
    '<': 'LessThanOperator',
    '<<': 'LeftShiftOperator',
    '<=': 'LessThanEqualOperator',
    '==': 'EqualOperator',
    '>': 'GreaterThanOperator',
    '>=': 'GreaterThanEqualOperator',
    '>>': 'RightShiftOperator',
    '>>>': 'UnsignedRightShiftOperator',
    '?': 'QuestionOperator',
    '^': 'InverseOperator',
    '|': 'BinaryOrOperator',
    '||': 'OrOperator',
    '~': 'BinaryNotOperator',
    
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

AUGMENTS = ['BOF', 'EOF']

THROWAWAY_TOKENS = {'WhiteSpace', 'SingleComment', 'MultiComment'}

Token = namedtuple('Token', ['label', 'value', 'pos', 'line'])

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
    pos = 0
    line = 0
    tokens = [Token('BOF', '', pos, line)]

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
        best_match = None
        best_match_len = -1
        
        # first, we try to match string tokens from STRINGS dict.
        # this is pretty inefficient.  TODO:  use a trie
        prefix = find_prefix(program, strings, pos)
        if prefix != None:
            best_match = ((STRINGS[prefix], prefix)) 
            best_match_len = len(prefix)
    
        # now, we match regex patterns.
        for token_label in patterns:
            for pattern in patterns[token_label]:
                match = pattern.match(program, pos)
                if match != None:
                    if len(match.group(1)) > best_match_len:
                        best_match = (token_label, match.group(1))
                        best_match_len = len(match.group(1))
        
        if best_match_len != -1:
            # find the match that consumes the most characters in program
            (token_label, token_value) = best_match
            line += token_value.count('\n')
            pos += len(token_value)
           
            # ignore whitespace and comments
            if (token_label not in THROWAWAY_TOKENS):

                if token_label in ['StringLiteral', 'CharacterLiteral']:
                    token_value = unescape_str(token_value[1:-1])
                tokens.append(Token(token_label, token_value, pos, line))
        else:
            logging.error("LEXER FAILURE: pos = %d, line = %d; next few chars:\n%s"
                % (pos, line, program[pos:pos+20].replace("\n", "\\n")))

            sys.exit(42)

    tokens.append(Token('EOF', '', pos, line)) # End of file augmentation token.
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

    logging.setLogLevel("NONE")
    ts = test.TestRunner("Scanner", test_work)
    ts.assignment = "a1"
    ts.re_expected = "LEXER_EXCEPTION"
    #ts.verbose = True

    ts.run()

