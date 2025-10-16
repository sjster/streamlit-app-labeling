import streamlit as st
import json
import pandas as pd
import boto3
import os
import json
from rich import print


aws = st.secrets["aws"]

session = boto3.Session(
    aws_access_key_id=aws["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=aws["AWS_SECRET_ACCESS_KEY"],
    region_name=aws["AWS_REGION"],
)
s3 = session.client("s3")

bucket_name = aws["bucket_name"]
prefix = aws["prefix"]

def read_json_from_s3(s3, bucket_name, s3_key):
    """Read a JSON object directly from S3 without saving to a file"""
    try:
        response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        content = response['Body'].read().decode('utf-8')
        json_obj = json.loads(content)
        print(f"✅ Successfully read JSON from s3://{bucket_name}/{s3_key}")
        return json_obj
    except Exception as e:
        print(f"❌ Error reading JSON from S3: {str(e)}")
        return None


# Set page config
st.set_page_config(
    page_title="Data Labeling (Triplets)",
    page_icon="📊",
    layout="centered"
)

# Main content
st.title("Data Labeling (Triplets)")
#st.write("Upload a JSON file to display its contents in a table.")

# Initialize session state for S3 data
if 's3_data' not in st.session_state:
    st.session_state.s3_data = None

# File uploader section
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("⬇️ Download data"):
        try:
            json_obj = read_json_from_s3(s3, bucket_name, f"{prefix}assembled_data.json")
            if json_obj is not None:
                st.session_state.s3_data = json_obj
                st.success(f"✅ Successfully downloaded data")
            else:
                st.error("Failed to download data from S3")
        except Exception as e:
            st.error(f"Error downloading file from S3: {str(e)}")

with col2:
    if st.button("🗑️ Clear Data"):
        st.session_state.s3_data = None
        st.session_state.validation_states = []
        st.success("Data cleared!")

# Show data status
if st.session_state.s3_data is not None:
    st.info(f"📊 Data loaded: {len(st.session_state.s3_data)} rows ready for validation")

# Use session state data
json_obj = st.session_state.s3_data

if json_obj is not None:

    try:
        # Read and parse JSON
        #json_data = json.load(uploaded_file)
        json_data = json_obj
        
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
        
        # Pagination setup
        rows_per_page = 5
        total_pages = (len(df) + rows_per_page - 1) // rows_per_page
        
        # Initialize page in session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # Always use session state for the current page
        page = st.session_state.current_page
        
        # Page navigation - just show current page info
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.write(f"**Current Page: {page} of {total_pages}**")
        
        # Calculate start and end indices for current page
        start_idx = (page - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, len(df))
        
        # Display pagination info
        st.info(f"Showing rows {start_idx + 1}-{end_idx} of {len(df)} total rows (Page {page} of {total_pages})")
        
        # Display each row with validation checkbox for current page
        for idx in range(start_idx, end_idx):
            row = df.iloc[idx]
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
        
        # Current page validation stats
        current_page_validated = sum(st.session_state.validation_states[start_idx:end_idx])
        current_page_total = end_idx - start_idx
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", total_count)
        with col2:
            st.metric("Validated", validated_count)
        with col3:
            st.metric("Remaining", total_count - validated_count)
        with col4:
            st.metric("Page Validated", f"{current_page_validated}/{current_page_total}")
        
        # Progress bar
        progress = validated_count / total_count if total_count > 0 else 0
        st.progress(progress, text=f"Overall Progress: {validated_count}/{total_count} ({progress:.1%})")
        
        # Page navigation
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                jump_page = st.number_input(
                    "Jump to page:",
                    min_value=1,
                    max_value=total_pages,
                    value=page,
                    step=1,
                    key="jump_page_input"
                )
                if jump_page != page:
                    st.session_state.current_page = int(jump_page)
                    st.rerun()
        
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
    st.info("👆 Please click download data to get started")
    
