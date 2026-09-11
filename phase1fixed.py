class LexicalAnalyzer:
    def __init__(self):
        self.ArithOp = ["+", "-", "*", "/", "%"]
        self.RelationalOp = ["==", ">", "<", ">=", "<=", "!="]
        self.logOp = ["||", "&&", "!"]
        self.BitwiseOp = ["|", "&", "^", "~", "<<", ">>"]
        self.AssignOp = ["=", "+=", "-=", "*=", "/=", "%="]
        self.Increment_Decrement_Op = ["++", "--"]

        self.keyword = [
            "int", "float", "char", "if", "else", "for",
            "while", "return", "void", "break"
        ]

        self.separators = ["(", ")", "{", "}", ";", ",", "[", "]"]

        self.separator_names = {
            "(": "Left Bracket",
            ")": "Right Bracket",
            "{": "Left Curly Bracket",
            "}": "Right Curly Bracket",
            "[": "Left Square Bracket",
            "]": "Right Square Bracket",
            ",": "Comma",
            ";": "Semi Colon"
        }

        self.token_table = []
        self.symbol_table = {}
        self.errors = []

        self.i = 0
        self.line_number = 1
        self.column_number = 1
        self.current_type = None
        self.in_declaration = False
        self.input_code = ""

    def add_token(self, lexeme, token_type, line=None, column=None):
        if line is None:
            line = self.line_number
        if column is None:
            column = self.column_number

        self.token_table.append({
            "lexeme": lexeme,
            "type": token_type,
            "line": line,
            "column": column
        })

    def advance(self, steps=1):
        for _ in range(steps):
            if self.i < len(self.input_code):
                if self.input_code[self.i] == "\n":
                    self.line_number += 1
                    self.column_number = 1
                else:
                    self.column_number += 1
                self.i += 1

    def get_input(self):
        print("Enter your code line by line. Type 'end' on a new line when finished:")
        lines = []

        while True:
            line = input()
            if line == "end":
                break
            lines.append(line)

        self.input_code = "\n".join(lines)

    def analyze(self, source_code=None):
        if source_code is not None:
            self.input_code = source_code
        else:
            self.get_input()

        self.token_table = []
        self.symbol_table = {}
        self.errors = []

        self.i = 0
        self.line_number = 1
        self.column_number = 1
        self.current_type = None
        self.in_declaration = False

        while self.i < len(self.input_code):
            ch = self.input_code[self.i]

            if self.handle_whitespace(ch):
                continue

            if self.handle_comments():
                continue

            if self.handle_separators(ch):
                continue

            if self.handle_two_char_operators():
                continue

            if self.handle_one_char_operators(ch):
                continue

            if self.handle_identifier_keyword(ch):
                continue

            if ch == '"':
                self.handle_string_literal()
                continue

            if ch == "'":
                self.handle_char_literal()
                continue

            if ch.isdigit():
                self.handle_number()
                continue

            if ch == ".":
                self.handle_period()
                continue

            self.errors.append(
                "Line " + str(self.line_number) +
                ", Column " + str(self.column_number) +
                ": Invalid token '" + ch + "'"
            )
            self.advance()

        return self.token_table, self.symbol_table, self.errors

    def handle_whitespace(self, ch):
        if ch == "\n":
            self.advance()
            return True

        if ch == " " or ch == "\t":
            self.advance()
            return True

        return False

    def handle_comments(self):
        if self.i + 1 < len(self.input_code) and self.input_code[self.i:self.i + 2] == "//":
            self.advance(2)

            while self.i < len(self.input_code) and self.input_code[self.i] != "\n":
                self.advance()

            return True

        if self.i + 1 < len(self.input_code) and self.input_code[self.i:self.i + 2] == "/*":
            start_line = self.line_number
            start_column = self.column_number

            self.advance(2)
            found_end = False

            while self.i < len(self.input_code):
                if self.i + 1 < len(self.input_code) and self.input_code[self.i:self.i + 2] == "*/":
                    self.advance(2)
                    found_end = True
                    break

                self.advance()

            if not found_end:
                self.errors.append(
                    "Line " + str(start_line) +
                    ", Column " + str(start_column) +
                    ": Unterminated multi-line comment"
                )

            return True

        return False

    def handle_separators(self, ch):
        if ch in self.separators:
            self.add_token(ch, self.separator_names[ch])

            if ch == ";":
                self.current_type = None
                self.in_declaration = False

            self.advance()
            return True

        return False

    def handle_two_char_operators(self):
        if self.i + 1 < len(self.input_code):
            two_char = self.input_code[self.i:self.i + 2]
            start_line = self.line_number
            start_column = self.column_number

            if two_char in self.Increment_Decrement_Op:
                self.add_token(two_char, "Increment/Decrement Operator", start_line, start_column)
                self.advance(2)
                return True

            if two_char in self.RelationalOp:
                self.add_token(two_char, "Relational Operator", start_line, start_column)
                self.advance(2)
                return True

            if two_char in self.logOp:
                self.add_token(two_char, "Logical Operator", start_line, start_column)
                self.advance(2)
                return True

            if two_char in self.BitwiseOp:
                self.add_token(two_char, "Bitwise Operator", start_line, start_column)
                self.advance(2)
                return True

            if two_char in self.AssignOp:
                self.add_token(two_char, "Assignment Operator", start_line, start_column)
                self.advance(2)
                return True

        return False

    def handle_one_char_operators(self, ch):
        start_line = self.line_number
        start_column = self.column_number

        if ch in self.AssignOp:
            self.add_token(ch, "Assignment Operator", start_line, start_column)
            self.advance()
            return True

        if ch in self.RelationalOp:
            self.add_token(ch, "Relational Operator", start_line, start_column)
            self.advance()
            return True

        if ch in self.logOp:
            self.add_token(ch, "Logical Operator", start_line, start_column)
            self.advance()
            return True

        if ch in self.BitwiseOp:
            self.add_token(ch, "Bitwise Operator", start_line, start_column)
            self.advance()
            return True

        if ch in self.ArithOp:
            self.add_token(ch, "Arithmetic Operator", start_line, start_column)
            self.advance()
            return True

        return False

    def handle_identifier_keyword(self, ch):
        if ch.isalpha() or ch == "_":
            start_line = self.line_number
            start_column = self.column_number

            word = ""

            while self.i < len(self.input_code) and (
                self.input_code[self.i].isalnum() or self.input_code[self.i] == "_"
            ):
                word += self.input_code[self.i]
                self.advance()

            if word in self.keyword:
                self.add_token(word, "Keyword", start_line, start_column)

                if word in ["int", "float", "char", "void"]:
                    self.current_type = word
                    self.in_declaration = True
            else:
                self.add_token(word, "Identifier", start_line, start_column)

                if self.in_declaration:
                    j = self.i

                    while j < len(self.input_code) and self.input_code[j] in [" ", "\t", "\n"]:
                        j += 1

                    if j < len(self.input_code) and self.input_code[j] == "(":
                        if word not in self.symbol_table:
                            self.symbol_table[word] = self.current_type + " function"
                        self.in_declaration = False
                    else:
                        if word not in self.symbol_table:
                            self.symbol_table[word] = self.current_type

            return True

        return False

    def handle_string_literal(self):
        start_line = self.line_number
        start_column = self.column_number

        string_literal = '"'
        self.advance()

        while self.i < len(self.input_code):
            if self.input_code[self.i] == '"':
                string_literal += '"'
                self.advance()
                self.add_token(string_literal, "String Literal", start_line, start_column)
                return

            if self.input_code[self.i] == "\n":
                self.errors.append(
                    "Line " + str(start_line) +
                    ", Column " + str(start_column) +
                    ": Unterminated string literal"
                )
                return

            if self.input_code[self.i] == "\\" and self.i + 1 < len(self.input_code):
                string_literal += self.input_code[self.i]
                self.advance()
                string_literal += self.input_code[self.i]
                self.advance()
            else:
                string_literal += self.input_code[self.i]
                self.advance()

        self.errors.append(
            "Line " + str(start_line) +
            ", Column " + str(start_column) +
            ": Unterminated string literal"
        )

    def handle_char_literal(self):
        start_line = self.line_number
        start_column = self.column_number

        char_literal = "'"
        self.advance()

        if self.i < len(self.input_code):
            if self.input_code[self.i] == "\\" and self.i + 1 < len(self.input_code):
                char_literal += self.input_code[self.i]
                self.advance()
                char_literal += self.input_code[self.i]
                self.advance()
            else:
                char_literal += self.input_code[self.i]
                self.advance()

        if self.i < len(self.input_code) and self.input_code[self.i] == "'":
            char_literal += "'"
            self.advance()
            self.add_token(char_literal, "Character Literal", start_line, start_column)
        else:
            self.errors.append(
                "Line " + str(start_line) +
                ", Column " + str(start_column) +
                ": Unterminated character literal"
            )

    def handle_number(self):
        start_line = self.line_number
        start_column = self.column_number

        number = ""
        dot_count = 0
        has_exponent = False

        while self.i < len(self.input_code) and (
            self.input_code[self.i].isdigit() or self.input_code[self.i] == "."
        ):
            if self.input_code[self.i] == ".":
                dot_count += 1

            number += self.input_code[self.i]
            self.advance()

        if self.i < len(self.input_code) and self.input_code[self.i] in ["e", "E"]:
            has_exponent = True
            number += self.input_code[self.i]
            self.advance()

            if self.i < len(self.input_code) and self.input_code[self.i] in ["+", "-"]:
                number += self.input_code[self.i]
                self.advance()

            if self.i < len(self.input_code) and self.input_code[self.i].isdigit():
                while self.i < len(self.input_code) and self.input_code[self.i].isdigit():
                    number += self.input_code[self.i]
                    self.advance()
            else:
                self.errors.append(
                    "Line " + str(start_line) +
                    ", Column " + str(start_column) +
                    ": Invalid exponent in number " + number
                )
                return

        suffix = ""

        while self.i < len(self.input_code) and self.input_code[self.i].isalpha():
            suffix += self.input_code[self.i]
            number += self.input_code[self.i]
            self.advance()

        if dot_count > 1:
            self.errors.append(
                "Line " + str(start_line) +
                ", Column " + str(start_column) +
                ": Invalid number " + number
            )
        elif suffix.upper() in ["L", "U", "UL", "LU"]:
            self.add_token(number, "Integer Literal", start_line, start_column)
        elif has_exponent or dot_count == 1:
            self.add_token(number, "Float Literal", start_line, start_column)
        else:
            self.add_token(number, "Integer Literal", start_line, start_column)

    def handle_period(self):
        start_line = self.line_number
        start_column = self.column_number

        next_char = self.input_code[self.i + 1] if self.i + 1 < len(self.input_code) else ""

        if next_char.isdigit():
            number = "."
            self.advance()

            while self.i < len(self.input_code) and self.input_code[self.i].isdigit():
                number += self.input_code[self.i]
                self.advance()

            self.errors.append(
                "Line " + str(start_line) +
                ", Column " + str(start_column) +
                ": Invalid token '" + number + "' - number cannot start with a dot"
            )
        else:
            self.errors.append(
                "Line " + str(start_line) +
                ", Column " + str(start_column) +
                ": Invalid token '.'"
            )
            self.advance()

    def print_results(self):
        print("\nTokens:")
        for token in self.token_table:
            print(token)

        print("\nSymbol Table:")
        for name, typ in self.symbol_table.items():
            print(name, ":", typ)

        print("\nErrors:")
        if len(self.errors) == 0:
            print("No lexical errors found.")
        else:
            for error in self.errors:
                print(error)


if __name__ == "__main__":
    lexer = LexicalAnalyzer()
    lexer.analyze()
    lexer.print_results()