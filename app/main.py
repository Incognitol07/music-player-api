from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv
import os
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# B2 and Database setup
APPLICATION_KEY_ID = os.getenv("B2_KEY_ID")
APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

# Authorize B2 and set bucket
info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", APPLICATION_KEY_ID, APPLICATION_KEY)
bucket = b2_api.get_bucket_by_name(BUCKET_NAME)

# Database setup
DATABASE_URL = "sqlite:///./files.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define the database model
class FilePath(Base):
    __tablename__ = "file_paths"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)


Base.metadata.create_all(bind=engine)


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint to upload file to Backblaze B2 and store in database
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Read file data and upload to B2
        file_data = await file.read()
        bucket.upload_bytes(file_data, file.filename)

        # Store file path in SQLite database
        db_file = FilePath(filename=file.filename)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return JSONResponse(
            content={
                "message": f"File '{file.filename}' uploaded successfully!",
                "id": db_file.id,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint to download a file directly
@app.get("/download/{file_name}")
async def download_file(file_name: str):
    try:
        # Retrieve file content from B2
        file_version = bucket.get_file_info_by_name(file_name)
        file_info = bucket.download_file_by_id(file_version.id_)

        # Read content into BytesIO for streaming
        file_data = BytesIO()
        file_info.save(file_data)
        file_data.seek(0)

        # Stream file content as a response
        return StreamingResponse(
            file_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")


# Endpoint to retrieve all files stored in the database
@app.get("/files/")
async def list_files(db: Session = Depends(get_db)):
    query = select(FilePath)
    result = db.execute(query)
    files = result.scalars().all()
    return {"files": [{"id": file.id, "filename": file.filename} for file in files]}
