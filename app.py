import os
import pandas as pd
import streamlit as st
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
import google.generativeai as genai
from streamlit.components.v1 import html

# Set Streamlit page configuration
st.set_page_config(
    page_title="🌍 Regional Language Case Study",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .stRadio [role=radiogroup] {
        align-items: center;
        gap: 1rem;
    }
    .st-bb {
        background-color: green;
    }
    .st-at {
        background-color: green;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: bold;
    }
    
</style>
""", unsafe_allow_html=True)

st.title("🌍 Regional Language Case Study")

# Session state initialization
session_keys = {
    "data": False, 
    SESSION_PRODUCT_KEY: "",
    "chosen_title": None, 
    "chosen_text": None,
    "summary": None,
    "summary_word_count": 0,
    "selected_language": "English"
}

for key, default in session_keys.items():
    st.session_state.setdefault(key, default)

def show_fancy_divider():
    html(
        """
        <hr style="
            height: 2px;
            border: none;
            background: linear-gradient(
                90deg,
                rgba(255, 0, 0, 0.5) 0%,
                rgba(0, 255, 255, 0.5) 100%
            );
            margin: 1.5rem 0;
        ">
        """
    )

def form_input():
    # Language selection in columns
    cols = st.columns(5)
    with cols[0]:
        st.session_state["selected_language"] = st.selectbox(
            "🌐 Preferred Language",
            ["English", "Russian", "Hindi", "French", "Japanese"]
        )

    with cols[2]:
        category = st.selectbox("📚 Your Interest", ["articles"])

    with cols[4]:
        search_case_study = st.text_input("🔍 Search Case Study")

    # Reset selections when new search is performed
    if st.button("🚀 Search", use_container_width=True):
        st.session_state["chosen_title"] = None
        st.session_state["chosen_text"] = None
        st.session_state["summary"] = None

        mongodb = MongoIO()
        try:
            with st.spinner("🔍 Searching MongoDB..."):
                case_studies = mongodb.get_case_study(category)

            if isinstance(case_studies, pd.DataFrame) and not case_studies.empty:
                st.success("✅ Found {} case studies".format(len(case_studies)))
                
                search_query = search_case_study.strip().lower()
                if search_query:
                    filtered_df = case_studies[
                        case_studies["article_title"].str.lower().str.contains(search_query, na=False)
                    ]
                else:
                    filtered_df = case_studies

                if not filtered_df.empty:
                    st.session_state["search_results"] = filtered_df
                else:
                    st.warning("⚠️ No matching case studies found")
                    return
            else:
                st.warning("⚠️ No case studies found")
                return

        except Exception as e:
            st.error(f"🔴 Database connection failed: {str(e)}")
            return

    # Show search results if available
    if "search_results" in st.session_state:
        show_fancy_divider()
        st.subheader("📄 Search Results")
        
        # Create tabs for better organization
        tab1, tab2 = st.tabs(["📜 Article List", "🔍 Advanced Filters"])
        
        with tab1:
            if not st.session_state["search_results"].empty:
                # Use selectbox instead of radio for better UX
                titles = st.session_state["search_results"]["article_title"].tolist()
                selected_title = st.selectbox(
                    "📰 Choose a case study:",
                    options=titles,
                    index=None if not titles else 0,
                    placeholder="Select an article..."
                )

                if selected_title:
                    selected_row = st.session_state["search_results"][
                        st.session_state["search_results"]["article_title"] == selected_title
                    ].iloc[0]
                    
                    st.session_state["chosen_title"] = selected_row["article_title"]
                    st.session_state["chosen_text"] = selected_row["article_text"]

        # Show selected article
        if st.session_state.get("chosen_title"):
            show_fancy_divider()
            st.subheader("📑 Selected Article")
            
            with st.expander(f"**{st.session_state['chosen_title']}**", expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(st.session_state["chosen_text"])
                with col2:
                    st.metric("📏 Character Count", len(st.session_state["chosen_text"]))
                    st.metric("📊 Approx Word Count", len(st.session_state["chosen_text"].split()))

            # Summarization section
            show_fancy_divider()
            st.subheader("📝 AI Summarization")
            
            

            if st.button("✨ Generate Summary", type="primary"):
                with st.spinner("🧠 Generating summary using Gemini..."):
                    try:
                        summary, word_count = summarize_text(
                            st.session_state["chosen_text"], 
                            st.session_state["selected_language"]
                        )
                        st.session_state["summary"] = summary
                        st.session_state["summary_word_count"] = word_count
                    except Exception as e:
                        st.error(f"❌ Summarization failed: {str(e)}")

            if st.session_state.get("summary"):
                st.success("✅ Summary generated successfully!")
                with st.expander("📄 View Summary", expanded=True):
                    st.write(st.session_state["summary"])
                    st.caption(f"📝 Word count: {st.session_state['summary_word_count']} words")

def summarize_text(text, language):
    """Enhanced summarization function with better error handling"""
    genai.configure(api_key="AIzaSyDVqZItqdXFTeyPwP3h917RjGxxsd_FUMs")
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = f"""Create a comprehensive summary in {language} with these requirements:
    - Maintain original technical terms
    - Preserve key numbers and statistics
    - Use clear paragraph structure
    - Maximum 500 words
    Text: {text}"""
    
    response = model.generate_content(prompt)
    
    if not response.text:
        raise ValueError("Empty response from Gemini API")
    
    # Language-specific word counting
    if language in ["Japanese", "Chinese"]:
        word_count = len(response.text)
    else:
        word_count = len(response.text.split())
    
    return response.text.strip(), word_count

if __name__ == "__main__":
    form_input() 