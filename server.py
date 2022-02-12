#Fast API server

import hmac
import hashlib
import base64
import json

from fastapi import FastAPI, Form, Cookie, Body, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from typing import Optional




templates = Jinja2Templates(directory="templates")
app = FastAPI()

SECRET_KEY = "cf9fee43b30cb4f54f991ad0ef952feb9fa28ec0ca2685b098f90a247a14d295"
PASSWORD_SALT = "7434c88948f15c3359538ff5c1fff2ba8540b441490160099a6623214d64a861"

def make_signed_data(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        msg = data.encode(),
        digestmod= hashlib.sha256
    ).hexdigest().upper()

def data_to_datab64(data: str) -> str:
    data_b64 = base64.b64encode(data.encode()).decode()
    return data_b64

def get_username_from_signed_username(signed_username: str) -> Optional[str]:
    try:
        username_b64, sign = signed_username.split(".")
        username = base64.b64decode(username_b64.encode()).decode()
        if hmac.compare_digest(sign, make_signed_data(username)): # for disabling opportunity for timing attacks
            return username
        else: 
            return None
    except ValueError:
        return None


def verify_password(username: str, password: str) -> bool:
    try:
        password_hash = hashlib.sha256( (password+PASSWORD_SALT).encode() ).hexdigest().lower()
        stored_password_hash = users[username]["password"].lower()
    except KeyError:
        return False
    print(f"{users[username]['password']}")
    print(f"{password}")
    return password_hash == stored_password_hash 


users = {
    "angelina@gmail.com":{
        "name": "Angelina",
        "password": "8d8567225b6bb1bd717316975f7ae6e936d548c9cac10a7f3280e4385b7309ae", #
        "balance":100_00
    },
    "nastya@mail.ru":{
        "name": "Nastya",
        "password": "14eae6224c4ed74ffad15ec033188839165962133d8d88e2877d7ec4cac67d76", #
        "balance": 50_00
    },
    "bob@gmail.com":{
        "name":"Bob",
        "password":"1a04d3e06c6d711ffeca3bb6c12f2e73ab44b44cea8278859ec92b2a0b952bde", #
        "balance": 600_00
    }
}


def get_name_of_users():
    names = []
    for user in users.values():
        names.append(user["name"])
    return names




@app.get("/")
async def show_index_page(request: Request,signed_username: str = Cookie(default=None)) -> Optional[str]:
    if signed_username:
        
        username = get_username_from_signed_username(signed_username)
        
        if username:

            with open("templates/profile.html","r") as f:
                
                file = f.read()
                response = Response()

            return templates.TemplateResponse("profile.html",
                            {"request":request,"users":get_name_of_users(),"name":users[username]["name"],"balance":users[username]["balance"]})

    with open("templates/index.html","r") as f:
        
        file = f.read()
        response = Response(file,media_type="text/html")
        response.set_cookie(key="signed_username")
    
    return response



@app.get("/transfer")
async def transfer_money(request: Request):
    url = request.url
    
    
    values = str(url).split("?")[-1].split("&")
    sender = values[0].split("=")[-1] 
    receiver = values[1].split("=")[-1]
    amount = values[2].split("=")[-1]  

    # if sender and receiver exist
    all_names = []
    for key in users.keys():
        all_names.append(users[key]["name"])

    if sender in all_names and receiver in all_names:
        # find record about that user
        login_of_sender = ""
        for key in users.keys():
            if users[key]["name"] == sender:
                login_of_sender = key
            
        if not login_of_sender:
            return {"Error":"Something went wrong"}

        amount_of_money = 0
        try: 
            amount_of_money = int(amount)
        except ValueError:
            return {"Error":"<h1>In field about amount of money not a number!!!</h1>"}

        if amount_of_money <= users[login_of_sender]["balance"]:
            login_of_receiver = ""
            for key in users.keys():
                if users[key]["name"] == receiver:
                    login_of_receiver = key
            if not login_of_receiver:
                return {"Error":"Something went wrong!"}

            # transfering money from one account to another
            users[login_of_sender]["balance"] -= amount_of_money
            users[login_of_receiver]["balance"] += amount_of_money

        else:
            return json.dumps({"Error":"You want to transfer more money that you have!"})


    else:
        return {"Error":"Somethig went wrong"}
        




@app.post("/login")
async def authorize_user(data: dict = Body(...)):
    username = data["username"]
    password = data["password"]
    user = users.get(username)
    
    try:
        
        if user  and verify_password(username,password):
            
            response = Response(
                    json.dumps({
                        "success": True,
                        "message": f"Hi, {users[username]['name']}<br>Your balance: {users[username]['balance']}"
                    }),
                    media_type="application/json",
                    )
            
            username_b64 = data_to_datab64(username)
            signed_username = username_b64 + "." + make_signed_data(username)
            response.set_cookie(key="signed_username", value = signed_username)
            return response
        
        else:

            return Response(
            json.dumps({
                        "success": False,
                        "message": "I don't know you!"
                    }),
            media_type="application/json")

    except KeyError:

        return Response(
        json.dumps({
                        "success": False,
                        "message": "I don't remember you!"
                    }),
        media_type="application/json")
    


