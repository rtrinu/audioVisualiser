from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import os
from dotenv import load_dotenv
from django.conf import settings
from .utils import generate_secret_string
from django.http import JsonResponse
import urllib.parse
import jsonify
from datetime import datetime as datetime

load_dotenv()

CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URL = os.getenv("AUTH_URL")
TOKEN_URL = os.getenv("TOKEN_URL")
API_BASE_URL = os.getenv("API_BASE_URL")
SCOPE = os.getenv("SCOPE")


def login(request):
    state = generate_secret_string(16)
    request.session["state"] = state
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "show_dialog": True,  # For logging debugging, set to false in final
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


def callback(request):
    received_state = request.GET.get("state")
    session_state = request.session.get("state")
    if not session_state or received_state != session_state:
        return HttpResponse("State mismatch, possible CSRF", status=400)

    code = request.GET.get("code")
    if not code:
        return HttpResponse("No code returned", status=400)

    error = request.GET.get("error")
    if error:
        return JsonResponse({"error": error})

    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        request.session["access_token"] = token_info["access_token"]
        request.session["refresh_token"] = token_info["refresh_token"]
        request.session["expires_at"] = (
            datetime.now().timestamp() + token_info["expires_in"]
        )
    return redirect("render_homepage")


def refresh_token(request):
    if "refresh_token" not in request.session:
        return redirect("login")

    if datetime.now().timestamp() > request.session["refresh_token"]:
        req_body = {
            "grant_type": "authorization_code",
            "refresh_token": request.session["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        request.session["access_token"] = new_token_info["access_token"]
        request.session["expires_at"] = (
            datetime.now().timestamp() + new_token_info["expires_in"]
        )
