from fastapi import FastAPI
from mongodb import collection

# API Methods
app = FastAPI()


@app.get('/')
async def root():
    return {'example': 'This is an example', 'data': 0}


@app.post('/')
async def root():
    collection.insert_one({"name": "V", "role": "Mercenary"})
    return {'message': 'Dados salvos com sucesso!'}
