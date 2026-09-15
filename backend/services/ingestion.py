import pandas as pd
import os
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize Presidio globally so it doesn't reload on every request
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def load_dataset(file_path: str, filename: str) -> pd.DataFrame:
    """Loads a dataset into a Pandas DataFrame based on file extension."""
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        elif ext == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        return df
    except Exception as e:
        raise ValueError(f"Failed to read dataset: {str(e)}")

def scan_and_anonymize_pii(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Scans a dataframe for PII (Names, Emails, Phone numbers, etc.)
    and redacts the data to ensure privacy.
    Returns the anonymized DataFrame and a list of columns where PII was found.
    """
    pii_columns = []
    
    # We sample up to 100 rows to speed up PII detection instead of scanning millions
    sample_df = df.sample(min(100, len(df)))
    
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].dtype == 'string':
            # Join sampled text to analyze
            text_to_analyze = " ".join(sample_df[col].dropna().astype(str).tolist())
            
            # Analyze for PII entities
            results = analyzer.analyze(
                text=text_to_analyze,
                entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "US_SSN"],
                language='en'
            )
            
            if results:
                pii_columns.append(col)
                # If PII is found, we anonymize the entire column in the full dataframe
                def redact_text(text):
                    if pd.isna(text): return text
                    res = analyzer.analyze(text=str(text), entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "US_SSN"], language='en')
                    anonymized = anonymizer.anonymize(text=str(text), analyzer_results=res)
                    return anonymized.text
                
                df[col] = df[col].apply(redact_text)
                
    return df, pii_columns

def extract_metadata(df: pd.DataFrame, filename: str, file_size: int, pii_cols: list[str]) -> dict:
    """Extracts metadata from the dataframe to conform to the DatasetMetadata model."""
    return {
        "filename": filename,
        "file_size_bytes": file_size,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "datatypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "pii_columns_detected": pii_cols
    }
