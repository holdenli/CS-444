# List of CFG rules for Joos.
# There are two grammars presented in the specification. The first grammar
# presented broken down between the sections of the specifications, and the
# second is found in chapter 18. They are semantically-equivalent; the former
# was used.
#
# Representation:
# Each rule is represented by a key-value-pair [A, B], where A is a
# non-terminal and B is a (possibly empty) list of lists. Each sublist
# is an expansion for A.
# For now, all "opts" are expanded. That means for a given rule with k "opt"
# elements in the expansion, that will correspond to 2^k rules.

START_SYMBOL = 'START'
RULES = {
    # Augmented grammar starting rule.
    'START' : [
        ['BOF', 'CompilationUnit', 'EOF'],
    ],

    # Literals (S3.10)
    'Literal': [
        ['IntegerLiteral'],
        # ['FloatingPointLiteral'],
        ['BooleanLiteral'],
        ['CharacterLiteral'],
        ['StringLiteral'],
        ['NullLiteral'],
    ],
    'IntegerLiteral': [
        ['DecimalIntegerLiteral'],
        # ['HexIntegerLiteral'],
        # ['OctalIntegerLiteral'],
    ],

    # Operators (S3.12)
    'AssignmentOperator': [
        # ['ModuloAssignmentOperator'],
        # ['BinaryAndAssignmentOperator'],
        # ['MultiplyAssignmentOperator'],
        # ['AddAssignmentOperator'],
        # ['SubtractAssignmentOperator'],
        # ['DivideAssignmentOperator'],
        # ['LeftShiftAssignmentOperator'],
        ['DirectAssignmentOperator'],
        # ['RightShiftAssignmentOperator'],
        # ['UnsignedRightShiftAssignmentOperator'],
        # ['InverseAssignmentOperator'],
        # ['BinaryOrAssignmentOperator'],
    ],

    # Types (S4.1)
    'Type': [
        ['PrimitiveType'],
        ['ReferenceType'],
    ],

    # Primitive types (S4.2)
    'PrimitiveType': [
        ['NumericType'],
        ['Boolean'],
    ],
    'NumericType': [
        ['IntegralType'],
    #     ['FloatingPointType'],
    ],
    'IntegralType': [
        ['Byte'],
        ['Short'],
        ['Int'],
        ['Long'],
        ['Char'],
    ],
    # 'FloatingPointType': [
    #     ['Float'],
    #     ['Double'],
    # ],
    
    # Reference types (S4.3)
    'ReferenceType': [
        ['ClassOrInterfaceType'],
        ['ArrayType'],
    ],
    'ClassOrInterfaceType': [
        ['ClassType'],
        ['InterfaceType'],
    ],
    'ClassType': [
        ['TypeName'],
    ],
    'InterfaceType': [
        ['TypeName'],
    ],
    'ArrayType': [
        ['Type', 'LeftBracket', 'RightBracket'],
    ],
   
    # Naming (S6.5)
    'PackageName': [
        ['Identifier'],
        ['PackageName', 'Dot', 'Identifier'],
    ],
    'TypeName': [
        ['Identifier'],
        ['PackageOrTypeName', 'Dot', 'Identifier'],
    ],
    'ExpressionName': [
        ['Identifier'],
        ['AmbiguousName', 'Dot', 'Identifier'],
    ],
    'MethodName': [
        ['Identifier'],
        ['AmbiguousName', 'Dot', 'Identifier'],
    ],
    'PackageOrTypeName': [
        ['Identifier'],
        ['PackageOrTypeName', 'Dot', 'Identifier'],
    ],
    'AmbiguousName': [
        ['Identifier'],
        ['AmbiguousName', 'Dot', 'Identifier'],
    ],
    'SimpleTypeName': [ # Note: Not explicit in spec.
        ['Identifier'],
    ],
    
    # Compilation units (S7.3)
    'CompilationUnit': [
        [],
        ['PackageDeclaration'],
        ['ImportDeclarations'],
        ['TypeDeclarations'],
        ['PackageDeclaration', 'ImportDeclarations'],
        ['PackageDeclaration', 'TypeDeclarations'],
        ['ImportDeclarations', 'TypeDeclarations'],
        ['PackageDeclaration', 'ImportDeclarations', 'TypeDeclarations'],
    ],
    'ImportDeclarations': [
        ['ImportDeclaration'],
        ['ImportDeclarations', 'ImportDeclaration'],
    ],
    'TypeDeclarations': [
        ['TypeDeclaration'],
        ['TypeDeclarations', 'TypeDeclaration'],
    ],

    # Package declarations (S7.4)
    'PackageDeclaration': [
        ['Package', 'PackageName', 'SemiColon'],
    ],

    # Import declarations (S7.5)
    'ImportDeclaration': [
        ['SingleTypeImportDeclaration'],
        ['TypeImportOnDemandDeclaration'],
    ],
    'SingleTypeImportDeclaration': [
        ['Import', 'TypeName', 'SemiColon'],
    ],
    'TypeImportOnDemandDeclaration': [
        ['Import', 'PackageOrTypeName', 'Dot', 'MultiplyOperator',
            'SemiColon'],
    ],
    
    # Top level type declarations (S7.6)
    # TODO: This one's kind of weird. Check this.
    'TypeDeclaration': [
        ['ClassDeclaration'],
        ['InterfaceDeclaration'],
        ['SemiColon'],
    ],

    # Class declaration (S8.1)
    # Note: "Super(Stmt)" is not to be confused with the "Super" token.
    'ClassDeclaration': [
        ['Class', 'Identifier', 'ClassBody'],
        ['ClassModifiers', 'Class', 'Identifier', 'ClassBody'],
        # ['Class', 'Identifier', 'Super(Stmt)', 'ClassBody'],
        ['Class', 'Identifier', 'Interfaces', 'ClassBody'],
        # ['ClassModifiers', 'Class', 'Identifier', 'Super(Stmt)', 'ClassBody'],
        ['ClassModifiers', 'Class', 'Identifier', 'Interfaces', 'ClassBody'],
        # ['Class', 'Identifier', 'Super', 'Interfaces',  'ClassBody'],
        # ['ClassModifiers', 'Class', 'Identifier', 'Super(Stmt)', 'Interfaces',
        #     'ClassBody'],
    ],
    'ClassModifiers': [
        ['ClassModifier'],
        ['ClassModifiers', 'ClassModifier'],
    ],
    'ClassModifier': [
        ['Public'],
        ['Protected'],
        # ['Private'],
        ['Abstract'],
        ['Static'],
        # ['Final'],
        # ['Strictfp'],
    ],
    # ['Super(Stmt)', [
    #     ['Extends', 'ClassType'],
    # ],
    'Interfaces': [
        ['Implements', 'InterfaceTypeList'],
    ],
    'InterfaceTypeList': [
        ['InterfaceType'],
        ['InterfaceTypeList', 'Comma', 'InterfaceType'],
    ],
    'ClassBody': [
        ['LeftBrace', 'RightBrace'],
        ['LeftBrace', 'ClassBodyDeclarations', 'RightBrace'],
    ],
    'ClassBodyDeclarations': [
        ['ClassBodyDeclaration'],
        ['ClassBodyDeclarations', 'ClassBodyDeclaration'],
    ],
    'ClassBodyDeclaration': [
        ['ClassMemberDeclaration'],
        ['InstanceInitializer'],
        # ['StaticInitializer'],
        ['ConstructorDeclaration'],
    ],
    'ClassMemberDeclaration': [
        ['FieldDeclaration'],
        ['MethodDeclaration'],
        # ['ClassDeclaration'],
        # ['InterfaceDeclaration'],
        ['SemiColon'],
    ],
    
    # Field declarations (S8.3)
    'FieldDeclaration': [
        ['Type', 'VariableDeclarators', 'SemiColon'],
        ['FieldModifiers', 'Type', 'VariableDeclarators', 'SemiColon'],
    ],
    'VariableDeclarators': [
        ['VariableDeclarators'],
        ['VariableDeclarators', 'Comma', 'VariableDeclarator'],
    ],
    'VariableDeclarator': [
        ['VariableDeclaratorId'],
        ['VariableDeclaratorId', 'AssignmentOperator', 'VariableInitializer'],
    ],
    'VariableDeclaratorId': [
        ['Identifier'],
        ['VariableDeclaratorId', 'LeftBracket', 'RightBracket'],
    ],
    'VariableInitializer': [
        ['Expression'],
        ['ArrayInitializer'],
    ],
    'FieldModifiers': [
        ['FieldModifier'],
        ['FieldModifiers', 'FieldModifier'],
    ],
    'FieldModifier': [
        ['Public'],
        ['Protected'],
        # ['Private'],
        ['Static'],
        # ['Final'],
        # ['Transient'],
        # ['Volatile'],
    ],
    
    # Method declarations (S8.4)
    'MethodDeclaration': [
        ['MethodHeader', 'MethodBody'],
    ],
    'MethodHeader': [
        ['ResultType', 'MethodDeclarator'],
        ['MethodModifiers', 'ResultType', 'MethodDeclarator'],
        # ['ResultType', 'MethodDeclarator', 'Throws'],
        # ['MethodModifiers', 'ResultType', 'MethodDeclarator', 'Throws'],
    ],
    'ResultType': [
        ['Type'],
        ['Void'],
    ],
    'MethodDeclarator': [
        ['Identifier', 'LeftParenthesis', 'RightParenthesis'],
        ['Identifier', 'LeftParenthesis', 'FormalParameterList',
            'RightParenthesis'],
    ],
    # TODO: Metioned in spec for "legacy" code.
    # 'MethodDeclarator': [
    #     ['MethodDeclarator', 'LeftBracket', 'RightBracket'],
    # ],
    'FormalParameterList': [
        ['FormalParameter'],
        ['FormalParameterList', 'Comma', 'FormalParameter'],
    ],
    'FormalParameter': [
        ['Type', 'VariableDeclaratorId'],
    #     ['Final', 'Type', 'VariableDeclaratorId'],
    ],
    'MethodModifiers': [
        ['MethodModifier'],
        ['MethodModifiers', 'MethodModifier'],
    ],
    'MethodModifier': [
        ['Public'],
        ['Protected'],
        # ['Private'],
        ['Abstract'],
        ['Static'],
        # ['Final'],
        # ['Synchronized'],
        # ['Native'],
        # ['Strictfp'],
    ],
    # 'Throws(Stmt)': [
    #     ['Throws', 'ClassTypeList']
    # ],
    # 'ClassTypeList': [
    #     ['ClassTypeList', 'Comma', 'ClassType'],
    # ],
    'MethodBody': [
        ['Block'],
        ['SemiColon'],
    ],
    
    # Instance initializers (S8.6)
    'InstanceInitializer': [
        ['Block'],
    ],
    
    # Static initializers (S8.7)
    # 'StaticInitializer': [
    #     ['Block'],
    # ],

    # Constructor declarations (S8.8)
    'ConstructorDeclaration': [
        ['ConstructorDeclarator', 'ConstructorBody'],
        ['ConstructorModifiers', 'ConstructorDeclarator', 'ConstructorBody'],
        # ['ConstructorDeclarator', 'Throws(Stmt)', 'ConstructorBody'],
        # ['ConstructorModifiers', 'ConstructorDeclarator', 'Throws(Stmt)',
        #     'ConstructorBody'],
    ],
    'ConstructorDeclarator': [
        ['SimpleTypeName', 'LeftParenthesis', 'RightParenthesis'],
        ['SimpleTypeName', 'LeftParenthesis', 'FormalParameterList',
            'RightParenthesis'],
    ],
    'ConstructorModifiers': [
        ['ConstructorModifier'],
        ['ConstructorModifiers', 'ConstructorModifier'],
    ],
    'ConstructorModifier': [
        ['Public'],
        ['Protected'],
        # ['Private'],
    ],
    'ConstructorBody': [
        ['LeftBrace', 'RightBrace'],
        # ['LeftBrace', 'ExplicitConstructorInvocation', 'RightBrace'],
        ['LeftBrace', 'BlockStatements', 'RightBrace'],
        # ['LeftBrace', 'ExplicitConstructorInvocation', 'BlockStatements',
        #     'RightBrace'],
    ],
    # 'ExplicitConstructorInvocation': [
    #     ['This', 'LeftParenthesis', 'RightParenthesis', 'SemiColon'],
    #     ['This', 'LeftParenthesis', 'ArgumentList', 'RightParenthesis',
    #         'SemiColon'],
    #     ['Super', 'LeftParenthesis', 'RightParenthesis', 'SemiColon'],
    #     ['Super', 'LeftParenthesis', 'ArgumentList', 'RightParenthesis',
    #         'SemiColon'],
    #     ['Primary', 'Dot', 'Super(stmt)', 'LeftParenthesis', 'RightParenthesis',
    #         'SemiColon'],
    #     ['Primary', 'Dot', 'Super(stmt)', 'LeftParenthesis', 'ArgumentList',
    #         'RightParenthesis', 'SemiColon'],
    # ],
    
    # Interface declarations (S9.1)
    'InterfaceDeclaration': [
        ['Interface', 'Identifier', 'InterfaceBody'],
        ['InterfaceModifiers', 'Identifier', 'InterfaceBody'],
        ['Interface', 'Identifier', 'ExtendsInterfaces', 'InterfaceBody'],
        ['InterfaceModifiers', 'Identifier', 'ExtendsInterfaces',
            'InterfaceBody'],
    ],
    'InterfaceModifiers': [
        ['InterfaceModifier'],
        ['InterfaceModifiers', 'InterfaceModifier'],
    ],
    'InterfaceModifier': [
        ['Public'],
        ['Protected'],
        # ['Private'],
        ['Abstract'],
        ['Static'],
        # ['Strictfp'],
    ],
    'ExtendsInterfaces': [
        ['Extends', 'InterfaceType'],
        ['ExtendsInterfaces', 'Comma', 'InterfaceType'],
    ],
    'InterfaceBody': [
        ['LeftBrace', 'RightBrace'],
        ['LeftBrace', 'InterfaceMemberDeclarations', 'RightBrace'],
    ],
    'InterfaceMemberDeclarations': [
        ['InterfaceMemberDeclaration'],
        ['InterfaceMemberDeclarations', 'InterfaceMemberDeclaration'],
    ],
    'InterfaceMemberDeclaration': [
        ['ConstantDeclaration'],
        ['AbstractMethodDeclaration'],
        ['ClassDeclaration'],
        ['InterfaceDeclaration'],
        ['SemiColon'],
    ],
    
    # Field (constant) declarations (S9.3)
    'ConstantDeclaration': [
        ['Type', 'VariableDeclarators'],
        ['ConstantModifiers', 'Type', 'VariableDeclarators'],
    ],
    'ConstantModifiers': [
        ['ConstantModifier'],
        ['ConstantModifiers', 'ConstantModifier'],
    ],
    'ConstantModifier': [
        ['Public'],
        ['Static'],
        # ['Final'],
    ],

    # Abstract method declarations (S9.4)
    'AbstractMethodDeclaration': [
        ['ResultType', 'MethodDeclarator', 'SemiColon'],
        ['AbstractMethodModifiers', 'ResultType', 'MethodDeclarator',
            'SemiColon'],
        # ['ResultType', 'MethodDeclarator', 'Throws(Stmt)', 'SemiColon'],
        # ['AbstractMethodModifiers', 'ResultType', 'MethodDeclarator',
        #     'Throws(Stmt)', 'SemiColon'],
    ],
    'AbstractMethodModifiers': [
        ['AbstractMethodModifier'],
        ['AbstractMethodModifiers', 'AbstractMethodModifier'],
    ],
    'AbstractMethodModifier': [
        ['Public'],
        ['Abstract'],
    ],
    
    # Array intializers (S10.6)
    'ArrayInitializer': [
        ['LeftBrace', 'RightBrace'],
        ['LeftBrace', 'VariableInitializers', 'RightBrace'],
        ['LeftBrace', 'Comma', 'RightBrace'],
        ['LeftBrace', 'VariableInitializers', 'Comma', 'RightBrace'],
    ],
    'VariableInitializers': [
        ['VariableInitializer'],
        ['VariableInitializers', 'Comma', 'VariableInitializer'],
    ],
    
    # Blocks (S14.2)
    'Block': [
        ['LeftBrace', 'RightBrace'],
        ['LeftBrace', 'BlockStatements', 'RightBrace'],
    ],
    'BlockStatements': [
        ['BlockStatement'],
        ['BlockStatements', 'BlockStatement'],
    ],
    'BlockStatement': [
        ['LocalVariableDeclarationStatement'],
        ['ClassDeclaration'],
        ['Statement'],
    ],

    # Local variable declaration statements (S14.4)
    'LocalVariableDeclarationStatement': [
        ['LocalVariableDeclaration', 'SemiColon'],
    ],
    'LocalVariableDeclaration': [
        ['Type', 'VariableDeclarators'],
        # ['Final', 'Type', 'VariableDeclarators'],
    ],
    
    # Statements (S14.5)
    'Statement': [
        ['StatementWithoutTrailingSubstatement'],
        # ['LabeledStatement'],
        ['IfThenStatement'],
        ['IfThenElseStatement'],
        ['WhileStatement'],
        ['ForStatement'],
    ],
    'StatementWithoutTrailingSubstatement': [
        ['Block'],
        ['EmptyStatement'],
        ['ExpressionStatement'],
        # ['SwitchStatement'],
        # ['DoStatement'],
        # ['BreakStatement'],
        # ['ContinueStatement'],
        ['ReturnStatement'],
        # ['SynchronizedStatement'],
        # ['ThrowStatement'],
        # ['TryStatement'],
    ],
    'StatementNoShortIf': [
        ['StatementWithoutTrailingSubstatement'],
        # ['LabeledStatementNoShortIf'],
        ['IfThenElseStatementNoShortIf'],
        ['ForStatementNoShortIf'],
    ],
    
    # The empty statement (S14.6)
    'EmptyStatement': [
        ['SemiColon'],
    ],

    # Labeled statements (S16.7)
    # 'LabeledStatement': 
    #     ['Identifier', 'ColonOperator', 'Statement'],
    # ],
    # 'LabeledStatementNoShortIf': 
    #     ['Identifier', 'ColonOperator', 'StatementNoShortIf'],
    # ],

    # Expression statements (S14.8)
    'ExpressionStatement': [
        ['StatementExpression', 'SemiColon'],
    ],
    'StatementExpression': [
        ['Assignment'],
        # ['PreIncrementExpression'],
        # ['PreDecrementExpression'],
        # ['PostIncrementExpression'],
        # ['PostDecrementExpression'],
        ['MethodInvocation'],
        ['ClassInstanceCreationExpression'],
    ],

    # The if statement (S14.9)
    'IfThenStatement': [
        ['If', 'LeftParenthesis', 'Expression', 'Statement'],
    ],
    'IfThenElseStatement': [
        ['If', 'LeftParenthesis', 'Expression', 'StatementNoShortIf', 'Else',
            'Statement'],
    ],
    'IfThenElseStatementNoShortIf': [
        ['If', 'LeftParenthesis', 'Expression', 'StatementNoShortIf', 'Else',
            'StatementNoShortIf'],
    ],
    
    # The switch statement (S14.10)
    # Note: Section omitted.

    # The while statement (S14.11)
    'WhileStatement': [
        ['While', 'LeftParenthesis', 'Expression', 'RightParenthesis',
            'Statement'],
    ],
    'WhileStatementNoShortIf': [
        ['While', 'LeftParenthesis', 'Expression', 'RightParenthesis',
            'StatementNoShortIf'],
    ],
    
    # The do statement (S14.12)
    # Note: Section omitted.

    # The for statement (S14.13)
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
        ['For', 'LeftParenthesis', 'SemiColon', 'SemiColon',
            'RightParenthesis', 'StatementNoShortIf'],
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
    'StatementExpressionList': [ # Note, we do not allow for (general)s.
        ['StatementExpression'],
        # ['StatementExpressionList', 'Comma', 'StatementExpression'],
    ],

    # The break statement (S14.14)
    # Note: Section omitted
    
    # The continue statement (S14.15)
    # Note: Section omitted

    # The return statement (S14.16)
    'ReturnStatement': [
        ['Return'],
        ['Return', 'Expression'],
    ],

    # The throw statement (S14.17)
    # Note: Section omitted

    # The synchronized statement (S14.18)
    # Note: Section omitted

    # The try statement (S14.19)
    # Note: Section omitted

    # Primary expressions (S15.8)
    'Primary': [
        ['PrimaryNoNewArray'],
        ['ArrayCreationExpression'],
    ],
    'PrimaryNoNewArray': [
        ['Literal'],
        # ['Type', 'Dot', 'Class'],
        # ['Void', 'Dot', 'Class'],
        ['This'],
        # ['ClassName', 'Dot', 'This'],
        ['LeftParenthesis', 'Expression', 'RightParenthesis'],
        ['ClassInstanceCreationExpression'],
        ['FieldAccess'],
        ['MethodInvocation'],
        ['ArrayAccess'],
    ],
    
    # Class instance creation expressions (S15.9)
    'ClassInstanceCreationExpression': [
        ['New', 'ClassOrInterfaceType', 'LeftParenthesis', 'RightParenthesis'],
        ['New', 'ClassOrInterfaceType', 'LeftParenthesis', 'ArgumentList',
            'RightParenthesis'],
        ['New', 'ClassOrInterfaceType', 'LeftParenthesis', 'RightParenthesis',
            'ClassBody'],
        ['New', 'ClassOrInterfaceType', 'LeftParenthesis', 'ArgumentList',
            'RightParenthesis', 'ClassBody'],
        ['Primary', 'Dot', 'New', 'Identifier', 'LeftParenthesis',
            'RightParenthesis'],
        ['Primary', 'Dot', 'New', 'Identifier', 'LeftParenthesis',
            'ArgumentList', 'RightParenthesis'],
        ['Primary', 'Dot', 'New', 'Identifier', 'LeftParenthesis',
            'RightParenthesis', 'ClassBody'],
        ['Primary', 'Dot', 'New', 'Identifier', 'LeftParenthesis',
            'ArgumentList', 'RightParenthesis', 'ClassBody'],
    ],
    'ArgumentList': [
        ['Expression'],
        ['ArgumentList', 'Comma', 'Expression'],
    ],

    # Array creation expressions (S15.10)
    'ArrayCreationExpression': [
        ['New', 'PrimitiveType', 'DimExprs'],
        ['New', 'PrimitiveType', 'DimExprs', 'Dims'],
        ['New', 'TypeName', 'DimExprs'],
        ['New', 'TypeName', 'DimExprs', 'Dims'],
        ['New', 'PrimitiveType', 'Dims', 'ArrayInitializer'],
        ['New', 'TypeName', 'Dims', 'ArrayInitializer'],
    ],
    'DimExprs': [
        ['DimExpr'],
        ['DimExprs', 'DimExpr'],
    ],
    'DimExpr': [
        ['LeftBracket', 'Expression', 'RightBracket'],
    ],
    'Dims': [
        ['LeftBracket', 'RightBracket'],
        ['Dims', 'LeftBracket', 'RightBracket'],
    ],

    # Field access expressions (S15.11)
    'FieldAccess': [
        ['Primary', 'Dot', 'Identifier'],
        # ['Super', 'Dot', 'Identifier'],
        # ['ClassName', 'Dot', 'Super', 'Dot', 'Identifier'],
    ],
    
    # Method invocation expressions (S15.12)
    'MethodInvocation': [
        ['MethodName', 'LeftParenthesis', 'RightParenthesis'],
        ['MethodName', 'LeftParenthesis', 'ArgumentList', 'RightParenthesis'],
        ['Primary', 'Dot', 'Identifier', 'LeftParenthesis',
            'RightParenthesis'],
        ['Primary', 'Dot', 'Identifier', 'LeftParenthesis', 'ArgumentList',
            'RightParenthesis'],
        ['Super', 'Dot', 'Identifier', 'LeftParenthesis', 'RightParenthesis'],
        ['Super', 'Dot', 'Identifier', 'LeftParenthesis', 'ArgumentList',
            'RightParenthesis'],
        # ['ClassName', 'Dot', 'Super', 'Dot', 'Identifier', 'LeftParenthesis',
        #     'RightParenthesis'],
        # ['ClassName', 'Dot', 'Super', 'Dot', 'Identifier', 'LeftParenthesis',
        #     'ArgumentList', 'RightParenthesis'],
    ],
    
    # Array access expressions (S15.13)
    'ArrayAccess': [
        ['ExpressionName', 'LeftBracket', 'Expression', 'RightBracket'],
        ['PrimaryNoNewArray', 'LeftBracket', 'Expression', 'RightBracket'],
    ],
    
    # Postfix expressions (S15.14)
    'PostfixExpression': [
        ['Primary'],
        ['ExpressionName'],
        # ['PostIncrementExpression'],
        # ['PostDecrementExpression'],
    ],
    # 'PostIncrementExpression': [
    #     ['PostfixExpression', 'IncrementOperator'],
    # ],
    # 'PostDecrementExpression': [
    #     ['PostfixExpression', 'DecrementOperator'],
    # ],

    # Unary operators (S15.15)
    'UnaryExpression': [
        #['PreIncrementExpression'],
        #['PreDecrementExpression'],
        ['AddOperator', 'UnaryExpression'],
        ['SubtractOperator', 'UnaryExpression'],
        ['UnaryExpressionNotPlusMinus'],
    ],
    # 'PreIncrementExpression': [
    #     ['IncrementOperator', 'UnaryExpression'],
    # ],
    # 'PreDecrementExpression': [
    #     ['DecrementOperator', 'UnaryExpression'],
    # ],
    'UnaryExpressionNotPlusMinus': [
        ['PostfixExpression'],
        # ['BinaryNotOperator', 'UnaryExpression'],
        ['NotOperator', 'UnaryExpression'],
        ['CastExpression'],
    ],

    # Cast expressions (S15.16)
    'CastExpression': [
        ['LeftParenthesis', 'PrimitiveType', 'RightParenthesis',
            'UnaryExpression'],
        ['LeftParenthesis', 'PrimitiveType', 'Dims', 'RightParenthesis',
            'UnaryExpression'],
        ['LeftParenthesis', 'ReferenceType', 'RightParenthesis',
            'UnaryExpressionNotPlusMinus'],
    ],
    
    # Multiplicative operators (S15.17)
    'MultiplicativeExpression': [
        ['UnaryExpression'],
        ['MultiplicativeExpression', 'MultiplyOperator', 'UnaryExpression'],
        ['MultiplicativeExpression', 'DivideOperator', 'UnaryExpression'],
        ['MultiplicativeExpression', 'ModuloOperator', 'UnaryExpression'],
    ],

    # Additive operators (S15.18)
    'AdditiveExpression': [
        ['MultiplicativeExpression'],
        ['AdditiveExpression', 'AddOperator', 'MultiplicativeExpression'],
        ['AdditiveExpression', 'SubtractOperator', 'MultiplicativeExpression'],
    ],

    # Shift operators (S15.19)
    'ShiftExpression': [
        ['AdditiveExpression'],
        # ['ShiftExpression', 'LeftShiftOperator', 'AdditiveExpression'],
        # ['ShiftExpression', 'RightShiftOperator', 'AdditiveExpression'],
        # ['ShiftExpression', 'UnsignedRightShiftOperator',
        #     'AdditiveExpression'],
    ],

    # Relational operators (S15.20)
    'RelationalExpression': [
        ['ShiftExpression'],
        ['RelationalExpression', 'LessThanOperator', 'ShiftExpression'],
        ['RelationalExpression', 'GreaterThanOperator', 'ShiftExpression'],
        ['RelationalExpression', 'LessThanEqualOperator', 'ShiftExpression'],
        ['RelationalExpression', 'GreaterThanEqualOperator',
            'ShiftExpression'],
        ['RelationalExpression', 'Instanceof', 'ReferenceType'],
    ],

    # Equality operators (S15.21)
    'EqualityExpression': [
        ['RelationalExpression'],
        ['EqualityExpression', 'EqualOperator', 'RelationalExpression'],
        ['EqualityExpression', 'NotEqualOperator', 'RelationalExpression'],
    ],

    # Bitwise and logical operators (S15.22)
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
        # ['InclusiveOrExpression', 'BinaryOrOperator',  'ExclusiveOrExpression'],
    ],

    # Conditional-and operator && (S15.23)
    'ConditionalAndExpression': [
        ['InclusiveOrExpression'],
        ['ConditionalAndExpression', 'AndOperator', 'InclusiveOrExpression'],
    ],

    # Conditional-or operator || (S15.24)
    'ConditionalOrExpression': [
        ['ConditionalAndExpression'],
        ['ConditionalOrExpression', 'OrOperator', 'ConditionalAndExpression'],
    ],

    # Condtional operator ? : (S15.25)
    'ConditionalExpression': [
        ['ConditionalOrExpression'],
        # ['ConditionalOrExpression', 'QuestionOperator', 'Expression',
        #     'ConditionalExpression'],
    ],

    # Assignment operators (S15.26)
    'AssignmentExpression': [
        ['ConditionalExpression'],
        ['Assignment'],
    ],
    'Assignment': [ # Note: Only one assignment operator in Joos.
        ['LeftHandSide', 'AssignmentOperator', 'AssignmentExpression'],
    ],
    'LeftHandSide': [
        ['ExpressionName'],
        ['FieldAccess'],
        ['ArrayAccess'],
    ],

    # Expression (S15.27)
    'Expression': [
        ['AssignmentExpression'],
    ],

    # Constant expression (S15.28)
    'ConstantExpression': [
        ['Expression'],
    ],
}

