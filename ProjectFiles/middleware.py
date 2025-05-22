from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
import re

class SecurityMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.paths_requiring_2fa = [
            r'^/api/orders/',
            r'^/api/cart/',
            r'^/api/wishlist/'
        ]

    def process_request(self, request):
        # Skip middleware for non-protected paths
        if not any(re.match(path, request.path) for path in self.paths_requiring_2fa):
            return None

        # Check for token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            token = AccessToken(auth_header.split(' ')[1])
            # Check if 2FA is required but not verified
            if '2fa_verified' in token and not token['2fa_verified']:
                return JsonResponse({'error': '2FA verification required'}, status=403)
        except Exception:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return None