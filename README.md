# ⚙️ Mini-C Compiler & GUI Suite

A lightweight, 3-phase compiler pipeline for a subset of the C programming language (Mini-C). Built with Python, featuring both a CLI runner and an interactive **Streamlit web interface** with Graphviz parse tree visualizers.

---

## 📌 Features

- **Phase 1: Lexical Analysis (`phase1fixed.py`)**
  - Custom scanner and tokenizer.
  - Recognizes keywords, operators (arithmetic, relational, logical, bitwise), literals (int, float, char, string), identifiers, and separators.
  - Handles single-line (`//`) and multi-line (`/* ... */`) comments.
  - Generates token streams and tracks source code locations (line and column numbers).

- **Phase 2: Syntax Analysis (`phase2.py`)**
  - Recursive Descent Parser based on a LL(1)-adapted clean grammar (`MiniC_Phase2_Clean_Grammar.md`).
  - Left-recursion removed and left-factored to support standard top-down parsing.
  - Handles control flow (`if`/`else`, `while`, `for`), variable declarations, expression trees, and function definitions/calls.
  - Generates a full parse tree dict structure with error recovery (panic mode).

- **Phase 3: Semantic Analysis (`phase3.py`)**
  - Scope management with a dynamic scope stack (`global`, function scopes, block scopes).
  - Symbol table tracking variable/function scopes, data types, and function parameters.
  - Type checking and implicit type conversion verification (e.g., `int` to `float`).
  - Detects duplicate declarations, undeclared variables, function signature mismatches, and return type discrepancies.

- **🎨 Web Dashboard GUI (`App.py`)**
  - Multi-page Streamlit web app.
  - Interactive source code editor with built-in code samples.
  - Graphical render of the **Parse Tree** using Graphviz.
  - Tabular views for Token Streams, Symbol Tables, and Phase-by-Phase Error Logs.

---

## 📂 Repository Structure

```text
├── App.py                            # Streamlit Web App GUI
├── main.py                           # CLI execution entry point
├── phase1fixed.py                    # Phase 1: Lexical Analyzer
├── phase2.py                         # Phase 2: Syntax Analyzer (Parser)
├── phase3.py                         # Phase 3: Semantic Analyzer
└── MiniC_Phase2_Clean_Grammar.md     # Grammar documentation (LL(1) compliant)
