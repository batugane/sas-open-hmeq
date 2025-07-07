# SWAT Guide: SAS Cloud Analytics Services with Python

## Overview

This guide demonstrates how to use **SAS Cloud Analytics Services (CAS)** with Python using the **SWAT** library. This approach is ideal for interactive analytics, real-time model building, and cloud-based data processing.

**Key Concept**: SWAT connects Python directly to SAS CAS, allowing you to perform analytics in the cloud while staying in your Python environment.

## Prerequisites

- Python 3.8+
- Access to SAS Cloud Analytics Services (CAS)
- SAS credentials for OAuth2 authentication

## Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install swat pandas numpy python-dotenv requests urllib3
```

### 3. Environment Setup
Create `.env` file:
```env
SAS_CLIENT_ID=your_client_id_here
SAS_CLIENT_SECRET=your_client_secret_here
SAS_BASE_URL=https://create.demo.sas.com
SAS_CERT_PATH=C:/sas/model-manager/demo-rootCA-Intermidiates_4CLI.pem
```

## Step-by-Step Implementation

### Step 1: Authentication Setup

Create `auth_utils.py`:
```python
import requests
import os
import base64
import swat
from dotenv import load_dotenv

load_dotenv()

def get_token():
    """Get OAuth2 access token for SAS Cloud"""
    # Implementation for token generation/refresh
    # See auth_utils.py in the project for full implementation
    pass

def connect_cas_https(access_token: str):
    """Connect to CAS using HTTPS and OAuth2"""
    return swat.CAS(
        "https://create.demo.sas.com/cas-shared-default-http",
        username=None,
        password=access_token,
        ssl_ca_list=os.getenv("SAS_CERT_PATH"),
        protocol="https"
    )
```

### Step 2: Basic CAS Connection

```python
import pandas as pd
import urllib3
from swat import CAS
from auth_utils import get_token, connect_cas_https

# Connect to CAS
token = get_token()
cas = connect_cas_https(token)
print("✅ Connected to CAS successfully!")
```

### Step 3: Data Upload

```python
# Load your dataset
data = pd.read_csv("your_data.csv")
print(f"Dataset: {data.shape[0]} rows, {data.shape[1]} columns")

# Upload to CAS
cas.upload(data, casout={"name":"mydata", "promote":True})
print("✅ Data uploaded to CAS!")
```

### Step 4: Data Exploration

```python
# Create CASTable object
tbl = cas.CASTable("mydata")

# Get table information
info = cas.table.tableinfo(table=tbl)
print(f"Table info: {info['TableInfo']['Rows'].iloc[0]} rows")

# Get column information
col_info = cas.table.columninfo(table=tbl)
print(f"Columns: {list(col_info['ColumnInfo']['Column'].values)}")
```

### Step 5: Descriptive Statistics

```python
# Load simple actionset for basic statistics
cas.loadactionset('simple')

# Summary statistics
summary = cas.simple.summary(table=tbl, inputs=["column1", "column2"])
print("📈 Summary statistics generated!")

# Frequency analysis
freq = cas.simple.freq(table=tbl, inputs=["categorical_column"])
print("📊 Frequency tables created!")

# Correlation analysis
corr = cas.simple.correlation(table=tbl, inputs=["numeric_col1", "numeric_col2"])
print("🔗 Correlation matrix computed!")
```

### Step 6: Model Building

```python
# Load regression actionset
cas.loadactionset('regression')

# Build linear regression model
result = cas.regression.glm(
    table={"name":"mydata"},
    inputs=["predictor_column"],
    target="target_column"
)

# Extract model parameters
if 'ParameterEstimates' in result:
    estimates = result['ParameterEstimates']
    intercept = estimates[estimates['Parameter'] == 'Intercept']['Estimate'].iloc[0]
    coef = estimates[estimates['Parameter'] == 'predictor_column']['Estimate'].iloc[0]
    
    print(f"Model: target = {intercept:.2f} + {coef:.6f} * predictor")
```

### Step 7: Making Predictions

```python
# Use model coefficients for predictions
sample_values = [100, 200, 300]
predictions = []

for value in sample_values:
    pred = intercept + coef * value
    predictions.append(pred)
    print(f"Input: {value} → Prediction: {pred:.2f}")
