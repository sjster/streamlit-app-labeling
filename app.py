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
        
        # Create table header
        header_col1, header_col2, header_col3, header_col4 = st.columns([2, 2, 2, 1])
        
        with header_col1:
            st.markdown("**🔗 Anchor Sentence**")
        
        with header_col2:
            st.markdown("**🔄 Opposite Sentence**")
        
        with header_col3:
            st.markdown("**✅ Same Meaning Sentence**")
        
        with header_col4:
            st.markdown("**✓ Validation**")
        
        # Add a separator line
        st.markdown("---")
        
        # Display each row with validation checkbox
        for idx, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.write(f"{row['anchor_sentence']}")
            
            with col2:
                st.write(f"{row['opposite_sentence']}")
            
            with col3:
                st.write(f"{row['same_meaning_sentence']}")
            
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
        
        # Download section
        st.subheader("📥 Download Results")
        
        # Create a copy of the dataframe with validation column
        df_with_validation = df.copy()
        df_with_validation['is_validated'] = st.session_state.validation_states
        
        # Convert to CSV for download
        csv_data = df_with_validation.to_csv(index=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download CSV with Validation",
                data=csv_data,
                file_name="validated_data.csv",
                mime="text/csv",
                help="Download the data with validation results as a CSV file"
            )
        
        with col2:
            # Download only validated rows
            validated_df = df_with_validation[df_with_validation['is_validated'] == True]
            if len(validated_df) > 0:
                validated_csv = validated_df.to_csv(index=False)
                st.download_button(
                    label="✅ Download Only Validated Rows",
                    data=validated_csv,
                    file_name="validated_only_data.csv",
                    mime="text/csv",
                    help="Download only the rows that have been validated"
                )
            else:
                st.info("No validated rows to download yet")
        
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
