from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from db import get_connection
import jwt
from typing import Annotated
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
    genre_id: int | None = None

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

@app.get("/films")
async def get_films(genre_id = None, page: int = 1, per_page: int = 20):
    per_page=int(per_page)
    page=int(page)
    with get_connection() as conn:
        cursor = conn.cursor()
        if genre_id == None:
            cursor.execute(f"SELECT * FROM Film")
        else:
            cursor.execute(f"SELECT * FROM Film WHERE Genre_ID = {genre_id}")
        ALL = cursor.fetchall()
        total = len(ALL)

        cursor = conn.cursor()
        offset = per_page * (page - 1)
        if genre_id == None : 
            cursor.execute(f"""SELECT * FROM Film ORDER BY DateSortie DESC LIMIT {per_page} OFFSET {offset}""")
        else : 
            cursor.execute(f"""SELECT * FROM Film  WHERE Genre_ID = {genre_id} ORDER BY Genre_ID,DateSortie DESC LIMIT {per_page} OFFSET {offset} """)
        data = cursor.fetchall()
        total = len(data)
        res = {"data":data,"page": page,"per_page": per_page,"total": total}
        return res



@app.get("/films/{id}")
async def get_film_by_id(id : int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM Film  WHERE Film.id = {id}""" )
        res = cursor.fetchone()
        if res == None :
            raise HTTPException(404, "film not found")
        else :
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
        adresse_mail= res[1]
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
        adresse_mail= res[1]
        
        token = jwt.encode({"ad":adresse_mail}, Mot_secret, algorithm = Algorithm)
        return {"access_token": token,
  "token_type": "bearer"}







class Genre_Utilisateur(BaseModel):
    id : int | None = None
    genre_id : int  
    id_user : int | None = None 

@app.post("/preferences",status_code=201)

async def create_preferences(genre:Genre_Utilisateur,authorization:str= Header(None)):
    if not authorization:
        raise HTTPException(status_code=422)

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, Mot_secret, algorithms=[Algorithm])
        adress_mail = payload.get("ad") or payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

    if not adress_mail:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    genre_id = genre.genre_id

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""SELECT ID FROM Utilisateur WHERE AdresseMail = '{adress_mail}'""")
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        user_id = user[0]

        cursor.execute(f"""
            SELECT ID FROM Genre_Utilisateur 
            WHERE ID_User = {user_id} AND ID_Genre = {genre_id}
        """)
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="genre déjà dans favoris")
        cursor.execute(f"""
            INSERT INTO Genre_Utilisateur (ID_User, ID_Genre) 
            VALUES ({user_id}, {genre_id})
        """)
        conn.commit()

    return {"genre_id": genre_id
        
    }
        

@app.delete("/preferences/{genre_id}")
async def remove_preferences(genre_id:int,authorization: Annotated[str | None, Header()] = None):
    if not authorization: #même structure que précédemment
        raise HTTPException(status_code=422)
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, Mot_secret, algorithms=[Algorithm])
        adress_mail = payload.get("ad") or payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token invalide")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""DELETE FROM Genre_Utilisateur WHERE ID_Genre={genre_id} AND ID_User= (SELECT ID FROM Utilisateur WHERE AdresseMail = '{adress_mail}')  """)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Préférence non trouvée")
        conn.commit()
    return {"status": "success"}
    
    
    

#@app.get("/genres")
#async def get_genres():
#    with get_connection() as conn:
#        cursor = conn.cursor()
 #       cursor.execute(f"""SELECT * FROM Genre""" )
 #       res = cursor.fetchall()
 #       print(res)
 #       return res

@app.get("/recommendations")
async def get_recommendations_no_preferences():
    res = {}
    return res

@app.get("/recommendations")
async def get_recommendations(preferences : int , authorization : Annotated[str | None, Header()] = None):
    if not authorization:
        raise HTTPException(status_code = 422)
    token = authorization.replace("Bearer ", "")
    


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
