from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from mybusiness import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from . tokens import generate_token

def home(request):
    return render(request, 'index.html')

# Create your views here.
def signup(request):
    if request.method == 'POST':
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username =username):
            messages.error(request, "Username already exist! Please add another username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('home')
        
        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters")
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-numeric!")
            # return redirect('home')
        


        #create user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        #save the user
        myuser.save()

        messages.success(request, "Your account has been successfully created. We have sent a confirmation email please confirm your email, inorder to activate your account")

        #welcome email

        subject = "Welccome to MyBusiness!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to MyBusiness \n We have also sent you a confirmation email, please confirm your email address in order to activate your account  \n \n Thank you \n MyBusiness"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)



        # confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your email for MYBusiness!!"
        message2 = render_to_string('email_confirmation.html'),{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),

        }

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST,
            [myuser.email],
        )

        email.fail_silently = True
        email.send()


        return redirect('signin')

    return render(request, 'signup.html')


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        #authenticate the user
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            context={'fname': fname}
            return render(request, "index.html", context)
        else:
            messages.error(request, 'Bad credentials')
            return redirect('home')

    return render(request, 'signin.html')

def signout(request):
    logout(request)
    messages.success(request, 'logged out successfully!')
    return redirect('home')
