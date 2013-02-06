# Compacted List of CFG rules for Joos.
# Rules are modified to use left recursion.

START_SYMBOL = 'START'
RULES = {
    # Starting rule.
    'START': [
        ['BOF', 'CompilationUnit', 'EOF'],
    ],

    # Identifier token. Not currently used.
    # 'Identifier': [
    #     ['IDENTIFIER'[,
    # ],

    'QualifiedIdentifier': [
        ['Identifier'],
        ['QualifiedIdentifier', 'Dot', 'Identifier'],
    ], 

    'Literal': [
        ['IntegerLiteral'],
        # ['FloatingPointLiteral'], 
        ['CharacterLiteral'],
        ['StringLiteral'],
        ['BooleanLiteral'],
        ['NullLiteral'],
    ],

    # Copied from extended rules.
    'IntegerLiteral': [
        ['DecimalIntegerLiteral'],
        # ['HexIntegerLiteral'],
        # ['OctalIntegerLiteral'],
    ],

    'Expression': [
        ['Expression1'],
        ['Expression1', 'AssignmentOperator', 'Expression1'],
    ],

    'AssignmentOperator': [
        ['DirectAssignmentOperator'],
        # ['AddAssignmentOperator'],
        # ['SubtractAssignmentOperator'],
        # ['MultiplyAssignmentOperator'],
        # ['DivideAssignmentOperator'],
        # ['BinaryAndAssignmentOperator'],
        # ['BinaryOrAssignmentOperator'],
        # ['InverseAssignmentOperator'],
        # ['ModuloAssignmentOperator'],
        # ['LeftShiftAssignmentOperator'],
        # ['RightShiftAssignmentOperator'],
        # ['UnsignedRightShiftAssignmentOperator'],
    ],

    'Type': [
        ['QualifiedIdentifier', 'BracketsOpt'], # Hack
        ['BasicType'],
    ],

    'StatementExpression': [
        ['Expression'],
    ],

    'ConstantExpression': [
        ['Expression'],
    ],

    'Expression1': [
        ['Expression2'],
        # ['Expression2', 'Expression1Rest'],
    ],

    # 'Expression1Rest': [
    #     [],
    #     ['QuestionOperator', 'Expression', 'ColonOperator', 'Expression1'], 
    # ],

    'Expression2': [
        ['Expression3'],
        ['Expression3', 'Expression2Rest'],
    ],

    'Expression2Rest': [
        [],
        ['Expression2Follow'], # Hack.
        ['Expression3', 'Instanceof', 'Type'],
    ],

    # Hack.
    'Expression2Follow': [
        ['Infixop', 'Expression3'],
        ['Expression2Follow', 'Infixop', 'Expression3'],
    ],

    'Infixop': [
        ['OrOperator'],
        ['AndOperator'],
        # ['BinaryOrOperator'],
        # ['InverseOperator'], 
        # ['BinaryAndOperator'],
        ['EqualOperator'],
        ['NotEqualOperator'],
        ['LessThanOperator'], 
        ['GreaterThanOperator'],
        ['LessThanEqualOperator'],
        ['GreaterThanEqualOperator'], 
        # ['LeftShiftOperator'],
        # ['RightShiftOperator'], 
        # ['UnsignedRightShiftOperator'],
        ['AddOperator'],
        ['SubtractOperator'],
        ['MultiplyOperator'],
        ['DivideOperator'],
        ['ModuloOperator'],
    ],

    'Expression3': [
        ['PrefixOp', 'Expression3'],
        ['LeftParenthesis', 'Expression', 'RightParenthesis', 'Expression3'],
        ['LeftParenthesis', 'Type', 'RightParenthesis', 'Expression3'],
        # ['Primary'],
        ['Primary', 'Selectors'],
        # ['Primary', 'PostfixOps'],
        # ['Primary', 'Selectors', 'PostfixOps'],
    ],

    # Hack.
    # 'PostfixOps': [
    #     ['PostfixOp'],
    #     ['PostfixOps', 'PostfixOp'],
    # ],

    # Hack.
    'Selectors': [
        # ['Selector'],
        [],
        ['Selectors', 'Selector'],
    ],

    'Primary': [
        ['LeftParenthesis', 'Expression', 'RightParenthesis'],
        ['This'],
        # ['This', 'Arguments'],
        # ['Super', 'SuperSuffix'],
        ['Literal'],
        ['New', 'Creator'],
        ['QualifiedIdentifier'], # Hack.
        ['QualifiedIdentifier', 'IdentifierSuffix'], # Hack.
        # ['BasicType', 'BracketsOpt', 'Dot', 'Class'],
        # ['Void', 'Dot', 'Class'],
    ],

    'IdentifierSuffix': [
        # ['LeftBracket', 'RightBracket', 'BracketsOpt', 'Dot', 'Class'],
        # ['LeftBracket', 'Expression', 'RightBracket'],
        ['Arguments'],
        # ['Dot', 'Class'],
        # ['Dot', 'This'],
        # ['Dot', 'Super', 'Arguments'],
        ['Dot', 'New', 'InnerCreator'],
    ],

    'PrefixOp': [
        # ['IncrementOperator'], 
        # ['DecrementOperator'],
        ['NotOperator'],
        # ['BinaryNotOperator'],
        # ['AddOperator'],
        ['SubtractOperator'],
    ],

    # 'PostfixOp': [
    #     ['IncrementOperator'],
    #     ['DecrementOperator'],
    # ],

    'Selector': [
        ['Dot', 'Identifier'],
        ['Dot', 'Identifier', 'Arguments'],
        # ['Dot', 'This'],
        # ['Dot', 'Super', 'SuperSuffix'],
        ['Dot', 'New', 'InnerCreator'],
        ['LeftBracket', 'Expression', 'RightBracket'],
    ],

    # 'SuperSuffix': [
    #     ['Arguments'],
    #     ['Dot', 'Identifier'],
    #     ['Dot', 'Identifier', 'Arguments'],
    # ],

    'BasicType': [
        ['Byte'],
        ['Short'],
        ['Char'],
        ['Int'],
        # ['Long'],
        # ['Float'],
        # ['Double'],
        ['Boolean'],
    ],

    'ArgumentsOpt': [
        [],
        ['Arguments'],
    ],

    'Arguments': [
        ['LeftParenthesis', 'RightParenthesis'],
        ['LeftParenthesis', 'ArgumentSubexpressions', 'RightParenthesis'],
    ],

    # Hack.
    'ArgumentSubexpressions': [
        ['Expression'],
        ['ArgumentSubexpressions', 'Comma', 'Expression'],
    ],

    'BracketsOpt': [
        [],
        ['BracketsOpt', 'LeftBracket', 'RightBracket'],
    ],

    'Creator': [
        ['QualifiedIdentifier', 'ArrayCreatorRest'],
        ['QualifiedIdentifier', 'ClassCreatorRest'],
    ],

    'InnerCreator': [
        ['Identifier', 'ClassCreatorRest'],
    ],

    'ArrayCreatorRest': [
        # ['LeftBracket', 'RightBracket', 'BracketsOpt', 'ArrayInitializer'],
        # ['LeftBracket', 'Expression', 'RightBracket',
        #     'BracketedExpressionsOpt', 'BracketsOpt'],
        ['LeftBracket', 'Expression', 'RightBracket',
            'BracketedExpressionsOpt'], # No multi-dim arrays in Joos.
    ],

    # Hack.
    'BracketedExpressionsOpt': [
        [],
        ['BracketedExpressionsOpt', 'LeftBracket', 'Expression',
            'RightBracket'],
    ],

    'ClassCreatorRest': [
        ['Arguments'],
        ['Arguments', 'ClassBody'],
    ],

    'ArrayInitializer': [
        ['LeftBrace', 'RightBrace'],
        ['LeftBrace', 'VariableInitializers', 'RightBrace'],
        ['LeftBrace', 'VariableInitializers', 'Comma', 'RightBrace'],
    ],

    # Hack.
    'VariableInitializers': [
        ['VariableInitializer'],
        ['VariableInitializers', 'Comma', 'VariableInitializer'],
    ],

    'VariableInitializer': [
        ['ArrayInitializer'],
        ['Expression'],
    ],

    'ParExpression': [
        ['LeftParenthesis', 'Expression', 'RightParenthesis'],
    ],

    'Block': [
        ['LeftBrace', 'BlockStatements', 'RightBrace'],
    ],

    'BlockStatements': [
        [],
        ['BlockStatements', 'BlockStatement'],
    ],

    'BlockStatement': [
        ['LocalVariableDeclarationStatement'],
        ['ClassOrInterfaceDeclaration'],
        ['Identifier', 'ColonOperator', 'Statement'],
        ['Statement'],
    ],

    'LocalVariableDeclarationStatement': [
        ['Type', 'VariableDeclarators', 'SemiColon'],
        # ['Final', 'Type', 'VariableDeclarators', 'SemiColon'],
    ],

    'Statement': [
        ['Block'],
        ['If', 'ParExpression', 'Statement'],
        ['If', 'ParExpression', 'Statement', 'Else', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInitOpt', 'SemiColon', 'SemiColon',
            'ForUpdateOpt', 'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInitOpt', 'SemiColon', 'Expression',
            'SemiColon', 'ForUpdateOpt', 'RightParenthesis', 'Statement'],
        ['While', 'ParExpression', 'Statement'],
        # ['Do', 'Statement', 'While', 'ParExpression', 'SemiColon'],
        # ['Try', 'Block', 'Catches'],
        # ['Try', 'Block', 'Finally', 'Block'],
        # ['Try', 'Block', 'Catches', 'Finally', 'Block'],
        # ['Switch', 'ParExpression', 'LeftParenthesis',
        #     'SwitchBlockStatementGroups', 'RightParenthesis'],
        # ['Synchronized', 'ParExpression', 'Block'],
        ['Return', 'SemiColon'],
        ['Return', 'Expression', 'SemiColon'],
        # ['Throw', 'Expression', 'SemiColon'],
        # ['Break'],
        # ['Break', 'Identifier'],
        # ['Continue'],
        # ['Continue', 'Identifier'],
        ['SemiColon'],
        ['StatementExpression'], # Typo in Spec? ['ExpressionStatement'],
        # ['Identifier', 'ColonOperator', 'Statement'],
    ],

    # 'Catches': [
    #     ['CatchClause'],
    #     ['Catches', 'CatchClause'],
    # ],

    # 'CatchClause': [
    #     ['Catch', 'LeftParenthesis', 'FormalParameter', 'RightParenthesis',
    #         'Block'],
    # ],

    'SwitchBlockStatementGroups': [
        [],
        ['SwitchBlockStatementGroups', 'SwitchBlockStatementGroups'],
    ],

    'SwitchBlockStatementGroup': [
        ['SwitchLabel', 'BlockStatements'],
    ],

    'SwitchLabel': [
        ['Case', 'ConstantExpression', 'ColonOperator'],
        ['Default', 'ColonOperator'],
    ],

    'MoreStatementExpressions': [
        [],
        ['MoreStatementExpressions', 'Comma', 'StatementExpression'],
    ],

    # Missing from spec.
    'ForInitOpt': [
        [],
        ['ForInit'],
    ],

    'ForInit': [
        # ['StatementExpression', 'MoreStatementExpressions'],
        ['StatementExpression'],
        ['Type', 'VariableDeclarators'],
        # ['Final', 'Type', 'VariableDeclarators'],
    ],

    # Missing from spec.
    'ForUpdateOpt': [
        [],
        ['ForUpdate'],
    ],

    'ForUpdate': [
        ['StatementExpression'],
        # ['StatementExpression', 'MoreStatementExpressions'],
    ],

    'ModifiersOpt': [
        [],
        ['ModifiersOpt', 'Modifier'],
    ],

    'Modifier': [
        ['Public'],
        ['Protected'],
        # ['Private'],
        ['Static'],
        ['Abstract'],
        ['Final'],
        ['Native'],
        # ['Synchronized'],
        # ['Transient'],
        # ['Volatile'],
        # ['Strictfp'],
    ],

    'VariableDeclarators': [
        ['VariableDeclarator', 'VariableDeclaratorOpt'], # Hack.
    ],

    'VariableDeclaratorsRest': [
        ['VariableDeclaratorRest', 'VariableDeclaratorOpt'], # Hack.
    ],

    # Hack.
    'VariableDeclaratorOpt': [
        [],
        ['VariableDeclaratorOpt', 'Comma', 'VariableDeclarator'],
    ],

    'ConstantDeclaratorsRest': [
        ['ConstantDeclaratorRest', 'ConstantDeclaratorOpt'], # Hack.
    ],

    'ConstantDeclaratorOpt': [
        [],
        ['ConstantDeclaratorOpt', 'Comma', 'ConstantDeclarator'],
    ],

    'VariableDeclarator': [
        ['Identifier', 'VariableDeclaratorRest'],
    ],

    'ConstantDeclarator': [
        ['Identifier', 'ConstantDeclaratorRest'],
    ],

    'VariableDeclaratorRest': [
        ['BracketsOpt'],
        ['BracketsOpt', 'AssignmentOperator', 'VariableInitializer'],
    ],

    'ConstantDeclaratorRest': [
        ['BracketsOpt', 'AssignmentOperator', 'VariableInitializer'],
    ],

    'VariableDeclaratorId': [
        # ['Identifier', 'BracketsOpt'],
        ['Identifier'], # No array declaration after variable name in Joos.
    ],

    'CompilationUnit': [
        ['ImportDeclarations', 'TypeDeclarations'],
        ['Package', 'QualifiedIdentifier', 'SemiColon', 'ImportDeclarations',
            'TypeDeclarations'],
    ],

    # Hack.
    'ImportDeclarations': [
        [],
        ['ImportDeclarations', 'ImportDeclaration'],
    ],

    # Hack.
    'TypeDeclarations': [
        [],
        ['TypeDeclarations', 'TypeDeclaration'],
    ],

    'ImportDeclaration': [
        ['Import', 'QualifiedIdentifier', 'SemiColon'], # Hack
        ['Import', 'QualifiedIdentifier', 'Dot', 'MultiplyOperator',
            'SemiColon'],
    ],

    'TypeDeclaration': [
        ['ClassOrInterfaceDeclaration', 'SemiColon'],
    ],

    'ClassOrInterfaceDeclaration': [
        ['ModifiersOpt', 'ClassDeclaration'],
        ['ModifiersOpt', 'InterfaceDeclaration'],
    ],

    'ClassDeclaration': [
        ['Class', 'Identifier', 'ClassBody'],
        ['Class', 'Identifier', 'Extends', 'Type', 'ClassBody'],
        ['Class', 'Identifier', 'Implements', 'TypeList', 'ClassBody'],
        ['Class', 'Identifier', 'Extends', 'Type', 'Implements', 'TypeList',
            'ClassBody'],
    ],

    'InterfaceDeclaration': [
        ['Interface', 'Identifier', 'InterfaceBody'],
        ['Interface', 'Identifier', 'Extends', 'TypeList', 'InterfaceBody'],
    ],

    'TypeList': [
        ['Type'],
        ['TypeList', 'Comma', 'Type'],
    ],

    'ClassBody': [
        ['LeftBrace', 'ClassBodyDeclarationOpt', 'RightBrace'],
    ],

    # Hack.
    'ClassBodyDeclarationOpt': [
        [],
        ['ClassBodyDeclarationOpt', 'ClassBodyDeclaration'],
    ],

    'InterfaceBody': [
        ['LeftBrace', 'InterfaceBodyDeclarationOpt', 'RightBrace'],
    ],

    # Hack.
    'InterfaceBodyDeclarationOpt': [
        [],
        ['InterfaceBodyDeclarationOpt', 'InterfaceBodyDeclaration'],
    ],

    'ClassBodyDeclaration': [
        ['SemiColon'],
        # ['Block'],
        # ['Static', 'Block'],
        ['ModifiersOpt', 'MemberDecl'],
    ],

    'MemberDecl': [
        ['MethodOrFieldDecl'],
        ['Void', 'Identifier', 'MethodDeclaratorRest'],
        ['Identifier', 'ConstructorDeclaratorRest'],
        # ['ClassOrInterfaceDeclaration'],
    ],

    'MethodOrFieldDecl': [
        ['Type', 'Identifier', 'MethodOrFieldRest'],
    ],

    'MethodOrFieldRest': [
        ['VariableDeclaratorRest'],
        ['MethodDeclaratorRest'],
    ],

    'InterfaceBodyDeclaration': [
        ['SemiColon'],
        ['ModifiersOpt', 'InterfaceMemberDecl'],
    ],

    'InterfaceMemberDecl': [
        ['InterfaceMethodOrFieldDecl'],
        ['Void', 'Identifier', 'VoidInterfaceMethodDeclaratorRest'],
        ['ClassOrInterfaceDeclaration'],
    ],

    'InterfaceMethodOrFieldDecl': [
        ['Type', 'Identifier', 'InterfaceMethodOrFieldRest'],
    ],

    'InterfaceMethodOrFieldRest': [
        ['ConstantDeclaratorsRest', 'SemiColon'],
        ['InterfaceMethodDeclaratorRest'],
    ],

    'MethodDeclaratorRest': [
        ['FormalParameters', 'BracketsOpt', 'MethodBody'],
        # ['FormalParameters', 'BracketsOpt', 'Throws', 'QualifiedIdentifierList',
        #     'MethodBody'],
        ['FormalParameters', 'BracketsOpt', 'SemiColon'],
        # ['FormalParameters', 'BracketsOpt', 'Throws', 'QualifiedIdentifierList',
        #     'SemiColon'],
    ],

    'VoidMethodDeclaratorRest': [
        ['FormalParameters', 'MethodBody'],
        # ['FormalParameters', 'Throws', 'QualifiedIdentifierList', 'MethodBody'],
        ['FormalParameters', 'SemiColon'],
        # ['FormalParameters', 'Throws', 'QualifiedIdentifierList', 'SemiColon'],
    ],

    'InterfaceMethodDeclaratorRest': [
        ['FormalParameters', 'BracketsOpt', 'SemiColon'],
        # ['FormalParameters', 'BracketsOpt', 'Throws',
        #     'QualifiedIdentifierList', 'SemiColon'],
    ],

    'VoidInterfaceMethodDeclaratorRest': [
        ['FormalParameters', 'SemiColon'],
        # ['FormalParameters', 'Throws', 'QualifiedIdentifierList', 'SemiColon'],
    ],

    'ConstructorDeclaratorRest': [
        ['FormalParameters', 'MethodBody'],
        # ['FormalParameters', 'Throws', 'QualifiedIdentifierList',
        #     'MethodBody'],
    ],

    'QualifiedIdentifierList': [
        ['QualifiedIdentifier'],
        ['QualifiedIdentifierList', 'Comma', 'QualifiedIdentifier'],
    ],

    'FormalParameters': [
        ['LeftParenthesis', 'FormalParametersOpt', 'RightParenthesis'],
    ],

    # Hack.
    'FormalParametersOpt': [
        [],
        ['FormalParametersOpt', 'Comma', 'FormalParameter'],
    ],

    'FormalParameter': [
        ['Type', 'VariableDeclaratorId'],
        # ['Final', 'Type', 'VariableDeclaratorId'],
    ],

    'MethodBody': [
        ['Block'],
    ],
}

