import pandas as pd
import os
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize Presidio globally so it doesn't reload on every request
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# In-memory dictionary to track progress for the frontend
UPLOAD_PROGRESS = {}

def load_dataset(file_path: str, filename: str) -> pd.DataFrame:
    """Loads a dataset into a Pandas DataFrame based on file extension."""
    UPLOAD_PROGRESS[filename] = {"status": "Loading dataset into memory...", "percent": 10}
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.csv':
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        elif ext == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        return df
    except Exception as e:
        raise ValueError(f"Failed to read dataset: {str(e)}")

def scan_and_anonymize_pii(df: pd.DataFrame, filename: str) -> tuple[pd.DataFrame, list[str]]:
    """
    Scans a dataframe for PII (Names, Emails, Phone numbers, etc.)
    and redacts the data to ensure privacy.
    Returns the anonymized DataFrame and a list of columns where PII was found.
    """
    UPLOAD_PROGRESS[filename] = {"status": "Scanning sample for PII...", "percent": 10}
    pii_columns = []
    
    sample_df = df.sample(min(100, len(df)))
    columns_to_process = []
    
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].dtype == 'string':
            text_to_analyze = " ".join(sample_df[col].dropna().astype(str).tolist())
            results = analyzer.analyze(
                text=text_to_analyze,
                entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "US_SSN"],
                language='en'
            )
            if results:
                columns_to_process.append(col)
                pii_columns.append(col)
                
    total_cols = len(columns_to_process)
    
    for i, col in enumerate(columns_to_process):
        print(f"Anonymizing column '{col}' row-by-row. This may take a while...")
        UPLOAD_PROGRESS[filename] = {"status": f"Anonymizing column '{col}'...", "percent": 15 + int((i / total_cols) * 70)}
        total_rows = len(df)
        
        def redact_text(text, idx=[0]):
            if idx[0] % max(1, (total_rows // 20)) == 0 and idx[0] > 0:
                base_pct = 15 + int((i / total_cols) * 70)
                col_progress = int((idx[0] / total_rows) * (70 / total_cols))
                UPLOAD_PROGRESS[filename] = {"status": f"Anonymizing '{col}' (row {idx[0]}/{total_rows})...", "percent": base_pct + col_progress}
            idx[0] += 1
            
            if pd.isna(text): return text
            res = analyzer.analyze(text=str(text), entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "US_SSN"], language='en')
            anonymized = anonymizer.anonymize(text=str(text), analyzer_results=res)
            return anonymized.text
        
        df[col] = df[col].apply(redact_text)
        print(f"Finished anonymizing '{col}'.")
                
    UPLOAD_PROGRESS[filename] = {"status": "Saving anonymized dataset...", "percent": 90}
    return df, pii_columns

def extract_metadata(df: pd.DataFrame, filename: str, file_size: int, pii_cols: list[str]) -> dict:
    """Extracts metadata from the dataframe to conform to the DatasetMetadata model."""
    UPLOAD_PROGRESS[filename] = {"status": "Extracting dataset metadata...", "percent": 95}
    
    total_cells = df.size
    total_missing = int(df.isnull().sum().sum())
    missing_pct = round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0
    quality_score = round(1.0 - (total_missing / total_cells), 2) if total_cells > 0 else 1.0
    memory_usage_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    
    return {
        "filename": filename,
        "file_size_bytes": file_size,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "datatypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "missing_values_percentage": missing_pct,
        "quality_score": quality_score,
        "memory_usage_mb": memory_usage_mb,
        "pii_columns_detected": pii_cols
    }
