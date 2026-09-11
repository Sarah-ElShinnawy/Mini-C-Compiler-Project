class SyntaxAnalysis:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.errors = []

    def make_node(self, name, children=None, line=None, column=None, lexeme=None, token_type=None):
        node = {
            "name": name,
            "children": children if children is not None else []
        }

        if line is not None:
            node["line"] = line

        if column is not None:
            node["column"] = column

        if lexeme is not None:
            node["lexeme"] = lexeme

        if token_type is not None:
            node["token_type"] = token_type

        return node

    def current_token(self):
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None

    def peek_token(self):
        if self.current_index + 1 < len(self.tokens):
            return self.tokens[self.current_index + 1]
        return None

    def advance(self):
        if self.current_index < len(self.tokens):
            self.current_index += 1

    def error(self, message):
        token = self.current_token()
        if token is not None:
            self.errors.append(
                f"Syntax Error: {message} at line {token['line']}, column {token['column']}"
            )
        else:
            self.errors.append(f"Syntax Error: {message} at end of file")

    def panic_mode(self):
        while self.current_token() is not None:
            token = self.current_token()

            if token["lexeme"] == ";":
                self.advance()
                return

            if token["lexeme"] == "}":
                return

            self.advance()

    def match_lexeme(self, expected_lexeme):
        token = self.current_token()

        if token is not None and token["lexeme"] == expected_lexeme:
            leaf = self.make_node(
                f"{token['type']}: {token['lexeme']}",
                line=token["line"],
                column=token["column"],
                lexeme=token["lexeme"],
                token_type=token["type"]
            )
            self.advance()
            return leaf

        found = token["lexeme"] if token is not None else "EOF"
        self.error(f"Expected '{expected_lexeme}' but found '{found}'")

        if expected_lexeme in [";", ")", "}"]:
            self.panic_mode()

        return self.make_node(f"Error: expected {expected_lexeme}")

    def match_type(self, expected_type):
        token = self.current_token()

        if token is not None and token["type"] == expected_type:
            leaf = self.make_node(
                f"{token['type']}: {token['lexeme']}",
                line=token["line"],
                column=token["column"],
                lexeme=token["lexeme"],
                token_type=token["type"]
            )
            self.advance()
            return leaf

        found = token["type"] if token is not None else "EOF"
        self.error(f"Expected token type '{expected_type}' but found '{found}'")

        self.panic_mode()

        return self.make_node(f"Error: expected {expected_type}")

    def EOF(self):
        if self.current_token() is not None:
            self.error("Expected end of file")
        return self.make_node("EOF")

    def Program(self):
        node = self.make_node("Program")
        node["children"].append(self.StatementList())
        node["children"].append(self.EOF())

        if len(self.errors) == 0:
            print("Parsing Successful")
        else:
            print("Parsing Failed")
            for error in self.errors:
                print(error)

        return node

    def StatementList(self):
        node = self.make_node("StatementList")

        if self.is_statement_start():
            node["children"].append(self.Statement())
            node["children"].append(self.StatementList())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def is_statement_start(self):
        token = self.current_token()

        if token is None:
            return False

        lexeme = token["lexeme"]
        token_type = token["type"]

        if lexeme in ["int", "float", "char", "void"]:
            return True

        if token_type == "Identifier":
            return True

        if lexeme in ["if", "while", "for", "return", "{"]:
            return True

        return False

    def Statement(self):
        node = self.make_node("Statement")
        token = self.current_token()

        if token is None:
            node["children"].append(self.make_node("ε"))
            return node

        lexeme = token["lexeme"]

        if self.is_DeclarationOrFunction():
            node["children"].append(self.DeclarationOrFunction())

        elif self.is_Assignment():
            node["children"].append(self.Assignment())

        elif lexeme == "if":
            node["children"].append(self.IfStatement())

        elif lexeme == "while":
            node["children"].append(self.WhileStatement())

        elif lexeme == "for":
            node["children"].append(self.ForStatement())

        elif self.is_FunctionCall():
            node["children"].append(self.FunctionCall())

        elif lexeme == "return":
            node["children"].append(self.ReturnStatement())

        elif lexeme == "{":
            node["children"].append(self.Block())

        else:
            self.error("Unexpected statement")
            self.advance()

        return node

    def is_DeclarationOrFunction(self):
        token = self.current_token()
        return token is not None and token["lexeme"] in ["int", "float", "char", "void"]

    def is_Assignment(self):
        token = self.current_token()
        next_token = self.peek_token()
        return (
            token is not None
            and next_token is not None
            and token["type"] == "Identifier"
            and next_token["lexeme"] == "="
        )

    def is_FunctionCall(self):
        token = self.current_token()
        next_token = self.peek_token()
        return (
            token is not None
            and next_token is not None
            and token["type"] == "Identifier"
            and next_token["lexeme"] == "("
        )

    def Block(self):
        node = self.make_node("Block")
        node["children"].append(self.match_lexeme("{"))
        node["children"].append(self.StatementList())
        node["children"].append(self.match_lexeme("}"))
        return node

    def DeclarationOrFunction(self):
        node = self.make_node("DeclarationOrFunction")
        node["children"].append(self.Type())
        node["children"].append(self.match_type("Identifier"))
        node["children"].append(self.DeclarationOrFunctionTail())
        return node

    def DeclarationOrFunctionTail(self):
        node = self.make_node("DeclarationOrFunctionTail")
        token = self.current_token()

        if token is None:
            self.error("Expected declaration or function tail")
            return node

        if token["lexeme"] == ";":
            node["children"].append(self.match_lexeme(";"))

        elif token["lexeme"] == "=":
            node["children"].append(self.match_lexeme("="))
            node["children"].append(self.Expression())
            node["children"].append(self.match_lexeme(";"))

        elif token["lexeme"] == "(":
            node["children"].append(self.match_lexeme("("))
            node["children"].append(self.ParameterList())
            node["children"].append(self.match_lexeme(")"))
            node["children"].append(self.Block())

        else:
            self.error("Expected ';', '=', or '(' after identifier")

        return node

    def Type(self):
        node = self.make_node("Type")
        token = self.current_token()

        if token is not None and token["lexeme"] in ["int", "float", "char", "void"]:
            node["children"].append(self.match_lexeme(token["lexeme"]))
        else:
            self.error("Expected type")

        return node

    def Assignment(self):
        node = self.make_node("Assignment")
        node["children"].append(self.match_type("Identifier"))
        node["children"].append(self.match_lexeme("="))
        node["children"].append(self.Expression())
        node["children"].append(self.match_lexeme(";"))
        return node

    def IfStatement(self):
        node = self.make_node("IfStatement")
        node["children"].append(self.match_lexeme("if"))
        node["children"].append(self.match_lexeme("("))
        node["children"].append(self.Condition())
        node["children"].append(self.match_lexeme(")"))
        node["children"].append(self.Block())
        node["children"].append(self.ElsePart())
        return node

    def ElsePart(self):
        node = self.make_node("ElsePart")
        token = self.current_token()

        if token is not None and token["lexeme"] == "else":
            node["children"].append(self.match_lexeme("else"))
            node["children"].append(self.Block())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def WhileStatement(self):
        node = self.make_node("WhileStatement")
        node["children"].append(self.match_lexeme("while"))
        node["children"].append(self.match_lexeme("("))
        node["children"].append(self.Condition())
        node["children"].append(self.match_lexeme(")"))
        node["children"].append(self.Block())
        return node

    def ForStatement(self):
        node = self.make_node("ForStatement")
        node["children"].append(self.match_lexeme("for"))
        node["children"].append(self.match_lexeme("("))
        node["children"].append(self.ForInit())
        node["children"].append(self.Condition())
        node["children"].append(self.match_lexeme(";"))
        node["children"].append(self.ForUpdate())
        node["children"].append(self.match_lexeme(")"))
        node["children"].append(self.Block())
        return node

    def ForInit(self):
        node = self.make_node("ForInit")
        token = self.current_token()

        if token is None:
            self.error("Expected for-loop initialization")
            return node

        if self.is_DeclarationOrFunction():
            node["children"].append(self.DeclarationNoSemi())

        elif self.is_Assignment():
            node["children"].append(self.AssignmentNoSemi())

        elif token["lexeme"] == ";":
            node["children"].append(self.match_lexeme(";"))

        else:
            self.error("Invalid for-loop initialization")

        return node

    def DeclarationNoSemi(self):
        node = self.make_node("DeclarationNoSemi")
        node["children"].append(self.Type())
        node["children"].append(self.match_type("Identifier"))
        node["children"].append(self.DeclarationNoSemiTail())
        return node

    def DeclarationNoSemiTail(self):
        node = self.make_node("DeclarationNoSemiTail")
        token = self.current_token()

        if token is not None and token["lexeme"] == "=":
            node["children"].append(self.match_lexeme("="))
            node["children"].append(self.Expression())
            node["children"].append(self.match_lexeme(";"))
        else:
            node["children"].append(self.match_lexeme(";"))

        return node

    def AssignmentNoSemi(self):
        node = self.make_node("AssignmentNoSemi")
        node["children"].append(self.match_type("Identifier"))
        node["children"].append(self.match_lexeme("="))
        node["children"].append(self.Expression())
        node["children"].append(self.match_lexeme(";"))
        return node

    def ForUpdate(self):
        node = self.make_node("ForUpdate")
        token = self.current_token()
        next_token = self.peek_token()

        if token is None:
            node["children"].append(self.make_node("ε"))
            return node

        if next_token is not None and token["type"] == "Identifier" and next_token["lexeme"] == "=":
            node["children"].append(self.match_type("Identifier"))
            node["children"].append(self.match_lexeme("="))
            node["children"].append(self.Expression())

        elif next_token is not None and token["type"] == "Identifier" and next_token["lexeme"] == "++":
            node["children"].append(self.match_type("Identifier"))
            node["children"].append(self.match_lexeme("++"))

        elif next_token is not None and token["type"] == "Identifier" and next_token["lexeme"] == "--":
            node["children"].append(self.match_type("Identifier"))
            node["children"].append(self.match_lexeme("--"))

        elif self.is_expression_start():
            node["children"].append(self.Expression())

        else:
            node["children"].append(self.make_node("ε"))

        return node

    def FunctionCall(self):
        node = self.make_node("FunctionCall")
        node["children"].append(self.match_type("Identifier"))
        node["children"].append(self.match_lexeme("("))
        node["children"].append(self.ArgumentList())
        node["children"].append(self.match_lexeme(")"))
        node["children"].append(self.match_lexeme(";"))
        return node

    def ReturnStatement(self):
        node = self.make_node("ReturnStatement")
        node["children"].append(self.match_lexeme("return"))
        node["children"].append(self.ReturnValue())
        node["children"].append(self.match_lexeme(";"))
        return node

    def ReturnValue(self):
        node = self.make_node("ReturnValue")

        if self.is_expression_start():
            node["children"].append(self.Expression())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def ParameterList(self):
        node = self.make_node("ParameterList")
        token = self.current_token()

        if token is not None and token["lexeme"] in ["int", "float", "char", "void"]:
            node["children"].append(self.Parameter())
            node["children"].append(self.ParameterListTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def ParameterListTail(self):
        node = self.make_node("ParameterListTail")
        token = self.current_token()

        if token is not None and token["lexeme"] == ",":
            node["children"].append(self.match_lexeme(","))
            node["children"].append(self.Parameter())
            node["children"].append(self.ParameterListTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def Parameter(self):
        node = self.make_node("Parameter")
        node["children"].append(self.Type())
        node["children"].append(self.match_type("Identifier"))
        return node

    def ArgumentList(self):
        node = self.make_node("ArgumentList")

        if self.is_expression_start():
            node["children"].append(self.Expression())
            node["children"].append(self.ArgumentListTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def ArgumentListTail(self):
        node = self.make_node("ArgumentListTail")
        token = self.current_token()

        if token is not None and token["lexeme"] == ",":
            node["children"].append(self.match_lexeme(","))
            node["children"].append(self.Expression())
            node["children"].append(self.ArgumentListTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def Expression(self):
        node = self.make_node("Expression")
        node["children"].append(self.Term())
        node["children"].append(self.ExpressionTail())
        return node

    def ExpressionTail(self):
        node = self.make_node("ExpressionTail")
        token = self.current_token()

        if token is not None and token["lexeme"] in ["+", "-"]:
            node["children"].append(self.match_lexeme(token["lexeme"]))
            node["children"].append(self.Term())
            node["children"].append(self.ExpressionTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def Term(self):
        node = self.make_node("Term")
        node["children"].append(self.Factor())
        node["children"].append(self.TermTail())
        return node

    def TermTail(self):
        node = self.make_node("TermTail")
        token = self.current_token()

        if token is not None and token["lexeme"] in ["*", "/", "%"]:
            node["children"].append(self.match_lexeme(token["lexeme"]))
            node["children"].append(self.Factor())
            node["children"].append(self.TermTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def Factor(self):
        node = self.make_node("Factor")
        token = self.current_token()

        if token is None:
            self.error("Expected factor")
            return node

        if token["type"] == "Identifier":
            node["children"].append(self.match_type("Identifier"))
            node["children"].append(self.FactorTail())

        elif token["type"] in ["Integer Literal", "Float Literal"]:
            node["children"].append(self.match_type(token["type"]))

        elif token["type"] == "Character Literal":
            node["children"].append(self.match_type("Character Literal"))

        elif token["type"] == "String Literal":
            node["children"].append(self.match_type("String Literal"))

        elif token["lexeme"] == "(":
            node["children"].append(self.match_lexeme("("))
            node["children"].append(self.Expression())
            node["children"].append(self.match_lexeme(")"))

        else:
            self.error("Expected identifier, number, string, character, or '('")

        return node

    def FactorTail(self):
        node = self.make_node("FactorTail")
        token = self.current_token()

        if token is not None and token["lexeme"] == "(":
            node["children"].append(self.match_lexeme("("))
            node["children"].append(self.ArgumentList())
            node["children"].append(self.match_lexeme(")"))
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def is_expression_start(self):
        token = self.current_token()

        if token is None:
            return False

        if token["type"] in [
            "Identifier",
            "Integer Literal",
            "Float Literal",
            "Character Literal",
            "String Literal"
        ]:
            return True

        if token["lexeme"] == "(":
            return True

        return False

    def Condition(self):
        node = self.make_node("Condition")
        node["children"].append(self.LogicalOr())
        return node

    def LogicalOr(self):
        node = self.make_node("LogicalOr")
        node["children"].append(self.LogicalAnd())
        node["children"].append(self.LogicalOrTail())
        return node

    def LogicalOrTail(self):
        node = self.make_node("LogicalOrTail")
        token = self.current_token()

        if token is not None and token["lexeme"] == "||":
            node["children"].append(self.match_lexeme("||"))
            node["children"].append(self.LogicalAnd())
            node["children"].append(self.LogicalOrTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def LogicalAnd(self):
        node = self.make_node("LogicalAnd")
        node["children"].append(self.NotCondition())
        node["children"].append(self.LogicalAndTail())
        return node

    def LogicalAndTail(self):
        node = self.make_node("LogicalAndTail")
        token = self.current_token()

        if token is not None and token["lexeme"] == "&&":
            node["children"].append(self.match_lexeme("&&"))
            node["children"].append(self.NotCondition())
            node["children"].append(self.LogicalAndTail())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def NotCondition(self):
        node = self.make_node("NotCondition")
        token = self.current_token()

        if token is not None and token["lexeme"] == "!":
            node["children"].append(self.match_lexeme("!"))
            node["children"].append(self.NotCondition())
        else:
            node["children"].append(self.RelCondition())

        return node

    def RelCondition(self):
        node = self.make_node("RelCondition")
        token = self.current_token()

        if token is not None and token["lexeme"] == "(":
            node["children"].append(self.match_lexeme("("))
            node["children"].append(self.Condition())
            node["children"].append(self.match_lexeme(")"))
        else:
            node["children"].append(self.Expression())
            node["children"].append(self.RelConditionTail())

        return node

    def RelConditionTail(self):
        node = self.make_node("RelConditionTail")
        token = self.current_token()

        if token is not None and token["lexeme"] in ["==", "!=", "<", ">", "<=", ">="]:
            node["children"].append(self.RelOp())
            node["children"].append(self.Expression())
        else:
            node["children"].append(self.make_node("ε"))

        return node

    def RelOp(self):
        node = self.make_node("RelOp")
        token = self.current_token()

        if token is not None and token["lexeme"] in ["==", "!=", "<", ">", "<=", ">="]:
            node["children"].append(self.match_lexeme(token["lexeme"]))
        else:
            self.error("Expected relational operator")

        return node

    def print_tree(self, node, level=0):
        print("  " * level + node["name"])
        for child in node["children"]:
            self.print_tree(child, level + 1)