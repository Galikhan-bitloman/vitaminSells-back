from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from pathlib import Path
from typing import Optional

app = FastAPI()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.csv'}



@app.post("/upload-excel/")
async def upload_excel_file(file: UploadFile = File(...)):
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    try:
        # Get file size by reading it
        
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to validate file size")
    

    #change to unified file name
    spaced_filename = file.filename.replace(" ", "_")

    name_without_ext = spaced_filename.split(".")[0]

    file_ext =  spaced_filename.split(".")[1]

    get_month = name_without_ext.split("_")[-1]

    # TODO here has to be saving in minIO
    

    return {
        "message": "File uploaded successfully",
        "filename": spaced_filename,
        "month": get_month,
        "file_extension": file_ext, 
        "size_mb": round(file_size / (1024 * 1024), 2),
    }
    
   