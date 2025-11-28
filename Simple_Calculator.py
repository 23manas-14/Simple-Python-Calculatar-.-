import streamlit as st
import math

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Python Calculator", page_icon="🧮", layout="centered")

# ---------------- CUSTOM CSS WITH RESPONSIVENESS ----------------
st.markdown("""
    <style>
        @import url('https://fonts.cdnfonts.com/css/algerian');

        /* ---------------- Base Layout ---------------- */
        .stApp {
            background: linear-gradient(135deg, #1e1e2f, #2d354d);
            padding-top: 20px;
            overflow: hidden;
        }

        /* Sparkles */
        .sparkles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            z-index: 1;
        }
        .sparkle {
            position: absolute;
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            opacity: 0.8;
            animation: fall 4s linear infinite;
        }
        @keyframes fall {
            0% { transform: translateY(-10px); opacity: 1; }
            100% { transform: translateY(100vh); opacity: 0; }
        }

        /* ---------------- Title ---------------- */
        .title {
            font-family: 'Algerian', sans-serif;
            text-align: center;
            font-size: 55px;
            font-weight: bold;
            background: linear-gradient(90deg, #4CAF50, #9be15d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 1px 1px 8px rgba(0,255,0,0.3);
            position: relative;
            z-index: 3;
            margin-bottom: 20px;
        }

        /* ---------------- Inputs & Buttons ---------------- */
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {
            border-radius: 10px !important;
            background-color: rgba(255,255,255,0.1);
            color: white !important;
        }

        .stButton>button {
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            color: white;
            padding: 12px 20px;
            font-size: 18px;
            border-radius: 10px;
            border: none;
            width: 100%;
            transition: 0.3s;
            font-weight: bold;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #66ff77, #55cc44);
            transform: scale(1.05);
        }

        /* ---------------- Result ---------------- */
        .result {
            padding: 15px;
            border-radius: 10px;
            background: rgba(76, 175, 80, 0.15);
            color: #caffca;
            font-size: 22px;
            text-align: center;
            font-weight: bold;
            margin-top: 15px;
            border: 1px solid rgba(76,175,80,0.4);
            animation: fadeIn 0.8s ease-in-out;
        }

        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(10px);}
            to {opacity: 1; transform: translateY(0);}
        }

        /* ---------------- Footer ---------------- */
        .footer {
            text-align: center;
            color: #aaa;
            margin-top: 30px;
        }

        /* ---------------- RESPONSIVE DESIGN ---------------- */
        @media (max-width: 768px) {
            /* Tablets */
            .title {
                font-size: 42px;
            }
            .stButton>button {
                font-size: 16px;
                padding: 10px;
            }
            .result {
                font-size: 20px;
            }
        }

        @media (max-width: 480px) {
            /* Phones */
            .title {
                font-size: 34px;
                margin-bottom: 15px;
            }
            .stNumberInput label, .stSelectbox label {
                font-size: 16px !important;
            }
            .stNumberInput > div > div > input,
            .stSelectbox > div > div {
                font-size: 16px !important;
                padding: 6px !important;
            }
            .stButton>button {
                font-size: 15px;
                padding: 8px;
            }
            .result {
                font-size: 18px;
            }
            .footer {
                font-size: 13px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- SPARKLES ----------------
sparkles_html = """
<div class="sparkles">
    %s
</div>
""" % ("\n".join([
        f'<div class="sparkle" style="left:{i*2.5}%; animation-duration:{2 + (i % 3)}s; animation-delay:{i*0.2}s;"></div>'
        for i in range(40)
]))
st.markdown(sparkles_html, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Extra Features")

if "history" not in st.session_state:
    st.session_state.history = []

# Theme toggle
theme = st.sidebar.radio("Theme Mode", ["🌑 Dark", "🌕 Light"])
if theme == "🌕 Light":
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e6f7e6, #b7f0b7);
        color: #000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Scientific mode
sci_mode = st.sidebar.checkbox("🧪 Scientific Mode")

# History
st.sidebar.subheader("📜 Calculation History")
if st.session_state.history:
    for h in reversed(st.session_state.history[-5:]):
        st.sidebar.write(h)
else:
    st.sidebar.info("No calculations yet.")

# ---------------- MAIN UI ----------------
st.markdown("<h1 class='title'>🧮 Python Calculator</h1>", unsafe_allow_html=True)

if sci_mode:
    operations = ("Addition", "Subtraction", "Multiplication", "Division",
                  "Power", "Modulus", "Square Root", "Sine", "Cosine", "Tangent")
else:
    operations = ("Addition", "Subtraction", "Multiplication", "Division")

operation = st.selectbox("Select an Operation", operations)
num1 = st.number_input("Enter First Number", value=0.0, step=1.0)

if operation not in ("Square Root", "Sine", "Cosine", "Tangent"):
    num2 = st.number_input("Enter Second Number", value=0.0, step=1.0)
else:
    num2 = None

if st.button("Calculate"):
    result = None
    try:
        if operation == "Addition":
            result = num1 + num2
        elif operation == "Subtraction":
            result = num1 - num2
        elif operation == "Multiplication":
            result = num1 * num2
        elif operation == "Division":
            result = num1 / num2 if num2 != 0 else "❌ Cannot divide by zero!"
        elif operation == "Power":
            result = num1 ** num2
        elif operation == "Modulus":
            result = num1 % num2
        elif operation == "Square Root":
            result = math.sqrt(num1)
        elif operation == "Sine":
            result = math.sin(math.radians(num1))
        elif operation == "Cosine":
            result = math.cos(math.radians(num1))
        elif operation == "Tangent":
            result = math.tan(math.radians(num1))
    except Exception as e:
        st.error(f"Error: {e}")

    if result is not None:
        st.markdown(f"<div class='result'>Result: {result}</div>", unsafe_allow_html=True)
        expr = f"{operation}: {num1}" + (f", {num2}" if num2 is not None else "") + f" = {result}"
        st.session_state.history.append(expr)
