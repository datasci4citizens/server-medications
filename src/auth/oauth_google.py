from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from auth.auth_service import AuthService
from db.manager import Database
from db.models import User
from sqlmodel import Session, select
import requests as rq
from google_auth_oauthlib.flow import Flow
import os

login_router = APIRouter()

# Add this line to disable HTTPS checking during development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

@login_router.get('/auth/login/google')
async def call_google_signin(request: Request):
    CLIENT_CONFIG = {
        "web":{
            "client_id":os.getenv("CLIENT_ID"),
            "project_id":"medications",
            "auth_uri":"https://accounts.google.com/o/oauth2/auth",
            "token_uri":"https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
            "client_secret":os.getenv("CLIENT_SECRET"),
            "redirect_uris":[os.getenv("REDIRECT_URIS")]
        }
    }
    print(CLIENT_CONFIG)
    flow = Flow.from_client_config( 
        CLIENT_CONFIG, 
        scopes=SCOPES
    )
    flow.redirect_uri = f"{os.getenv('SERVER_URL')}auth/login/google/callback"
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return RedirectResponse(auth_url)

@login_router.get('/auth/login/google/callback')
async def callback_uri(request: Request, session: Session = Depends(Database.get_session)):
    CLIENT_CONFIG = {
        "web":{
            "client_id":os.getenv("CLIENT_ID"),
            "project_id":"medications",
            "auth_uri":"https://accounts.google.com/o/oauth2/auth",
            "token_uri":"https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
            "client_secret":os.getenv("CLIENT_SECRET"),
            "redirect_uris":[os.getenv("REDIRECT_URIS")]
        }
    }
    state = request.session.get('state')
    flow = Flow.from_client_config(
        CLIENT_CONFIG, 
        scopes=SCOPES, 
        state=state
    )
    flow.redirect_uri = f"{os.getenv('SERVER_URL')}auth/login/google/callback"
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    user_info=None

    try:
        info = rq.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={flow.credentials.token}")
        user_info = info.json()
    except ValueError:
        raise HTTPException(status_code=401, detail="token inválido")
    
    statement = select(User).where(User.email == user_info['email'])
    user = session.exec(statement).first()
    if user is None:
        user = User(email=user_info['email'], name=user_info["name"])
        session.add(user)
        session.commit()
        session.refresh(user)

    # adds the information we need from the user to the cookies
    request.session['id'] = user.id
    request.session['email'] = user_info['email']

    return RedirectResponse(os.getenv("LOGIN_CALLBACK_URL"))

# endpoint 'protegido' para buscar o usario ativo atualmente usando o token dos cookies
@login_router.get("/current_user/me")
async def me(request: Request, current_user = Depends(AuthService.get_current_user)):
    return request.session

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}