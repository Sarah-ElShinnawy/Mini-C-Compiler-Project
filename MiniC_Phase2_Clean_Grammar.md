# Mini C Grammar for Recursive Descent Parser

## Original Grammar Problems

The original grammar from Phase 2 had several issues:

1. Some grammar rules were missing.
2. The grammar had left recursion.
3. Some rules had common prefixes and needed left factoring.
4. The `Block` rule was used but not defined.
5. Parameter and argument rules were missing.
6. Nested statements needed clearer support.

---

# Final Clean Grammar

```text
Program → StatementList EOF

StatementList → Statement StatementList
              | ε

Statement → DeclarationOrFunction
          | Assignment
          | IfStatement
          | WhileStatement
          | ForStatement
          | FunctionCall
          | ReturnStatement
          | Block

Block → '{' StatementList '}'

DeclarationOrFunction → Type Identifier DeclarationOrFunctionTail

DeclarationOrFunctionTail → ';'
                          | '=' Expression ';'
                          | '(' ParameterList ')' Block

Type → int
     | float
     | char
     | void

Assignment → Identifier '=' Expression ';'

IfStatement → 'if' '(' Condition ')' Block ElsePart

ElsePart → 'else' Block
         | ε

WhileStatement → 'while' '(' Condition ')' Block

ForStatement → 'for' '(' ForInit Condition ';' ForUpdate ')' Block

ForInit → DeclarationNoSemi
        | AssignmentNoSemi
        | ';'

DeclarationNoSemi → Type Identifier DeclarationNoSemiTail

DeclarationNoSemiTail → '=' Expression ';'
                       | ';'

AssignmentNoSemi → Identifier '=' Expression ';'

ForUpdate → Identifier '=' Expression
          | Identifier '++'
          | Identifier '--'
          | Expression
          | ε

FunctionCall → Identifier '(' ArgumentList ')' ';'

ReturnStatement → 'return' ReturnValue ';'

ReturnValue → Expression
            | ε

ParameterList → Parameter ParameterListTail
              | ε

ParameterListTail → ',' Parameter ParameterListTail
                  | ε

Parameter → Type Identifier

ArgumentList → Expression ArgumentListTail
             | ε

ArgumentListTail → ',' Expression ArgumentListTail
                 | ε

Expression → Term ExpressionTail

ExpressionTail → '+' Term ExpressionTail
               | '-' Term ExpressionTail
               | ε

Term → Factor TermTail

TermTail → '*' Factor TermTail
         | '/' Factor TermTail
         | '%' Factor TermTail
         | ε

Factor → Identifier FactorTail
       | Number
       | CharacterLiteral
       | StringLiteral
       | '(' Expression ')'

FactorTail → '(' ArgumentList ')'
           | ε

Condition → LogicalOr

LogicalOr → LogicalAnd LogicalOrTail

LogicalOrTail → '||' LogicalAnd LogicalOrTail
              | ε

LogicalAnd → NotCondition LogicalAndTail

LogicalAndTail → '&&' NotCondition LogicalAndTail
               | ε

NotCondition → '!' NotCondition
             | RelCondition

RelCondition → Expression RelConditionTail
             | '(' Condition ')'

RelConditionTail → RelOp Expression
                 | ε

RelOp → '=='
      | '!='
      | '<'
      | '>'
      | '<='
      | '>='
```

---

# Changes Made to the Original Grammar

## 1. Added Missing Rules

The original grammar was incomplete. The following rules were added:

```text
Block
Type
ParameterList
Parameter
ArgumentList
FactorTail
DeclarationNoSemi
AssignmentNoSemi
ForInit
ForUpdate
ReturnValue
```

These rules were necessary because:

- Functions require parameters.
- Function calls require arguments.
- Nested statements require blocks.
- For loops require initialization and update rules.
- Recursive descent parsing needs complete productions.

---

## 2. Added the Block Rule

The original grammar used `Block`, but it did not define it.

Added:

```text
Block → '{' StatementList '}'
```

This allows nested statements such as:

```c
if (x > 0) {
    int y = 5;
}
```

---

## 3. Added EOF

Added:

```text
Program → StatementList EOF
```

This ensures that the parser checks the whole input program.

Without `EOF`, a program like this might incorrectly pass:

```c
int x = 5; @@@
```

---

## 4. Added Function Definitions into Statements

