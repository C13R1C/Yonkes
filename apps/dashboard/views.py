from django.shortcuts import render


def index(request):
    return render(
        request,
        "dashboard/index.html",
        {
            "active_module": "dashboard",
        },
    )
