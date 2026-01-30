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
from .models import User, City, Country, Countrylanguage, Product, Category
import requests
from bs4 import BeautifulSoup
import re

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

def sync_products(request):
    context = {}
    default_url = 'https://ultimateorganiclife.com/product-categories/2/Coffee%20&%20Tea'
    context['ecommerce_url'] = default_url

    if request.method == 'POST':
        if 'sync_products' in request.POST:
            ecommerce_url = request.POST.get('ecommerce_url', '').strip()
            if not ecommerce_url:
                context['error'] = 'Ecommerce URL is required.'
                return render(request, 'sync_products.html', context)

            try:
                session = requests.Session()
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = session.get(ecommerce_url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # For WooCommerce category pages, products are typically in <li class="product"> or <div class="product">
                product_elements = soup.find_all('li', class_='product') or soup.find_all('div', class_='product')

                synced_count = 0
                for prod_elem in product_elements:
                    # Extract title - WooCommerce often uses <h2 class="woocommerce-loop-product__title"> or <a>
                    title_elem = prod_elem.find('h2', class_='woocommerce-loop-product__title') or prod_elem.find('a')
                    title = title_elem.get_text(strip=True) if title_elem else 'Unknown'

                    # Extract price - Look for <span class="woocommerce-Price-amount amount">
                    price_elem = prod_elem.find('span', class_='woocommerce-Price-amount')
                    if price_elem:
                        price_text = price_elem.find('bdi').get_text(strip=True) if price_elem.find('bdi') else price_elem.get_text(strip=True)
                    else:
                        price_text = '0'
                    try:
                        price = float(price_text.replace('$', '').replace(',', '').strip())
                    except ValueError:
                        price = 0.0

                    # Extract image - <img class="attachment-woocommerce_thumbnail">
                    img_elem = prod_elem.find('img', class_='attachment-woocommerce_thumbnail') or prod_elem.find('img')
                    image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''

                    # Extract product URL - The link to the product page
                    link_elem = prod_elem.find('a', href=True)
                    product_url = link_elem['href'] if link_elem else ''
                    # Extract external_id from URL, e.g., last part or query param
                    if product_url:
                        parsed_url = product_url.rstrip('/').split('/')[-1]
                        external_id = parsed_url.split('?')[0] if '?' in parsed_url else parsed_url
                    else:
                        external_id = ''

                    # Extract category from URL or page title
                    category_name = 'Coffee & Tea'  # Hardcoded for this URL; can parse from page
                    category, _ = Category.objects.get_or_create(name=category_name)

                    # Only save if we have at least title and url
                    if title != 'Unknown' and product_url:
                        Product.objects.update_or_create(
                            source_url=product_url,
                            defaults={
                                'external_id': external_id,
                                'name': title,
                                'price': price,
                                'category': category,
                                'description': '',  # Not available on category page
                                'image_url': image_url,
                            }
                        )
                        synced_count += 1

                context['synced_count'] = synced_count
                if synced_count == 0:
                    context['error'] = 'No products found on the page. Please check the URL or HTML structure.'
                else:
                    context['message'] = f'Synced {synced_count} products successfully.'
                context['ecommerce_url'] = ecommerce_url

            except requests.RequestException as e:
                context['error'] = f'Failed to fetch data: {str(e)}'
                context['ecommerce_url'] = ecommerce_url
            except Exception as e:
                context['error'] = f'Error parsing data: {str(e)}'
                context['ecommerce_url'] = ecommerce_url

        elif 'search_contact' in request.POST:
            website_url = request.POST.get('website_url', '').strip()
            if not website_url:
                context['contact_error'] = 'Website URL is required.'
                return render(request, 'sync_products.html', context)

            try:
                session = requests.Session()
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = session.get(website_url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for contact details in specific sections
                contact_texts = []

                # From footer
                footer = soup.find('footer')
                if footer:
                    contact_texts.append(footer.get_text())

                # From elements with class containing 'contact'
                contact_elements = soup.find_all(class_=re.compile(r'contact', re.I))
                for elem in contact_elements:
                    contact_texts.append(elem.get_text())

                # From meta tags or specific tags
                meta_emails = soup.find_all('meta', attrs={'name': re.compile(r'email', re.I)})
                for meta in meta_emails:
                    content = meta.get('content', '')
                    if content:
                        contact_texts.append(content)

                # From all text as fallback
                contact_texts.append(soup.get_text())

                # Combine and find patterns
                full_text = ' '.join(contact_texts)

                # Find emails
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, full_text)
                emails = list(set(emails))  # Remove duplicates

                # Find phone numbers (improved pattern)
                phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
                phones = re.findall(phone_pattern, full_text)
                phones = ['-'.join(phone) for phone in phones]  # Format as XXX-XXX-XXXX
                phones = list(set(phones))  # Remove duplicates

                contacts = []
                if emails:
                    contacts.extend([f"Email: {email}" for email in emails])
                if phones:
                    contacts.extend([f"Phone: {phone}" for phone in phones])

                total_contacts = len(emails) + len(phones)
                context['contact_count'] = total_contacts
                if contacts:
                    context['contact_message'] = f'Found {len(emails)} emails and {len(phones)} phones.'
                    context['contacts'] = contacts
                else:
                    context['contact_error'] = 'No contact details found.'

            except requests.RequestException as e:
                context['contact_error'] = f'Failed to fetch website: {str(e)}'
            except Exception as e:
                context['contact_error'] = f'Error extracting contacts: {str(e)}'

    return render(request, 'sync_products.html', context)

