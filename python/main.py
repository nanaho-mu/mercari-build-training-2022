import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import sqlite3
import hashlib

# con=sqlite3.connect("../db/mercari.sqlite3", check_same_thread=False)
# cur=con.cursor()
# cur.execute('CREATE TABLE items(id int, name string, category string)')

# cur.execute('ALTER TABLE items ADD image string')
# con.commit()
DATABASE_NAME = str(pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent/"db"/"mercari.sqlite3")

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

def get_hash(image):
    image_name=image.split('.')[0]
    hashed_image=hashlib.sha256(image_name.encode()).hexdigest()
    return hashed_image + '.jpg'

@app.get("/")
def root():
    return {"message": "Hello, world!"}

# @app.get("/items")
# # print(json_load)
# def add_items(): 
#     json_open = open('items.json', 'r')
#     json_load = json.load(json_open)   
#     return json_load

@app.get("/items")
def add_items():
    con=sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cur=con.cursor()
    cur.execute('SELECT items.name, items.category, items.image FROM items')
    items=cur.fetchall()
    cur.close()
    json_items = {"items": [dict(zip(["name", "category", "image"], item)) for item in items]}
    return json_items

@app.get("/search")
def search(keyword: str):
    con=sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cur=con.cursor()
    cur.execute(f"SELECT items.name, items.category FROM items WHERE items.name == '{keyword}'")
    res=cur.fetchall()
    con.close()
    json_items = {"items": [dict(zip(["name", "category"], item)) for item in res]}
    return json_items


@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image:str=Form(...)):
    logger.info(f"Receive item: {name}")
    # return {"message": f"item received: {name}"}
    hashed_image=get_hash(image)
    con=sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cur=con.cursor()
    cur.execute("SELECT items.id FROM items")
    items_id=cur.fetchall()
    if items_id is None:
        item_id=1
    else:
        item_id=len(items_id)+1
    cur.execute(f"INSERT INTO items(id, name, category, image) VALUES ({item_id},?,?,?)",(name, category, hashed_image))
    con.commit()
    con.close()

@app.get("/items/{item_id}")
def get_items(item_id):
    con=sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cur=con.cursor()
    cur.execute(f"SELECT  items.name, items.category, items.image FROM items WHERE items.id=='{item_id}'")
    res=cur.fetchall()
    # cur.colse()
    json_items = {(zip(["name", "category", "image"], item)) for item in res}
    return json_items

# json
# @app.post("/items")
# def add_item(name: str = Form(...), category: str = Form(...)):
#     logger.info(f"Receive item: {name}")
#     # return {"message": f"item received: {name}"}
#     d={"items": [{"name": f"{name}", "category": f"{category}"}]}
#     with open('items.json', 'w') as f:
#         json.dump(d, f, indent=4)

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
