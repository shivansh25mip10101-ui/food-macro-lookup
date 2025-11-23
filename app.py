import streamlit as st
import pandas as pd
from difflib import get_close_matches

# Small built-in macro database (values are grams per 100 g)

MACRO_DB = {
    "apple": {"protein": 0.3, "fat": 0.2, "carbs": 14.0},
    "banana": {"protein": 1.1, "fat": 0.3, "carbs": 23.0},
    "white rice (cooked)": {"protein": 2.7, "fat": 0.3, "carbs": 28.0},
    "brown rice (cooked)": {"protein": 2.6, "fat": 1.0, "carbs": 23.0},
    "boiled potato": {"protein": 2.0, "fat": 0.1, "carbs": 17.0},
    "chicken breast (cooked)": {"protein": 31.0, "fat": 3.6, "carbs": 0.0},
    "salmon (cooked)": {"protein": 25.0, "fat": 13.0, "carbs": 0.0},
    "egg (whole, cooked)": {"protein": 13.0, "fat": 11.0, "carbs": 1.1},
    "cheddar cheese": {"protein": 25.0, "fat": 33.0, "carbs": 1.3},
    "pizza (average)": {"protein": 11.0, "fat": 10.0, "carbs": 26.0},
    "peanut butter": {"protein": 25.0, "fat": 50.0, "carbs": 20.0},
    "paneer (cottage cheese)": {"protein": 18.0, "fat": 20.0, "carbs": 1.2},
    "apple pie": {"protein": 2.4, "fat": 11.0, "carbs": 42.0},
    "ice cream (vanilla)": {"protein": 3.5, "fat": 11.0, "carbs": 24.0},
    "fried rice": {"protein": 6.0, "fat": 8.0, "carbs": 28.0}
}

def find_best_match(query, choices, cutoff=0.5, n=3):
    q = query.strip().lower()
    if q in choices:
        return q, 1.0
    
    possible = get_close_matches(q, choices, n=n, cutoff=0.0)
    
    def score(a, b):
        a2, b2 = a.replace(" ", ""), b.replace(" ", "")
        common = sum((1 for ch in set(a2) if ch in b2))
        return common / max(len(set(a2)), 1)
    best = None
    best_score = -1.0
    for cand in possible:
        s = score(q, cand)
        if s > best_score:
            best_score = s; best = cand
    
    if best is None and possible:
        return possible[0], 0.0
    return best, best_score

def scale_macros(macros_per100g, serving_g):
    if macros_per100g is None:
        return None
    return {k: (v * (serving_g / 100.0) if v is not None else None) for k, v in macros_per100g.items()}

# Streamlit UI
st.set_page_config(page_title="Food Macro Lookup", layout="centered")
st.title("🍽 Food Macro Lookup — Quick Demo")
st.write("Type a food name (e.g. 'pizza', 'chicken breast') or pick from the dropdown.")

col1, col2 = st.columns([2,1])
with col1:
    user_text = st.text_input("Food name (type here)", value="")
    selected = st.selectbox("Or choose from known foods", options=[""] + sorted(MACRO_DB.keys()))
with col2:
    serving = st.number_input("Serving (grams)", value=100.0, min_value=1.0, max_value=5000.0, step=5.0)

# Determine query
query = user_text.strip() if user_text.strip() else (selected.strip() if selected else "")
if not query:
    st.info("Enter a food name or choose one from the dropdown to see macros.")
    st.stop()

# find best match
choices = list(MACRO_DB.keys())
best, confidence = find_best_match(query, choices)
if best is None:
    st.error("No match found. Try a different name or edit the built-in database.")
    st.stop()

st.write(f"*Best match:* {best} (confidence ~ {confidence:.2f})")

macros100 = MACRO_DB.get(best)
scaled = scale_macros(macros100, serving)

# show table
df = pd.DataFrame([
    {"measure": "per 100 g", "protein_g": macros100["protein"], "fat_g": macros100["fat"], "carb_g": macros100["carbs"]},
    {"measure": f"per {serving} g", "protein_g": scaled["protein"], "fat_g": scaled["fat"], "carb_g": scaled["carbs"]}
])
st.table(df.set_index("measure").round(2))

# allow download
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button("Download result as CSV", data=csv_bytes, file_name="macro_lookup_result.csv", mime="text/csv")

st.markdown("---")
st.write("Want more foods? Edit the MACRO_DB dictionary in app.py to add entries (protein/fat/carbs per 100 g).")