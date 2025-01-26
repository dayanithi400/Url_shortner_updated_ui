from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import random
import string
from .models import URL

def generate_short_url():
    """Generate a random short URL if no custom alias is provided."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def index(request):
    short_url = None  # Initialize short_url for the response
    error_message = None  # Initialize error message
    
    if request.method == "POST":
        original_url = request.POST.get('long-url')  # Get the long URL from the form
        custom_alias = request.POST.get('customize-link')  # Get the custom alias, if provided

        if original_url:
            if custom_alias:
                # Use custom alias if provided
                if URL.objects.filter(Short_Url=custom_alias).exists():
                    error_message = f"The alias '{custom_alias}' is already taken. Please choose another."
                else:
                    short_url = custom_alias
            else:
                # Generate a random alias if no custom alias is provided
                short_url = generate_short_url()
                while URL.objects.filter(Short_Url=short_url).exists():
                    short_url = generate_short_url()  # Ensure the short URL is unique

            if not error_message:
                # Save the new URL mapping
                new_url, created = URL.objects.get_or_create(
                    Original_Url=original_url,
                    defaults={'Short_Url': short_url}
                )
                if not created:
                    # If the URL already exists in the database, use the existing short URL
                    short_url = new_url.Short_Url

                # Build the full shortened URL with the current domain
                full_short_url = request.build_absolute_uri(f'/{short_url}/')
                domain=request.build_absolute_uri
                # Retrieve recent URLs to display
                recent_urls = URL.objects.order_by('-created_at')[:5]
                return render(request, 'index.html', {
                    'success_message': f"Short URL created: {full_short_url}",
                    'recent_urls': recent_urls,
                    'domain': domain,
                })
        else:
            error_message = "Please provide a valid URL."

    # Handle GET requests or errors
    recent_urls = URL.objects.order_by('-created_at')[:5]
    return render(request, 'index.html', {
        'error_message': error_message,
        'recent_urls': recent_urls,
    })

def redirect_to_original(request, short_url):
    """Redirects to the original URL."""
    try:
        url_entry = URL.objects.get(Short_Url=short_url)
        return redirect(url_entry.Original_Url)
    except URL.DoesNotExist:
        return render(request, 'index.html', {
            'error_message': "Short URL not found.",
            'recent_urls': URL.objects.order_by('-created_at')[:5]
        })
