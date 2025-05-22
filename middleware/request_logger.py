import json
from django.utils.deprecation import MiddlewareMixin

class RequestLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("\n------ [REQUEST INFO] ------")

        # Method and Path
        print(f"Method: {request.method}")
        print(f"Path: {request.path}")

        # GET Params
        print(f"GET Params: {dict(request.GET)}")

        # POST Params
        print(f"POST Params: {dict(request.POST)}")

        # JSON Body
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            print(f"JSON Body: {json.dumps(json_data, indent=2)}")
        except Exception:
            print("JSON Body: Invalid or not present")

        # Headers
        print("Headers:")
        for key, value in request.headers.items():
            print(f"  {key}: {value}")

        # Cookies
        print(f"Cookies: {request.COOKIES}")

        # Files
        if request.FILES:
            print("Files:")
            for k, f in request.FILES.items():
                print(f"  {k}: {f.name} ({f.content_type})")
        else:
            print("Files: None")

        # User
        print(f"User: {request.user if request.user.is_authenticated else 'Anonymous'}")

        print("------ [END REQUEST INFO] ------\n")