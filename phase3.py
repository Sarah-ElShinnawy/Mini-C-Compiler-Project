class SemanticAnalyzer:
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        self.symbol_table = []
        self.errors = []
        self.scope_stack = ["global"]
        self.current_function = None

    # -------------------------
    # Helpers
    # -------------------------

    def current_scope(self):
        return self.scope_stack[-1]

    def enter_scope(self, scope_name):
        self.scope_stack.append(scope_name)

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def get_children(self, node):
        return node.get("children", [])

    def get_name(self, node):
        return node.get("name", "")

    def is_leaf(self, node, prefix):
        return self.get_name(node).startswith(prefix + ":")

    def leaf_value(self, node):
        if "lexeme" in node:
            return node["lexeme"]

        name = self.get_name(node)
        if ":" in name:
            return name.split(":", 1)[1].strip()
        return name

    def get_node_position(self, node):
        if node is None:
            return None, None

        if "line" in node and "column" in node:
            return node["line"], node["column"]

        for child in self.get_children(node):
            line, column = self.get_node_position(child)
            if line is not None and column is not None:
                return line, column

        return None, None

    def add_error(self, message, node=None):
        line, column = self.get_node_position(node)

        if line is not None and column is not None:
            self.errors.append(
                f"Semantic Error: {message} at line {line}, column {column}"
            )
        else:
            self.errors.append("Semantic Error: " + message)

    def find_first_leaf_node(self, node, prefix):
        if self.is_leaf(node, prefix):
            return node

        for child in self.get_children(node):
            result = self.find_first_leaf_node(child, prefix)
            if result is not None:
                return result

        return None

    def find_first_leaf(self, node, prefix):
        leaf = self.find_first_leaf_node(node, prefix)
        if leaf is not None:
            return self.leaf_value(leaf)
        return None

    def lookup(self, name):
        for scope in reversed(self.scope_stack):
            for symbol in reversed(self.symbol_table):
                if symbol["name"] == name and symbol["scope"] == scope:
                    return symbol

        for symbol in self.symbol_table:
            if symbol["name"] == name and symbol["scope"] == "global":
                return symbol

        return None

    def lookup_current_scope(self, name):
        for symbol in self.symbol_table:
            if symbol["name"] == name and symbol["scope"] == self.current_scope():
                return symbol
        return None

    def add_symbol(self, name, symbol_type, kind, parameters=None, node=None):
        if self.lookup_current_scope(name) is not None:
            self.add_error(
                f"Redeclaration of '{name}' in scope '{self.current_scope()}'",
                node
            )
            return None

        symbol = {
            "name": name,
            "type": symbol_type,
            "kind": kind,
            "scope": self.current_scope(),
            "parameters": parameters if parameters is not None else []
        }

        self.symbol_table.append(symbol)

        if node is not None:
            node["symbol_ref"] = {
                "name": name,
                "type": symbol_type,
                "kind": kind,
                "scope": self.current_scope()
            }

        return symbol

    # -------------------------
    # Main Analyze
    # -------------------------

    def analyze(self):
        self.visit(self.parse_tree)

        if len(self.errors) == 0:
            print("Semantic Analysis Successful. Program is valid.")
        else:
            print("Semantic Analysis Failed.")
            for error in self.errors:
                print(error)

        self.print_symbol_table()

    # -------------------------
    # Visitor
    # -------------------------

    def visit(self, node):
        name = self.get_name(node)

        if name in ["Program", "StatementList", "Statement"]:
            for child in self.get_children(node):
                self.visit(child)

        elif name == "DeclarationOrFunction":
            self.handle_declaration_or_function(node)

        elif name == "Assignment":
            self.handle_assignment(node)

        elif name == "FunctionCall":
            self.handle_function_call(node)

        elif name == "IfStatement":
            self.handle_if_statement(node)

        elif name == "WhileStatement":
            self.handle_while_statement(node)

        elif name == "ForStatement":
            self.handle_for_statement(node)

        elif name == "ReturnStatement":
            self.handle_return_statement(node)

        elif name == "Block":
            self.handle_block(node)

        else:
            for child in self.get_children(node):
                self.visit(child)

    # -------------------------
    # Declarations / Functions
    # -------------------------

    def handle_declaration_or_function(self, node):
        children = self.get_children(node)

        if len(children) < 3:
            self.add_error("Invalid declaration or function structure", node)
            return

        declared_type = self.extract_type(children[0])
        identifier_node = self.find_first_leaf_node(children[1], "Identifier")
        identifier = self.leaf_value(identifier_node) if identifier_node else None
        tail = children[2]

        if identifier is None:
            self.add_error("Missing identifier in declaration", node)
            return

        tail_children = self.get_children(tail)

        if len(tail_children) == 0:
            return

        first = self.get_name(tail_children[0])

        # Variable declaration: int x;
        if first.startswith("Semi Colon"):
            self.add_symbol(identifier, declared_type, "variable", node=identifier_node)
            node["data_type"] = declared_type

        # Variable declaration with assignment: int x = 5;
        elif first.startswith("Assignment Operator"):
            self.add_symbol(identifier, declared_type, "variable", node=identifier_node)

            expression_type = self.evaluate_expression(tail_children[1])
            node["data_type"] = declared_type

            if not self.are_types_compatible(declared_type, expression_type):
                self.add_error(
                    f"Type mismatch in declaration of '{identifier}'. "
                    f"Expected {declared_type} but found {expression_type}",
                    tail_children[1]
                )

        # Function definition: int add(...)
        elif first.startswith("Left Bracket"):
            parameters = self.extract_parameters(tail_children[1])

            self.add_symbol(
                identifier,
                declared_type,
                "function",
                parameters,
                node=identifier_node
            )

            node["data_type"] = declared_type

            previous_function = self.current_function
            self.current_function = {
                "name": identifier,
                "return_type": declared_type
            }

            self.enter_scope(identifier)

            for param in parameters:
                self.add_symbol(
                    param["name"],
                    param["type"],
                    "parameter",
                    node=param.get("node")
                )

            self.visit(tail_children[3])

            self.exit_scope()
            self.current_function = previous_function

    def extract_type(self, type_node):
        result = self.find_first_leaf(type_node, "Keyword")
        type_node["data_type"] = result
        return result

    def extract_parameters(self, parameter_list_node):
        parameters = []
        self.collect_parameters(parameter_list_node, parameters)
        return parameters

    def collect_parameters(self, node, parameters):
        if self.get_name(node) == "Parameter":
            param_type = None
            param_name = None
            param_node = None

            for child in self.get_children(node):
                if self.get_name(child) == "Type":
                    param_type = self.extract_type(child)
                elif self.is_leaf(child, "Identifier"):
                    param_name = self.leaf_value(child)
                    param_node = child

            if param_type is not None and param_name is not None:
                node["data_type"] = param_type
                parameters.append({
                    "name": param_name,
                    "type": param_type,
                    "node": param_node
                })

        for child in self.get_children(node):
            self.collect_parameters(child, parameters)

    # -------------------------
    # Assignments
    # -------------------------

    def handle_assignment(self, node):
        children = self.get_children(node)

        if len(children) < 3:
            self.add_error("Invalid assignment structure", node)
            return

        variable_node = self.find_first_leaf_node(children[0], "Identifier")
        variable_name = self.leaf_value(variable_node) if variable_node else None

        symbol = self.lookup(variable_name)

        if symbol is None:
            self.add_error(
                f"Variable '{variable_name}' used before declaration",
                variable_node
            )
            return

        if symbol["kind"] == "function":
            self.add_error(
                f"Cannot assign value to function '{variable_name}'",
                variable_node
            )
            return

        variable_node["symbol_ref"] = {
            "name": symbol["name"],
            "type": symbol["type"],
            "kind": symbol["kind"],
            "scope": symbol["scope"]
        }

        expression_type = self.evaluate_expression(children[2])
        node["data_type"] = symbol["type"]

        if not self.are_types_compatible(symbol["type"], expression_type):
            self.add_error(
                f"Type mismatch in assignment to '{variable_name}'. "
                f"Expected {symbol['type']} but found {expression_type}",
                children[2]
            )

    # -------------------------
    # Function Calls
    # -------------------------

    def handle_function_call(self, node):
        self.evaluate_function_call(node)

    def evaluate_function_call(self, node):
        children = self.get_children(node)

        if len(children) < 3:
            self.add_error("Invalid function call structure", node)
            node["data_type"] = "unknown"
            return "unknown"

        function_node = self.find_first_leaf_node(children[0], "Identifier")
        function_name = self.leaf_value(function_node) if function_node else None

        symbol = self.lookup(function_name)

        if symbol is None:
            self.add_error(
                f"Function '{function_name}' called before declaration",
                function_node
            )
            node["data_type"] = "unknown"
            return "unknown"

        if symbol["kind"] != "function":
            self.add_error(
                f"'{function_name}' is not a function",
                function_node
            )
            node["data_type"] = "unknown"
            return "unknown"

        function_node["symbol_ref"] = {
            "name": symbol["name"],
            "type": symbol["type"],
            "kind": symbol["kind"],
            "scope": symbol["scope"]
        }

        argument_types = self.extract_argument_types(children[2])
        parameters = symbol["parameters"]

        if len(argument_types) != len(parameters):
            self.add_error(
                f"Function '{function_name}' expects {len(parameters)} arguments "
                f"but got {len(argument_types)}",
                node
            )
        else:
            for i in range(len(argument_types)):
                expected = parameters[i]["type"]
                found = argument_types[i]

                if not self.are_types_compatible(expected, found):
                    self.add_error(
                        f"Argument {i + 1} of function '{function_name}' has wrong type. "
                        f"Expected {expected} but found {found}",
                        node
                    )

        node["data_type"] = symbol["type"]
        return symbol["type"]

    def extract_argument_types(self, argument_list_node):
        argument_types = []
        self.collect_argument_expressions(argument_list_node, argument_types)
        return argument_types

    def collect_argument_expressions(self, node, argument_types):
        if self.get_name(node) == "Expression":
            argument_types.append(self.evaluate_expression(node))
            return

        for child in self.get_children(node):
            self.collect_argument_expressions(child, argument_types)

    # -------------------------
    # Control Statements
    # -------------------------

    def handle_if_statement(self, node):
        children = self.get_children(node)

        condition_type = self.evaluate_condition(children[2])

        if condition_type != "bool":
            self.add_error("If condition must be boolean", children[2])

        self.visit(children[4])
        self.visit(children[5])

    def handle_while_statement(self, node):
        children = self.get_children(node)

        condition_type = self.evaluate_condition(children[2])

        if condition_type != "bool":
            self.add_error("While condition must be boolean", children[2])

        self.visit(children[4])

    def handle_for_statement(self, node):
        self.enter_scope("for_block")

        for child in self.get_children(node):
            self.visit(child)

        self.exit_scope()

    def handle_block(self, node):
        self.enter_scope("block_" + str(len(self.scope_stack)))

        for child in self.get_children(node):
            self.visit(child)

        self.exit_scope()

    # -------------------------
    # Return Statement
    # -------------------------

    def handle_return_statement(self, node):
        if self.current_function is None:
            self.add_error("Return statement outside function", node)
            return

        children = self.get_children(node)

        return_type = "void"

        if len(children) > 1:
            return_type = self.evaluate_return_value(children[1])

        expected_type = self.current_function["return_type"]
        node["data_type"] = return_type

        if not self.are_types_compatible(expected_type, return_type):
            self.add_error(
                f"Wrong return type in function '{self.current_function['name']}'. "
                f"Expected {expected_type} but found {return_type}",
                node
            )

    def evaluate_return_value(self, node):
        for child in self.get_children(node):
            if self.get_name(child) == "Expression":
                return self.evaluate_expression(child)

        node["data_type"] = "void"
        return "void"

    # -------------------------
    # Expressions
    # -------------------------

    def evaluate_expression(self, node):
        types = []
        self.collect_factor_types(node, types)

        if len(types) == 0:
            node["data_type"] = "unknown"
            return "unknown"

        if "string" in types:
            if len(types) > 1:
                self.add_error("Invalid expression using string with arithmetic", node)
            node["data_type"] = "string"
            return "string"

        if "float" in types:
            node["data_type"] = "float"
            return "float"

        if "char" in types:
            node["data_type"] = "char"
            return "char"

        node["data_type"] = "int"
        return "int"

    def collect_factor_types(self, node, types):
        name = self.get_name(node)

        if name.startswith("Integer Literal"):
            node["data_type"] = "int"
            types.append("int")
            return

        if name.startswith("Float Literal"):
            node["data_type"] = "float"
            types.append("float")
            return

        if name.startswith("Character Literal"):
            node["data_type"] = "char"
            types.append("char")
            return

        if name.startswith("String Literal"):
            node["data_type"] = "string"
            types.append("string")
            return

        if name.startswith("Identifier"):
            identifier = self.leaf_value(node)
            symbol = self.lookup(identifier)

            if symbol is None:
                self.add_error(
                    f"Identifier '{identifier}' used before declaration",
                    node
                )
                node["data_type"] = "unknown"
                types.append("unknown")
            else:
                node["data_type"] = symbol["type"]
                node["symbol_ref"] = {
                    "name": symbol["name"],
                    "type": symbol["type"],
                    "kind": symbol["kind"],
                    "scope": symbol["scope"]
                }
                types.append(symbol["type"])

            return

        for child in self.get_children(node):
            self.collect_factor_types(child, types)

    # -------------------------
    # Conditions
    # -------------------------

    def evaluate_condition(self, node):
        expression_types = []
        self.collect_condition_expression_types(node, expression_types)

        for expression_type in expression_types:
            if expression_type == "string":
                self.add_error("Invalid condition: cannot compare string values", node)

        node["data_type"] = "bool"
        return "bool"

    def collect_condition_expression_types(self, node, expression_types):
        if self.get_name(node) == "Expression":
            expression_types.append(self.evaluate_expression(node))
            return

        for child in self.get_children(node):
            self.collect_condition_expression_types(child, expression_types)

    # -------------------------
    # Type Compatibility
    # -------------------------

    def are_types_compatible(self, expected, found):
        if expected == found:
            return True

        if expected == "float" and found == "int":
            return True

        return False

    # -------------------------
    # Output
    # -------------------------

    def print_symbol_table(self):
        print("\nSymbol Table:")
        print("--------------------------------------------")
        print("Name\tType\tKind\tScope\tParameters")
        print("--------------------------------------------")

        for symbol in self.symbol_table:
            params = ""

            if symbol["kind"] == "function":
                param_types = []
                for param in symbol["parameters"]:
                    param_types.append(param["type"])
                params = "(" + ", ".join(param_types) + ")"

            print(
                f"{symbol['name']}\t{symbol['type']}\t{symbol['kind']}\t"
                f"{symbol['scope']}\t{params}"
            )