The original grammar had `FunctionDef`, but it was not reachable from `Statement`.

Instead of keeping a separate unreachable rule, I combined declaration and function definition into:

```text
Statement → DeclarationOrFunction
```

Then:

```text
DeclarationOrFunction → Type Identifier DeclarationOrFunctionTail
```

This allows both variable declarations and function definitions.

---

## 5. Added Function Parameters

The original grammar had:

```text
FunctionDef → Type Identifier '(' ParameterList ')' Block
```

but `ParameterList` was not defined.

Added:

```text
ParameterList → Parameter ParameterListTail | ε
ParameterListTail → ',' Parameter ParameterListTail | ε
Parameter → Type Identifier
```

Example:

```c
int add(int a, int b) {
    return a + b;
}
```

---

## 6. Added Function Arguments

The original grammar had:

```text
FunctionCall → Identifier '(' ArgumentList ')' ';'
```

but `ArgumentList` was not defined.

Added:

```text
ArgumentList → Expression ArgumentListTail | ε
ArgumentListTail → ',' Expression ArgumentListTail | ε
```

Example:

```c
add(x, y + 5);
```

---

# Left Recursion Removal

## Original Problem

The original grammar had this rule:

```text
Condition → Condition LogicalOp Condition
          | '!' Condition
          | Expression RelOp Expression
```

This is left recursive because `Condition` appears first on the right-hand side:

```text
Condition → Condition ...
```

Recursive descent parsers cannot handle left recursion because it can cause infinite recursion.

---

## Left Recursion Rule Used

The standard rule is:

```text
A → Aα | β

becomes

A → βA'
A' → αA' | ε
```

---

## Transformation Applied

The problematic part was:

```text
Condition → Condition LogicalOp Condition
```

I changed it into levels:

```text
Condition → LogicalOr

LogicalOr → LogicalAnd LogicalOrTail

LogicalOrTail → '||' LogicalAnd LogicalOrTail
              | ε

LogicalAnd → NotCondition LogicalAndTail

LogicalAndTail → '&&' NotCondition LogicalAndTail
               | ε
```

This removes left recursion and also gives correct logical operator precedence:

1. `!`
2. `&&`
3. `||`

---

# Left Factoring

## Original Problem

The original grammar had rules like:

```text
Declaration → Type Identifier ';'
            | Type Identifier '=' Expression ';'
            | Type Identifier '(' ParameterList ')' Block
```

All productions start with:

```text
Type Identifier
```

This creates a common prefix problem. A recursive descent parser would not immediately know which rule to choose.

---

## Left Factoring Rule Used

The standard rule is:

```text
A → αβ1 | αβ2

becomes

A → αA'
A' → β1 | β2
```

Another simple version is:

```text
A → αβ | α

becomes

A → αA'
A' → β | ε
```

---

## Transformation Applied

Original:

```text
Declaration → Type Identifier ';'
            | Type Identifier '=' Expression ';'
            | Type Identifier '(' ParameterList ')' Block
```

Converted into:

```text
DeclarationOrFunction → Type Identifier DeclarationOrFunctionTail

DeclarationOrFunctionTail → ';'
                          | '=' Expression ';'
                          | '(' ParameterList ')' Block
```

Now the parser matches `Type Identifier` once, then checks the next token.

---

# Lookahead Conflicts

Another conflict exists between assignment and function call:

```text
Assignment → Identifier '=' Expression ';'
FunctionCall → Identifier '(' ArgumentList ')' ';'
```

Both start with:

```text
Identifier
```

This is handled in the parser using one-token lookahead.

Example:

```python
if current_token["type"] == "Identifier":
    if next_token["lexeme"] == "=":
        parse_assignment()
    elif next_token["lexeme"] == "(":
        parse_function_call()
```

---

# Why This Grammar Works for Recursive Descent Parsing

This grammar is suitable for a Recursive Descent Parser because it is:

- Non-left-recursive
- Left-factored
- Easier to implement manually
- Compatible with one-token lookahead
- Able to support nested statements
- Able to support function definitions
- Able to support function calls
- Able to support arithmetic expressions
- Able to support complex conditions

Each grammar rule can be implemented as one parser function, for example:

```python
parse_program()
parse_statement_list()
parse_statement()
parse_expression()
parse_condition()
parse_block()
```
