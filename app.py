import streamlit as st
import json
import pandas as pd

# Set page config
st.set_page_config(
    page_title="JSON File Uploader",
    page_icon="📊",
    layout="centered"
)

# Main content
st.title("JSON File Uploader")
st.write("Upload a JSON file to display its contents in a table.")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a JSON file",
    type=['json'],
    help="Upload a JSON file to view its contents"
)

if uploaded_file is not None:
    try:
        # Read and parse JSON
        json_data = json.load(uploaded_file)
        
        try:
            df = pd.DataFrame(json_data["data_deduplicated"])
            df = df[["anchor_sentence", "opposite_sentence", "same_meaning_sentence"]]
        except Exception as e:
            st.error("Unsupported JSON format. Please upload a JSON file with an array of objects or a single object.")
            st.stop()

        # Display the table
        st.subheader("📊 Data Table")
        st.dataframe(df, use_container_width=True)
        
        # Show summary info
        st.info(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns")
        
            
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON file. Please check the file format.")
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
else:
    st.info("👆 Please upload a JSON file to get started")
    
    # Show example of expected format
    with st.expander("📝 Example JSON format"):
        st.code("""
[
  {"name": "John", "age": 30, "city": "New York"},
  {"name": "Jane", "age": 25, "city": "Los Angeles"},
  {"name": "Bob", "age": 35, "city": "Chicago"}
]
        """, language="json")
