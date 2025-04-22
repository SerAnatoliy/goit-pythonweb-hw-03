from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Environment(loader=FileSystemLoader("templates"))

DATA_FILE = Path("storage/data.json")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    template = templates.get_template("index.html")
    return HTMLResponse(content=template.render(), status_code=200)


@app.get("/message", response_class=HTMLResponse)
async def read_message():
    template = templates.get_template("message.html")
    return HTMLResponse(content=template.render(), status_code=200)


@app.post("/message")
async def post_message(username: str = Form(...), message: str = Form(...)):
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {}

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    data[timestamp] = {"username": username, "message": message}

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return RedirectResponse(url="/", status_code=302)


@app.get("/read", response_class=HTMLResponse)
async def read_messages():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {}

    template = templates.get_template("read.html")
    return HTMLResponse(content=template.render(messages=data), status_code=200)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    template = templates.get_template("error.html")
    return HTMLResponse(content=template.render(), status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)
