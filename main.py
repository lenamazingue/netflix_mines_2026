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

@app.post("/films")
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

#@app.get("/films")
#async def get_films(genreID = None, page: int = 1, per_page: int = 20):
#    per_page=int(per_page)
#    page=int(page)
#    with get_connection() as conn:
#        cursor = conn.cursor()
#        if genreID == None:
#            cursor.execute(f"SELECT * FROM Film")
#        else:
#            cursor.execute(f"SELECT * FROM Film WHERE Genre_ID = {genreID}")
#        ALL = cursor.fetchall()
#        total = len(ALL)

#        cursor = conn.cursor()
#        offset = per_page * (page - 1)
#        if genreID == None : 
#            cursor.execute(f"""SELECT * FROM Film ORDER BY DateSortie DESC LIMIT {per_page} OFFSET {offset}""")
#        else : 
#            cursor.execute(f"""SELECT * FROM Film  WHERE Genre_ID = {genreID} ORDER BY Genre_ID,DateSortie DESC LIMIT {per_page} OFFSET {offset} """)
#        data = cursor.fetchall()
#        #total = len(data)
#        res = {"data":data,"page": page,"per_page": per_page,"total": total}
#        return res


@app.get("/film")
async def getFilms(page = 1, per_page = 20, genre_id = None):
    per_page=int(per_page)
    page=int(page)
    with get_connection() as conn:
        cursor = conn.cursor()
        if genre_id == None:
            cursor.execute(f"SELECT * FROM Film ORDER BY Genre_ID,DateSortie  LIMIT {per_page} OFFSET {(page-1)*per_page}")
        else:
            cursor.execute(f"SELECT * FROM Film WHERE Genre_ID = {genre_id} ORDER BY DateSortie LIMIT {per_page} OFFSET {(page-1)*per_page}")
        data = cursor.fetchall()
        cursor = conn.cursor()
        if genre_id == None:
            cursor.execute(f"SELECT * FROM Film")
        else:
            cursor.execute(f"SELECT * FROM Film WHERE Genre_ID = {genre_id}")
        Tout = cursor.fetchall()
        total = len(Tout)
        #res = PaginatedResponse(data = data, page = page, per_page = per_page, total = total)
        res = {"data" : data, "page" : page, "per_page" : per_page, "total" : total}
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

#@app.get("/films")
#async def get_film_by_genre(genreID : int = None ):
#    with get_connection() as conn:
#        cursor = conn.cursor()
#        query = f"""SELECT *
#                       FROM Film 
#                       WHERE Film.Genre_ID = {genreID}"""
#        if genreID == None:
#            query= f"""SELECT *
#                       FROM Film"""
#        cursor.execute(query)
#        res = cursor.fetchmany()
#        print(res)
#        return res

class Utilisateur(BaseModel):
    id : int | None = None
    email : str
    pseudo : str|None=None
    password : str|None

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


@app.post("/auth/login")
async def connexion(utilisateur: Utilisateur):
    with get_connection() as conn:
        cursor = conn.cursor()
        #on va tester si l'adresse mail existe bien dans la base

        cursor.execute(f"""  SELECT* FROM Utilisateur WHERE AdresseMail='{utilisateur.email}' AND MotDePasse= '{utilisateur.password}' """) 

        res = cursor.fetchone()        
        if not res:
            raise HTTPException(status_code=401)
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