```

### Step 8: Data Download

```python
# Download data back to Python
table = cas.CASTable("mydata")
downloaded_data = table.to_frame()
print(f"📥 Downloaded data: {downloaded_data.shape}")
```

### Step 9: Cleanup

```python
# Close CAS connection
cas.close()
```

## Complete Example: HMEQ Dataset

Here's a complete working example using the HMEQ dataset:

```python
import pandas as pd
import urllib3
from swat import CAS
from auth_utils import get_token, connect_cas_https

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    # 1. Connect to CAS
    token = get_token()
    cas = connect_cas_https(token)
    
    # 2. Load and upload data
    data = pd.read_csv("data/hmeq.csv")
    cas.upload(data, casout={"name":"hmeq", "promote":True})
    
    # 3. Explore data
    tbl = cas.CASTable("hmeq")
    info = cas.table.tableinfo(table=tbl)
    print(f"Dataset: {info['TableInfo']['Rows'].iloc[0]} rows")
    
    # 4. Build model
    cas.loadactionset('regression')
    result = cas.regression.glm(
        table={"name":"hmeq"},
        inputs=["LOAN"],
        target="DEBTINC"
    )
    
    # 5. Extract results
    if 'ParameterEstimates' in result:
        estimates = result['ParameterEstimates']
        intercept = estimates[estimates['Parameter'] == 'Intercept']['Estimate'].iloc[0]
        loan_coef = estimates[estimates['Parameter'] == 'LOAN']['Estimate'].iloc[0]
        print(f"Model: DEBTINC = {intercept:.2f} + {loan_coef:.6f} * LOAN")
    
    cas.close()

if __name__ == '__main__':
    main()
```

## Key SWAT Concepts

### CASTable Objects
```python
# Create CASTable reference
tbl = cas.CASTable("table_name")

# Use in actions
result = cas.simple.summary(table=tbl)
```

### Action Sets
```python
# Load different analytics capabilities
cas.loadactionset('simple')    # Basic statistics
cas.loadactionset('regression') # Regression models
cas.loadactionset('clustering') # Clustering algorithms
```

### Result Handling
```python
# CAS results are dictionaries with multiple components
result = cas.regression.glm(...)

# Access different parts
if 'ParameterEstimates' in result:
    params = result['ParameterEstimates']
if 'FitStatistics' in result:
    stats = result['FitStatistics']
```

## Common Use Cases

### 1. Interactive Analytics
- Real-time data exploration
- Quick model prototyping
- Ad-hoc analysis

### 2. Large Data Processing
- Handle datasets too large for local memory
- Leverage CAS distributed computing
- Cloud-based analytics

### 3. Model Development
- Rapid model iteration
- Multiple algorithm comparison
- Feature engineering

## Best Practices

### 1. Connection Management
```python
# Always close connections
try:
    cas = connect_cas_https(token)
    # Your code here
finally:
    cas.close()
```

### 2. Error Handling
```python
# Handle table operations gracefully
try:
    cas.table.droptable(caslib="CASUSER", name="table_name")
except:
    pass  # Table doesn't exist
```

### 3. Data Validation
```python
# Check data before modeling
info = cas.table.tableinfo(table=tbl)
if info['TableInfo']['Rows'].iloc[0] == 0:
    print("Warning: Empty table!")
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify OAuth2 credentials
   - Check network connectivity
   - Ensure certificate path is correct

2. **Table Not Found**
   - Use `cas.table.tableinfo()` to list available tables
   - Check caslib permissions

3. **Action Set Not Available**
   - Use `cas.loadactionset('actionset_name')`
   - Verify your CAS instance has the required capabilities

### Debug Tips

```python
# List available action sets
print(cas.builtins.actionSetInfo())

# List available tables
print(cas.table.tableinfo())

# Check connection status
print(cas.builtins.serverStatus())
```

## Summary

SWAT provides a powerful bridge between Python and SAS Cloud Analytics Services, enabling:

- **Interactive analytics** in the cloud
- **Real-time model development**
- **Large-scale data processing**
- **Seamless Python integration**

This approach is ideal for data scientists who want to leverage SAS analytics capabilities while staying in their Python workflow.

## Next Steps

1. **Explore more action sets**: clustering, decision trees, neural networks
2. **Try different data types**: time series, text analytics, image processing
3. **Build production pipelines**: automated model training and scoring
4. **Integrate with other tools**: combine with pandas, scikit-learn, or other Python libraries

---

**Note**: This guide focuses on the SWAT approach. For model deployment and management, see the [SASCTL Guide](SASCTL_GUIDE.md). 