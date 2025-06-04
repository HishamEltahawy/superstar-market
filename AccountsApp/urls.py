from django.urls import path
from . import views
from .views import *

urlpatterns = [

    # api/accounts/
    path('register/', RegisterView.as_view(), name='register'), # register/   
    path('login/', LoginView.as_view(), name='login'), # login/                                                   
    path('logout/', LogoutView.as_view(), name='logout'), # logout/
    
    # APIs forget password system
    path('forget-password/', ForgetPassword.as_view(), name='forgetPassword'), # forget-password/
    path('verify-otp/', VerifyOtp.as_view(), name='verifyOtp'), # verify-otp/
    path('change-password/', ChangePassword.as_view(), name='changePassword'), # change-password/


    path('update_user_view/', UpdateUserView.as_view, name='update_user_view'), # update_user/
    path('reset_password/<str:token>', views.reset_password), # reset_password/
    
 

    path('2fa/enable/', Enable2FAView.as_view(), name='enable-2fa'), # 2fa/enable/     >>bug with logout
    path('2fa/disable/', Disable2FAView.as_view(), name='disable-2fa'), # 2fa/disable/    >>bug with logout
    path('2fa/verify/', Verify2FAView.as_view(), name='verify-2fa'), # 2fa/verify/      >>bug with logout
    path('2fa/request-code/', Request2FACodeView.as_view(), name='request-2fa-code'), # 2fa/request-code/       >>bug with logout
]