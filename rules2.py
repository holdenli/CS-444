# Compacted List of CFG rules for Joos.
# Rules are modified to use left recursion.

START_SYMBOL = 'CompilationUnit'
RULES = {
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
        ['FloatingPointLiteral'], 
        ['CharacterLiteral'],
        ['StringLiteral'],
        ['BooleanLiteral'],
        ['NullLiteral'],
    ],

    'Expression': [
        ['Expression1'],
        ['Expression1', 'AssignmentOperator', 'Expression1'],
    ],

    # Omitted since it is a terminal.
    # 'AssignmentOperator': [
    #     ['AssignmentOperator'],
    # ],

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
        ['Expression2', 'Expression1Rest'],
    ],

    'Expression1Rest': [
        [],
        ['QuestionOperator', 'Expression', 'ColonOperator', 'Expression1'], 
    ],

    'Expression2': [
        ['Expression3'],
        ['Expression3', 'Expression2Rest'],
    ],

    'Expression2Rest': [
        [],
        ['Expression3Rest'],
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
        ['BinaryOrOperator'],
        ['InverseOperator'], 
        ['BinaryAndOperator'],
        ['EqualOperator'],
        ['NotEqualOperator'],
        ['LessThanOperator'], 
        ['GreaterThanOperator'],
        ['LessThanEqualOperator'],
        ['GreaterThanEqualOperator'], 
        ['LeftShiftOperator'],
        ['RightShiftOperator'], 
        ['UnsignedRightShiftOperator'],
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
        ['Primary'],
        ['Primary', 'Selectors'],
        ['Primary', 'PostfixOps'],
        ['Primary', 'Selectors', 'PostfixOps'],
    ],

    # Hack.
    'PostfixOps': [
        ['PostfixOp'],
        ['PostfixOps', 'PostfixOp'],
    ],

    # Hack.
    'Selectors': [
        ['Selector'],
        ['Selectors', 'Selector'],
    ],

    'Primary': [
        ['LeftParenthesis', 'Expression', 'RightParenthesis'],
        ['This'],
        ['This', 'Arguments'],
        ['Super', 'SuperSuffix'],
        ['Literal'],
        ['New', 'Creator'],
        ['QuantifiedIdentifier'], # Hack.
        ['QuantifiedIdentifier', 'IdentifierSuffix'], # Hack.
        ['BasicType', 'BracketsOpt', 'Dot', 'Class'],
        ['Void', 'Dot', 'Class'],
    ],

    'IdentifierSuffix': [
        ['LeftBracket', 'RightBracket', 'BracketsOpt', 'Dot', 'Class'],
        ['LeftBracket', 'Expression', 'RightBracket'],
        ['Arguments'],
        ['Dot', 'Class'],
        ['Dot', 'This'],
        ['Dot', 'Super', 'Arguments'],
        ['Dot', 'New', 'InnerCreator'],
    ],

    'PrefixOp': [
        ['IncrementOperator'], 
        ['DecrementOperator'],
        ['NotOperator'],
        ['BinaryNotOperator'],
        ['AddOperator'],
        ['SubtractOperator'],
    ],

    'PostfixOp': [
        ['IncrementOperator'],
        ['DecrementOperator'],
    ],

    'Selector': [
        ['Dot', 'Identifier'],
        ['Dot', 'Identifier', 'Arguments'],
        ['Dot', 'This'],
        ['Dot', 'Super', 'SuperSuffix'],
        ['Dot', 'New', 'InnerCreator'],
        ['LeftBracket', 'Expression', 'RightBracket'],
    ],

    'SuperSuffix': [
        ['Arguments'],
        ['Dot', 'Identifier'],
        ['Dot', 'Identifier', 'Arguments'],
    ],

    'BasicType': [
        ['Byte'],
        ['Short'],
        ['Char'],
        ['Int'],
        ['Long'],
        ['Float'],
        ['Double'],
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
        ['LeftBracket', 'RightBracket', 'BracketsOpt', 'ArrayInitializer'],
        ['LeftBracket', 'Expression', 'RightBracket',
            'BracketedExpressionsOpt', 'BracketsOpt'],
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

    'BlockStatements': [
        [],
        ['BlockStatements', 'BlockStatement'],

    'BlockStatement': [
        ['LocalVariableDeclarationStatement'],
        ['ClassOrInterfaceDeclaration'],
        ['Identifier', 'Colon', 'Statement'],
        ['Statement'],
    ],

    'LocalVariableDeclarationStatement': [
        ['Type', 'VariableDeclarators', 'SemiColon'],
        ['Final', 'Type', 'VariableDeclarators', 'SemiColon'],
    ],

    'Statement': [
        ['Block'],
        ['If', 'ParExpression' 'Statement'],
        ['If', 'ParExpression' 'Statement', 'Else', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInitOpt', 'SemiColon', 'SemiColon',
            'ForUpdateOpt', 'RightParenthesis', 'Statement'],
        ['For', 'LeftParenthesis', 'ForInitOpt', 'SemiColon', 'Expression',
            'SemiColon', 'ForUpdateOpt', 'RightParenthesis', 'Statement'],
        ['While', 'ParExpression', 'Statement'],
        ['Do', 'Statement', 'While', 'ParExpression', 'SemiColon'],
        ['Try', 'Block', 'Catches'],
        ['Try', 'Block', 'Finally', 'Block'],
        ['Try', 'Block', 'Catches', 'Finally', 'Block'],
        ['Switch', 'ParExpression', 'LeftParenthesis',
            'SwitchBlockStatementGroups', 'RightParenthesis'],
        ['Synchronized', 'ParExpression', 'Block'],
        ['Return', 'SemiColon'],
        ['Return', 'Expression', 'SemiColon'],
        ['Throw', 'Expression', 'SemiColon'],
        ['Break'],
        ['Break', 'Identifier'],
        ['Continue'],
        ['Continue', 'Identifier'],
        ['SemiColon'],
        ['ExpressionStatement'],
        ['Identifier', 'Colon', 'Statement'],
    ],

    'Catches': [
        ['CatchClause'],
        ['Catches', 'CatchClause'],
    ],

    'CatchClause': [
        ['Catch', 'LeftParenthesis', 'FormalParameter', 'RightParenthesis',
            'Block'],
    ],

    'SwitchBlockStatementGroups': [
        [],
        ['SwitchBlockStatementGroups', 'SwitchBlockStatementGroups'],
    ],

    'SwitchBlockStatementGroup': [
        ['SwitchLabel', 'BlockStatements'],
    ],

    'SwitchLabel': [
        ['Case', 'ConstantExpression', 'Colon'],
        ['Default', 'Colon'],
    ],

    'MoreStatementExpressions': [
        [],
        ['MoreStatementExpressions', 'Comma', 'StatementExpression'],
    ],

    'ForInit': [
        ['StatementExpression', 'MoreStatementExpressions'],
        ['Type', 'VariableDeclarators'],
        ['Final', 'Type', 'VariableDeclarators'],
    ],

    'ForUpdate': [
        ['StatementExpression', 'MoreStatementExpressions'],
    ],

    'ModifiersOpt': [
        [],
        ['ModifiersOpt', 'Modifier'],
    ],

    'Modifier': [
        ['Public'],
        ['Protected'],
        ['Private'],
        ['Static'],
        ['Abstract'],
        ['Final'],
        ['Native'],
        ['Synchronized'],
        ['Transient'],
        ['Volatile'],
        ['Strictfp'],
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
        ['BracketsOpt' 'AssignmentOperator', 'VariableInitializer'],
    ],

    'VariableDeclaratorId': [
        ['Identifier', 'BracketsOpt'],
    ],

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

    # Hack.
    'ImportDeclarations': [
        [],
        ['ImportDeclarations', 'ImportDeclaration'],
    ],

    # Hack.
    'TypeDeclarations': [
        [],
        ['TypeDeclarations', 'TypeDeclarations'],
    ],

ImportDeclaration: 
    import Identifier {   .   Identifier } [   .     *   ] ;  

TypeDeclaration: 
    ClassOrInterfaceDeclaration
    ;

ClassOrInterfaceDeclaration: 
    ModifiersOpt (ClassDeclaration | InterfaceDeclaration)

ClassDeclaration: 
    class Identifier [extends Type] [implements TypeList] ClassBody

InterfaceDeclaration: 
    interface Identifier [extends TypeList] InterfaceBody

TypeList: 
    Type {  ,   Type}

ClassBody: 
    { {ClassBodyDeclaration} }

InterfaceBody: 
    { {InterfaceBodyDeclaration} }

ClassBodyDeclaration:
    ; 
    [static] Block
    ModifiersOpt MemberDecl

MemberDecl:
    MethodOrFieldDecl
    void Identifier MethodDeclaratorRest
    Identifier ConstructorDeclaratorRest
    ClassOrInterfaceDeclaration

MethodOrFieldDecl:
    Type Identifier MethodOrFieldRest

MethodOrFieldRest:
    VariableDeclaratorRest
    MethodDeclaratorRest

InterfaceBodyDeclaration:
    ; 
    ModifiersOpt InterfaceMemberDecl

InterfaceMemberDecl:
    InterfaceMethodOrFieldDecl
    void Identifier VoidInterfaceMethodDeclaratorRest
    ClassOrInterfaceDeclaration

InterfaceMethodOrFieldDecl:
    Type Identifier InterfaceMethodOrFieldRest

InterfaceMethodOrFieldRest:
    ConstantDeclaratorsRest ;
    InterfaceMethodDeclaratorRest

MethodDeclaratorRest:
        FormalParameters BracketsOpt [throws QualifiedIdentifierList] ( 
MethodBody |   ;  )

VoidMethodDeclaratorRest:
        FormalParameters [throws QualifiedIdentifierList] ( MethodBody |   ;  )

InterfaceMethodDeclaratorRest:
    FormalParameters BracketsOpt [throws QualifiedIdentifierList]   ;  

VoidInterfaceMethodDeclaratorRest:
    FormalParameters [throws QualifiedIdentifierList]   ;  

ConstructorDeclaratorRest:
    FormalParameters [throws QualifiedIdentifierList] MethodBody

QualifiedIdentifierList: 
    QualifiedIdentifier {  ,   QualifiedIdentifier}

FormalParameters: 
    ( [FormalParameter { , FormalParameter}] )

FormalParameter: 
    [final] Type VariableDeclaratorId


eq
MethodBody:
    Block
