from django.shortcuts import redirect


class LoginRequiredMiddleware:
    PUBLIC_PREFIXES = (
        "/login/",
        "/register/",
        "/logout/",
        "/accounts/login/",
        "/accounts/logout/",
        "/admin/",
        "/api/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if request.user.is_authenticated or path.startswith(self.PUBLIC_PREFIXES):
            return self.get_response(request)

        return redirect(f"/login/?next={request.get_full_path()}")
