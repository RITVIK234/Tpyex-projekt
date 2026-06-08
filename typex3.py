import streamlit as st

# ==============================================================================
# ALPHABET DEFINITION & DETERMINISTIC WIRING GENERATION
# ==============================================================================
ALPHABET = "".join(chr(i) for i in range(32, 127))
ALPHABET_SIZE = len(ALPHABET)

def generate_permutation(seed_shift):
    prime_steps = [37, 43, 47, 53, 59]
    step = prime_steps[seed_shift % len(prime_steps)]
    return "".join(ALPHABET[(i * step + seed_shift) % ALPHABET_SIZE] for i in range(ALPHABET_SIZE))

WIRING_SLOW    = generate_permutation(1)
WIRING_MEDIUM  = generate_permutation(2)
WIRING_FAST    = generate_permutation(3)
WIRING_STATOR2 = generate_permutation(4)
WIRING_STATOR1 = generate_permutation(5)

NOTCHES_FAST   = [' ', 'E', 'a', 't', '5', '!', 'M']
NOTCHES_MEDIUM = ['A', 'o', 's', '9', '#', 'x', 'I']

# ==============================================================================
# CORE CIPHER ENGINE
# ==============================================================================
def char_to_idx(char): return ord(char) - 32
def idx_to_char(idx): return chr((idx % ALPHABET_SIZE) + 32)

def rotor_pass_forward(idx, wiring, offset):
    shifted_in = (idx + offset) % ALPHABET_SIZE
    return (char_to_idx(wiring[shifted_in]) - offset) % ALPHABET_SIZE

def rotor_pass_backward(idx, wiring, offset):
    shifted_in = (idx + offset) % ALPHABET_SIZE
    return (wiring.index(idx_to_char(shifted_in)) - offset) % ALPHABET_SIZE

def process_message(text, s_pos, m_pos, f_pos, st2_pos, st1_pos):
    s_off, m_off, f_off = char_to_idx(s_pos), char_to_idx(m_pos), char_to_idx(f_pos)
    st2_off, st1_off = char_to_idx(st2_pos), char_to_idx(st1_pos)
    output_chars = []
    
    for char in text:
        if char not in ALPHABET: continue
        
        # Stepping Mechanism
        step_medium = idx_to_char(f_off) in NOTCHES_FAST
        step_slow = step_medium and (idx_to_char(m_off) in NOTCHES_MEDIUM)
        
        f_off = (f_off + 1) % ALPHABET_SIZE
        if step_medium: m_off = (m_off + 1) % ALPHABET_SIZE
        if step_slow: s_off = (s_off + 1) % ALPHABET_SIZE
            
        # Encryption Path
        signal = char_to_idx(char)
        for w, o in [(WIRING_STATOR1, st1_off), (WIRING_STATOR2, st2_off), (WIRING_FAST, f_off), (WIRING_MEDIUM, m_off), (WIRING_SLOW, s_off)]:
            signal = rotor_pass_forward(signal, w, o)
        
        signal = (ALPHABET_SIZE - 1) - signal # Reflector
        
        for w, o in [(WIRING_SLOW, s_off), (WIRING_MEDIUM, m_off), (WIRING_FAST, f_off), (WIRING_STATOR2, st2_off), (WIRING_STATOR1, st1_off)]:
            signal = rotor_pass_backward(signal, w, o)
        
        output_chars.append(idx_to_char(signal))
    return "".join(output_chars)

# ==============================================================================
# STREAMLIT USER INTERFACE
# ==============================================================================
st.set_page_config(page_title="Typex Mark II Simulator", page_icon="🔒", layout="centered")

st.title("🔒 Typex Mark II Simulator")
st.write("An extended ASCII replica of the iconic British WW2 cipher machine.")
st.markdown("---")

### 1. Rotor Settings Layout (5 Columns side-by-side)
st.subheader("⚙️ Machine Configuration")
col1, col2, col3, col4, col5 = st.columns(5)

with col1: slow_pos = st.selectbox("Slow Rotor", list(ALPHABET), index=33)  # Defaults to 'A'
with col2: med_pos  = st.selectbox("Med Rotor", list(ALPHABET), index=33)
with col3: fast_pos = st.selectbox("Fast Rotor", list(ALPHABET), index=33)
with col4: stat2_pos = st.selectbox("Stator 2", list(ALPHABET), index=33)
with col5: stat1_pos = st.selectbox("Stator 1", list(ALPHABET), index=33)

st.markdown("---")

### 2. Text Input Area
st.subheader("📝 Message Processing")
mode = st.radio("Select Operation Mode:", ["Encrypt / Decrypt"])
input_text = st.text_area("Enter your text here:", value="Typex web app is live! Try sharing a secret code.")

# Process text automatically when the user types
if input_text:
    output_text = process_message(input_text, slow_pos, med_pos, fast_pos, stat2_pos, stat1_pos)
    
    ### 3. Display Output
    st.subheader("📤 Output")
    st.code(output_text, language=None)
    st.info("💡 Tip: Because Typex is perfectly reciprocal, copying this output text, resetting the rotors to your chosen configuration, and pasting it back in will instantly decrypt it!")