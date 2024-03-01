from fastapi import FastAPI, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
import uuid

dog_map = {}
selected_id = '';

def add_dog(name, breed):
    id = str(uuid.uuid4())
    dog = {'id': id, 'name': name, 'breed': breed}
    dog_map[id] = dog
    return dog

add_dog('Comet', 'Whippet')
add_dog('Oscar', 'German Shorthaired Pointer')

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get('/')
def index():
    return RedirectResponse(url='/dogs')

@app.get('/dogs', response_class=HTMLResponse)
def all_dogs(request: Request):
    return templates.TemplateResponse(request, name="dogs.html")

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
        request, name="form.html", context={'dog': dog}
    )

# Gets table rows for all the dogs.
@app.get('/rows', response_class=HTMLResponse)
def rows(request: Request):
    sorted_dogs = sorted(dog_map.values(), key=lambda x: x['name'])
    return templates.TemplateResponse(
        request, name="dog-rows.html", context={"dogs": sorted_dogs}
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
    res = templates.TemplateResponse(
        request, name="dog-row.html", context={"dog": new_dog}
    )
    res.status_code = status.HTTP_201_CREATED
    return res

# Updates a dog
@app.put('/dog/{id}', response_class=HTMLResponse)
def update(
    request: Request,
    id,
    name: Annotated[str, Form()],
    breed: Annotated[str, Form()]
):
    updatedDog = {'id': id, 'name': name, 'breed': breed};

    global dog_map, selected_id
    dog_map[id] = updatedDog;
    selected_id = '';

    res = templates.TemplateResponse(
        request, name="dog-row.html", context={"dog": updatedDog, "swap": True}
    )
    res.headers['HX-Trigger'] = 'selection-change'
    return res