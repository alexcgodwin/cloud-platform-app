import os,time,jwt
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
app=FastAPI(); SECRET=os.getenv("JWT_SECRET","change-me")
class Login(BaseModel): username:str; password:str
@app.get("/health")
def health(): return {"status":"ok","service":"auth"}
@app.post("/token")
def token(body:Login):
 if body.password!="portfolio": raise HTTPException(401,"invalid credentials")
 return {"access_token":jwt.encode({"sub":body.username,"iat":int(time.time())},SECRET,algorithm="HS256")}
