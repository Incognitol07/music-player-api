# Music Player API

## Overview
The Music Player API is a comprehensive FastAPI application designed to manage a music library with capabilities for uploading and downloading tracks. It leverages Backblaze B2 for file storage and SQLite for metadata management.

## Features
- Upload audio files to Backblaze B2.
- Download audio files.
- List all uploaded files.

## Technologies Used
- **FastAPI**: A modern web framework for building APIs with Python.
- **Backblaze B2**: Cloud storage service for storing uploaded files.
- **SQLAlchemy**: ORM for managing SQLite database.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/music-player-api.git
   cd music-player-api
   ```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
Rename .env.example to .env and fill in your Backblaze B2 credentials.

4. Running the API
You can run the API using Uvicorn:

```bash
uvicorn app.main:app --reload
```

5. Endpoints
POST /upload/: Upload a file.
GET /download/{file_name}: Download a file.
GET /files/: List all uploaded files.
License
This project is licensed under the MIT License.


### Steps to Create the Repository
1. Go to GitHub and create a new repository named `music-player-api`.
2. Clone it to your local machine.
3. Create the folder structure and files as described above.
4. Push the changes to GitHub.





