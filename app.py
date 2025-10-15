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

        # Initialize session state for validation checkboxes if not exists
        if 'validation_states' not in st.session_state:
            st.session_state.validation_states = [False] * len(df)
        
        # Ensure validation states match current dataframe length
        if len(st.session_state.validation_states) != len(df):
            st.session_state.validation_states = [False] * len(df)

        # Display validation interface
        st.subheader("📊 Data Validation Table")
        st.write("Review the sentences and check the box if they are correctly labeled:")
        
        # Create columns for layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**Data Preview:**")
        
        with col2:
            st.write("**Validation:**")
        
        # Display each row with validation checkbox
        for idx, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.write(f"**Anchor:** {row['anchor_sentence']}")
            
            with col2:
                st.write(f"**Opposite:** {row['opposite_sentence']}")
            
            with col3:
                st.write(f"**Same Meaning:** {row['same_meaning_sentence']}")
            
            with col4:
                # Create unique key for each checkbox
                checkbox_key = f"validate_{idx}"
                is_valid = st.checkbox(
                    "✓ Valid", 
                    value=st.session_state.validation_states[idx],
                    key=checkbox_key
                )
                # Update session state
                st.session_state.validation_states[idx] = is_valid
            
            st.divider()
        
        # Show validation summary
        validated_count = sum(st.session_state.validation_states)
        total_count = len(df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", total_count)
        with col2:
            st.metric("Validated", validated_count)
        with col3:
            st.metric("Remaining", total_count - validated_count)
        
        # Progress bar
        progress = validated_count / total_count if total_count > 0 else 0
        st.progress(progress, text=f"Validation Progress: {validated_count}/{total_count} ({progress:.1%})")
        
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
