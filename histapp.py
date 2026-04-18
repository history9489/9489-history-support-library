import os
import streamlit as st
import fitz  # PyMuPDF
from docx import Document

# --- 1. GLOBAL CONFIGURATION ---
st.set_page_config(page_title="History 9489 Portal", layout="wide")

# Updated folders to match your repository Year 10-13 structure
FOLDERS = ["Year 10", "Year 11", "Year 12", "Year 13"]
for folder in FOLDERS:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Initialize session states
if 'basket' not in st.session_state:
    st.session_state.basket = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# --- 2. CORE FUNCTIONS ---

def search_pdfs(keyword):
    """Scans local PDFs for keyword text"""
    results = []
    for folder in FOLDERS:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith(".pdf"):
                    file_path = os.path.join(folder, file)
                    try:
                        doc = fitz.open(file_path)
                        found_in_file = False
                        for page in doc:
                            if keyword.lower() in page.get_text().lower():
                                found_in_file = True
                                break
                        doc.close()
                        if found_in_file:
                            results.append({"name": file, "path": file_path})
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
    return results

# --- 3. MAIN INTERFACE ---
st.title("PUSAT TINGKATAN ENAM SENGKURONG")
st.title("📜 9489 A Level History PYP Portal")
st.info("Manual Upload: Tutors please add new papers directly to the GitHub repository folders.")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🔍 Search Topics", "🧺 Handout Basket", "🔐 Lecturer Hub"])

# --- TAB 1: SEARCH ---
with tab1:
    st.subheader("Search Past Papers")
    keyword = st.text_input("Enter a historical topic (e.g., 'Civil War'):", key="search_input")

    if st.button("Run Search"):
        if keyword:
            with st.spinner('Scanning archives...'):
                st.session_state.search_results = search_pdfs(keyword)
        else:
            st.warning("Please enter a keyword.")

    if st.session_state.search_results:
        st.success(f"Found {len(st.session_state.search_results)} relevant papers.")
        for item in st.session_state.search_results:
            col1, col2 = st.columns([4, 1])
            col1.write(f"📄 {item['name']}")

            is_in_basket = any(b['name'] == item['name'] for b in st.session_state.basket)
            if col2.button("➕ Add", key=f"add_{item['name']}"):
                if not is_in_basket:
                    st.session_state.basket.append(item)
                    st.toast(f"Added {item['name']}!")
                else:
                    st.toast("Already in basket!")

# --- TAB 2: BASKET ---
with tab2:
    st.subheader("Your Handout Collection")
    if st.session_state.basket:
        for i, paper in enumerate(st.session_state.basket):
            st.write(f"{i + 1}. {paper['name']}")

        st.divider()
        col_clear, col_word = st.columns([1, 1.5])

        with col_clear:
            if st.button("🗑️ Clear All"):
                st.session_state.basket = []
                st.rerun()

        with col_word:
            if st.button("📄 Generate Handout (Word)"):
                doc = Document()
                doc.add_heading('PTES History 9489 Handout', 0)
                for paper in st.session_state.basket:
                    doc.add_heading(f"Source: {paper['name']}", level=1)
                    pdf = fitz.open(paper['path'])
                    for page in pdf:
                        doc.add_paragraph(page.get_text())
                    pdf.close()
                from io import BytesIO
                bio_word = BytesIO()
                doc.save(bio_word)
                st.download_button("📥 Download Word", bio_word.getvalue(), "handout.docx")
    else:
        st.info("Basket is empty.")

# --- TAB 3: LECTURER HUB ---
with tab3:
    st.subheader("📚 Lecturer Resource Manager")
    password = st.text_input("Enter Admin Password", type="password", key="admin_pw")

    if password == "brunei9489":
        st.write("Current Archive Contents:")
        for folder in FOLDERS:
            if os.path.exists(folder):
                files = os.listdir(folder)
                if files:
                    st.markdown(f"**{folder}**")
                    for f in files:
                        st.write(f" - {f}")
    elif password != "":
        st.error("Incorrect Password")
