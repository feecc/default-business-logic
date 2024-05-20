from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    video_path: str = "./vids"

    ipfs_gateway_uri: str = "http://127.0.0.1:8082/publish-to-ipfs/upload-file"
    ipfs_link: str = "http://sample/ipfs/"

    camera_overview_vid_start: str = "http://feecc-camera-gateway/start-record"
    camera_overview_vid_stop: str = "http://feecc-camera-gateway/stop-record"


settings = Settings()
