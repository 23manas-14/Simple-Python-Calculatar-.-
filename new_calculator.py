import streamlit as st
import math
import random

# ---------------- OPTIONAL VOICE LIBS (LOCAL ONLY) ----------------
# These libraries are only required if you want to use voice input/output locally.
# If they are not installed, the app will still run (voice features will just do nothing).
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# ---------------- PAGE CONFIG ----------------
# Basic Streamlit page settings: title, icon, and layout.
st.set_page_config(page_title="Python Calculator", page_icon="🧮", layout="centered")

# ---------------- CSS (snow + styles) ----------------
# All the styling of the app (backgrounds, fonts, buttons, etc.) is done here.
st.markdown(
    """
<style>
@import url('https://fonts.cdnfonts.com/css/algerian');

/* -------- APP BACKGROUND -------- */
.stApp {
  background: linear-gradient(135deg, #1e1e2f, #2d354d);
  padding-top: 18px;
  overflow: hidden;
}

/* -------- SNOW ANIMATION -------- */
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

/* -------- TITLE STYLING -------- */
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

/* -------- DISPLAY AREA (SMALL EXPRESSION + BIG RESULT) -------- */
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

/* -------- GRID & BUTTONS LAYOUT -------- */
.calc-grid { padding-left: 24px; padding-right: 24px; margin-bottom: 12px; }
.calc-row { display:flex; gap:12px; margin-bottom:12px; }

/* Base button shape: applies to all Streamlit buttons */
.stButton > button {
  border-radius: 12px !important;
  padding: 16px 0 !important;
  font-size: 20px !important;
  font-weight: 600 !important;
  min-height: 48px;
}

/* Normal buttons (type="secondary") – transparent with orange border + orange text */
.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: #ff9500 !important;
  border: 2px solid #ff9500 !important;
}

/* Equals button (type="primary") – solid yellow button */
.stButton > button[kind="primary"] {
  background: #ffeb3b !important;
  color: #000 !important;
  border: 2px solid #ffeb3b !important;
}

/* -------- VOICE BUTTONS (🎙️ Speak & 🔊 Result) -------- */
/* We target them via HTML title attribute set from Streamlit `help="..."`. */

/* Shared size: make both voice buttons bigger than normal buttons */
button[title="voice_speak"],
button[title="voice_result"] {
  border-radius: 18px !important;
  padding: 18px 40px !important;      /* Bigger click area */
  font-size: 26px !important;         /* Larger text */
  font-weight: 700 !important;
  min-width: 260px;                   /* Wider buttons */
}

/* 🎙️ Speak  -> orange background, yellow text */
button[title="voice_speak"] {
  background: #ff9500 !important;     /* orange */
  color: #ffeb3b !important;          /* yellow text */
  border: 2px solid #ff9500 !important;
}

/* 🔊 Result -> yellow background, orange text */
button[title="voice_result"] {
  background: #ffeb3b !important;     /* yellow */
  color: #ff9500 !important;          /* orange text */
  border: 2px solid #ffeb3b !important;
}

/* -------- RESPONSIVE DESIGN (SMALLER SCREENS) -------- */
@media (max-width: 768px) {
  .title { font-size: 42px; }
  .calc-display-res { font-size: 40px; }
}
@media (max-width: 480px) {
  .title { font-size: 32px; margin-bottom: 8px; }
  .calc-display-res { font-size: 30px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------- SNOW HTML (ACTUAL SNOW DOT ELEMENTS) ----------------
# This builds several "•" elements with random positions and animation speeds to look like snow.
snow_html = '<div class="snow">\n'
for i in range(30):
    left = random.uniform(0, 100)   # horizontal position in percentage
    dur = random.uniform(4, 10)     # animation duration
    delay = random.uniform(0, 6)    # animation delay
    size = random.uniform(6, 12)    # font size (dot size)
    snow_html += (
        f'<div class="dot" style="left:{left}%; font-size:{size}px; '
        f'animation-duration:{dur}s; animation-delay:{delay}s;">•</div>\n'
    )
snow_html += "</div>"
st.markdown(snow_html, unsafe_allow_html=True)

# ---------------- SIDEBAR (THEME + HISTORY) ----------------
st.sidebar.title("⚙️ Extra Features")

# Theme toggle radio button (Dark / Light)
theme = st.sidebar.radio("Theme Mode", ["🌑 Dark", "🌕 Light"])

# When Light theme is selected, override background and button style a bit
if theme == "🌕 Light":
    st.markdown(
        """
    <style>
    .stApp {
      background: linear-gradient(135deg, #e6f7e6, #b7f0b7);
      color: #000 !important;
    }
    .stButton > button[kind="secondary"] {
      background: #ffffff !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

# ---------------- SESSION STATE INITIALIZATION ----------------
# We use Streamlit's session_state to remember data across interactions.
if "history" not in st.session_state:
    st.session_state.history = []           # list of past calculations
if "expression" not in st.session_state:
    st.session_state.expression = ""        # current expression string
if "display_result" not in st.session_state:
    st.session_state.display_result = ""    # current result to display

# Show history in the sidebar (latest at the top)
st.sidebar.subheader("📜 Calculation History")
if st.session_state.history:
    for h in reversed(st.session_state.history[-12:]):  # show up to last 12 entries
        st.sidebar.write(h)
else:
    st.sidebar.info("No calculations yet.")

# ---------------- MAIN TITLE ----------------
st.markdown("<div class='title'>🧮 Python Calculator</div>", unsafe_allow_html=True)

# ---------------- VOICE HELPER FUNCTIONS (LOCAL ONLY) ----------------
def recognize_speech_from_mic() -> str:
    """
    Listen once from the local microphone and return recognized text using Google Speech.
    If speech_recognition is not installed or something fails, return an empty string.
    """
    if sr is None:
        return ""
    try:
        recog = sr.Recognizer()
        with sr.Microphone() as source:
            # Try to reduce background noise
            recog.adjust_for_ambient_noise(source, duration=0.5)
            # Listen for up to 5 seconds
            audio = recog.listen(source, phrase_time_limit=5)
        # Use Google's free speech recognition API
        text = recog.recognize_google(audio)
        return text
    except Exception:
        # Any error -> return empty so the app does not crash
        return ""

def speak_text_out_loud(text: str):
    """
    Speak given text out loud using the local speakers (pyttsx3).
    If pyttsx3 is not installed or something fails, do nothing.
    """
    if pyttsx3 is None:
        return
    try:
        engine = pyttsx3.init()
        engine.say(str(text))
        engine.runAndWait()
        engine.stop()
    except Exception:
        # Silent failure to avoid breaking the app
        pass

def spoken_to_expr(text: str) -> str:
    """
    Convert recognized speech into a calculator expression.

    Supports verbal phrases like:
      - "plus", "minus", "times", "divided by"
      - "square root of", "sine of", "cosine of", "tangent of"
      - "percent", "percentage of"
      - powers: "to the power of", "squared", "cubed"
    And converts simple number words ("one", "two", etc.) to digits.
    """
    t = text.lower().strip()

    # Map common spoken phrases to operators / functions
    phrase_replacements = {
        # Division
        "divided by": "/",
        "divide by": "/",
        "over": "/",

        # Multiplication
        "multiplied by": "*",
        "times": "*",
        "x": "*",

        # Powers
        "to the power of": "^",
        "power of": "^",
        "raised to the power of": "^",
        "raised to": "^",

        # Roots
        "square root of": "sqrt",
        "square root": "sqrt",
        "root of": "sqrt",

        # Trigonometric functions
        "sine of": "sin",
        "cosine of": "cos",
        "tangent of": "tan",
        "sin of": "sin",
        "cos of": "cos",
        "tan of": "tan",

        # Percent / percentage
        "percent of": "/ 100 *",
        "percentage of": "/ 100 *",
        "percent": "/ 100",
        "percentage": "/ 100",

        # Addition / subtraction
        "plus": "+",
        "add": "+",
        "minus": "-",
        "subtract": "-",
    }

    # Replace phrases with symbols
    for phrase, sym in phrase_replacements.items():
        t = t.replace(phrase, f" {sym} ")

    # Simple mapping from spoken numbers to digits
    number_words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "for": "4",   # common mis-recognition
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "ate": "8",   # common mis-recognition
        "nine": "9",
        "ten": "10",
    }

    tokens = t.split()
    out = []
    open_funcs = 0  # count unclosed function parentheses

    for tok in tokens:
        if tok in number_words:
            # Word-number -> digit
            out.append(number_words[tok])
        elif tok in {"+", "-", "*", "/", "^"}:
            # Math operators
            out.append(tok)
        elif tok in {"sqrt", "sin", "cos", "tan"}:
            # Functions get an opening parenthesis
            out.append(tok + "(")
            open_funcs += 1
        elif tok in {"squared", "square"}:
            out.append("^2")
        elif tok in {"cubed", "cube"}:
            out.append("^3")
        else:
            # If token looks like a number (including decimal)
            if tok.replace(".", "", 1).isdigit():
                out.append(tok)

    # Close all opened function parentheses
    out.extend(")" for _ in range(open_funcs))

    # Join without spaces to create expression string
    expr = "".join(out)
    # If we couldn't parse anything, just return original text with no spaces
    if not expr:
        expr = text.replace(" ", "")
    return expr

# ---------------- VOICE BUTTONS ROW ----------------
# Two big buttons at the top for voice input and voice output.
col_v1, col_v2 = st.columns(2)

with col_v1:
    # 🎙️ Speak button: listens to microphone and fills the expression.
    if st.button(
        "🎙️ Speak",
        key="speak_expr_btn",
        help="voice_speak",              # used as HTML title for CSS targeting
        use_container_width=True,
    ):
        spoken_raw = recognize_speech_from_mic()
        if spoken_raw:
            expr_from_voice = spoken_to_expr(spoken_raw)
            if expr_from_voice:
                st.session_state.expression = expr_from_voice
                # Clear result so expression appears as the main display
                st.session_state.display_result = ""

with col_v2:
    # 🔊 Result button: speaks the current result or expression.
    if st.button(
        "🔊 Result",
        key="result_btn",
        help="voice_result",             # used as HTML title for CSS targeting
        use_container_width=True,
    ):
        value = st.session_state.display_result
        # If there is no result yet, speak the expression or "0"
        if value in ("", None):
            value = st.session_state.expression or "0"
        speak_text_out_loud(value)

# ---------------- CALCULATION HELPER FUNCTIONS ----------------
def prep_expr_for_eval(expr: str) -> str:
    """
    Take the user-visible expression string and convert it into a valid
    Python expression that can be safely evaluated.
    """
    # Normalize special characters to Python operators
    e = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("–", "-")
    e = e.replace("➕", "+")
    # Handle ^ as exponentiation
    e = e.replace("^", "**")
    # Replace pi character with its numeric value
    e = e.replace("π", str(math.pi))

    # Map functions to math module
    e = e.replace("sin(", "math.sin(")
    e = e.replace("cos(", "math.cos(")
    e = e.replace("tan(", "math.tan(")
    e = e.replace("sqrt(", "math.sqrt(")

    # Important: replace log() and ln() in a safe order to avoid "math.math.log10(" bugs.
    # "log(" -> math.log10()  (base 10)
    e = e.replace("log(", "math.log10(")
    # "ln("  -> math.log()    (natural log)
    e = e.replace("ln(", "math.log(")

    return e

def evaluate_expression(expr: str):
    """
    Safely evaluate the mathematical expression.
    Returns either:
      - a number (int or float), or
      - the string "Error" if evaluation fails.
    """
    if not expr:
        return ""
    try:
        safe = prep_expr_for_eval(expr)
        # Evaluate with no builtins and only 'math' module allowed.
        result = eval(safe, {"__builtins__": None, "math": math}, {})
        # Clean up float representation to avoid long tails like 1.00000000000001
        if isinstance(result, float):
            result = float(f"{result:.12g}")
        return result
    except Exception:
        return "Error"

def press(btn: str):
    """
    Handle button presses for all calculator buttons.
    This function updates st.session_state.expression and st.session_state.display_result.
    """
    # Clear everything
    if btn == "AC":
        st.session_state.expression = ""
        st.session_state.display_result = ""
        return

    # Backspace: remove last character
    if btn == "⌫":
        st.session_state.expression = st.session_state.expression[:-1]
        return

    # Toggle sign of the entire current expression
    if btn == "+/-":
        exp = st.session_state.expression
        if exp:
            st.session_state.expression = exp[1:] if exp.startswith("-") else "-" + exp
        return

    # Percentage: evaluate current expression and divide by 100
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

    # Equals: evaluate full expression
    if btn == "=":
        res = evaluate_expression(st.session_state.expression)
        st.session_state.display_result = res
        st.session_state.history.append(f"{st.session_state.expression} = {res}")
        return

    # Special mapping for ➕ (fancy plus sign) to '+'
    if btn == "➕":
        st.session_state.expression += "+"
        return

    # Otherwise, just append the button text to the expression
    st.session_state.expression += btn

# ---------------- TABS (BASIC & SCIENTIFIC) ----------------
tab1, tab2 = st.tabs(["Basic", "Scientific"])

def render_col_button(col, label, key, on_click=None, args=()):
    """
    Helper that renders a calculator button inside a given Streamlit column.
    It automatically chooses primary style for '=' and secondary for others.
    """
    btn_type = "primary" if label == "=" else "secondary"
    col.button(
        label,
        key=key,
        use_container_width=True,
        on_click=on_click,
        args=args,
        type=btn_type,
    )

# -------- BASIC TAB --------
with tab1:
    # Small expression display (top)
    st.markdown(
        f"<div class='calc-display-exp'>{st.session_state.expression}</div>",
        unsafe_allow_html=True,
    )

    # Big display: show result if available, otherwise current expression, or 0
    if st.session_state.display_result not in ("", None):
        big_display = st.session_state.display_result
    elif st.session_state.expression:
        big_display = st.session_state.expression
    else:
        big_display = "0"

    st.markdown(
        f"<div class='calc-display-res'>{big_display}</div>",
        unsafe_allow_html=True,
    )

    # Layout for basic calculator buttons
    rows_basic = [
        ["AC", "⌫", "%", "÷"],
        ["7", "8", "9", "×"],
        ["4", "5", "6", "−"],
        ["1", "2", "3", "➕"],
        ["00", "0", ".", "="],
    ]

    # Render each row of buttons
    for r in rows_basic:
        cols = st.columns(4, gap="small")
        for i, label in enumerate(r):
            key = f"basic_{label}_{i}"
            render_col_button(cols[i], label, key, on_click=press, args=(label,))

# -------- SCIENTIFIC TAB --------
with tab2:
    # Small expression display (top)
    st.markdown(
        f"<div class='calc-display-exp'>{st.session_state.expression}</div>",
        unsafe_allow_html=True,
    )

    # Big display: show result if available, otherwise current expression, or 0
    if st.session_state.display_result not in ("", None):
        big_display = st.session_state.display_result
    elif st.session_state.expression:
        big_display = st.session_state.expression
    else:
        big_display = "0"

    st.markdown(
        f"<div class='calc-display-res'>{big_display}</div>",
        unsafe_allow_html=True,
    )

    # First block of scientific function buttons
    sci_rows = [
        ["sin(", "cos(", "tan(", "sqrt("],
        ["ln(", "log(", "π", "e"],
        ["x^y", "x^2", "+/-", "⌫"],
        ["AC", "%", "÷", "×"],
    ]

    for r_idx, row in enumerate(sci_rows):
        cols = st.columns(4, gap="small")
        for c_idx, label in enumerate(row):

            # Each scientific button uses a small wrapper to map its label to the correct input
            def _click(l=label):
                if l == "x^y":
                    # Insert ^ which later becomes ** in prep_expr_for_eval()
                    press("^")
                elif l == "x^2":
                    # Direct Python exponent operator for squaring
                    press("**2")
                elif l == "π":
                    # Insert pi symbol; will be replaced with number later
                    press("π")
                elif l == "e":
                    # Insert math.e directly to avoid replacing every 'e' character
                    press("math.e")
                else:
                    press(l)

            render_col_button(
                cols[c_idx],
                label,
                key=f"sci_{r_idx}_{label}",
                on_click=_click,
            )

    # Numeric keypad section in scientific tab (same layout as basic)
    sci_num_rows = [
        ["7", "8", "9", "×"],
        ["4", "5", "6", "−"],
        ["1", "2", "3", "➕"],
        ["00", "0", ".", "="],
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