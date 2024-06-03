import os
import pathlib

import requests
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel
from uuid import uuid4

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
        filename = uuid4().hex
        video_path = pathlib.Path(f"{settings.video_path}/{filename}.mp4")
        if not os.path.isdir(settings.video_path):
            os.mkdir(settings.video_path)
        with open(video_path, "wb") as f:
            f.write(file_response.content)

        if not settings.ipfs_gateway_uri:
            raise ValueError("IPFS_GATEWAY_URI not provided")
        with open(video_path, 'rb') as f:
            response = requests.post(f"{settings.ipfs_gateway_uri}publish-to-ipfs/upload-file", files={"file_data": f})
            if response.status_code != 200:
                message = f"Could not post to IPFS. Status code: {response.status_code}; details: {response.json()}"
                logger.error(message)
                return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
            basic_response = {"ipfs_cid": response.json()["ipfs_cid"], "ipfs_link": response.json()["ipfs_link"]}
            return basic_response
    except Exception as e:
        logger.error("Could not stop the recording process.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
