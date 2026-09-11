"""
MiniC Compiler – Streamlit GUI  (app.py)
Run with:  streamlit run app.py
Requires:  phase1fixed.py  phase2.py  phase3.py  in the same folder.
"""

import io
import streamlit as st
import graphviz
from contextlib import redirect_stdout

from phase1fixed import LexicalAnalyzer
from phase2      import SyntaxAnalysis
from phase3      import SemanticAnalyzer

# ══════════════════════════════════════════════════════════════════════════════
# Page config
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Mini-C Compiler - Three Phase Analysis",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# Custom CSS – Modern light theme with soft background
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── global reset & base ── */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #fef9f0 0%, #fdf4e8 100%);
    color: #2d3a4a;
}

/* ── sidebar styling ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #fef9f0 100%);
    border-right: 2px solid #f0e6d2;
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #2d3a4a;
}

/* Sidebar title */
.sidebar-title {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c9a03d 0%, #b8860b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 1rem 0 0.5rem 0;
    text-align: center;
    border-bottom: 2px solid #f0e6d2;
    margin-bottom: 1.5rem;
}

/* Navigation menu items */
.nav-item {
    padding: 0.75rem 1rem;
    margin: 0.25rem 0;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
    color: #5a6e8a;
    background: transparent;
}
.nav-item:hover {
    background: linear-gradient(135deg, #fff8f0 0%, #fef5e8 100%);
    color: #c9a03d;
    transform: translateX(5px);
}
.nav-item-active {
    background: linear-gradient(135deg, #fff8f0 0%, #fef0e0 100%);
    color: #b8860b;
    border-left: 3px solid #c9a03d;
    font-weight: 600;
}

/* ── main header with gold accent ── */
.main-header {
    background: linear-gradient(135deg, #ffffff 0%, #fef9f0 100%);
    border: 1px solid rgba(201, 160, 61, 0.2);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02), 0 1px 2px rgba(0, 0, 0, 0.05);
}
.main-header h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c9a03d 0%, #b8860b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.02em;
}
.main-header p {
    color: #7a8a9a;
    margin: 0.5rem 0 0;
    font-size: 0.9rem;
}

/* ── phase cards ── */
.phase-container {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(5px);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #f0e6d2;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.phase-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, #c9a03d 0%, #b8860b 100%);
    border-radius: 12px;
    padding: 0.5rem 1.2rem;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: white;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 8px rgba(201, 160, 61, 0.2);
}

/* ── status pills ── */
.status-pass {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}
.status-fail {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

/* ── metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #fefaf5 100%);
    border: 1px solid #f0e6d2;
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #c9a03d, #b8860b, #e6b84e);
    border-radius: 16px 16px 0 0;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(201, 160, 61, 0.1);
}
.metric-card .val {
    font-family: 'Inter', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #c9a03d 0%, #b8860b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.metric-card .lbl {
    font-size: 0.7rem;
    color: #7a8a9a;
    margin-top: 0.4rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── code editor ── */
.stTextArea textarea {
    background: #ffffff !important;
    color: #2d3a4a !important;
    border: 2px solid #f0e6d2 !important;
    border-radius: 16px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    line-height: 1.6 !important;
    transition: all 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: #c9a03d !important;
    box-shadow: 0 0 0 3px rgba(201, 160, 61, 0.1) !important;
}

/* ── buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #c9a03d 0%, #b8860b 100%) !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(201, 160, 61, 0.3) !important;
}

/* ── tables ── */
div[data-testid="stDataFrame"] {
    border: 1px solid #f0e6d2 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
div[data-testid="stDataFrame"] th {
    background: linear-gradient(135deg, #fefaf5 0%, #fef5e8 100%) !important;
    color: #c9a03d !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}

/* ── alerts ── */
.stAlert {
    border-radius: 16px !important;
    border-left: 4px solid !important;
}
.stSuccess {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
    border-left-color: #10b981 !important;
}

/* ── expanders ── */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #fefaf5 0%, #fef5e8 100%) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: #c9a03d !important;
    border: 1px solid #f0e6d2 !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Initialize session state for navigation
# ══════════════════════════════════════════════════════════════════════════════
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📝 Editor"
if 'compiled_data' not in st.session_state:
    st.session_state.compiled_data = None

# ══════════════════════════════════════════════════════════════════════════════
# Sidebar Navigation
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Mini-C Compiler</div>', unsafe_allow_html=True)
    
    st.markdown("### 🧭 Navigation")
    
    # Navigation buttons
    nav_options = [
        "📝 Editor",
        "🔍 Phase 1: Lexical Analysis",
        "🌳 Phase 2: Syntax Analysis", 
        "📚 Phase 3: Semantic Analysis",
        "📊 Summary"
    ]
    
    for option in nav_options:
        if st.button(option, use_container_width=True, key=f"nav_{option}"):
            st.session_state.current_page = option
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    **Three-Phase Compiler:**
    - **Phase 1:** Tokenization & Lexical Analysis
    - **Phase 2:** Parsing & Syntax Tree
    - **Phase 3:** Type Checking & Semantics
    """)
    
    st.markdown("---")
    st.markdown("### 🎨 Features")
    st.markdown("""
    ✅ Keyword recognition  
    ✅ Operator detection  
    ✅ Parse tree generation  
    ✅ Symbol table management  
    ✅ Type compatibility checking  
    ✅ Error reporting with line numbers
    """)

# ══════════════════════════════════════════════════════════════════════════════
# Main content area
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="main-header">
  <h1>⚙️ Mini-C Compiler Suite</h1>
  <p>Multi-phase compilation pipeline — Lexical → Syntax → Semantic Analysis</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE CODE
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
}"""

def capture(fn):
    """Run fn(), return (result, captured_stdout)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        result = fn()
    return result, buf.getvalue()

def build_graphviz_tree(node, graph=None, parent_id=None, counter=None):
    """Recursively build a graphviz.Digraph from the parse-tree dict."""
    if graph is None:
        graph = graphviz.Digraph(
            graph_attr={
                "bgcolor": "#ffffff", 
                "rankdir": "TB", 
                "nodesep": "0.4", 
                "ranksep": "0.6",
                "fontname": "Inter"
            },
            node_attr={
                "style": "filled,rounded", 
                "fontname": "JetBrains Mono", 
                "fontsize": "10",
                "shape": "box", 
                "margin": "0.15,0.08",
                "penwidth": "1.2"
            },
            edge_attr={"color": "#c9a03d", "arrowsize": "0.7", "penwidth": "1.2"},
        )
        counter = [0]

    node_id = f"n{counter[0]}"
    counter[0] += 1

    label = node["name"]
    children = node.get("children", [])

    if label == "ε":
        fillcolor, fontcolor = "#fefaf5", "#a08a6a"
    elif "Error" in label:
        fillcolor, fontcolor = "#fef2f2", "#dc2626"
    elif ":" in label:
        fillcolor, fontcolor = "#fef5e8", "#c9a03d"
    elif not children:
        fillcolor, fontcolor = "#fefaf5", "#7a8a9a"
    else:
        fillcolor, fontcolor = "#ffffff", "#2d3a4a"

    graph.node(node_id, label=label, fillcolor=fillcolor, fontcolor=fontcolor)

    if parent_id is not None:
        graph.edge(parent_id, node_id)

    for child in children:
        build_graphviz_tree(child, graph, node_id, counter)

    return graph

def status_pill(errors):
    if not errors:
        return '<span class="status-pass">✓ PASS</span>'
    return f'<span class="status-fail">✗ {len(errors)} ERRORS</span>'

# ══════════════════════════════════════════════════════════════════════════════
# Editor Page
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.current_page == "📝 Editor":
    st.markdown("### ✏️ Source Code Editor")
    st.markdown("*Write or paste your Mini-C program below*")
    
    col_in, col_btn = st.columns([5, 1], gap="medium")
    
    with col_in:
        source = st.text_area(
            "Source Code",
            value=SAMPLE_CODE,
            height=400,
            label_visibility="collapsed",
            placeholder="// Write your Mini-C code here...\n\nint main() {\n    return 0;\n}",
            key="source_editor"
        )
    
    with col_btn:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        run = st.button("▶ COMPILE", use_container_width=True, type="primary")
        if st.button("↺ RESET", use_container_width=True):
            st.session_state["_load_sample"] = True
            st.rerun()
    
    if st.session_state.get("_load_sample"):
        source = SAMPLE_CODE
        st.session_state["_load_sample"] = False
    
    if run:
        if not source.strip():
            st.warning("⚠️ Please enter some Mini-C source code before compiling.")
            st.stop()
        
        # Progress tracking
        progress_placeholder = st.empty()
        
        with progress_placeholder.container():
            st.markdown("### 🔄 Compilation Progress")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.info("📊 Phase 1: Lexical Analysis - Scanning tokens...")
            progress_bar.progress(20)
            
        lexer = LexicalAnalyzer()
        tokens, lex_sym_table, lex_errors = lexer.analyze(source)
        
        with progress_placeholder.container():
            status_text.info("📊 Phase 2: Syntax Analysis - Building parse tree...")
            progress_bar.progress(50)
            
        parser = SyntaxAnalysis(tokens)
        parse_tree, _ = capture(parser.Program)
        syn_errors = parser.errors
        
        with progress_placeholder.container():
            status_text.info("📊 Phase 3: Semantic Analysis - Type checking...")
            progress_bar.progress(75)
            
        analyzer = SemanticAnalyzer(parse_tree)
        _, _ = capture(analyzer.analyze)
        sem_errors = analyzer.errors
        symbol_table = analyzer.symbol_table
        
        with progress_placeholder.container():
            progress_bar.progress(100)
            status_text.success("✅ Compilation complete!")
            
        import time
        time.sleep(0.5)
        progress_placeholder.empty()
        
        total_errors = len(lex_errors) + len(syn_errors) + len(sem_errors)
        
        # Store compiled data in session state
        st.session_state.compiled_data = {
            'tokens': tokens,
            'lex_errors': lex_errors,
            'parse_tree': parse_tree,
            'syn_errors': syn_errors,
            'symbol_table': symbol_table,
            'sem_errors': sem_errors,
            'total_errors': total_errors
        }
        
        # Summary banner
        if total_errors == 0:
            st.success("✨ COMPILATION SUCCESSFUL! All three phases passed — program is semantically valid.")
        else:
            st.error(f"❌ COMPILATION FAILED: {total_errors} error(s) found across all phases.")
        
        st.info("💡 Tip: Use the sidebar to navigate through each phase's detailed results!")

# ══════════════════════════════════════════════════════════════════════════════
# Phase 1: Lexical Analysis Page
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "🔍 Phase 1: Lexical Analysis":
    st.markdown('<div class="phase-container"><div class="phase-badge">🔍 Phase 1 — Lexical Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.compiled_data:
        data = st.session_state.compiled_data
        
        st.markdown(f"**Status:** {status_pill(data['lex_errors'])}", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="val">{len(data['tokens'])}</div><div class="lbl">Tokens Produced</div></div>
            <div class="metric-card"><div class="val">{len(data['lex_errors'])}</div><div class="lbl">Lexical Errors</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Token table
        st.markdown("#### 📋 Token Stream")
        import pandas as pd
        if data['tokens']:
            df_tok = pd.DataFrame(data['tokens'])[["lexeme", "type", "line", "column"]]
            df_tok.columns = ["Lexeme", "Type", "Line", "Column"]
            st.dataframe(df_tok, use_container_width=True, height=400)
        else:
            st.info("ℹ️ No tokens produced.")
        
        # Errors
        if data['lex_errors']:
            st.markdown("#### ⚠️ Lexical Errors")
            for e in data['lex_errors']:
                st.markdown(f'<div class="error-item">{e}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No lexical errors detected!")
    else:
        st.info("ℹ️ No compilation data available. Please go to the Editor page and compile a program first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Phase 2: Syntax Analysis Page
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "🌳 Phase 2: Syntax Analysis":
    st.markdown('<div class="phase-container"><div class="phase-badge">🌳 Phase 2 — Syntax Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.compiled_data:
        data = st.session_state.compiled_data
        
        st.markdown(f"**Status:** {status_pill(data['syn_errors'])}", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="val">{len(data['syn_errors'])}</div><div class="lbl">Syntax Errors</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Parse tree
        st.markdown("#### 🌲 Parse Tree Visualization")
        if data['parse_tree']:
            try:
                dot = build_graphviz_tree(data['parse_tree'])
                st.graphviz_chart(dot, use_container_width=True)
            except Exception as ex:
                st.warning(f"⚠️ Could not render tree: {ex}")
        else:
            st.info("ℹ️ No parse tree available.")
        
        # Errors
        if data['syn_errors']:
            st.markdown("#### ⚠️ Syntax Errors")
            for e in data['syn_errors']:
                st.markdown(f'<div class="error-item">{e}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No syntax errors detected!")
    else:
        st.info("ℹ️ No compilation data available. Please go to the Editor page and compile a program first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Phase 3: Semantic Analysis Page
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "📚 Phase 3: Semantic Analysis":
    st.markdown('<div class="phase-container"><div class="phase-badge">📚 Phase 3 — Semantic Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.compiled_data:
        data = st.session_state.compiled_data
        
        st.markdown(f"**Status:** {status_pill(data['sem_errors'])}", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="val">{len(data['symbol_table'])}</div><div class="lbl">Symbols</div></div>
            <div class="metric-card"><div class="val">{len(data['sem_errors'])}</div><div class="lbl">Semantic Errors</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Symbol table
        st.markdown("#### 📊 Symbol Table")
        if data['symbol_table']:
            import pandas as pd
            rows = []
            for sym in data['symbol_table']:
                params = sym.get("parameters") or "-"
                if isinstance(params, list):
                    params = ", ".join(
                        f"{p.get('type','')} {p.get('name','')}" if isinstance(p, dict) else str(p)
                        for p in params
                    ) or "-"
                rows.append({
                    "Name": sym.get("name", ""),
                    "Type": sym.get("type", ""),
                    "Kind": sym.get("kind", ""),
                    "Scope": sym.get("scope", ""),
                    "Parameters": params,
                })
            df_sym = pd.DataFrame(rows)
            st.dataframe(df_sym, use_container_width=True, height=400)
        else:
            st.info("ℹ️ Symbol table is empty.")
        
        # Errors
        if data['sem_errors']:
            st.markdown("#### ⚠️ Semantic Errors")
            for e in data['sem_errors']:
                st.markdown(f'<div class="error-item">{e}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No semantic errors detected!")
    else:
        st.info("ℹ️ No compilation data available. Please go to the Editor page and compile a program first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Summary Page
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "📊 Summary":
    st.markdown('<div class="phase-container"><div class="phase-badge">📊 Compilation Summary</div>', unsafe_allow_html=True)
    
    if st.session_state.compiled_data:
        data = st.session_state.compiled_data
        
        import pandas as pd
        df_sum = pd.DataFrame([
            {"Phase": "Phase 1 – Lexical Analysis", "Status": "✓ PASS" if not data['lex_errors'] else "✗ FAIL", "Errors": len(data['lex_errors'])},
            {"Phase": "Phase 2 – Syntax Analysis", "Status": "✓ PASS" if not data['syn_errors'] else "✗ FAIL", "Errors": len(data['syn_errors'])},
            {"Phase": "Phase 3 – Semantic Analysis", "Status": "✓ PASS" if not data['sem_errors'] else "✗ FAIL", "Errors": len(data['sem_errors'])},
        ])
        st.dataframe(df_sum, use_container_width=True, hide_index=True)
        
        # Overall verdict
        st.markdown("---")
        if data['total_errors'] == 0:
            st.success("### 🎉 VERDICT: PROGRAM IS VALID")
            st.markdown("The program passed all three phases of compilation successfully!")
        else:
            st.error(f"### ❌ VERDICT: COMPILATION FAILED")
            st.markdown(f"Found **{data['total_errors']}** error(s) across all phases. Please fix the errors and recompile.")
    else:
        st.info("ℹ️ No compilation data available. Please go to the Editor page and compile a program first.")
    
    st.markdown('</div>', unsafe_allow_html=True)