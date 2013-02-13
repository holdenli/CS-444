START_SYMBOL="Goal"
RULES = {'AbstractMethodDeclaration': [['MethodHeader', 'SemiColon']],
 'AdditiveExpression': [['MultiplicativeExpression'],
                        ['AdditiveExpression',
                         'AddOperator',
                         'MultiplicativeExpression'],
                        ['AdditiveExpression',
                         'SubtractOperator',
                         'MultiplicativeExpression']],
 'AndExpression': [['EqualityExpression'],
                   ['AndExpression',
                    'BinaryAndOperator',
                    'EqualityExpression']],
 'ArgumentList': [['Expression'], ['ArgumentList', 'Comma', 'Expression']],
 'ArgumentListopt': [[], ['ArgumentList']],
 'ArrayAccess': [['Name', 'LeftBracket', 'Expression', 'RightBracket'],
                 ['PrimaryNoNewArray',
                  'LeftBracket',
                  'Expression',
                  'RightBracket']],
 'ArrayCreationExpression': [['New', 'PrimitiveType', 'DimExprs', 'Dimsopt'],
                             ['New',
                              'ClassOrInterfaceType',
                              'DimExprs',
                              'Dimsopt']],
 'ArrayInitializer': [['LeftBrace',
                       'VariableInitializers',
                       'Comma',
                       'RightBrace'],
                      ['LeftBrace', 'VariableInitializers', 'RightBrace'],
                      ['LeftBrace', 'Comma', 'RightBrace'],
                      ['LeftBrace', 'RightBrace']],
 'ArrayType': [['PrimitiveType', 'LeftBracket', 'RightBracket'],
               ['Name', 'LeftBracket', 'RightBracket'],
               ['ArrayType', 'LeftBracket', 'RightBracket']],
 'Assignment': [['LeftHandSide',
                 'AssignmentOperator',
                 'AssignmentExpression']],
 'AssignmentExpression': [['ConditionalExpression'], ['Assignment']],
 'AssignmentOperator': [['DirectAssignmentOperator']],
 'Block': [['LeftBrace', 'BlockStatements', 'RightBrace'],
           ['LeftBrace', 'RightBrace']],
 'BlockStatement': [['LocalVariableDeclarationStatement'], ['Statement']],
 'BlockStatements': [['BlockStatement'],
                     ['BlockStatements', 'BlockStatement']],
 'BreakStatement': [['Break', 'Identifieropt', 'SemiColon']],
 'CastExpression': [['LeftParenthesis',
                     'PrimitiveType',
                     'Dimsopt',
                     'RightParenthesis',
                     'UnaryExpression'],
                    ['LeftParenthesis',
                     'Expression',
                     'RightParenthesis',
                     'UnaryExpressionNotPlusMinus'],
                    ['LeftParenthesis',
                     'Name',
                     'Dims',
                     'RightParenthesis',
                     'UnaryExpressionNotPlusMinus']],
 'CatchClause': [['Catch',
                  'LeftParenthesis',
                  'FormalParameter',
                  'RightParenthesis',
                  'Block']],
 'Catches': [['CatchClause'], ['Catches', 'CatchClause']],
 'Catchesopt': [[], ['Catches']],
 'ClassBody': [['LeftBrace', 'RightBrace'],
               ['LeftBrace', 'ClassBodyDeclarations', 'RightBrace']],
 'ClassBodyDeclaration': [['ClassMemberDeclaration'],
                          ['StaticInitializer'],
                          ['ConstructorDeclaration']],
 'ClassBodyDeclarations': [['ClassBodyDeclaration'],
                           ['ClassBodyDeclarations', 'ClassBodyDeclaration']],
 'ClassDeclaration': [['Class',
                       'Identifier',
                       'SuperStuff',
                       'Interfaces',
                       'ClassBodyDeclaration'],
                      ['Class',
                       'Identifier',
                       'Interfaces',
                       'ClassBodyDeclarations'],
                      ['Class',
                       'Identifier',
                       'SuperStuff',
                       'ClassBodyDeclaration'],
                      ['Class', 'Identifier', 'ClassBodyDeclarations'],
                      ['Modifiers',
                       'Class',
                       'Identifier',
                       'Super',
                       'Interfaces',
                       'ClassBodyDeclaration'],
                      ['Modifiers',
                       'Class',
                       'Identifier',
                       'Interfaces',
                       'ClassBodyDeclarations'],
                      ['Modifiers',
                       'Class',
                       'Identifier',
                       'Super',
                       'ClassBodyDeclaration'],
                      ['Modifiers',
                       'Class',
                       'Identifier',
                       'ClassBodyDeclarations']],
 'ClassInstanceCreationExpression': [['New',
                                      'ClassType',
                                      'LeftParenthesis',
                                      'ArgumentListopt',
                                      'RightParenthesis']],
 'ClassMemberDeclaration': [['FieldDeclaration'], ['MethodDeclaration']],
 'ClassOrInterfaceType': [['Name']],
 'ClassType': [['ClassOrInterfaceType']],
 'ClassTypeList': [['ClassType'], ['ClassTypeList', 'Comma', 'ClassType']],
 'CompilationUnit': [['PackageDeclarationopt',
                      'ImportDeclarationsopt',
                      'TypeDeclarationsopt']],
 'ConditionalAndExpression': [['InclusiveOrExpression'],
                              ['ConditionalAndExpression',
                               'AndOperator',
                               'InclusiveOrExpression']],
 'ConditionalExpression': [['ConditionalOrExpression']],
 'ConditionalOrExpression': [['ConditionalAndExpression'],
                             ['ConditionalOrExpression',
                              'OrOperator',
                              'ConditionalAndExpression']],
 'ConstantDeclaration': [['FieldDeclaration']],
 'ConstantExpression': [['Expression']],
 'ConstructorBody': [['LeftBrace',
                      'ExplicitConstructorInvocation',
                      'BlockStatement',
                      'RightBrace'],
                     ['LeftBrace',
                      'ExplicitConstructorInvocation',
                      'RightBrace'],
                     ['LeftBrace', 'BlockStatements', 'RightBrace'],
                     ['LeftBrace', 'RightBrace']],
 'ConstructorDeclaration': [['Modifiers',
                             'ConstructorDeclarator',
                             'ThrowsStuff',
                             'ConstructorBody'],
                            ['Modifiers',
                             'ConstructorDeclarator',
                             'ConstructorBody'],
                            ['ConstructorDeclarator',
                             'ThrowsStuff',
                             'ConstructorBody'],
                            ['ConstructorDeclarator', 'ConstructorBody']],
 'ConstructorDeclarator': [['SimpleName',
                            'LeftParenthesis',
                            'FormalParameterList',
                            'RightParenthesis'],
                           ['SimpleName',
                            'LeftParenthesis',
                            'RightParenthesis']],
 'ContinueStatement': [['Continue', 'Identifieropt', 'SemiColon']],
 'DimExpr': [['LeftBracket', 'Expression', 'RightBracket']],
 'DimExprs': [['DimExpr'], ['DimExprs', 'DimExpr']],
 'Dims': [['LeftBracket', 'RightBracket'],
          ['Dims', 'LeftBracket', 'RightBracket']],
 'Dimsopt': [[], ['Dims']],
 'DoStatement': [['Do',
                  'Statement',
                  'While',
                  'LeftParenthesis',
                  'Expression',
                  'RightParenthesis',
                  'SemiColon']],
 'EmptyStatement': [['SemiColon']],
 'EqualityExpression': [['RelationalExpression'],
                        ['EqualityExpression',
                         'EqualOperator',
                         'RelationalExpression'],
                        ['EqualityExpression',
                         'NotEqualOperator',
                         'RelationalExpression']],
 'ExclusiveOrExpression': [['AndExpression'],
                           ['ExclusiveOrExpression',
                            'InverseOperator',
                            'AndExpression']],
 'ExplicitConstructorInvocation': [['This',
                                    'LeftParenthesis',
                                    'ArgumentList',
                                    'RightParenthesis',
                                    'SemiColon'],
                                   ['This',
                                    'LeftParenthesis',
                                    'RightParenthesis',
                                    'SemiColon'],
                                   ['Super',
                                    'LeftParenthesis',
                                    'ArgumentList',
                                    'RightParenthesis',
                                    'SemiColon'],
                                   ['Super',
                                    'LeftParenthesis',
                                    'RightParenthesis',
                                    'SemiColon']],
 'Expression': [['AssignmentExpression']],
 'ExpressionStatement': [['StatementExpression', 'SemiColon']],
 'Expressionopt': [[], ['Expression']],
 'ExtendsInterfaces': [['Extends', 'InterfaceType'],
                       ['ExtendsInterfaces', 'Comma', 'InterfaceType']],
 'FieldAccess': [['Primary', 'Dot', 'Identifier'],
                 ['Super', 'Dot', 'Identifier']],
 'FieldDeclaration': [['Modifiers',
                       'Type',
                       'VariableDeclarators',
                       'SemiColon'],
                      ['Type', 'VariableDeclarators', 'SemiColon']],
 'FinallyStuff': [['Finally', 'Block']],
 'FloatingPointType': [['Float'], ['Double']],
 'ForInit': [['StatementExpressionList'], ['LocalVariableDeclaration']],
 'ForInitopt': [[], ['ForInit']],
 'ForStatement': [['For',
                   'LeftParenthesis',
                   'ForInitopt',
                   'SemiColon',
                   'Expressionopt',
                   'SemiColon',
                   'ForUpdateopt',
                   'RightParenthesis',
                   'Statement']],
 'ForStatementNoShortIf': [['For',
                            'LeftParenthesis',
                            'ForInitopt',
                            'SemiColon',
                            'Expressionopt',
                            'SemiColon',
                            'ForUpdateopt',
                            'RightParenthesis',
                            'StatementNoShortIf']],
 'ForUpdate': [['StatementExpressionList']],
 'ForUpdateopt': [[], ['ForUpdate']],
 'FormalParameter': [['Type', 'VariableDeclaratorId']],
 'FormalParameterList': [['FormalParameter'],
                         ['FormalParameterList', 'Comma', 'FormalParameter']],
 'Goal': [['CompilationUnit']],
 'Identifieropt': [[], ['Identifier']],
 'IfThenElseStatement': [['If',
                          'LeftParenthesis',
                          'Expression',
                          'RightParenthesis',
                          'StatementNoShortIf',
                          'Else',
                          'Statement']],
 'IfThenElseStatementNoShortIf': [['If',
                                   'LeftParenthesis',
                                   'Expression',
                                   'RightParenthesis',
                                   'StatementNoShortIf',
                                   'Else',
                                   'StatementNoShortIf']],
 'IfThenStatement': [['If',
                      'LeftParenthesis',
                      'Expression',
                      'RightParenthesis',
                      'Statement']],
 'ImportDeclaration': [['SingleTypeImportDeclaration'],
                       ['TypeImportOnDemandDeclaration']],
 'ImportDeclarations': [['ImportDeclaration'],
                        ['ImportDeclarations', 'ImportDeclaration']],
 'ImportDeclarationsopt': [[], ['ImportDeclarations']],
 'InclusiveOrExpression': [['ExclusiveOrExpression'],
                           ['InclusiveOrExpression',
                            'BinaryOrOperator',
                            'ExclusiveOrExpression']],
 'IntegralType': [['Byte'], ['Short'], ['Int'], ['Long'], ['Char']],
 'InterfaceBody': [['LeftBrace', 'InterfaceMemberDeclarations', 'RightBrace'],
                   ['LeftBrace', 'RightBrace']],
 'InterfaceDeclaration': [['Modifiers',
                           'Interface',
                           'Identifier',
                           'ExtendsInterfaces',
                           'InterfaceBody']],
 'InterfaceMemberDeclaration': [['ConstantDeclaration'],
                                ['AbstractMethodDeclaration']],
 'InterfaceMemberDeclarations': [['InterfaceMemberDeclaration'],
                                 ['InterfaceMemberDeclarations',
                                  'InterfaceMemberDeclaration']],
 'InterfaceType': [['ClassOrInterfaceType']],
 'InterfaceTypeList': [['InterfaceType'],
                       ['InterfaceTypeList', 'Comma', 'InterfaceType']],
 'Interfaces': [['Implements', 'InterfaceTypeList']],
 'LabeledStatement': [['Identifier', 'ColonOperator', 'Statement']],
 'LabeledStatementNoShortIf': [['Identifier',
                                'ColonOperator',
                                'StatementNoShortIf']],
 'LeftHandSide': [['Name'], ['FieldAccess'], ['ArrayAccess']],
 'Literal': [['DecimalIntegerLiteral'],
             ['FloatingPointLiteral'],
             ['BooleanLiteral'],
             ['CharacterLiteral'],
             ['StringLiteral'],
             ['NullLiteral']],
 'LocalVariableDeclaration': [['Type', 'VariableDeclarators']],
 'LocalVariableDeclarationStatement': [['LocalVariableDeclaration',
                                        'SemiColon']],
 'MethodBody': [['Block'], ['SemiColon']],
 'MethodDeclaration': [['MethodHeader', 'MethodBody']],
 'MethodDeclarator': [['Identifier',
                       'LeftParenthesis',
                       'FormalParameterList',
                       'RightParenthesis'],
                      ['Identifier', 'LeftParenthesis', 'RightParenthesis'],
                      ['MethodDeclarator', 'LeftBracket', 'RightBracket']],
 'MethodHeader': [['Modifiers', 'Type', 'MethodDeclarator', 'ThrowsStuff'],
                  ['Modifiers', 'Type', 'MethodDeclarator'],
                  ['Type', 'MethodDeclarator', 'ThrowsStuff'],
                  ['Type', 'MethodDeclarator'],
                  ['Modifiers', 'Void', 'MethodDeclarator', 'ThrowsStuff'],
                  ['Modifiers', 'Void', 'MethodDeclarator'],
                  ['Void', 'MethodDeclarator', 'ThrowsStuff'],
                  ['Void', 'MethodDeclarator']],
 'MethodInvocation': [['Name',
                       'LeftParenthesis',
                       'ArgumentListopt',
                       'RightParenthesis'],
                      ['Primary',
                       'Dot',
                       'Identifier',
                       'LeftParenthesis',
                       'ArgumentListopt',
                       'RightParenthesis'],
                      ['Super',
                       'Dot',
                       'Identifier',
                       'LeftParenthesis',
                       'ArgumentListopt',
                       'RightParenthesis']],
 'Modifier': [['Public'],
              ['Protected'],
              ['Private'],
              ['Static'],
              ['Abstract'],
              ['Final'],
              ['Native'],
              ['Synchronized'],
              ['Transient'],
              ['Volatile']],
 'Modifiers': [['Modifier'], ['Modifiers', 'Modifier']],
 'MultiplicativeExpression': [['UnaryExpression'],
                              ['MultiplicativeExpression',
                               'MultiplyOperator',
                               'UnaryExpression'],
                              ['MultiplicativeExpression',
                               'DivideOperator',
                               'UnaryExpression'],
                              ['MultiplicativeExpression',
                               'ModuloOperator',
                               'UnaryExpression']],
 'Name': [['SimpleName'], ['QualifiedName'], ['Identifier']],
 'NumericType': [['IntegralType'], ['FloatingPointType']],
 'PackageDeclaration': [['Package', 'Name', 'SemiColon']],
 'PackageDeclarationopt': [[], ['PackageDeclaration']],
 'PostfixExpression': [['Primary'], ['Name']],
 'Primary': [['PrimaryNoNewArray'], ['ArrayCreationExpression']],
 'PrimaryNoNewArray': [['Literal'],
                       ['This'],
                       ['LeftParenthesis', 'Expression', 'RightParenthesis'],
                       ['ClassInstanceCreationExpression'],
                       ['FieldAccess'],
                       ['MethodInvocation'],
                       ['ArrayAccess']],
 'PrimitiveType': [['NumericType'], ['Boolean']],
 'QualifiedName': [['Name', 'Dot', 'Identifier']],
 'ReferenceType': [['ClassOrInterfaceType'], ['ArrayType']],
 'RelationalExpression': [['ShiftExpression'],
                          ['RelationalExpression',
                           'LessThanOperator',
                           'ShiftExpression'],
                          ['RelationalExpression',
                           'GreaterThanOperator',
                           'ShiftExpression'],
                          ['RelationalExpression',
                           'LessThanEqualOperator',
                           'ShiftExpression'],
                          ['RelationalExpression',
                           'GreaterThanEqualOperator',
                           'ShiftExpression'],
                          ['RelationalExpression',
                           'Instanceof',
                           'ReferenceType']],
 'ReturnStatement': [['Return', 'Expressionopt', 'SemiColon']],
 'ShiftExpression': [['AdditiveExpression'],
                     ['ShiftExpression',
                      'LeftShiftOperator',
                      'AdditiveExpression'],
                     ['ShiftExpression',
                      'RightShiftOperator',
                      'AdditiveExpression']],
 'SimpleName': [['Identifier']],
 'SingleTypeImportDeclaration': [['Import', 'Name', 'SemiColon']],
 'Statement': [['StatementWithoutTrailingSubstatement'],
               ['LabeledStatement'],
               ['IfThenStatement'],
               ['IfThenElseStatement'],
               ['WhileStatement'],
               ['ForStatement']],
 'StatementExpression': [['Assignment'],
                         ['MethodInvocation'],
                         ['ClassInstanceCreationExpression']],
 'StatementExpressionList': [['StatementExpression'],
                             ['StatementExpressionList',
                              'Comma',
                              'StatementExpression']],
 'StatementNoShortIf': [['StatementWithoutTrailingSubstatement'],
                        ['LabeledStatementNoShortIf'],
                        ['IfThenElseStatementNoShortIf'],
                        ['WhileStatementNoShortIf'],
                        ['ForStatementNoShortIf']],
 'StatementWithoutTrailingSubstatement': [['Block'],
                                          ['EmptyStatement'],
                                          ['ExpressionStatement'],
                                          ['SwitchStatement'],
                                          ['DoStatement'],
                                          ['BreakStatement'],
                                          ['ContinueStatement'],
                                          ['ReturnStatement'],
                                          ['SynchronizedStatement'],
                                          ['ThrowStatement'],
                                          ['TryStatement']],
 'StaticInitializer': [['Static', 'Block']],
 'SuperStuff': [['Extends', 'ClassType']],
 'SwitchBlock': [['LeftBrace',
                  'SwitchBlockStatementGroupsopt',
                  'SwitchLabelsopt',
                  'RightBrace'],
                 ['LeftBrace', 'SwitchBlockStatementGroupsopt', 'RightBrace'],
                 ['LeftBrace', 'SwitchLabelsopt', 'RightBrace'],
                 ['LeftBrace', 'RightBrace']],
 'SwitchBlockStatementGroup': [['SwitchLabels', 'BlockStatements']],
 'SwitchBlockStatementGroups': [['SwitchBlockStatementGroup'],
                                ['SwitchBlockStatementGroups',
                                 'SwitchBlockStatementGroup']],
 'SwitchBlockStatementGroupsopt': [[], ['SwitchBlockStatementGroups']],
 'SwitchLabel': [['Case', 'ConstantExpression', 'ColonOperator'],
                 ['Default', 'ColonOperator']],
 'SwitchLabels': [['SwitchLabel'], ['SwitchLabels', 'SwitchLabel']],
 'SwitchLabelsopt': [[], ['SwitchLabels']],
 'SwitchStatement': [['Switch',
                      'LeftParenthesis',
                      'Expression',
                      'RightParenthesis',
                      'SwitchBlock']],
 'SynchronizedStatement': [['Synchronized',
                            'LeftParenthesis',
                            'Expression',
                            'RightParenthesis',
                            'Block']],
 'ThrowStatement': [['Throw', 'Expression', 'SemiColon']],
 'ThrowsStuff': [['Throws', 'ClassTypeList']],
 'TryStatement': [['Try', 'Block', 'Catches'],
                  ['Try', 'Block', 'Catchesopt', 'FinallyStuff']],
 'Type': [['PrimitiveType'], ['ReferenceType']],
 'TypeDeclaration': [['ClassDeclaration'],
                     ['InterfaceDeclaration'],
                     ['SemiColon']],
 'TypeDeclarations': [['TypeDeclaration'],
                      ['TypeDeclarations', 'TypeDeclaration']],
 'TypeDeclarationsopt': [[], ['TypeDeclarations']],
 'TypeImportOnDemandDeclaration': [['Import',
                                    'Name',
                                    'Dot',
                                    'MultiplyOperator',
                                    'SemiColon']],
 'UnaryExpression': [['AddOperator', 'UnaryExpression'],
                     ['SubtractOperator', 'UnaryExpression'],
                     ['UnaryExpressionNotPlusMinus']],
 'UnaryExpressionNotPlusMinus': [['PostfixExpression'],
                                 ['BinaryNotOperator', 'UnaryExpression'],
                                 ['NotOperator', 'UnaryExpression'],
                                 ['CastExpression']],
 'VariableDeclarator': [['VariableDeclaratorId'],
                        ['VariableDeclaratorId',
                         'DirectAssignmentOperator',
                         'VariableInitializer']],
 'VariableDeclaratorId': [['Identifier'],
                          ['VariableDeclaratorId',
                           'LeftBracket',
                           'RightBracket']],
 'VariableDeclarators': [['VariableDeclarator'],
                         ['VariableDeclarators',
                          'Comma',
                          'VariableDeclarator']],
 'VariableInitializer': [['Expression'], ['ArrayInitializer']],
 'VariableInitializers': [['VariableInitializer'],
                          ['VariableInitializers',
                           'Comma',
                           'VariableInitializer']],
 'WhileStatement': [['While',
                     'LeftParenthesis',
                     'Expression',
                     'RightParenthesis',
                     'Statement']],
 'WhileStatementNoShortIf': [['While',
                              'LeftParenthesis',
                              'Expression',
                              'RightParenthesis',
                              'StatementNoShortIf']]}
