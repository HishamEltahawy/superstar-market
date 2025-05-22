from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .serializers import SzSignup, SzUsers
from rest_framework.views import APIView
from ProductsApp.models import Products
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.tokens import OutstandingToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
import logging

logger = logging.getLogger(__name__)



class RegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = SzSignup(data=data)
        if serializer.is_valid():
            if not User.objects.filter(email=data['email']).exists():
                user = User.objects.create(
                    username=data['username'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    password=make_password(data['password']),
                )
                # # Update the automatically created profile with user type
                user_type = data.get('user_type', 'Customer')
                user.profile.user_type = user_type
                user.profile.save()
                
                return Response({'details': 'Add User Successful'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'details': 'This Account Already Exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors)

class LoginView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return Response({"error": "User is not signed up."}, status=status.HTTP_404_NOT_FOUND)

        if user:
            profile = user.profile
            if profile.two_factor_enabled:
                # Generate temporary token with a 5-minute expiration
                temp_token = AccessToken.for_user(user)
                temp_token['2fa_verified'] = False  # Important! 2FA not verified yet
                temp_token.set_exp(lifetime=timedelta(minutes=5))  # Set expiration to 5 minutes

                # Generate a random 6-digit code
                code = get_random_string(length=6, allowed_chars='0123456789')
                profile.set_two_factor_code(code)  # Use the encryption method to set the code

                # Send the code via email
                send_mail(
                    subject="Your 2FA Code",
                    message=f"Your 2FA code is: {code}",
                    from_email="hishameltahawy555@gmail.com",  # Sender Email
                    recipient_list=[user.email],  # Receiver Email
                )
                
                return Response({
                    "message": "2FA verification required.",
                    "temp_token": str(temp_token)
                }, status=status.HTTP_200_OK)
            else:
                # If no 2FA required, issue normal token
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

class Enable2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        if profile.two_factor_enabled:
            return Response({"error": "2FA is already enabled."}, status=status.HTTP_400_BAD_REQUEST)

        profile.two_factor_enabled = True
        profile.save()
        return Response({"message": "2FA has been enabled."}, status=status.HTTP_200_OK)

class Disable2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        if not profile.two_factor_enabled:
            return Response({"error": "2FA is not enabled."}, status=status.HTTP_400_BAD_REQUEST)

        profile.two_factor_enabled = False
        profile.two_factor_code = None
        profile.save()
        return Response({"message": "2FA has been disabled."}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            # Blacklist the refresh token
            refresh_token = request.data.get("refresh_token")
            token = OutstandingToken.objects.get(token=refresh_token)
            BlacklistedToken.objects.create(token=token)
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except  OutstandingToken:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Generate  new code and send it to email
class Request2FACodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile

        if not profile.two_factor_enabled:
            return Response({"error": "2FA is not enabled."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a random 6-digit code
        code = get_random_string(length=6, allowed_chars='0123456789')
        profile.set_two_factor_code(code)  # Use the encryption method to set the code

        # Send the code via email using Celery task
        from AccountsApp.tasks import send_email_task
        
        send_email_task.delay(
            subject="Your 2FA Code",
            message=f"Your 2FA code is: {code}",
            from_email=None,  # Will use DEFAULT_FROM_EMAIL from settings
            recipient_list=[request.user.email],
        )

        return Response({"message": "2FA code has been sent to your email."}, status=status.HTTP_200_OK)

class Verify2FAView(APIView):
    # @ratelimit(key='ip', rate='3/m', block=True)
    def post(self, request):
        code = request.data.get("code")
        temp_token = request.data.get("temp_token")
        if not temp_token:
            logger.error("Temporary token is missing in the request body.")
            return Response({"error": "Temporary token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            decoded_token = AccessToken(temp_token)
            user_id = decoded_token["user_id"]
            user = User.objects.get(id=user_id)
        except Exception as e:
            logger.error(f"Error decoding temp_token: {e}")
            return Response({"error": "Invalid or expired temporary token."}, status=status.HTTP_400_BAD_REQUEST)
        profile = user.profile
        if not profile.two_factor_enabled:
            logger.warning(f"2FA is not enabled for user {user.username}.")
            return Response({"error": "2FA is not enabled."}, status=status.HTTP_400_BAD_REQUEST)
        if profile.verify_two_factor_code(code):
            profile.two_factor_code = None
            profile.save()
            refresh = RefreshToken.for_user(user)
            return Response({"refresh": str(refresh),"access": str(refresh.access_token)}, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Invalid 2FA code provided for user {user.username}.")
            return Response({"error": "Invalid 2FA code."}, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([IsAuthenticated])
@api_view(['GET'])
def current_user(request):
    user = request.user # Get the currently authenticated user
    serializer = SzUsers(user)
    return Response(serializer.data)

class ForgetPassword(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        user = data['username']
        email = data['username']
        user = data['username']
        user = data['username']

# Update user details
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_user(request):
    user = request.user
    data = request.data

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.username = data['username']
    user.email = data['email']

    if data['password'] != "":
        user.password = make_password(data['password'])
    
    user.save()
    serializer = SzUsers(user, many=False)
    return Response(serializer.data)

class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)

        if data.get('password', "") != "":
            user.password = make_password(data['password'])

        user.save()

        serializer = SzUsers(user, many=False)
        return Response(serializer.data)



def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return '{protocol}://{host}/'.format(protocol=protocol, host = host)

# Forget password
@api_view(['POST'])
def forget_password(request):
    data = request.data
    user = get_object_or_404(User, email=data['email'])
    generate_token = get_random_string(40)
    token_ex_date = datetime.now() + timedelta(minutes=30)
    user.profile.new_token = generate_token
    user.profile.ex_date = token_ex_date
    user.profile.save()
    link = f'http://127.0.0.1:8000/api/accounts/reset_password/{generate_token}'
    body = f'Your password-reset link is {link}'
    send_mail('Password reset from hisham', body, 'hishameltahawy555@gmail.com', [data['email']])
    return Response({'details': f'Password reset link sent to email: {data["email"]}'})

# Reset password
@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(User, profile__new_token=token)  # all fields about this user (id, username, password, ...)
    
    if user.profile.ex_date is None or user.profile.ex_date.replace(tzinfo=None) < datetime.now():
        return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    # Make token and its expire date empty to never user or anyone use this api again without call forget password 
    user.password = make_password(data['password'])
    user.profile.new_token = ""
    user.profile.ex_date = None
    
    user.profile.save()
    user.save()
    return Response({'result': 'Password changed successfully.'}, status=status.HTTP_200_OK)

