from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# TODO: Is "async" needed here?
@app.get('/dogs', response_class=HTMLResponse)
async def all_dogs(request: Request):
    return templates.TemplateResponse(
        request=request, name="dogs.html", context={"dogs": dog_map.values()}
    )

@app.get('/dogs/{id}')
def one_dog(id):
    dog = dog_map[id]
    return dog # returns JSON

# # Deletes the dog with a given id.
# @app.route('/dog/<id>', methods=['DELETE'])
# def delete_dog(id):
#     global dog_map
#     del dog_map[id]
#     return ''

# # Deselects the currently selected dog.
# @app.route('/deselect')
# def deselect():
#     global selected_id
#     selected_id = ''
#     res = Response('')
#     res.headers['HX-Trigger'] = 'selection-change'
#     return res

# Gets the proper form for either adding or updating a dog.
@app.get('/form')
def form(request: Request):
    dog = dog_map.get(selected_id)
    return templates.TemplateResponse(
        request=request, name="form.html", context={'dog': dog}
    )

# Gets table rows for all the dogs.
@app.get('/rows')
def rows(request: Request):
    sorted_dogs = sorted(dog_map.values(), key=lambda x: x['name'])
    return templates.TemplateResponse(
        request=request, name="dog-rows.html", context={"dogs": sorted_dogs}
    )

# # Selects a dog.
# @app.route('/select/<id>')
# def select(id):
#     global selected_id
#     selected_id = id;
#     res = Response('')
#     res.headers['HX-Trigger'] = 'selection-change'
#     return res

# # Creates a dog.
# @app.route('/dog', methods=['POST'])
# def create():
#     name = request.form.get('name')
#     breed = request.form.get('breed')
#     new_dog = add_dog(name, breed);
#     return render_template('dog-row.html', dog=new_dog, status=201);

# # Updates a dog
# @app.route('/dog/<id>', methods=['PUT'])
# def update(id):
#     name = request.form.get('name')
#     breed = request.form.get('breed')
#     updatedDog = {'id': id, 'name': name, 'breed': breed};

#     global dog_map
#     dog_map[id] = updatedDog;

#     global selected_id
#     selected_id = '';

#     res = make_response(
#         render_template('dog-row.html', dog=updatedDog, swap=True)
#     )
#     res.headers['HX-Trigger'] = 'selection-change'
#     return res