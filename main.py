from fastapi import FastAPI
from pydantic import BaseModel
from db import get_connection
import jwt
app = FastAPI()


@app.get("/ping")
def ping():
    return {"message": "pong"}

class Film(BaseModel):
    id: int | None = None
    nom: str
    note: float | None = None
    dateSortie: int
    image: str | None = None
    video: str | None = None
    genreId: int | None = None

class Genre(BaseModel):
    id : int | None = None
    type : str | None = None 

@app.post("/film")
async def createFilm(film : Film):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO Film (Nom,Note,DateSortie,Image,Video)  
            VALUES('{film.nom}',{film.note},{film.dateSortie},'{film.image}','{film.video}') RETURNING *
            """)
        res = cursor.fetchone()
        print(res)
        return res

@app.get("/films")
async def get_films( page:int =1, per_page: int=20 ):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM Film  ORDER BY DateSortie limit {per_page} OFFSET {per_page}*{page - 1} """ )
        res = cursor.fetchall()
        print(res)
        return res
    


@app.get("/films/{id}")
async def get_film_by_id(id : int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM Film  WHERE Film.id = {id}""" )
        res = cursor.fetchone()
        print(res)
        return res


@app.post("/genre")
async def createGenre(genre : Genre):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
    INSERT INTO Genre (Type) 
        VALUES ('{genre.type}') RETURNING*
""")
        res = cursor.fetchone()
        print(res)
        return res

@app.get("/genres")
async def get_genres():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM Genre""" )
        res = cursor.fetchall()
        print(res)
        return res
                       
@app.get("/films")
async def get_film_by_genre(genreID : int = None ):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = f"""SELECT *
                       FROM Film 
                       WHERE Film.Genre_ID = {genreID}"""
        if genreID == None:
            query= f"""SELECT *
                       FROM Film"""
        cursor.execute(query)
        res = cursor.fetchmany()
        print(res)
        return res

class Utilisateur(BaseModel):
    id : int | None = None
    adresse_mail : str | None = None 
    pseudo : str | None = None 
    mot_de_passe : str | None = None 

@app.post("/register")
<<<<<<< HEAD
Cle_secrete = "4e1ac1e3df1ad5186b1bb9089b9e64e219d7aa1339525b6869b53a483ba3d849619aa9b9812b37a3838f8133503b3108f140a16476b7e6009c4445c6c1bdf1bd5f6bea3c6972a8f0d12ca0257d553db5"

# générer aléatoirement 
=======

>>>>>>> 8e4158ce99decd1e3bdf4cf41436f4c9ba4d03c2
async def create_account(utilisateur: Utilisateur):
    encoded= jwt.encode({utilisateur.adresse_mail,utilisateur.pseudo, utilisateur.mot_de_passe},Cle_secrete, algorithm="HS256" )
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
    INSERT INTO Utilisateur (adresse_mail,pseudo,mot_de_passe) 
        VALUES('{utilisateur.adresse_mail}',{utilisateur.pseudo},{utilisateur.mot_de_passe}) RETURNING *
            """)
        
        res = cursor.fetchone()
        print(res)
        return res

class Genre_Utilisateur(BaseModel):
    id : int | None = None
    id_genre : int | None = None 
    id_user : int | None = None 

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
