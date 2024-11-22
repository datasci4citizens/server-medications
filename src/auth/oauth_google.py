from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from auth.auth_service import AuthService
from db.manager import Database
from db.models import Caretaker
from sqlmodel import Session, select
import requests as rq
from google_auth_oauthlib.flow import Flow
import os

login_router = APIRouter()

# Add this line to disable HTTPS checking during development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# This variable specifies the name of a file that contains the OAuth 2.0 information for this application
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")

# These OAuth 2.0 scopes allow access to the user's Google account OpenID, Email, and Profile.
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


@login_router.get('/auth/login/google')
async def call_google_signin(request: Request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, 
        scopes=SCOPES
    )
    flow.redirect_uri = 'http://localhost:8000/auth/login/google/callback'
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return RedirectResponse(auth_url)

@login_router.get('/auth/login/google/callback')
async def callback_uri(request: Request, session: Session = Depends(Database.get_session)):
    state = request.session.get('state')
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, 
        scopes=SCOPES, 
        state=state
    )
    flow.redirect_uri = 'http://localhost:8000/auth/login/google/callback'
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)
    user_info=None

    try:
        info = rq.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={flow.credentials.token}")
        user_info = info.json()
    except ValueError:
        raise HTTPException(status_code=401, detail="token inválido")
    
    statement = select(Caretaker).where(Caretaker.email == user_info['email'])
    caretaker = session.exec(statement).first()
    if caretaker is None:
        caretaker = Caretaker(email=user_info['email'], name=user_info["name"])
        session.add(caretaker)
        session.commit()
        session.refresh(caretaker)

    # adds the information we need from the user to the cookies
    request.session['id'] = user_info['sub'] 
    request.session['email'] = user_info['email']
    required_fields = [caretaker.email, caretaker.name]

    if all(field is None for field in required_fields):
        return RedirectResponse(os.getenv("LOGIN_CALLBACK_URL", 'http://localhost:8000/caretaker/'))
    else:
        return RedirectResponse(os.getenv("LOGIN_CALLBACK_URL", 'http://localhost:8000/docs'))

# endpoint 'protegido' para buscar o usario ativo atualmente usando o token dos cookies
@login_router.get("/current_caretaker/me")
async def me(request: Request, current_user = Depends(AuthService.get_current_user)):
    return request.session

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}