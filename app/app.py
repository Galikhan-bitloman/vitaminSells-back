from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List
from botocore.exceptions import EndpointConnectionError, ClientError

from tools.s3_service import s3_bucket_service_factory

app = FastAPI()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.csv'}



@app.post("/upload-excel/")
async def upload_excel_file(files: List[UploadFile] = File(...)):
    # Validate file extension
    list_response = []
    
    for file in files:
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
        strip_filename = file.filename.replace(" .xlsx", ".xlsx")

        spaced_filename = strip_filename.replace(" ", "_")


        name_without_ext = spaced_filename.split(".")[0]

        file_ext =  spaced_filename.split(".")[1]

        name_with_month = name_without_ext.split("_")[-1]
    
        file_name = name_without_ext.split("_")[-2]
        #TODO change to apropriate checker func
        if file_name == "питание" or file_name == "бады":
            file_name = "nutritions_and_vitamins"

        file_content = await file.read()

        #s3 service factory and upload data
        
        s3_constructor = s3_bucket_service_factory()


        #TODO when uploading file need to check that if the file exist in storage?

        try:
            s3_constructor.upload_file_object(prefix=file_name, source_file_name=spaced_filename, content=file_content)
        except EndpointConnectionError as e:
            print(f"Could not connect to S3 endpoint: {e}")
            return False
        except ClientError as e:
            print(f"S3 Client error: {e}")
            return False    
        
        #TODO create response model
        response =  {
            "message": "File uploaded successfully",
            "filename": spaced_filename,
            "month": name_with_month,
            "file_extension": file_ext, 
            "name_without_ext": name_without_ext,
            "file_name": file_name,
            "size_mb": round(file_size / (1024 * 1024), 2),
        }
        list_response.append(response)
    
    
    return JSONResponse(content=list_response, status_code=200)
    
   