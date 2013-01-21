#!/usr/bin/python3
import re
import sys

DIGITS=r'(?:0|[1-9][0-9]*)'
ESCAPE_SEQUENCE=r'\\(?:[btnfr"\'\\]|[0-3][0-7]{2}|[0-7]{1,2})'

MULTILINE_PATTERNS = {
    #'LineTerminator': r'^(\r|\n)',
    'WhiteSpace': [r'^((?:\t|\n|\r|\f| )+)'],
    
    'MultiComment': [r'^(\/\*(?:.+?)\*\/)'],  
}

SINGLELINE_PATTERNS = {
    'SingleComment': [r'^(\/\/.*)'],
    
    'Identifier': [r'^([a-zA-Z_$][a-zA-Z0-9_$]*)'],
    
    # integer literals
    'DecimalIntegerLiteral': [r'^('+DIGITS+'[lL]?)'],
    'HexIntegerLiteral': [r'^(0[xX][0-9abcedfABCDEF]+[lL]?)'],
    'OctalIntegerLiteral': [r'^(0[0-7]+[lL]?)'],
    
    # floating point literals:
    #     Digits . Digitsopt ExponentPartopt FloatTypeSuffixopt
    #     . Digits ExponentPartopt FloatTypeSuffixopt
    #     Digits ExponentPart FloatTypeSuffixopt
    #     Digits ExponentPartopt FloatTypeSuffix
    'FloatingPointLiteral': [
        r'^('+DIGITS+'\.'+DIGITS+'?(?:[eE][+-]?'+DIGITS+'+)?[dDfF]?)',
        r'^(\.'+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)?[dDfF]?)',
        r'^('+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)[dDfF]?)',
        r'^('+DIGITS+'(?:[eE][+-]?'+DIGITS+'+)?[dDfF])',
    ],
    
    'BooleanLiteral': [r'^(true|false)'],
    
    # this one was a bit confusing to write:
    #   (?!\\|\') rejects ' and \ and new lines,
    #   while [\x00-\x7F] matches all other ascii
    'CharacterLiteral': [r'^(\'(?:(?!\\|\'|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')\')'],
    
    'StringLiteral': [r'^("(?:(?!\\|\"|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')*")'],
    
    'NullLiteral': [r'^(null)'],
    
    'Separator': [r'^([(){}\[\];,.])'],
}

# this is a token string -> token label mapping
STRINGS = {
    
    # assignment operators
    '%=': 'AssignmentOperator',
    '&=': 'AssignmentOperator',
    '*=': 'AssignmentOperator',
    '+=': 'AssignmentOperator',
    '-=': 'AssignmentOperator',
    '/=': 'AssignmentOperator',
    '<<<=': 'AssignmentOperator',
    '<<=': 'AssignmentOperator',
    '=': 'AssignmentOperator',
    '>>=': 'AssignmentOperator',
    '>>>=': 'AssignmentOperator',
    '^=': 'AssignmentOperator',
    '|=': 'AssignmentOperator',
    
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
    '>=': 'GreatherThanEqualOperator',
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
    'const': 'Const',
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
    
    # type of (TOKEN LABEL, token value, position, line)
    tokens = []
    pos = 0
    line = 0
    
    # get the list of tokens to match for, sorted by length of token (desc)
    strings = sorted(STRINGS, reverse=True, key=lambda x: len(x))
    
    # compile the regex and merge them into one `patterns` dict
    patterns = {k: [re.compile(p, re.ASCII)
                    for p in SINGLELINE_PATTERNS[k]]
                    for k in SINGLELINE_PATTERNS}

    patterns.update({k: [re.compile(p, re.ASCII | re.DOTALL)
                        for p in MULTILINE_PATTERNS[k]]
                        for k in MULTILINE_PATTERNS})

    while pos != len(program):
        # first, we try to match string tokens from STRINGS dict.
        # this is pretty inefficient.  TODO:  use a trie
        prefix = find_prefix(program, strings, pos)
        if prefix != None:
            pos += len(prefix)
            tokens.append((STRINGS[prefix], prefix, len(prefix), line))
            continue
    
        # now, we match regex patterns.  In the event we have more than 1 regex
        # that matches, keep a list of matches and pick the greediest match
        matches = []
        for token_label in patterns:
            for pattern in patterns[token_label]:
                match = pattern.match(program[pos:])
                if match != None:
                    matches.append((token_label, match.group(1)))
        
        if len(matches) > 0:
            # find the match that consumes the most characters in program
            (token_label, token_value) = max(matches, key=lambda x: len(x[1]))
            line += token_value.count('\n')
            pos += len(token_value)
            
            # ignore whitespace
            if token_label != 'WhiteSpace':
                tokens.append((token_label, token_value, pos, line))
            
            continue

        print(tokens, "pos = %d, line = %d, next few chars: %s" % (pos, line, program[pos:pos+10]))
        sys.exit(42)
    
    return tokens
