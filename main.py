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
    


#@app.get("/films"/{id})
#def films():
    #with get_connection() as conn:
        #cursor = conn.cursor()
        #cursor.execute(f"""SELECT * FROM Film WHERE id == id""" )
        #res = cursor.fetchall()
        #print(res)
        #return res




class Genre(BaseModel):
    id : int | None = None
    type : str | None = None 

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
def genres():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM Genre""" )
        res = cursor.fetchall()
        print(res)
        return res
                       


class Utilisateur(BaseModel):
    id : int | None = None
    adresse_mail : str | None = None 
    pseudo : str | None = None 
    mot_de_passe : str | None = None 

class Genre_Utilisateur(BaseModel):
    id : int | None = None
    id_genre : int | None = None 
    id_user : int | None = None 

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
