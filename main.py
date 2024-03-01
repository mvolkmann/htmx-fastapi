from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

dog_map = {}
selected_id = '';

def add_dog(name, breed):
    id = str(uuid.uuid4())
    dog = {'id': id, 'name': name, 'breed': breed}
    dog_map[id] = dog
    return dog

add_dog('Comet', 'Whippet')
add_dog('Oscar', 'German Shorthaired Pointer')

@app.get('/')
def index():
    return RedirectResponse(url='/dogs')

@app.get('/dogs', response_class=HTMLResponse)
def all_dogs(request: Request):
    return templates.TemplateResponse(
        request=request, name="dogs.html", context={"dogs": dog_map.values()}
    )

@app.get('/dogs/{id}')
def one_dog(id):
    dog = dog_map[id]
    return dog # returns JSON

# Deletes the dog with a given id.
@app.delete('/dog/{id}', response_class=HTMLResponse)
def delete_dog(id):
    global dog_map
    del dog_map[id]

# Deselects the currently selected dog.
@app.get('/deselect')
def deselect(response: Response):
    global selected_id
    selected_id = ''
    response.headers['HX-Trigger'] = 'selection-change'

# Gets the proper form for either adding or updating a dog.
@app.get('/form', response_class=HTMLResponse)
def form(request: Request):
    dog = dog_map.get(selected_id)
    return templates.TemplateResponse(
        request=request, name="form.html", context={'dog': dog}
    )

# Gets table rows for all the dogs.
@app.get('/rows', response_class=HTMLResponse)
def rows(request: Request):
    sorted_dogs = sorted(dog_map.values(), key=lambda x: x['name'])
    return templates.TemplateResponse(
        request=request, name="dog-rows.html", context={"dogs": sorted_dogs}
    )

# Selects a dog.
@app.get('/select/{id}')
def select(response: Response, id):
    global selected_id
    selected_id = id;
    response.headers['HX-Trigger'] = 'selection-change'

# Creates a dog.
@app.post('/dog', response_class=HTMLResponse)
def create(
    request: Request,
    name: Annotated[str, Form()],
    breed: Annotated[str, Form()]
):
    new_dog = add_dog(name, breed);
    return templates.TemplateResponse(
        request=request, status=201, name="dog-row.html", context={"dog": new_dog}
    )

# Updates a dog
@app.put('/dog/{id}', response_class=HTMLResponse)
def update(
    request: Request,
    name: Annotated[str, Form()],
    breed: Annotated[str, Form()],
    id
):
    updatedDog = {'id': id, 'name': name, 'breed': breed};

    global dog_map
    dog_map[id] = updatedDog;

    global selected_id
    selected_id = '';

    res = templates.TemplateResponse(
        request=request, name="dog-row.html", context={"dog": updatedDog, "swap": True}
    )
    res.headers['HX-Trigger'] = 'selection-change'
    return res