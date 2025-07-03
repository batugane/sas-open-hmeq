# sas-open-hmeq

A modular Python pipeline for training, evaluating, and serializing a Gradient Boosting classifier on the HMEQ dataset, with optional import into SAS Model Manager via OAuth2.

## Features

- **Modular Architecture**: Clean separation of concerns across data loading, preprocessing, training, evaluation, and serialization
- **Logging**: Comprehensive logging throughout the pipeline for better traceability and debugging
- **Error Handling**: Robust exception handling for production reliability
- **Configuration Management**: YAML-based configuration for easy experimentation
- **OAuth2 Integration**: Secure authentication with SAS Model Manager

## Project Structure

```
sas-open-hmeq/
├── .env                               # Env vars for OAuth2 (create from env.sample)
├── config/                           # Pipeline parameters
│   └── params.yaml
├── data/                              # Raw data and model outputs
│   ├── hmeq.csv
│   └── hmeqModels/                   # Serialized models
├── src/                               # Modular code
│   ├── data_loading.py               # Data ingestion
│   ├── preprocessing.py              # Data preprocessing and splitting
│   ├── training.py                   # Model training
│   ├── evaluation.py                 # Model evaluation with logging
│   ├── serialization.py              # Model serialization for SAS
│   ├── import_model.py               # SAS Model Manager import with error handling
│   └── utils/auth_utils.py           # OAuth2 helpers with logging
├── tests/                             # Unit tests (if present)
├── run_pipeline.py                    # Main pipeline orchestrator
├── requirements.txt                   # Python dependencies with versions
└── .gitignore                         # Ignored files
```

## Installation

1. Create and activate a virtual environment:
   ```bash
   python3.10 -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Copy the sample environment file
   cp env.sample .env
   # Edit .env with your SAS credentials and settings
   ```

## Usage

- **Dry run (serialize only):**
  ```bash
  python run_pipeline.py --skip-import
  ```
- **Full pipeline (including SAS import):**
  ```bash
  python run_pipeline.py
  ```

## Scoring with MAS

**Note:** Before using these scoring scripts, you must first publish your model to the destination: SAS Micro Analytic Service (maslocal).

This project provides two command-line scripts for scoring data using a MAS-deployed model:

### 1. score_with_mas_rest.py (Direct REST API)
- Uses direct HTTP requests to the MAS REST API.
- Good for debugging or when you need full control over the request/response.
- Outputs a CSV with predictions and (optionally) input fields.

**Example usage:**
```bash
python score_with_mas_rest.py -H https://create.demo.sas.com -m <module_name> -i data/hmeq_test.csv -o data/hmeq_scored.csv
```

### 2. score_with_mas_sasctl.py (sasctl Library, Recommended)
- Uses the official `sasctl` Python library for a higher-level, more robust interface.
- Handles authentication, session management, and error handling for you.
- Outputs a CSV with both predictions and all original input fields for traceability.
- Preferred for most users.

**Example usage:**
```bash
python score_with_mas_sasctl.py -H https://create.demo.sas.com -m <module_name> -i data/hmeq_test.csv -o data/hmeq_scored.csv
```

**Note:** Both scripts require the same environment setup (see Installation above) and should be run from the project root directory.

## Configuration

Adjust `config/params.yaml` for model parameters, data paths, and pipeline settings. Set OAuth2 credentials and SAS connection details in `.env` file (use `env.sample` as template).

## Logging

The pipeline uses Python's logging module for comprehensive output tracking:
- **INFO**: General pipeline progress and results
- **WARNING**: Non-critical issues (e.g., token refresh failures)  
- **ERROR**: Critical failures with detailed error messages

## Dependencies

Key dependencies (see `requirements.txt` for full list with versions):
- `pandas`, `numpy`: Data manipulation
- `scikit-learn`: Machine learning
- `pyyaml`: Configuration management
- `sasctl[all]`: SAS Model Manager integration
- `swat`: SAS connection utilities
- `python-dotenv`: Environment variable management
