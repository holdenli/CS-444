#!/usr/bin/python3
import re

DIGITS=r'(?:0|[1-9][0-9]*)'
ESCAPE_SEQUENCE=r'\\(?:[btnfr"\'\\]|[0-3][0-7]{2}|[0-7]{1,2})'

multiline_patterns = {
    #'LineTerminator': r'^(\r|\n)',
    'WhiteSpace': r'^((?:\t|\n|\r|\f)+)',
    
    'MultiComment': r'^(\/\*(?:.+?)\*\/)',  
}

singleline_patterns = {
    'SingleComment': r'^(\/\/.*)',
    
    'Identifier': r'^([a-zA-Z_$][a-zA-Z0-9_$]*)',
    
    # fixme: these were copy-pasted and or'd together.
    #   some of these aren't in Joos.
    'Keyword': r'^(synchronized|implements|instanceof|protected|transient|interface|abstract|strictfp|volatile|continue|default|private|boolean|extends|finally|package|double|import|public|throws|return|static|native|switch|throw|break|short|catch|final|class|float|super|while|const|this|byte|else|case|void|char|long|goto|int|try|for|new|if|do)',
    
    # integer literals
    'DecimalIntegerLiteral': r'^(0|[1-9][0-9]+[lL]?)',
    'HexIntegerLiteral': r'^(0[xX][0-9abcedfABCDEF]+[lL]?)',
    'OctalIntegerLiteral': r'^(0[0-7]+[lL]?)',
    
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
    
    'BooleanLiteral': r'^(true|false)',
    
    # this one was a bit confusing to write:
    #   (?!\\|\') rejects ' and \ and new lines,
    #   while [\x00-\x7F] matches all other ascii
    'CharacterLiteral': r'^(\'(?:(?!\\|\'|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')\')',
    
    'StringLiteral': r'^("(?:(?!\\|\"|\r|\n)[\x00-\x7F]|'+ESCAPE_SEQUENCE+')*")',
    
    'NullLiteral': r'^(null)',
    
    'Separator': r'^([(){}\[\];,.])',
    
    # make sure it's sort by length of operator in descending order
    'Operator': r'^(>>>=|>>>|<<=|>>=|==|<=|>=|!=|&&|\|\||\+\+|--|<<|>>|\+=|-=|\*=|\/=|&=|\|=|\^=|%=|=|>|<|!|~|\?|:|\+|-|\*|/|&|\||\^|%)'
}

def scan(program: "Joos program as a string") -> "list of tokens":
    return []    