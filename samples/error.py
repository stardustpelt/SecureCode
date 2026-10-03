# settings.py / views.py combined for demo

# 🔴 HIGH: Hardcoded Django secret key
SECRET_KEY = "django-insecure-hardcoded-secret-123456"

# 🟠 MEDIUM: Debug enabled in non-production
DEBUG = True

# 🟠 MEDIUM: Wildcard host allowed
ALLOWED_HOSTS = ["*"]

# 🔴 HIGH: Hardcoded API key
STRIPE_API_KEY = "sk_test_exposedAPIKey987"

# 🟠 MEDIUM: Session cookie not secure
SESSION_COOKIE_SECURE = False

from django.http import HttpResponse
from django.db import connection
import os

def unsafe_user_lookup(request):
user_input = request.GET.get("id")   # 🟡 LOW: indentation error

    # 🔴 HIGH: SQL Injection
    query = "SELECT * FROM users WHERE id = '%s'" % user_input
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()

    # 🔴 HIGH: Reflected XSS
    return HttpResponse("User ID: " + user_input)

def dangerous_command(request):
    cmd = request.GET.get("cmd")
    
    # 🔴 HIGH: Command Injection
    os.system(cmd)
    
    return HttpResponse("Executed command")

# 🟡 LOW: Insecure file upload
from django import forms

class UploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        # No file type or size validation
        return self.cleaned_data["file"]

# 🔴 HIGH: XSS in template example
profile_template = """
<h1>User Profile</h1>
<p>Welcome {{ username }}</p>
"""
