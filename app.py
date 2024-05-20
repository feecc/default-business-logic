import os

import requests
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel

from config import settings

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE", "PUT"],
    allow_headers=["*"],
)


class BasicResponse(BaseModel):
    cid: str
    ipfs_link: str


@app.post("/start")
def start_record():
    try:
        response = requests.get(settings.camera_overview_vid_start)

        return Response(status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error("Could not start the recording process.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/stop")
def stop_record():
    try:
        file_response: FileResponse = requests.get(settings.camera_overview_vid_stop)

        if not os.path.isdir(settings.video_path):
            os.mkdir(settings.video_path)
        with open(f"{settings.video_path}/{file_response.path}", "wb") as f:
            f.write(file_response.content)
        video_path = os.path.abspath(f"{settings.video_path}/{file_response.path}")

        if not settings.ipfs_gateway_uri:
            raise ValueError("IPFS_GATEWAY_URI not provided")

        response = requests.post(settings.ipfs_gateway_uri, files={"file_data": open(video_path, "rb")})
        basic_response = BaseModel(cid=response.json()["ipfs_cid"], ipfs_link=response.json()["ipfs_link"])
        os.remove(video_path)  # Delete3 video file so it doesn't take space
        return basic_response
    except Exception as e:
        logger.error("Could not stop the recording process.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
