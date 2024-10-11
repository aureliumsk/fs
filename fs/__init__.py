import falcon
from pathlib import Path
import mimetypes

BUFFER_SIZE: int = 1024

class FileResource:
    def __init__(self, storage: Path) -> None:
        self.storage = storage        

    def on_put(self, req: falcon.Request, resp: falcon.Response, name: str) -> None:
        path = self.storage / name
        with path.open("wb") as f:
            while chunk := req.bounded_stream.read(BUFFER_SIZE):
                f.write(chunk)
        if path.exists():
            resp.status = falcon.HTTP_NO_CONTENT
        else:
            resp.status = falcon.HTTP_CREATED

    def on_get(self, req: falcon.Request, resp: falcon.Response, name: str) -> None:
        path = self.storage / name
        if not path.exists():
            raise falcon.HTTPNotFound()
        resp.content_type = mimetypes.guess_type(path)[0]
        resp.set_stream(path.open("rb"), path.stat().st_size)


def make_app() -> falcon.App:
    app = falcon.App()
    app.add_route("/files/{name}", FileResource(Path("uploads")))
    return app

app = make_app()