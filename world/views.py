import json

from django.shortcuts import render
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db import IntegrityError



from .util import otp_generator, send_otp_email, validate_otp
from .models import User, City, Country, Countrylanguage

def home(request):
    return render(request, "home.html")

def search(request):
    query = request.GET.get("query", "").strip()
    result = {"cities": [], "countries": [], "languages": []}
    
    if not query or len(query) < 3:
        return JsonResponse(result)

    # Mock data for cities
    mock_cities = [
        {"id": 1, "name": "New York", "countrycode": "USA", "district": "New York", "population": 8000000},
        {"id": 2, "name": "Los Angeles", "countrycode": "USA", "district": "California", "population": 4000000},
    ]
    # Mock data for countries
    mock_countries = [
        {"code": "USA", "name": "United States", "continent": "North America", "region": "North America", "population": 327000000},
        {"code": "IND", "name": "India", "continent": "Asia", "region": "Southern Asia", "population": 1380000000},
    ]
    # Mock data for languages
    mock_languages = [
        {"countrycode": "USA", "language": "English", "isofficial": "T", "percentage": 80.0},
        {"countrycode": "IND", "language": "Hindi", "isofficial": "T", "percentage": 41.0},
    ]

    # Filter based on query (simple contains)
    result["cities"] = [city for city in mock_cities if query.lower() in city["name"].lower()]
    result["countries"] = [country for country in mock_countries if query.lower() in country["name"].lower()]
    result["languages"] = [lang for lang in mock_languages if query.lower() in lang["language"].lower()]

    return render(request, "search_results.html", result)

def signup(request):
    return render(request, "signup.html")

@csrf_exempt
def signup_validate(request):
    body = json.loads(request.body)
    email = body.get("email", "")
    first_name = body.get("first_name", "")
    last_name = body.get("last_name", "")
    gender = body.get("gender", "female")
    phone_number = body.get("phone_number", "")

    if not email:
        result = {"success": False, "message": "email not found"}
        return JsonResponse(result)

    if not first_name:
        result = {"success": False, "message": "first name not found"}
        return JsonResponse(result)

    # Mock: always succeed signup
    otp = "123456"  # Mock OTP
    request.session["auth_otp"] = otp
    request.session["auth_email"] = email
    result = {"success": True, "message": "otp sent to email"}
    return JsonResponse(result)

def c_login(request):
    return render(request, "login.html")


@csrf_exempt
def send_otp(request):
    '''
    When you will click on 'Send Otp" button on front end then ajax call will be hit and
    that lead to call this function
    '''
    body = json.loads(request.body)
    email = body.get("email", "")

    otp = otp_generator()
    otp_status = send_otp_email(email, otp)
    if not otp_status:
        result = {"success": False, "message": "incorrect email"}
        return JsonResponse(result)
    
    request.session["auth_otp"] = otp
    request.session["auth_email"] = email
    # cache.set('{0}_auth_otp'.format(request.session.session_key), otp, 120)
    # cache.set('{0}_auth_email'.format(request.session.session_key), email, 120)
 
    result = {"successs": True, "message": "otp sent"}
    return JsonResponse(result)

@csrf_exempt
def login_validate(request):
    body = json.loads(request.body)
    email = body.get("email", "")
    password = body.get("password", "")

    if not email:
        result = {"success": False, "message": "email required"}
        return JsonResponse(result)

    if not password or len(password) < 6 or len(password) > 12:
        result = {"success": False, "message": "password must be between 6 and 12 characters"}
        return JsonResponse(result)

    # Mock login: always succeed
    request.session["user_email"] = email
    result = {"success": True, "message": "login succeeded"}
    return JsonResponse(result)

def c_logout(request):
    request.session.flush()
    return HttpResponseRedirect("/login")

def get_country_details(request, country_name):
    # Mock country data
    mock_countries = {
        "United States": {"code": "USA", "name": "United States", "continent": "North America", "region": "North America", "population": 327000000},
        "India": {"code": "IND", "name": "India", "continent": "Asia", "region": "Southern Asia", "population": 1380000000},
    }
    country = mock_countries.get(country_name, {"name": country_name, "code": "UNK", "continent": "Unknown", "region": "Unknown", "population": 0})
    result = {"country": country}
    
    return render(request, "country.html", result)

