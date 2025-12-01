import streamlit as st
import math
import random

# Optional voice libraries
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Python Calculator", page_icon="🧮", layout="centered")

# ---------------- CSS (snow + styles) ----------------
st.markdown("""
<style>
@import url('https://fonts.cdnfonts.com/css/algerian');

/* App */
.stApp {
  background: linear-gradient(135deg, #1e1e2f, #2d354d);
  padding-top: 18px;
  overflow: hidden;
}

/* Snow */
.snow {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}
.snow .dot {
  position: absolute;
  color: white;
  opacity: 0.85;
  font-size: 8px;
  animation: fall linear infinite;
}
@keyframes fall {
  0% { transform: translateY(-10vh); }
  100% { transform: translateY(120vh); }
}

/* Title */
.title {
  font-family: 'Algerian', sans-serif;
  text-align: center;
  font-size: 55px;
  font-weight: bold;
  background: linear-gradient(90deg, #4CAF50, #9be15d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 1px 1px 8px rgba(0,255,0,0.25);
  position: relative;
  z-index: 3;
  margin-bottom: 10px;
}

/* Display */
.calc-display-exp {
  text-align: right;
  color: #bdbdbd;
  font-size: 22px;
  margin-top: 12px;
  margin-bottom: -6px;
  padding-right: 24px;
}
.calc-display-res {
  text-align: right;
  color: white;
  font-size: 52px;
  font-weight: 700;
  padding-right: 24px;
  margin-bottom: 16px;
}

/* Grid & buttons */
.calc-grid { padding-left: 24px; padding-right: 24px; margin-bottom: 12px; }
.calc-row { display:flex; gap:12px; margin-bottom:12px; }

/* Base button shape (all buttons) */
.stButton > button {
  border-radius: 12px !important;
  padding: 16px 0 !important;
  font-size: 20px !important;
  font-weight: 600 !important;
  min-height: 48px;
}

/* Normal buttons (kind="secondary") – orange border + orange text */
.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: #ff9500 !important;
  border: 2px solid #ff9500 !important;
}

/* Equals button (kind="primary") – full yellow box */
.stButton > button[kind="primary"] {
  background: #ffeb3b !important;
  color: #000 !important;
  border: 2px solid #ffeb3b !important;
}

/* Voice buttons identified by their help (title) attribute */
button[title="voice_speak"] {
  background: #ffeb3b !important;     /* yellow */
  color: #ff6f00 !important;          /* orange text */
  border: 2px solid #ffeb3b !important;
  padding: 14px 24px !important;
  font-size: 22px !important;
  min-width: 180px;
}
button[title="voice_result"] {
  background: #ff6f00 !important;     /* orange */
  color: #ffeb3b !important;          /* yellow text */
  border: 2px solid #ff6f00 !important;
  padding: 14px 24px !important;
  font-size: 22px !important;
  min-width: 180px;
}

/* Responsive */
@media (max-width: 768px) {
  .title { font-size: 42px; }
  .calc-display-res { font-size: 40px; }
}
@media (max-width: 480px) {
  .title { font-size: 32px; margin-bottom: 8px; }
  .calc-display-res { font-size: 30px; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- Snow HTML ----------------
snow_html = '<div class="snow">\n'
for i in range(30):
    left = random.uniform(0, 100)
    dur = random.uniform(4, 10)
    delay = random.uniform(0, 6)
    size = random.uniform(6, 12)
    snow_html += (
        f'<div class="dot" style="left:{left}%; font-size:{size}px; '
        f'animation-duration:{dur}s; animation-delay:{delay}s;">•</div>\n'
    )
snow_html += '</div>'
st.markdown(snow_html, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Extra Features")

# Theme toggle
theme = st.sidebar.radio("Theme Mode", ["🌑 Dark", "🌕 Light"])

# Light theme override
if theme == "🌕 Light":
    st.markdown("""
    <style>
    .stApp {
      background: linear-gradient(135deg, #e6f7e6, #b7f0b7);
      color: #000 !important;
    }
    .stButton > button[kind="secondary"] {
      background: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- Session state ----------------
if "history" not in st.session_state:
    st.session_state.history = []
if "expression" not in st.session_state:
    st.session_state.expression = ""
if "display_result" not in st.session_state:
    st.session_state.display_result = ""

# History in sidebar
st.sidebar.subheader("📜 Calculation History")
if st.session_state.history:
    for h in reversed(st.session_state.history[-12:]):
        st.sidebar.write(h)
else:
    st.sidebar.info("No calculations yet.")

# ---------------- Title ----------------
st.markdown("<div class='title'>🧮 Python Calculator</div>", unsafe_allow_html=True)


# ---------------- Voice helpers (Python side) ----------------
def recognize_speech_from_mic() -> str:
    """Listen once from microphone and return recognized text; no UI messages."""
    if sr is None:
        return ""
    try:
        recog = sr.Recognizer()
        with sr.Microphone() as source:
            recog.adjust_for_ambient_noise(source, duration=0.5)
            audio = recog.listen(source, phrase_time_limit=5)
        text = recog.recognize_google(audio)
        return text
    except Exception:
        # Fail silently – do not show any boxes
        return ""


def speak_text_out_loud(text: str):
    """Use pyttsx3 to speak text; all errors are silent (no boxes)."""
    if pyttsx3 is None:
        return
    try:
        engine = pyttsx3.init()
        engine.say(str(text))
        engine.runAndWait()
        engine.stop()
    except Exception:
        # Fail silently – do not display messages
        pass


def spoken_to_expr(text: str) -> str:
    """
    Convert recognized speech into a calculator expression.
    Supports:
      - plus, minus, times, divided by
      - 'to the power of', 'squared', 'cubed'
      - sqrt/sin/cos/tan
      - percent / percent of
    """
    t = text.lower().strip()

    phrase_replacements = {
        "divided by": "/",
        "divide by": "/",
        "over": "/",

        "multiplied by": "*",
        "times": "*",
        "x": "*",

        "to the power of": "^",
        "power of": "^",
        "raised to the power of": "^",
        "raised to": "^",

        "square root of": "sqrt",
        "square root": "sqrt",
        "root of": "sqrt",

        "sine of": "sin",
        "cosine of": "cos",
        "tangent of": "tan",
        "sin of": "sin",
        "cos of": "cos",
        "tan of": "tan",

        "percent of": "/ 100 *",
        "percentage of": "/ 100 *",
        "percent": "/ 100",
        "percentage": "/ 100",

        "plus": "+",
        "add": "+",
        "minus": "-",
        "subtract": "-",
    }

    for phrase, sym in phrase_replacements.items():
        t = t.replace(phrase, f" {sym} ")

    number_words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "for": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "ate": "8",
        "nine": "9",
        "ten": "10",
    }

    tokens = t.split()
    out = []
    open_funcs = 0

    for tok in tokens:
        if tok in number_words:
            out.append(number_words[tok])
        elif tok in {"+", "-", "*", "/", "^"}:
            out.append(tok)
        elif tok in {"sqrt", "sin", "cos", "tan"}:
            out.append(tok + "(")
            open_funcs += 1
        elif tok in {"squared", "square"}:
            out.append("^2")
        elif tok in {"cubed", "cube"}:
            out.append("^3")
        else:
            if tok.replace(".", "", 1).isdigit():
                out.append(tok)

    out.extend(")" for _ in range(open_funcs))

    expr = "".join(out)
    if not expr:
        expr = text.replace(" ", "")
    return expr


# ---------------- Voice buttons row ----------------
col_v1, col_v2 = st.columns(2)

with col_v1:
    if st.button("🎙️ Speak", key="speak_expr_btn", help="voice_speak"):
        spoken_raw = recognize_speech_from_mic()
        if spoken_raw:
            expr_from_voice = spoken_to_expr(spoken_raw)
            if expr_from_voice:
                st.session_state.expression = expr_from_voice
                st.session_state.display_result = ""  # show expression in big display

with col_v2:
    if st.button("🔊 Result", key="result_btn", help="voice_result"):
        value = st.session_state.display_result
        if value in ("", None):
            value = st.session_state.expression or "0"
        speak_text_out_loud(value)


# ---------------- Calculation helpers ----------------
def prep_expr_for_eval(expr: str) -> str:
    e = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("–", "-")
    e = e.replace("➕", "+")
    e = e.replace("^", "**")
    e = e.replace("π", str(math.pi)).replace("e", str(math.e))
    e = e.replace("sin(", "math.sin(").replace("cos(", "math.cos(").replace("tan(", "math.tan(")
    e = e.replace("sqrt(", "math.sqrt(").replace("ln(", "math.log(").replace("log(", "math.log10(")
    return e

def evaluate_expression(expr: str):
    if not expr:
        return ""
    try:
        safe = prep_expr_for_eval(expr)
        result = eval(safe, {"__builtins__": None, "math": math}, {})
        if isinstance(result, float):
            result = float(f"{result:.12g}")
        return result
    except Exception:
        return "Error"

def press(btn: str):
    if btn == "AC":
        st.session_state.expression = ""
        st.session_state.display_result = ""
        return
    if btn == "⌫":
        st.session_state.expression = st.session_state.expression[:-1]
        return
    if btn == "+/-":
        exp = st.session_state.expression
        st.session_state.expression = exp[1:] if exp.startswith("-") else "-" + exp
        return
    if btn == "%":
        val = evaluate_expression(st.session_state.expression)
        if isinstance(val, (int, float)):
            res = val / 100
            st.session_state.display_result = res
            st.session_state.history.append(f"{st.session_state.expression}% = {res}")
            st.session_state.expression = str(res)
        else:
            st.session_state.display_result = "Error"
        return
    if btn == "=":
        res = evaluate_expression(st.session_state.expression)
        st.session_state.display_result = res
        st.session_state.history.append(f"{st.session_state.expression} = {res}")
        return
    if btn == "➕":
        st.session_state.expression += "+"
        return
    st.session_state.expression += btn

# ---------------- Tabs ----------------
tab1, tab2 = st.tabs(["Basic", "Scientific"])

def render_col_button(col, label, key, on_click=None, args=()):
    btn_type = "primary" if label == "=" else "secondary"
    col.button(
        label,
        key=key,
        use_container_width=True,
        on_click=on_click,
        args=args,
        type=btn_type
    )

# -------- BASIC TAB --------
with tab1:
    st.markdown(
        f"<div class='calc-display-exp'>{st.session_state.expression}</div>",
        unsafe_allow_html=True
    )

    # Big yellow display: result if exists, else current expression, else 0
    if st.session_state.display_result not in ("", None):
        big_display = st.session_state.display_result
    elif st.session_state.expression:
        big_display = st.session_state.expression
    else:
        big_display = "0"

    st.markdown(
        f"<div class='calc-display-res'>{big_display}</div>",
        unsafe_allow_html=True
    )

    rows_basic = [
        ["AC", "⌫", "%", "÷"],
        ["7", "8", "9", "×"],
        ["4", "5", "6", "−"],
        ["1", "2", "3", "➕"],
        ["00", "0", ".", "="]
    ]

    for r in rows_basic:
        cols = st.columns(4, gap="small")
        for i, label in enumerate(r):
            key = f"basic_{label}_{i}"
            render_col_button(cols[i], label, key, on_click=press, args=(label,))

# -------- SCIENTIFIC TAB --------
with tab2:
    st.markdown(
        f"<div class='calc-display-exp'>{st.session_state.expression}</div>",
        unsafe_allow_html=True
    )

    if st.session_state.display_result not in ("", None):
        big_display = st.session_state.display_result
    elif st.session_state.expression:
        big_display = st.session_state.expression
    else:
        big_display = "0"

    st.markdown(
        f"<div class='calc-display-res'>{big_display}</div>",
        unsafe_allow_html=True
    )

    sci_rows = [
        ["sin(", "cos(", "tan(", "sqrt("],
        ["ln(", "log(", "π", "e"],
        ["x^y", "x^2", "+/-", "⌫"],
        ["AC", "%", "÷", "×"]
    ]

    for r_idx, row in enumerate(sci_rows):
        cols = st.columns(4, gap="small")
        for c_idx, label in enumerate(row):
            def _click(l=label):
                if l == "x^y":
                    press("^")
                elif l == "x^2":
                    press("**2")
                elif l == "π":
                    press("π")
                elif l == "e":
                    press("e")
                else:
                    press(l)

            render_col_button(cols[c_idx], label, key=f"sci_{r_idx}_{label}", on_click=_click)

    sci_num_rows = [
        ["7","8","9","×"],
        ["4","5","6","−"],
        ["1","2","3","➕"],
        ["00","0",".","="]
    ]

    for r_idx, row in enumerate(sci_num_rows):
        cols = st.columns(4, gap="small")
        for c_idx, label in enumerate(row):
            render_col_button(
                cols[c_idx],
                label,
                key=f"sci_num_{r_idx}_{label}",
                on_click=press,
                args=(label,),
            )