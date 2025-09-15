import pandas as pd
import io
from fastapi import UploadFile

def parse_excel_to_chunks_from_bytes(file_bytes: bytes):
    buffer = io.BytesIO(file_bytes)
    df = pd.read_excel(buffer)
    chunks = []

    for i, row in df.iterrows():
        chunk = ", ".join([f"{col}: {row[col]}" for col in df.columns])
        chunks.append(chunk)

    return chunks
