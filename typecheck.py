from utils import node

# This function should be called for each statement in a method body.
def typecheck_statement(class_env, local_env, return_type, statement):
    pass

#
# Type check functions.
# Each type check function must do the following:
# 1. Determine the correct type of the input node.
# 2. Assign the above type to the input node.
# 3. Return the assigned type, so that it can be used by the caller.

# This function is called by typecheck_statement on a single expression.
def typecheck(class_env, local_env, return_type, node):
    pass
