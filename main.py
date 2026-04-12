from fastapi import FastAPI
from pydantic import BaseModel
from db import get_connection

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
async def get_films(genreID: int = None, page: int = 1, per_page: int = 20):
    with get_connection() as conn:
        cursor = conn.cursor()
        offset = per_page * (page - 1)
        if genreID is not None:
            cursor.execute(f"SELECT COUNT(*) FROM Film WHERE Genre_ID = {genreID}")
        else:
            cursor.execute("SELECT COUNT(*) FROM Film")
        total = cursor.fetchone()[0]
        if genreID is not None:
            query=(f"""SELECT * FROM Film limit {per_page} OFFSET {per_page}*{page} ORDER BY Date""" )
        else:
            query = f"""SELECT * FROM Film ORDER BY DateSortie DESC LIMIT {per_page} OFFSET {offset}"""

        cursor.execute(query)
        res = cursor.fetchall()
        print(res)
        return {"data":res,"page": page,"per_page": per_page,"total": total}



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

async def create_account(utilisateur: Utilisateur):
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