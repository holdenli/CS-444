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
        [],
        ['Type'],
    ],

    'Interfaces': [
        ['Type'], # Zero or more
    ],

    'Fields': [
        ['FieldDeclaration'], # Zero or more
    ],

    'FieldDeclaration': [
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
        ['ConstructorDeclaration'], # One or more
    ],

    'ConstructorDeclaration': [
        ['Modifier', 'Identifier', 'Parameters', 'Block'],
    ],

    'Parameters': [
        ['Parameter'], # Zero or more
    ],

    'Parameter': [
        ['Type', 'Identifier'],
    ],

    'Methods': [
        ['MethodDeclaration'], # Zero or more
    ],

    'MethodDeclaration': [
        ['Modifiers', 'Type', 'Identifier', 'Parameters', 'MethodBody'],
        ['Modifiers', 'Void', 'Identifier', 'Parameters', 'MethodBody'],
    ],

    'MethodBody': [
        [],
        ['Block'],
    ],

    'Block': [ # Zero or more
        ['Statement'],
    ],

    'Statement': [
        ['LocalVariableDeclaration'],
        ['Block'],
        ['EmptyStatement'],
        ['ExpressionStatement'],
        ['ReturnStatement'],
        ['IfStatement'],
        ['WhileStatement'],
        ['ForStatement'],
    ],

    'LocalVariableDeclaration': [
        ['Type', 'Identifier', 'Initializer'],
    ],

    'Initializer': [
        [],
        ['Expression'],
    ],

    'EmptyStatement': [ # TODO: find a way to get rid of this
        [],
    ],

    'ExpressionStatement': [
        ['Expression'],
    ],

    'ReturnStatement': [
        ['Expression'],
    ],

    'IfStatement': [
        ['Expression', 'Statement'],
        ['Expression', 'Statement', 'Statement'],
    ],

    'WhileStatement': [
        ['Expression', 'Statement'],
    ],

    'ForStatement': [
        ['ForInit', 'ForCondition', 'ForUpdate', 'ForBody'],
    ],

    'ForInit': [
        [],
        ['Expression'],
        ['LocalVariableDeclaration'],
    ],

    'ForCondition': [
        [],
        ['Expression'],
    ],

    'ForUpdate': [
        [],
        ['Expression'],
    ],

    'ForBody': [
        [],
        ['LocalVariableDeclaration'],
        ['Block'],
        ['EmptyStatement'],
        ['ExpressionStatement'],
        ['ReturnStatement'],
        ['IfStatement'],
        ['WhileStatement'],
        ['ForStatement'],
    ],

    # Expressions.

    # There is actually no Expression node. It directly resolves to one of
    # these below.
    'Expression': [
        ['Assignment'],
        ['MethodInvocation'],
        ['CreationExpression'],
        ['InstanceofExpression'],
        ['PostfixExpression'],
        ['CastExpression'],

        # Binary expressions.

        ['EqualExpression'],
        ['NotEqualExpression'],
        ['AndExpression'],
        ['OrExpression'],
        ['LessThanExpression'],
        ['LessThanEqualExpression'],
        ['GreaterThanExpression'],
        ['GreaterThanEqualExpression'],
        ['BinaryAndExpression'],
        ['BinaryOrExpression'],
        ['AddExpression'],
        ['SubtractExpression'],
        ['MultiplyExpression'],
        ['DivideExpression'],
        ['ModuloExpression'],

        # Unary expressions.

        ['NegateExpression'],
        ['NotExpression'],
    ],

    # Like Expression, there isn't a Primary node. It directly resolevs to one
    # of these.
    'Primary': [
        ['CreationExpression'],
        ['Literal'],
        ['This'],
        ['Expression'],
        ['FieldAccess'],
        ['MethodInvocation'],
        ['ArrayAccess'],
    ],

    'Literal': [
        ['DecimalIntegerLiteral'],
        # ['FloatingPointLiteral'],
        ['BooleanLiteral'],
        ['CharacterLiteral'],
        ['StringLiteral'],
        ['NullLiteral'],
    ],

    'Assignment': [
        ['Name', 'Expression'],
        ['FieldAccess', 'Expression'],
        ['ArrayAccess', 'Expression'],
    ],

    'MethodInvocation': [
        ['MethodName', 'MethodReceiver', 'Arguments'],
    ],

    'MethodName': [
        ['Identifier'],
    ],

    'MethodReceiver': [
        [],
        ['Name'],
        ['Primary'],
    ],

    'Arguments': [
        ['Expression'], # Zero or more
    ],

    # If Type is ArrayType, then Arguments is for the Array brackets.
    'CreationExpression': [
        ['Type', 'Arguments'],
    ],

    'CastExpression': [
        ['Type', 'Expression'],
    ],

    'InstanceofExpression': [
        ['Expression', 'Type'],
    ],

    'PostfixExpression': [
        ['Primary'],
        ['Name'],
    ],

    'ArrayAccess': [
        ['ArrayReceiver', 'Expression'],
    ],

    'ArrayReceiver': [
        ['Name'],
        ['Primary'],
    ],

    'FieldAccess': [
        ['FieldName', 'FieldReceiver'],
    ],

    'FieldName': [
        ['Identifier'],
    ],

    'FieldReceiver': [
        ['Primary'],
        # ['Super'],
    ],

    # Binary expressions.

    'EqualExpression': [
        ['Expression', 'Expression'],
    ],

    'NotEqualExpression': [
        ['Expression', 'Expression'],
    ],

    'OrExpression': [
        ['Expression', 'Expression'],
    ],

    'AndExpression': [
        ['Expression', 'Expression'],
    ],

    'LessThanExpression': [
        ['Expression', 'Expression'],
    ],

    'LessThanEqualExpression': [
        ['Expression', 'Expression'],
    ],

    'GreaterThanExpression': [
        ['Expression', 'Expression'],
    ],

    'GreaterThanEqualExpression': [
        ['Expression', 'Expression'],
    ],

    'BinaryAndExpression': [
        ['Expression', 'Expression'],
    ],

    'BinaryOrExpression': [
        ['Expression', 'Expression'],
    ],

    'AddExpression': [
        ['Expression', 'Expression'],
    ],

    'SubtractExpression': [
        ['Expression', 'Expression'],
    ],

    'MultiplyExpression': [
        ['Expression', 'Expression'],
    ],

    'DivideExpression': [
        ['Expression', 'Expression'],
    ],

    'ModuloExpression': [
        ['Expression', 'Expression'],
    ],

}

