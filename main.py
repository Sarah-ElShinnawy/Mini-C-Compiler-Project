"""
MiniC Compiler - Main Runner
Runs Phase 1 (Lexical), Phase 2 (Syntax), Phase 3 (Semantic)
then generates a full Word (.docx) report.
"""

import sys
import io
from contextlib import redirect_stdout

# ── Import the three phases ────────────────────────────────────────────────────
from phase1fixed import LexicalAnalyzer
from phase2 import SyntaxAnalysis
from phase3 import SemanticAnalyzer

# ══════════════════════════════════════════════════════════════════════════════
# Sample Mini-C programme used as input
# ══════════════════════════════════════════════════════════════════════════════
SAMPLE_CODE = """\
int add(int a, int b) {
    int result = a + b;
    return result;
}

float average(int x, int y) {
    float sum = x + y;
    return sum;
}

int main() {
    int num1 = 10;
    int num2 = 20;
    int total = add(num1, num2);

    if (total > 15) {
        int big = 1;
    } else {
        int small = 0;
    }

    int i;
    for (i = 0; i < 5; i++) {
        int square = i * i;
    }

    int count = 0;
    while (count < 3) {
        count = count + 1;
    }

    return 0;
}
"""

# ══════════════════════════════════════════════════════════════════════════════
# Helper: capture stdout of a callable
# ══════════════════════════════════════════════════════════════════════════════
def capture(fn):
    buf = io.StringIO()
    with redirect_stdout(buf):
        result = fn()
    return result, buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 – Lexical Analysis
# ══════════════════════════════════════════════════════════════════════════════
def run_phase1(source_code):
    print("=" * 60)
    print("PHASE 1 – LEXICAL ANALYSIS")
    print("=" * 60)

    lexer = LexicalAnalyzer()
    tokens, symbol_table, lex_errors = lexer.analyze(source_code)

    print(f"  Tokens produced : {len(tokens)}")
    print(f"  Lexical errors  : {len(lex_errors)}")

    if lex_errors:
        for e in lex_errors:
            print("  !", e)
    else:
        print("  No lexical errors.")

    return tokens, symbol_table, lex_errors


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 – Syntax Analysis
# ══════════════════════════════════════════════════════════════════════════════
def run_phase2(tokens):
    print()
    print("=" * 60)
    print("PHASE 2 – SYNTAX ANALYSIS (PARSING)")
    print("=" * 60)

    parser = SyntaxAnalysis(tokens)
    parse_tree, console_output = capture(parser.Program)

    print(console_output.strip())
    print(f"  Syntax errors   : {len(parser.errors)}")

    return parse_tree, parser.errors


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 – Semantic Analysis
# ══════════════════════════════════════════════════════════════════════════════
def run_phase3(parse_tree):
    print()
    print("=" * 60)
    print("PHASE 3 – SEMANTIC ANALYSIS")
    print("=" * 60)

    analyzer = SemanticAnalyzer(parse_tree)
    _, console_output = capture(analyzer.analyze)

    print(console_output.strip())
    print(f"  Semantic errors : {len(analyzer.errors)}")

    return analyzer.symbol_table, analyzer.errors


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # Accept optional path to a .c source file as argument
    if len(sys.argv) > 1:
        src_path = sys.argv[1]
        try:
            with open(src_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            print(f"Using source file: {src_path}")
        except FileNotFoundError:
            print(f"File not found: {src_path}. Using built-in sample.")
            source_code = SAMPLE_CODE
    else:
        # ── FIX: let the user type (or paste) their Mini-C code directly.
        #        Keep reading lines until the user types "end" on its own line.
        print("Enter your Mini-C code below.")
        print('When finished, type  end  on a new line and press Enter.\n')
        lines = []
        while True:
            line = input()
            if line.strip().lower() == "end":   # sentinel – stop collecting
                break
            lines.append(line)
        source_code = "\n".join(lines)

        # Fall back to the built-in sample if the user entered nothing
        if not source_code.strip():
            print("No code entered – using built-in sample Mini-C program.\n")
            source_code = SAMPLE_CODE
        # ─────────────────────────────────────────────────────────────────────

    # ── Run all three phases ───────────────────────────────────────────────
    tokens, lex_sym_table, lex_errors = run_phase1(source_code)

    if not tokens:
        print("\nNo tokens produced. Aborting.")
        sys.exit(1)

    parse_tree, syn_errors = run_phase2(tokens)
    symbol_table, sem_errors = run_phase3(parse_tree)

    # ── Summary ────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("COMPILATION SUMMARY")
    print("=" * 60)
    total_errors = len(lex_errors) + len(syn_errors) + len(sem_errors)
    if total_errors == 0:
        print("  ✔  All phases passed successfully.")
    else:
        print(f"  ✘  {total_errors} total error(s) found.")


if __name__ == "__main__":
    main()