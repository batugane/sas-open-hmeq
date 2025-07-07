import pandas as pd
import urllib3
from swat import CAS
from src.utils.auth_utils import get_token, connect_cas_https

# Suppress SSL warnings for demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("🚀 SWAT Package Demo - Core Functionalities")
    print("=" * 50)
    
    # 1. CONNECTION
    print("\n1️⃣ Connecting to SAS Cloud Analytics Services...")
    token = get_token()
    cas = connect_cas_https(token)
    print("✅ Connected to CAS successfully!")

    # 2. DATA UPLOAD
    print("\n2️⃣ Loading and uploading data...")
    hmeq_data = pd.read_csv("data/hmeq.csv")
    print(f"📊 Dataset: {hmeq_data.shape[0]} rows, {hmeq_data.shape[1]} columns")
    
    # Drop table if it exists, then upload
    try:
        cas.table.droptable(caslib="CASUSER", name="hmeq")
    except:
        pass
    
    cas.upload(hmeq_data, casout={"name":"hmeq", "promote":True})
    print("✅ Data uploaded to CAS!")

    # 3. BASIC DATA EXPLORATION
    print("\n3️⃣ Basic data exploration...")
    tbl = cas.CASTable("hmeq")
    
    # Get table info
    info = cas.table.tableinfo(table=tbl)
    print(f"📋 Table info: {info['TableInfo']['Rows'].iloc[0]} rows, {info['TableInfo']['Columns'].iloc[0]} columns")
    
    # Get column info
    col_info = cas.table.columninfo(table=tbl)
    print(f"📝 Columns: {list(col_info['ColumnInfo']['Column'].values)}")

    # 4. DESCRIPTIVE STATISTICS
    print("\n4️⃣ Descriptive statistics...")
    cas.loadactionset('simple')
    summary = cas.simple.summary(table=tbl, inputs=["LOAN", "DEBTINC", "BAD"])
    print("📈 Summary statistics generated!")

    # 5. FREQUENCY ANALYSIS
    print("\n5️⃣ Frequency analysis...")
    freq_bad = cas.simple.freq(table=tbl, inputs=["BAD"])
    freq_job = cas.simple.freq(table=tbl, inputs=["JOB"])
    print("📊 Frequency tables created!")

    # 6. CORRELATION ANALYSIS
    print("\n6️⃣ Correlation analysis...")
    corr = cas.simple.correlation(table=tbl, inputs=["LOAN", "DEBTINC", "VALUE"])
    print("🔗 Correlation matrix computed!")

    # 7. LINEAR REGRESSION
    print("\n7️⃣ Building linear regression model...")
    cas.loadactionset('regression')
    result = cas.regression.glm(
        table={"name":"hmeq"},
        inputs=["LOAN"],
        target="DEBTINC"
    )
    
    if 'ParameterEstimates' in result:
        estimates = result['ParameterEstimates']
        intercept = estimates[estimates['Parameter'] == 'Intercept']['Estimate'].iloc[0]
        loan_coef = estimates[estimates['Parameter'] == 'LOAN']['Estimate'].iloc[0]
        
        print(f"📊 Model: DEBTINC = {intercept:.2f} + {loan_coef:.6f} * LOAN")
        print(f"💡 Interpretation: Higher loan amounts predict slightly higher debt-to-income ratios")

    # 8. MAKING PREDICTIONS
    print("\n8️⃣ Making predictions...")
    # Use the model coefficients to make predictions manually
    if 'ParameterEstimates' in result:
        estimates = result['ParameterEstimates']
        intercept = estimates[estimates['Parameter'] == 'Intercept']['Estimate'].iloc[0]
        loan_coef = estimates[estimates['Parameter'] == 'LOAN']['Estimate'].iloc[0]
        
        # Sample loan amounts
        sample_loans = [50000, 75000, 100000]
        predictions = []
        
        for loan in sample_loans:
            pred = intercept + loan_coef * loan
            predictions.append(pred)
            print(f"   Loan: ${loan:,} → Predicted DEBTINC: {pred:.2f}")
        
        print("🎯 Predictions made successfully!")

    # 9. DOWNLOADING DATA
    print("\n9️⃣ Downloading data...")
    sample_table = cas.CASTable("hmeq")
    downloaded_data = sample_table.to_frame()
    print(f"📥 Downloaded HMEQ data: {downloaded_data.shape}")

    print("\n" + "=" * 50)
    print("✅ SWAT Demo Completed! Core functionalities demonstrated:")
    print("   • CAS Connection & Authentication")
    print("   • Data Upload & Management") 
    print("   • Data Exploration & Statistics")
    print("   • Frequency & Correlation Analysis")
    print("   • Model Building (Regression)")
    print("   • Model Prediction")
    print("   • Data Download")
    print("=" * 50)
    
    cas.close()

if __name__ == '__main__':
    main() 