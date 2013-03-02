# Grammar "rules" for the Abstract Syntax Tree.
# Not an actual "rules" dictionary - purely for documentation on the structure
# of the AST.

RULES = {

    'Root': [
        [],
        ['CompilationUnit']
    ],

    'CompilationUnit': [
        ['PackageDeclaration', 'TypeImports', 'PackageImports',
            'ClassDeclaration'],
        ['PackageDeclaration', 'TypeImports', 'PackageImports',
            'InterfaceDeclaration'],
    ],

    'PackageDeclaration': [
        ['Identifier'], # Zero or more
    ],

    'TypeImports': [
        ['ImportDeclaration'], # Zero or more
    ],

    'PackageImports': [
        ['ImportDeclaration'], # Zero or more
    ],

    'ImportDeclaration': [
        ['Identifier'], # Zero or more
    ],

    'ClassDeclaration': [
        ['Modifiers', 'ClassName', 'Superclass', 'Interfaces', 'Fields',
            'Constructors', 'Methods'],
    ],

    'InterfaceDeclaration': [
        ['Modifiers', 'InterfaceName', 'Interfaces', 'Methods'],
    ],

    'Modifiers': [
        ['Modifier'], # One or more
    ],

    'ClassName': [
        ['Identifier'],
    ],

    'InterfaceName': [
        ['Identifier'],
    ],

    'Superclass': [
        ['Identifier'], # One or more
    ],

    'Interfaces': [
        ['InterfaceType'], # Zero or more
    ],

    'InterfaceType': [
        ['Identifier'], # One or more
    ],

    'Fields': [
        ['Field'], # Zero or more
    ],

    'Field': [
        ['Modifiers', 'Type', 'Identifier', 'Initializer'],
    ],

    'Type': [
        ['PrimitiveType'],
        ['ReferenceType'],
        ['ArrayType'],
    ],

    'PrimitiveType': [
        ['Byte'],
        ['Short'],
        ['Char'],
        ['Boolean'],
        ['Int'],
    ],

    'ReferenceType': [
        ['Identifier'], # One or more
    ],

    'ArrayType': [
        ['PrimitiveType'],
        ['ReferenceType'],
    ],

    'Initializer': [
        [],
        ['Expression'],
    ],

    'Constructors': [
        ['Constructors'], # One or more
    ],

    'Constructor': [
        ['Modifier', 'Identifier', 'Parameters', 'Block'],
    ],

    'Parameters': [
        ['Parameter'], # Zero or more
    ],

    'Parameter': [
        ['Type', 'Identifier'],
    ],

    'Methods': [
        ['Method'], # Zero or more
    ],

    'Method': [
        ['Modifiers', 'Type', 'Identifier', 'Parameters', 'MethodBody'],
        ['Modifiers', 'Void', 'Identifier', 'Parameters', 'MethodBody'],
    ],

    'MethodBody': [
        [],
        ['Block'],
    ],
}

