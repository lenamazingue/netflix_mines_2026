from fastapi import FastAPI, HTTPException
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
    email : str 
    pseudo : str 
    password : str 

Mot_secret = "2f6c99a0445caff2b6a56bb3224c0359"
Algorithm = "HS256"

@app.post("/auth/register")
async def create_account(utilisateur: Utilisateur):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM Utilisateur WHERE AdresseMail = '{utilisateur.email}'""")
        test_existence_mail = cursor.fetchone()

        if test_existence_mail is not None:
            raise HTTPException(status_code=409) #comme demandé dans le test duplicate
        #Sinon on continue
        cursor.execute(f"""
    INSERT INTO Utilisateur (AdresseMail,Pseudo,MotDePasse) 
        VALUES('{utilisateur.email}','{utilisateur.pseudo}','{utilisateur.password}') RETURNING *
            """)
        res = cursor.fetchone()
        adresse_mail= res[0]
        token = jwt.encode({"ad":adresse_mail}, Mot_secret, algorithm = Algorithm)
        
        return {"access_token": token,
  "token_type": "bearer"}

class Genre_Utilisateur(BaseModel):
    id : int | None = None
    id_genre : int | None = None 
    id_user : int | None = None 

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
