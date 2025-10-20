# S3Manager CLI

A Python command-line tool for managing Amazon S3 operations including listing files, uploading files, and reading JSON objects from S3 buckets.

## Features

- **List Files**: Browse files in S3 buckets with detailed information (size, last modified date)
- **Upload Files**: Upload local files to S3 with custom or default paths
- **Read JSON**: Directly read and display JSON objects from S3 without downloading files
- **Flexible Configuration**: Support for custom bucket names and prefixes
- **Rich Output**: Beautiful console output with emojis and formatting using the `rich` library

## Prerequisites

- Python 3.6+
- AWS credentials configured via environment variables
- Required Python packages (see Installation section)

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install boto3 rich
```

## AWS Configuration

Set up your AWS credentials using environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export AWS_REGION="your_region_here"  # e.g., "us-east-1"
```

Alternatively, you can use AWS CLI configuration:

```bash
aws configure
```

## Usage

### Command Line Interface

The tool provides three main commands:

#### 1. List Files

List all files in the default S3 folder:

```bash
python test_aws_s3.py list
```

#### 2. Upload Files

Upload a local file to S3:

```bash
# Upload with default S3 key
python test_aws_s3.py upload /path/to/local/file.json

# Upload with custom S3 key
python test_aws_s3.py upload /path/to/local/file.json --s3-key custom/path/file.json
```

#### 3. Read JSON

Read and display a JSON object from S3:

```bash
# Read with default S3 key
python test_aws_s3.py read

# Read with custom S3 key
python test_aws_s3.py read --s3-key custom/path/file.json
```

### Programmatic Usage

You can also use the `S3Manager` class directly in your Python code:

```python
from test_aws_s3 import S3Manager

# Create an instance with default settings
s3_manager = S3Manager()

# Or with custom settings
s3_manager = S3Manager(
    bucket_name="my-custom-bucket",
    prefix="my/custom/path/"
)

# List files
s3_manager.list_objects_in_folder()

# Upload a file
success = s3_manager.upload_file_to_s3(
    s3_key="path/to/remote/file.json",
    file_path="/local/path/to/file.json"
)

# Read JSON data
json_data = s3_manager.read_json_from_s3("path/to/remote/file.json")
```

## Default Configuration

- **Default Bucket**: `redis-ai-research`
- **Default Prefix**: `srijithr/datasets/`
- **Default S3 Key for uploads/reads**: `srijithr/datasets/assembled_data.json`

## Command Reference

### `list`
Lists all files in the configured S3 folder.

**Usage:**
```bash
python test_aws_s3.py list
```

**Output:**
```
=== Listing existing files ===
Files in 'redis-ai-research/srijithr/datasets/':
  - srijithr/datasets/assembled_data.json (1024 bytes, 2024-01-15 10:30:00+00:00)
  - srijithr/datasets/backup_data.json (2048 bytes, 2024-01-14 15:45:00+00:00)
```

### `upload`
Uploads a local file to S3.

**Usage:**
```bash
python test_aws_s3.py upload <local_path> [--s3-key <s3_key>]
```

**Arguments:**
- `local_path` (required): Path to the local file to upload
- `--s3-key` (optional): S3 key (remote path) where the file should be stored

**Examples:**
```bash
# Upload with default S3 key
python test_aws_s3.py upload ./data.json

# Upload with custom S3 key
python test_aws_s3.py upload ./data.json --s3-key my-data/uploaded-file.json
```

### `read`
Reads and displays a JSON object from S3.

**Usage:**
```bash
python test_aws_s3.py read [--s3-key <s3_key>]
```

**Arguments:**
- `--s3-key` (optional): S3 key (remote path) of the JSON file to read

**Examples:**
```bash
# Read with default S3 key
python test_aws_s3.py read

# Read with custom S3 key
python test_aws_s3.py read --s3-key my-data/config.json
```

## Error Handling

The tool includes comprehensive error handling:

- **AWS Authentication Errors**: Clear messages when credentials are missing or invalid
- **File Not Found**: Helpful error messages when local files don't exist
- **S3 Access Errors**: Detailed error reporting for S3 permission issues
- **JSON Parsing Errors**: Graceful handling of malformed JSON files

## Exit Codes

- `0`: Success
- `1`: Error (upload failed, file not found, JSON parsing error, etc.)

## Examples

### Complete Workflow Example

```bash
# 1. List existing files
python test_aws_s3.py list

# 2. Upload a new file
python test_aws_s3.py upload ./my-data.json --s3-key srijithr/datasets/my-data.json

# 3. Verify the upload by listing again
python test_aws_s3.py list

# 4. Read the uploaded JSON
python test_aws_s3.py read --s3-key srijithr/datasets/my-data.json
```

### Using with Different Buckets

To work with different buckets, modify the `S3Manager` class initialization in the code:

```python
# In the main() function, change:
s3_manager = S3Manager(bucket_name="your-bucket-name", prefix="your/prefix/")
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   ```
   Error: AWS credentials not configured
   ```
   **Solution**: Set the required environment variables or run `aws configure`

2. **Permission Denied**
   ```
   ❌ Error uploading file to S3: Access Denied
   ```
   **Solution**: Ensure your AWS credentials have the necessary S3 permissions

3. **File Not Found**
   ```
   ❌ Error uploading file to S3: [Errno 2] No such file or directory
   ```
   **Solution**: Verify the local file path is correct

4. **Invalid JSON**
   ```
   ❌ Error reading JSON from S3: Expecting value: line 1 column 1 (char 0)
   ```
   **Solution**: Ensure the S3 object contains valid JSON

### Debug Mode

To see more detailed AWS configuration information, the tool prints the AWS config on startup:

```
AWS Config: {'access_key_id': 'AKIA...', 'secret_access_key': '***', 'region': 'us-east-1'}
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).