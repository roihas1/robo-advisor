import json

import django.middleware.csrf
from django.http import JsonResponse
from django.middleware import csrf
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from users.models import CustomUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from allauth.account.views import SignupView, LoginView
from .forms import UserRegisterForm, CustomLoginForm
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.exceptions import BadRequest
from users.forms import AccountMetadataForm
from .serializers import CustomUserSerializer


# @api_view(['GET', 'POST'])
# def users_list(request):
#     if request.method == 'GET':
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)
#
#     if request.method == 'POST':
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class SignUpView(SignupView):
    """
    Creates new employee
    """
    form_class = UserRegisterForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        form_fields = {field.name: field.label for field in form}
        response_data = {
            'form': form_fields,
            'title': "Sign Up"
        }
        return JsonResponse(response_data, status=200)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
        form = self.form_class(data)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            response_data = {'success': True, 'message': f"Successfully created your account - '{email}'."}
            return JsonResponse(response_data, status=201)

        errors = {field: error.get_json_data() for field, error in form.errors.items()}
        response_data = {'success': False, 'errors': errors}
        return JsonResponse(response_data, status=400)

    def non_field_errors(self) -> list[str]:
        if 'email' in self.errors and 'already exists' in self.errors['email'][0]:
            errors = ["A user is already assigned with this email. Please use a different email address."]
            return errors


def check_email(request):
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    email = body_data.get('email')
    try:
        validate_email(email)
        is_valid = True
    except ValidationError:
        is_valid = False

    return JsonResponse({'valid': is_valid})


def check_first_name(request):
    # Parse the JSON body of the request
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Create the form with the provided data
    form = UserRegisterForm(data)

    # Check if the first_name field is valid
    first_name_valid = not form['first_name'].errors

    # Return a JSON response with the validation result
    return JsonResponse({'valid': first_name_valid})


def check_last_name(request):
    # Parse the JSON body of the request
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Create the form with the provided data
    form = UserRegisterForm(data)

    # Check if the first_name field is valid
    last_name_valid = not form['last_name'].errors

    # Return a JSON response with the validation result
    return JsonResponse({'valid': last_name_valid})


def check_phone_number(request):
    try:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        phone_number = body_data.get('phone_number')
        validate_international_phonenumber(phone_number)
        is_valid = True
        return JsonResponse({'valid': is_valid})
        # Check if the phone number already exists in the User model
        # if CustomUser.objects.filter(phone_number=phone_number).exists():
        #     is_valid = False  # Phone number is already registered
        # else:
        #     is_valid = True  # Phone number is available
    except ValidationError:
        is_valid = False
        return JsonResponse({'valid': False, 'error': 'Invalid phone number format'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def check_password_confirmation(request):
    # TODO: check equals between password1 & password2 in front
    try:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        password = body_data.get('password2')

        # Validate the password using Django's built-in validators
        validate_password(password)
        return JsonResponse({'valid': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValidationError as e:
        return JsonResponse({'valid': False, 'errors': list(e.messages)}, status=400)


class AppLoginView(LoginView):
    form_class = CustomLoginForm

    def get(self, request, *args, **kwargs):
        # print(django.middleware.csrf.get_token(request))
        token = django.middleware.csrf.get_token(request)
        form = self.form_class()
        form_fields = {field.name: field.label for field in form}
        response_data = {
            'form': form_fields,
            'title': "Login",
            "token":token
        }
        return JsonResponse(response_data, status=200)

    # def form_valid(self, form):
    #     email: str = form.cleaned_data['login']
    #     try:
    #         user: CustomUser = CustomUser.objects.get(email=email)
    #     except CustomUser.DoesNotExist:
    #         raise ValueError(f'No user with email - `{email}`')
    #     try:
    #         if core_views.check_is_user_last_login_was_up_to_yesterday(user=user):
    #             # it will be displayed if the last date for the change is different from today's date
    #             web_actions.save_three_user_graphs_as_png(user=user)
    #             if service_settings.GOOGLE_DRIVE_DAILY_DOWNLOAD:
    #                 data_management.update_files_from_google_drive()
    #             """
    #             Dataset and static images are updated daily, only when the date of the last update is different
    #             from today
    #             """
    #     except InvestorUser.DoesNotExist:
    #         pass
    #     return super().form_valid(form)


def check_login_email(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        valid = CustomUser.objects.filter(email=email).exists()
        return JsonResponse({'valid': valid})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # def check_login_email_reset(request):
    #     form = CustomLoginForm(request.POST)
    #
    #     User = CustomUser
    #     email = request.POST.get('email')
    #     print(email)
    #     # print(form.cleaned_data.get['login'])
    #
    #     try:
    #         User.objects.get(email=email)
    #         valid = True
    #         print('valid true')
    #     except User.DoesNotExist:
    #         valid = False
    #     context = {
    #         'field': form['login'],
    #
    #         'valid': valid,
    #     }
    #     return render(request, 'partials/email_validation.html', context)

def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate user
            user = form.get_user()
            login(request, user)
            # Handle any additional logic
            return redirect('home')  # Redirect to a different page after login
    else:
        form = CustomLoginForm()
    return render(request, 'account/guest/login.html', {'form': form})


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            user_data = CustomUserSerializer(user).data
            return JsonResponse({'status': 'successful',"user":user_data}, status=200)
        else:
            return JsonResponse({'status': 'wrong password/username'}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

# @ensure_csrf_cookie
# @csrf_protect
@api_view(['POST','GET'])
def custom_login_system(request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', 'false').lower() == 'true'

            if not email or not password:
                return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                if remember:
                    # Set session expiry to a large number (e.g., 1 year)
                    request.session.set_expiry(60 * 60 * 24 * 365)
                else:
                    # Set session expiry to browser close (default behavior)
                    request.session.set_expiry(0)

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)
    # Determine if the logout operation was successful
    success = True  # Assuming logout always succeeds for simplicity

    # Return JSON response indicating success or failure
    return JsonResponse({'isvalid': success})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@require_http_methods(["GET"])
def profile_main(request):
    if request.method == 'GET':
        form = AccountMetadataForm(instance=request.user, disabled_project=True)
        # Prepare the data to be returned in JSON format
        data = {
            'title': f"{request.user.first_name}'s Profile",
            'form': {field.name: field.value() for field in form}
        }
    else:
        raise BadRequest("Invalid request method")

    return JsonResponse(data)