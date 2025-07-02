# sas-open-hmeq

A modular Python pipeline for training, evaluating, and serializing a Gradient Boosting classifier on the HMEQ dataset, with optional import into SAS Model Manager via OAuth2.

## Project Structure

```
hmeq_model_project/
├── .env                               # Env vars for OAuth2
├── config/                           # Pipeline parameters
│   └── params.yaml
├── data/                              # Raw data
│   └── hmeq.csv
├── src/                               # Modular code
│   ├── data_loading.py
│   ├── preprocessing.py
│   ├── training.py
│   ├── evaluation.py
│   ├── serialization.py
│   ├── import_model.py
│   └── utils/auth_utils.py           # OAuth2 helpers
├── run_pipeline.py                    # Orchestrator
├── requirements.txt                   # Python deps
└── .gitignore                         # Ignored files
```

## Installation

1. Create and activate a venv:
   ```bash
   python3.10 -m venv venv && source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
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

## Configuration

Adjust `config/params.yaml` or set env vars in `.env` for OAuth2 credentials, SAS host, certificate path, etc.
