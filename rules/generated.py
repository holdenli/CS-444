# Modified Java 1.0 grammar.
# Base grammar taken from:
# http://titanium.cs.berkeley.edu/doc/java-langspec-1.0/19.doc.html

START_SYMBOL = 'Goal'

RULES = {
    'Goal': [
        ['BOF', 'EOF'],
        ['BOF', 'CompilationUnit', 'EOF'],
    ],

    'Literal': [
        ['DecimalIntegerLiteral'],
        # ['FloatingPointLiteral'],
        ['BooleanLiteral'],
        ['CharacterLiteral'],
        ['StringLiteral'],
        ['NullLiteral'],
    ],

    'Type': [
        ['PrimitiveType'],
        ['ReferenceType'],
    ],

    'PrimitiveType': [
        ['NumericType'],
        ['Boolean'],
    ],

    'NumericType': [
        ['IntegralType'],
        # ['FloatingPointType'],
    ],

    'IntegralType': [
        ['Byte'],
        ['Short'],
        ['Int'],
        # ['Long'],
        ['Char'],
    ],

    # 'FloatingPointType': [
    #     ['Float'],
    #     ['Double'],
    # ],

    'ReferenceType': [
        ['ClassOrInterfaceType'],
        ['ArrayType'],
    ],

    'ClassOrInterfaceType': [
        ['Name'],
    ],

    'ClassType': [
        ['ClassOrInterfaceType'],
    ],

    'InterfaceType': [
        ['ClassOrInterfaceType'],
    ],

    # No multi-dimensional arrays.
    'ArrayType': [
        ['PrimitiveType', 'LeftBracket', 'RightBracket'],
        ['Name', 'LeftBracket', 'RightBracket'],
        # ['ArrayType', 'LeftBracket', 'RightBracket'],
    ],

    'Name': [
        ['SimpleName'],
        ['QualifiedName'],
    ],

    'SimpleName': [
        ['Identifier'],
    ],

    'QualifiedName': [
        ['Name', 'Dot', 'Identifier'],
    ],

    'CompilationUnit': [
        ['PackageDeclaration'],
        ['ImportDeclarations'],
        ['TypeDeclarations'],
        ['PackageDeclaration ImportDeclarations'],
        ['PackageDeclaration TypeDeclarations'],
        ['ImportDeclarations TypeDeclarations'],
        ['PackageDeclaration ImportDeclarations TypeDeclarations'],
    ],

    'ImportDeclarations': [
        ['ImportDeclaration'],
        ['ImportDeclarations ImportDeclaration'],
    ],

    # Only one type per file in Joos.
    'TypeDeclarations': [
        ['TypeDeclaration'],
        # ['TypeDeclarations', 'TypeDeclaration']
    ],

    'PackageDeclaration': [
        ['Package', 'Name', 'SemiColon'],
    ],

    'ImportDeclaration': [
        ['SingleTypeImportDeclaration'],
        ['TypeImportOnDemandDeclaration'],
    ],

    'SingleTypeImportDeclaration': [
        ['Import', 'Name', 'SemiColon'],
    ],

    'TypeImportOnDemandDeclaration': [
        ['Import', 'Name', 'Dot', 'MultiplyOperator', 'SemiColon'],
    ],

    'TypeDeclaration': [
        ['ClassDeclaration'],
        ['InterfaceDeclaration'],
        ['SemiColon'],
    ],

    'Modifiers': [
        ['Modifier'],
        ['Modifiers', 'Modifier'],
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
    ],

    # No package private => must have at least 1 modifier.
    'ClassDeclaration': [
        # ['Class Identifier SuperStuff Interfaces ClassBody'],
        # ['Class Identifier Interfaces ClassBody'],
        # ['Class Identifier SuperStuff ClassBody'],
        # ['Class Identifier ClassBody'],
        ['Modifiers', 'Class', 'Identifier', 'SuperStuff', 'Interfaces', 'ClassBody'],
        ['Modifiers', 'Class', 'Identifier', 'Interfaces', 'ClassBody'],
        ['Modifiers', 'Class', 'Identifier', 'SuperStuff', 'ClassBody'],
        ['Modifiers', 'Class', 'Identifier', 'ClassBody'],
    ],

    'SuperStuff': [
        ['Extends ClassType'],
    ],

    'Interfaces': [
        ['Implements', 'InterfaceTypeList'],
    ],

    'InterfaceTypeList': [
        ['InterfaceType'],
        ['InterfaceTypeList', 'Comma', 'InterfaceType'],
    ],

    # No omitted constructor => must have ClassBodyDeclarations.
    'ClassBody': [
        # ['LeftBrace', 'RightBrace'],
        ['LeftBrace', 'ClassBodyDeclarations', 'RightBrace'],
    ],

    'ClassBodyDeclarations': [
        ['ClassBodyDeclaration'],
        ['ClassBodyDeclarations', 'ClassBodyDeclaration'],
    ],

    'ClassBodyDeclaration': [
        ['ClassMemberDeclaration'],
        # ['StaticInitializer'],
        ['ConstructorDeclaration'],
    ],

    'ClassMemberDeclaration': [
        ['FieldDeclaration'],
        ['MethodDeclaration'],
    ],

    'FieldDeclaration': [
        ['Modifiers', 'Type', 'VariableDeclarators', 'SemiColon'],
        #    ['Type VariableDeclarators SemiColon'],
    ],

    # No multiple-declarations in Joos.
    'VariableDeclarators': [
        ['VariableDeclarator'],
        # ['VariableDeclarators', 'Comma', 'VariableDeclarator'],
    ],

    'VariableDeclarator': [
        ['VariableDeclaratorId'],
        ['VariableDeclaratorId', 'DirectAssignmentOperator', 
            'VariableInitializer'],
    ],

    # No multi-dimensional arrays.
    # No array declaration after variable name.
    'VariableDeclaratorId': [
        ['Identifier'],
        # ['VariableDeclaratorId', 'LeftBracket', 'RightBracket'],
        # ['Identifier', 'LeftBracket', 'RightBracket'],
    ],

    'VariableInitializer': [
        ['Expression'],
        # ['ArrayInitializer'],
    ],

    'MethodDeclaration': [
        ['MethodHeader', 'MethodBody'],
    ],

    # Methods cannot be package private - there must be a modifier.
    'MethodHeader': [
        # ['Modifiers Type MethodDeclarator ThrowsStuff'],
        ['Modifiers', 'Type', 'MethodDeclarator'],
        # ['Type MethodDeclarator ThrowsStuff'],
        # ['Type MethodDeclarator'],
        # ['Modifiers Void MethodDeclarator ThrowsStuff'],
        ['Modifiers', 'Void', 'MethodDeclarator'],
        # ['Void MethodDeclarator ThrowsStuff'],
        # ['Void MethodDeclarator'],
    ],

    # No array return type after method signature.
    'MethodDeclarator': [
        ['Identifier', 'LeftParenthesis', 'FormalParameterList',
            'RightParenthesis'],
        ['Identifier', 'LeftParenthesis', 'RightParenthesis'],
        # ['MethodDeclarator', 'LeftBracket', 'RightBracket'],
    ],

    'FormalParameterList': [
        ['FormalParameter'],
        ['FormalParameterList', 'Comma', 'FormalParameter'],
    ],

    'FormalParameter': [
        ['Type', 'VariableDeclaratorId'],
    ],

    # No Throws.
    # 'ThrowsStuff': [
    #     ['Throws', 'ClassTypeList'],
    # ],

    # Unused, only used by ThrowsStuff.
    # 'ClassTypeList': [
    #     ['ClassType'],
    #     ['ClassTypeList', 'Comma', 'ClassType'],
    # ],

    'MethodBody': [
        ['Block'],
        ['SemiColon'],
    ],

    # No static initializers. 
    # 'StaticInitializer': [
    #     ['Static', 'Block'],
    # ],

    # No package private, and no throws.
    'ConstructorDeclaration': [
        # ['Modifiers ConstructorDeclarator ThrowsStuff ConstructorBody'],
        ['Modifiers', 'ConstructorDeclarator', 'ConstructorBody'],
        # ['ConstructorDeclarator ThrowsStuff ConstructorBody'],
        # ['ConstructorDeclarator ConstructorBody'],
    ],

    'ConstructorDeclarator': [
        ['SimpleName', 'LeftParenthesis', 'FormalParameterList',
            'RightParenthesis'],
        ['SimpleName', 'LeftParenthesis', 'RightParenthesis'],
    ],

    'ConstructorBody': [
        #   ['LeftBrace ExplicitConstructorInvocation BlockStatement RightBrace'],
        #   ['LeftBrace ExplicitConstructorInvocation RightBrace'],
        ['LeftBrace', 'BlockStatements', 'RightBrace'],
        ['LeftBrace', 'RightBrace'],
    ],

    # No this() or super() calls.
    #ExplicitConstructorInvocation:
    #    ['This LeftParenthesis ArgumentList RightParenthesis SemiColon'],
    #    ['This LeftParenthesis RightParenthesis SemiColon'],
    #    ['Super LeftParenthesis ArgumentList RightParenthesis SemiColon'],
    #    ['Super LeftParenthesis RightParenthesis SemiColon'],

    'InterfaceDeclaration': [
        ['Modifiers', 'Interface', 'Identifier', 'ExtendsInterfaces',
            'InterfaceBody'],
        ['Modifiers', 'Interface', 'Identifier', 'InterfaceBody'],
        # ['Interface', 'Identifier', 'ExtendsInterfaces', 'InterfaceBody'],
        # ['Interface', 'Identifier', 'InterfaceBody'],
    ],

    'ExtendsInterfaces': [
        ['Extends', 'InterfaceType'],
        ['ExtendsInterfaces', 'Comma', 'InterfaceType'],
    ],

    'InterfaceBody': [
        ['LeftBrace', 'InterfaceMemberDeclarations', 'RightBrace'],
        ['LeftBrace', 'RightBrace'],
    ],

    'InterfaceMemberDeclarations': [
        ['InterfaceMemberDeclaration'],
        ['InterfaceMemberDeclarations', 'InterfaceMemberDeclaration'],
    ],

    'InterfaceMemberDeclaration': [
        #    ['ConstantDeclaration'],
        #    ['AbstractMethodDeclaration'],
        ['MethodHeader', 'SemiColon'],
    ],

    #ConstantDeclaration:
    #    ['FieldDeclaration'],

    #AbstractMethodDeclaration:
    #    ['MethodHeader SemiColon'],

    # No array data.
    # 'ArrayInitializer': [
    #     ['LeftBrace', 'VariableInitializers', 'Comma', 'RightBrace'],
    #     ['LeftBrace', 'VariableInitializers', 'RightBrace'],
    #     ['LeftBrace', 'Comma', 'RightBrace'],
    #     ['LeftBrace', 'RightBrace'],
    # ],

    'VariableInitializers': [
        ['VariableInitializer'],
        ['VariableInitializers', 'Comma', 'VariableInitializer'],
    ],

    'Block': [
        ['LeftBrace', 'BlockStatements', 'RightBrace'],
        ['LeftBrace', 'RightBrace'],
    ],

    'BlockStatements': [
        ['BlockStatement'],
        ['BlockStatements', 'BlockStatement'],
    ],

    'BlockStatement': [
        ['LocalVariableDeclarationStatement'],
        ['Statement'],
    ],

    'LocalVariableDeclarationStatement': [
        ['LocalVariableDeclaration SemiColon'],
    ],

    'LocalVariableDeclaration': [
        ['Type', 'VariableDeclarators'],
    ],

    # No labelled statements.
    'Statement': [
        ['StatementWithoutTrailingSubstatement'],
        # ['LabeledStatement'],
        ['IfThenStatement'],
        ['IfThenElseStatement'],
        ['WhileStatement'],
        ['ForStatement'],
    ],

    # No labelled statements.
    'StatementNoShortIf': [
        ['StatementWithoutTrailingSubstatement'],
        # ['LabeledStatementNoShortIf'],
        ['IfThenElseStatementNoShortIf'],
        ['WhileStatementNoShortIf'],
        ['ForStatementNoShortIf'],
    ],

    'StatementWithoutTrailingSubstatement': [
        ['Block'],
        ['EmptyStatement'],
        ['ExpressionStatement'],
        #    ['SwitchStatement'],
        #    ['DoStatement'],
        #    ['BreakStatement'],
        #    ['ContinueStatement'],
        ['ReturnStatement'],
        #    ['SynchronizedStatement'],
        #    ['ThrowStatement'],
        #    ['TryStatement'],
    ],

    'EmptyStatement': [
        ['SemiColon'],
    ],

    # 'LabeledStatement': [
    #     ['Identifier', 'ColonOperator', 'Statement'],
    # ],

    # 'LabeledStatementNoShortIf': [
    #     ['Identifier', 'ColonOperator', 'StatementNoShortIf'],
    # ],

    'ExpressionStatement': [
        ['StatementExpression', 'SemiColon'],
    ],

    'StatementExpression': [
        ['Assignment'],
        ['MethodInvocation'],
        ['ClassInstanceCreationExpression'],
    ],

    'IfThenStatement': [
        ['If', 'LeftParenthesis', 'Expression', 'RightParenthesis',
            'Statement'],
    ],

    'IfThenElseStatement': [
        ['If', 'LeftParenthesis', 'Expression', 'RightParenthesis',
            'StatementNoShortIf', 'Else', 'Statement'],
    ],

    'IfThenElseStatementNoShortIf': [
        ['If', 'LeftParenthesis', 'Expression', 'RightParenthesis',
            'StatementNoShortIf', 'Else', 'StatementNoShortIf'],
    ],

    #SwitchStatement:
    #    ['Switch LeftParenthesis Expression RightParenthesis SwitchBlock'],

    #SwitchBlock:
    #    ['LeftBrace SwitchBlockStatementGroups SwitchLabels RightBrace'],
    #    ['LeftBrace SwitchBlockStatementGroups RightBrace'],
    #    ['LeftBrace SwitchLabels RightBrace'],
    #    ['LeftBrace RightBrace'],

    #SwitchBlockStatementGroups:
    #    ['SwitchBlockStatementGroup'],
    #    ['SwitchBlockStatementGroups SwitchBlockStatementGroup'],

    #SwitchBlockStatementGroup:
    #    ['SwitchLabels BlockStatements'],

    #SwitchLabels:
    #    ['SwitchLabel'],
    #    ['SwitchLabels SwitchLabel'],

    #SwitchLabel:
    #    ['Case ConstantExpression ColonOperator'],
    #    ['Default ColonOperator'],

    'WhileStatement': [
        ['While', 'LeftParenthesis', 'Expression', 'RightParenthesis',
            'Statement'],
    ],

    'WhileStatementNoShortIf': [
        ['While', 'LeftParenthesis', 'Expression', 'RightParenthesis',
            'StatementNoShortIf'],
    ],

    #DoStatement:
    #    ['Do Statement While LeftParenthesis Expression RightParenthesis SemiColon'],
    
    'ForStatement': [
        ['For', 'LeftParenthesis', 'SemiColon', 'SemiColon',
            'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'SemiColon', 
            'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'SemiColon', 'Expression', 'SemiColon',
            'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'SemiColon', 'SemiColon', 'ForUpdate',
            'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'Expression',
            'SemiColon', 'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'SemiColon',
            'ForUpdate', 'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'SemiColon', 'Expression', 'SemiColon',
            'ForUpdate', 'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'Expression',
            'SemiColon', 'ForUpdate', 'RightParenthesis', 'Statement'],
    ],

    'ForStatementNoShortIf': [
        ['For', 'LeftParenthesis', 'SemiColon', 'SemiColon', 'RightParenthesis',
            'StatementNoShortIf'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'SemiColon',
            'RightParenthesis', 'StatementNoShortIf'],
        ['For', 'LeftParenthesis', 'SemiColon', 'Expression', 'SemiColon',
            'RightParenthesis', 'StatementNoShortIf'],
        ['For', 'LeftParenthesis', 'SemiColon', 'SemiColon', 'ForUpdate',
            'RightParenthesis', 'StatementNoShortIf'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'Expression',
            'SemiColon', 'RightParenthesis', 'StatementNoShortIf'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'SemiColon',
            'ForUpdate', 'RightParenthesis', 'StatementNoShortIf'],
        ['For', 'LeftParenthesis', 'SemiColon', 'Expression', 'SemiColon',
            'ForUpdate', 'RightParenthesis', 'StatementNoShortIf'],
        ['For', 'LeftParenthesis', 'ForInit', 'SemiColon', 'Expression',
            'SemiColon', 'ForUpdate', 'RightParenthesis', 'StatementNoShortIf'],
    ],

    'ForInit': [
        ['StatementExpressionList'],
        ['LocalVariableDeclaration'],
    ],

    'ForUpdate': [
        ['StatementExpressionList'],
    ],

    # No "general for" statements in Joos.
    'StatementExpressionList': [
        ['StatementExpression'],
        # ['StatementExpressionList', 'Comma', 'StatementExpression'],
    ],

    'ReturnStatement': [
        ['Return', 'SemiColon'],
        ['Return', 'Expression', 'SemiColon'],
    ],

    #BreakStatement:
    #    ['Break Identifieropt SemiColon'],

    #ContinueStatement:
    #    ['Continue Identifieropt SemiColon'],

    #ThrowStatement:
    #    ['Throw Expression SemiColon'],

    #SynchronizedStatement:
    #    ['Synchronized LeftParenthesis Expression RightParenthesis Block'],

    #TryStatement:
    #    ['Try Block Catches'],
    #    ['Try Block Catchesopt FinallyStuff'],

    #Catches:
    #    ['CatchClause'],
    #    ['Catches CatchClause'],

    #CatchClause:
    #    ['Catch LeftParenthesis FormalParameter RightParenthesis Block'],

    #FinallyStuff:
    #    ['Finally Block'],

    'Primary': [
        ['PrimaryNoNewArray'],
        ['ArrayCreationExpression'],
    ],

    'PrimaryNoNewArray': [
        ['Literal'],
        ['This'],
        ['LeftParenthesis', 'Expression', 'RightParenthesis'],
        ['ClassInstanceCreationExpression'],
        ['FieldAccess'],
        ['MethodInvocation'],
        ['ArrayAccess'],
    ],

    'ClassInstanceCreationExpression': [
        ['New', 'ClassType', 'LeftParenthesis', 'RightParenthesis'],
        ['New', 'ClassType', 'LeftParenthesis', 'ArgumentList',
            'RightParenthesis'],
    ],

    'ArgumentList': [
        ['Expression'],
        ['ArgumentList', 'Comma', 'Expression'],
    ],

    # A few changes are made here so that only single-dimension arrays work.
    'ArrayCreationExpression': [
        ['New', 'PrimitiveType', 'DimExprs'],
        # ['New', 'PrimitiveType', 'DimExprs', 'Dims'],
        ['New', 'ClassOrInterfaceType', 'DimExprs'],
        # ['New', 'ClassOrInterfaceType', 'DimExprs', 'Dims'],
        ['New', 'PrimitiveType', 'Dims'],
        ['New', 'ClassOrInterfaceType', 'Dims'],
    ],

    'DimExprs': [
        ['DimExpr'],
        # ['DimExprs DimExpr'],
    ],

    'DimExpr': [
        ['LeftBracket', 'Expression', 'RightBracket'],
    ],

    # Only one dimension allowed.
    'Dims': [
        ['LeftBracket', 'RightBracket'],
        # ['Dims', 'LeftBracket', 'RightBracket'],
    ],

    'FieldAccess': [
        ['Primary', 'Dot', 'Identifier'],
        ['Super', 'Dot', 'Identifier'],
    ],

    # No super method calls in Joos.
    'MethodInvocation': [
        ['Name', 'LeftParenthesis', 'RightParenthesis'],
        ['Primary', 'Dot', 'Identifier', 'LeftParenthesis', 'RightParenthesis'],
        # ['Super', 'Dot', 'Identifier', 'LeftParenthesis', 'RightParenthesis'],
        ['Name', 'LeftParenthesis', 'ArgumentList', 'RightParenthesis'],
        ['Primary', 'Dot', 'Identifier', 'LeftParenthesis', 'ArgumentList',
            'RightParenthesis'],
        # ['Super', 'Dot', 'Identifier', 'LeftParenthesis', 'ArgumentList',
        #     'RightParenthesis'],
    ],

    'ArrayAccess': [
        ['Name', 'LeftBracket', 'Expression', 'RightBracket'],
        ['PrimaryNoNewArray', 'LeftBracket', 'Expression', 'RightBracket'],
    ],

    'PostfixExpression': [
        ['Primary'],
        ['Name'],
    ],

    # No unary + in Joos.
    'UnaryExpression': [
        # ['AddOperator', 'UnaryExpression'],
        ['SubtractOperator', 'UnaryExpression'],
        ['UnaryExpressionNotPlusMinus'],
    ],

    # No binary not ~ in Joos.
    'UnaryExpressionNotPlusMinus': [
        ['PostfixExpression'],
        # ['BinaryNotOperator', 'UnaryExpression'],
        ['NotOperator', 'UnaryExpression'],
        ['CastExpression'],
    ],

    'CastExpression': [
        ['LeftParenthesis', 'PrimitiveType', 'RightParenthesis',
            'UnaryExpression'],
        ['LeftParenthesis', 'PrimitiveType', 'Dims', 'RightParenthesis',
            'UnaryExpression'],
        ['LeftParenthesis', 'Expression', 'RightParenthesis',
            'UnaryExpressionNotPlusMinus'],
        ['LeftParenthesis', 'Name', 'Dims', 'RightParenthesis', 
            'UnaryExpressionNotPlusMinus'],
    ],

    'MultiplicativeExpression': [
        ['UnaryExpression'],
        ['MultiplicativeExpression', 'MultiplyOperator', 'UnaryExpression'],
        ['MultiplicativeExpression', 'DivideOperator', 'UnaryExpression'],
        ['MultiplicativeExpression', 'ModuloOperator', 'UnaryExpression'],
    ],

    'AdditiveExpression': [
        ['MultiplicativeExpression'],
        ['AdditiveExpression', 'AddOperator', 'MultiplicativeExpression'],
        ['AdditiveExpression', 'SubtractOperator', 'MultiplicativeExpression'],
    ],

    # No shift operators in Joos.
    'ShiftExpression': [
        ['AdditiveExpression'],
        # ['ShiftExpression', 'LeftShiftOperator', 'AdditiveExpression'],
        # ['ShiftExpression', 'RightShiftOperator', 'AdditiveExpression'],
    ],

    'RelationalExpression': [
        ['ShiftExpression'],
        ['RelationalExpression', 'LessThanOperator', 'ShiftExpression'],
        ['RelationalExpression', 'GreaterThanOperator', 'ShiftExpression'],
        ['RelationalExpression', 'LessThanEqualOperator', 'ShiftExpression'],
        ['RelationalExpression', 'GreaterThanEqualOperator', 'ShiftExpression'],
        ['RelationalExpression', 'Instanceof', 'ReferenceType'],
    ],

    'EqualityExpression': [
        ['RelationalExpression'],
        ['EqualityExpression', 'EqualOperator', 'RelationalExpression'],
        ['EqualityExpression', 'NotEqualOperator', 'RelationalExpression'],
    ],

    'AndExpression': [
        ['EqualityExpression'],
        # ['AndExpression', 'BinaryAndOperator', 'EqualityExpression'],
    ],

    'ExclusiveOrExpression': [
        ['AndExpression'],
        # ['ExclusiveOrExpression', 'InverseOperator', 'AndExpression'],
    ],

    'InclusiveOrExpression': [
        ['ExclusiveOrExpression'],
        # ['InclusiveOrExpression', 'BinaryOrOperator', 'ExclusiveOrExpression'],
    ],

    'ConditionalAndExpression': [
        ['InclusiveOrExpression'],
        ['ConditionalAndExpression', 'AndOperator', 'InclusiveOrExpression'],
    ],

    'ConditionalOrExpression': [
        ['ConditionalAndExpression'],
        ['ConditionalOrExpression', 'OrOperator', 'ConditionalAndExpression'],
    ],

    'ConditionalExpression': [
        ['ConditionalOrExpression'],
    ],

    'AssignmentExpression': [
        ['ConditionalExpression'],
        ['Assignment'],
    ],

    'Assignment': [
        ['LeftHandSide', 'AssignmentOperator', 'AssignmentExpression'],
    ],

    'LeftHandSide': [
        ['Name'],
        ['FieldAccess'],
        ['ArrayAccess'],
    ],

    'AssignmentOperator': [
        ['DirectAssignmentOperator'],
    ],

    'Expression': [
        ['AssignmentExpression'],
    ],

    'ConstantExpression': [
        ['Expression'],
    ],
}

