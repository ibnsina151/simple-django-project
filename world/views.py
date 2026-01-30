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

from watson.search import search

from .util import otp_generator, send_otp_email, validate_otp
from .models import User, City, Country, Countrylanguage

@login_required
def home(request):
    return render(request, "home.html")

@login_required
def search(request):
    query = request.GET.get("query", "").strip()
    result = {"cities": [], "countries": [], "languages": []}

    if not query or len(query) < 3:
        return JsonResponse(result)

    city_results = search(query, models=[City])
    country_results = search(query, models=[Country])
    language_results = search(query, models=[Countrylanguage])

    result["cities"] = [ City.objects.filter(pk=result.object.pk).values().first() for result in city_results ]
    result["countries"] = [ Country.objects.filter(pk=result.object.pk).values().first() for result in country_results ]
    result["languages"] = [ Countrylanguage.objects.filter(pk=result.object.pk).values().first() for result in language_results ]

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

    try:
        User.objects.create(email=email, 
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            gender=gender
        )
    except IntegrityError:
        result = {"success": False, "message": "user already exists"}
        return JsonResponse(result)

    otp = otp_generator()
    otp_status = send_otp_email(email, otp)
    
    if not otp_status:
        result = {"success": False, "message": "incorrect email"}
        return JsonResponse(result)
 
    request.session["auth_otp"] = otp
    request.session["auth_email"] = email
    # cache.set('{0}_auth_otp'.format(request.session.session_key), otp, 120)
    # cache.set('{0}_auth_email'.format(request.session.session_key), email, 120)
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
 
    result = {"success": True, "message": "otp sent"}
    return JsonResponse(result)

@csrf_exempt
def login_validate(request):
    body = json.loads(request.body)
    sent_otp = request.session.get("auth_otp", "")
    sent_email = request.session.get("auth_email", "")
    email = body.get("email", "")
    otp = body.get("otp", "")

    result = validate_otp(otp, sent_otp, email, sent_email)
    
    if not result["success"]:
        return JsonResponse(result)

    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        result = {"success": False, "message": "please signup"}
        return JsonResponse(result)

    login(request, user)
    result = {"success": True, "message": "login succeeded"}
    return JsonResponse(result)

@login_required
def c_logout(request):
    logout(request)
    return HttpResponseRedirect("/login")

@login_required
def get_country_details(request, country_name):
    country = Country.objects.get(name=country_name)
    result = {"country": country}
    
    return render(request, "country.html", result)

