from django.shortcuts import render

# ------------------------------------------------Registration Logic--------------------------------------------------------------
from django.shortcuts import render
from .models import UserProfile
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.views.decorators.cache import never_cache

def signup_view(request):
    context = {}

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Email validation
        if '@' not in email or not email.endswith('.com'):
            context['email_error'] = 'Email must include "@" and end with ".com"'
        elif UserProfile.objects.filter(email=email).exists():
            context['email_error'] = 'Email is already registered'

        # Mobile validation
        if not mobile.isdigit() or len(mobile) != 10:
            context['mobile_error'] = 'Mobile number must be exactly 10 digits'
        elif UserProfile.objects.filter(mobile=mobile).exists():
            context['mobile_error'] = 'Mobile is already exists'    

        # Password confirmation
        if password != confirm_password:
            context['password_error'] = 'Passwords do not match'

        # If no errors, save the user
        if not context:
            UserProfile.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile=mobile,
                password=make_password(password),  # hashed password
                login_time=timezone.now()
            )
            context['success'] = 'User registered successfully'

    return render(request, 'registration.html', context)


def user_login(request):
    return render(request,'userlogin.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from .models import UserProfile

def user_login_check(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        print(f"[LOGIN ATTEMPT] Email: {email}, Password: {password}")

        try:
            user = UserProfile.objects.get(email=email)
            print(f"[USER FOUND] Email: {user.email}, Status: {user.status}")
        except UserProfile.DoesNotExist:
            print("[LOGIN FAILED] No user found with this email.")
            messages.error(request, "Invalid email or password.")
            return render(request, 'userlogin.html')

        # Check password
        if not check_password(password, user.password):
            print("[LOGIN FAILED] Password does not match.")
            messages.error(request, "Invalid email or password.")
            return render(request, 'userlogin.html')

        # Check user status
        if user.status == 'waiting':
            print(f"[LOGIN DENIED] User '{email}' status is WAITING.")
            messages.warning(request, "Your account is not approved yet. Please wait for approval.")
            return render(request, 'userlogin.html')

        elif user.status == 'blocked':
            print(f"[LOGIN BLOCKED] User '{email}' is BLOCKED.")
            messages.error(request, "Your account is blocked. Please contact our admin team.")
            return render(request, 'userlogin.html')

        # Successful login
        print(f"[LOGIN SUCCESSFUL] User '{email}' logged in.")
        user.last_login = now()
        user.login_time = now()
        user.save()

        # Set session
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.first_name} {user.last_name}"

        messages.success(request, f"Welcome {user.first_name} {user.last_name}!")
        return redirect(user_home_view)  # Make sure this matches your URL name

    return render(request, 'userlogin.html')



from django.utils import timezone
from .models import UserProfile
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect

@never_cache
def user_home_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        print("[ACCESS DENIED] Unauthorized user tried to access home page.")
        return redirect('user_login')

    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        print(f"[ERROR] No user found with ID: {user_id}")
        return redirect('user_login')

    # ✅ Increment visit count
    user.number_of_visitors += 1
    user.save(update_fields=['number_of_visitors'])

    current_time = timezone.now()

    print(f"[HOME ACCESS] User ID: {user_id}, Name: {user.first_name} {user.last_name}, Visits: {user.number_of_visitors}")

    return render(request, 'users/userhome.html', {
        'user': user,
        'current_time': current_time,
    })



@never_cache
def user_logout_view(request):
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    print(f"[LOGOUT] User '{user_name}' with ID {user_id} is logging out.")

    request.session.flush()  # Clears session data
    response = redirect('user_login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

# --------------------------------------------------------------------------------------------------------------------------------

# def chatbot_page(request):
#     return render(request, 'users/chatbot.html')



# views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from users.utility.llm_setup import LLMInitializer

# # Initialize the LLM once when the server starts
# llm_init = LLMInitializer()
# llm = llm_init.initialize_llm()

# @csrf_exempt  # For simplicity, in production use proper CSRF handling
# def chatbot(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             user_message = data.get('message', '')
            
#             # Get response from LLM
#             bot_response = llm(user_message)
            
#             return JsonResponse({
#                 'status': 'success',
#                 'response': bot_response
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'error': str(e)
#             }, status=500)
    
#     # For GET requests, just render the chat page
#     return render(request, 'users/chatbot1.html')
# -----------------------------------------------------------------------------------------
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .decorators import login_required_custom
from django.views.decorators.http import require_POST
from .models import Chat, Message, UserProfile
import json

# Import your LLM initializer (adjust import path if needed)
from users.utility.llm_setup import LLMInitializer

# Initialize the LLM once when the server starts
llm_init = LLMInitializer()
llm = llm_init.initialize_llm()

@login_required_custom
def chatbot_view(request):
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(id=user_id)

    if request.method == 'GET':
        chats = Chat.objects.filter(user=user)
        active_chat = chats.first() if chats.exists() else None
        messages = active_chat.message_set.all() if active_chat else []

        return render(request, 'users/chatbot1.html', {
            'chat_history': chats,
            'active_chat': active_chat,
            'initial_messages': messages,
            'user': user,
        })

    elif request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        chat_id = data.get('chat_id')

        # Get or create chat
        if chat_id:
            chat = get_object_or_404(Chat, id=chat_id, user=user)
        else:
            chat = Chat.objects.create(user=user, title=user_message[:50])

        # Save user's message
        Message.objects.create(chat=chat, sender='user', content=user_message)

        # Generate bot response using your LLM
        try:
            bot_response = llm(user_message)
        except Exception as e:
            bot_response = "Sorry, I couldn't process your request at the moment."

        # Save bot's response
        Message.objects.create(chat=chat, sender='bot', content=bot_response)

        return JsonResponse({
            'status': 'success',
            'response': bot_response,
            'chat_id': chat.id,
        })


@login_required_custom
def load_chat_history(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    messages = chat.message_set.all().values('sender', 'content')
    return JsonResponse({'status': 'success', 'messages': list(messages)})


@require_POST
@login_required_custom
def create_new_chat(request):
    chat = Chat.objects.create(user=request.user, title='New Chat')
    return JsonResponse({'status': 'success', 'chat_id': chat.id, 'title': chat.title})


@require_POST
@login_required_custom
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.delete()
    return JsonResponse({'status': 'success'})
