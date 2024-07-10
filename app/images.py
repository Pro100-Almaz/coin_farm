from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

router = APIRouter()


UPLOAD_DIRECTORY = "static/images"

Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

# @router.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Invalid image file")
#
#     file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
#     with open(file_path, "wb") as f:
#         f.write(file.file.read())
#
#     return {"filename": file.filename}

@router.get("/images/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)

