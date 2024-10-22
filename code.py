import ast
import operator

# Define AST Node structure
class Node:
    def _init_(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type  # "operator" or "operand"
        self.left = left  # Reference to left child (Node)
        self.right = right  # Reference to right child (Node)
        self.value = value  # Value for operand (e.g., condition)

    def _repr_(self):
        if self.node_type == "operand":
            return str(self.value)
        return f"({self.left} {self.value} {self.right})"

# Create a rule (string) into an AST
def create_rule(rule_string):
    # Parse Python-like expression and build AST
    tree = ast.parse(rule_string, mode='eval').body

    def build_ast(node):
        if isinstance(node, ast.BoolOp):
            left = build_ast(node.values[0])
            right = build_ast(node.values[1])
            if isinstance(node.op, ast.And):
                return Node("operator", left, right, "AND")
            elif isinstance(node.op, ast.Or):
                return Node("operator", left, right, "OR")
        elif isinstance(node, ast.Compare):
            left = Node("operand", value=node.left.id)
            right = Node("operand", value=node.comparators[0].n)
            if isinstance(node.ops[0], ast.Gt):
                return Node("operator", left, right, ">")
            elif isinstance(node.ops[0], ast.Lt):
                return Node("operator", left, right, "<")
            elif isinstance(node.ops[0], ast.Eq):
                return Node("operator", left, right, "=")
        return None

    return build_ast(tree)

# Combine multiple rules into a single AST
def combine_rules(rules):
    if not rules:
        return None

    # Create ASTs for all rules
    rule_asts = [create_rule(rule) for rule in rules]

    # Combine them into a single AST using OR (as default operator)
    root = rule_asts[0]
    for rule_ast in rule_asts[1:]:
        root = Node("operator", root, rule_ast, "OR")
    
    return root

# Evaluate AST against user data
def evaluate_rule(ast_node, data):
    operators_map = {
        ">": operator.gt,
        "<": operator.lt,
        "=": operator.eq,
        "AND": lambda a, b: a and b,
        "OR": lambda a, b: a or b
    }

    if ast_node.node_type == "operand":
        return data[ast_node.value]

    # Evaluate left and right nodes recursively
    left_result = evaluate_rule(ast_node.left, data)
    right_result = evaluate_rule(ast_node.right, data)
    
    # Apply operator
    return operators_map[ast_node.value](left_result, right_result)

# Test cases to verify the Rule Engine
if _name_ == "_main_":
    # Sample rules
    rule1 = "((age > 30 and department == 'Sales') or (age < 25 and department == 'Marketing')) and (salary > 50000 or experience > 5)"
    rule2 = "((age > 30 and department == 'Marketing')) and (salary > 20000 or experience > 5)"
    
    # Create individual rules
    ast_rule1 = create_rule(rule1)
    ast_rule2 = create_rule(rule2)

    print("AST for Rule 1:", ast_rule1)
    print("AST for Rule 2:", ast_rule2)

    # Combine rules
    combined_ast = combine_rules([rule1, rule2])
    print("\nCombined AST:", combined_ast)

    # Test data
    user_data_1 = {
        "age": 35,
        "department": "Sales",
        "salary": 60000,
        "experience": 3
    }
    user_data_2 = {
        "age": 32,
        "department": "Marketing",
        "salary": 21000,
        "experience": 6
    }

    # Evaluate rules
    result1 = evaluate_rule(ast_rule1, user_data_1)
    result2 = evaluate_rule(ast_rule2, user_data_2)
    combined_result = evaluate_rule(combined_ast, user_data_1)

    print("\nEvaluation Result for Rule 1 (User 1):", result1)
    print("Evaluation Result for Rule 2 (User 2):", result2)
    print("Evaluation Result for Combined Rule (User 1):", combined_result)
