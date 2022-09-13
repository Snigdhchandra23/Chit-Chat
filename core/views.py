from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token
from .graph_helper import *
from django.contrib.auth.models import User
from .forms import SignUpForm
from django.contrib import messages
def frontpage(request):
    return render(request, 'core/frontpage.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration successful." )
            return redirect('frontpage')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = SignUpForm()
    
    return render(request, 'core/signup.html', {'form': form})

def initialize_context(request):
    context = {}

    # Check for any errors in the session
    error = request.session.pop('flash_error', None)

    if error != None:
        context['errors'] = []
        context['errors'].append(error)

    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context
# </InitializeContextSnippet>

# <SignInViewSnippet>


def sign_in(request):
    # Get the sign-in flow

    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])
# </SignInViewSnippet>

# <SignOutViewSnippet>


def sign_out(request):
    # Clear out the user and token
    remove_user_and_token(request)
    logout(request)
    return HttpResponseRedirect(reverse('frontpage'))
# </SignOutViewSnippet>

# <CallbackViewSnippet>


def callback(request):
    # Make the token request
    result = get_token_from_code(request)
    print(result)
    # Get the user's profile
    user = get_user(result['access_token'])
    # Store user
    store_user(request, user)
    # print(user)
    # print(user['displayName'])
    # print(user['mail'])
    email = user['mail']
    domain = email[email.index('@') + 1 : ]
    if domain != "iitg.ac.in":
        messages.error(request,"Only iitg emails are allowed to use this app!")
        return HttpResponseRedirect(reverse('frontpage'))
    try:
        user_object = User.objects.get(username=user["displayName"])
    except:
        user_object = User.objects.create(
            username=user['displayName'], email=user['mail'])
        user_object.save()
    
    login(request, user_object, backend='django.contrib.auth.backends.ModelBackend')
    messages.success(request,"You have logged in successfully!")
    # if user_object is not None:
        # login(request,user_object)  # we call the login function to bind a user to current session, this way they get automatically logged in to django admin website
    # user_object.is_staff = True # we also need to set is_staff permission to true so that they have access to admin dashboard
    # user_object.save()
    # now we just redirect to admin view, search for httpresponseredirect on django docs for more info.
    return HttpResponseRedirect(reverse('frontpage'))
