from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import YonkeForm
from .models import Yonke


def yonke_list(request):
    queryset = Yonke.objects.all().order_by("nombre")

    q = request.GET.get("q", "").strip()
    estatus = request.GET.get("estatus", "").strip()
    mostrar_contacto = request.GET.get("mostrar_contacto", "").strip()
    contacto = request.GET.get("contacto", "").strip()

    if q:
        queryset = queryset.filter(Q(nombre__icontains=q) | Q(razon_social__icontains=q))
    if estatus:
        queryset = queryset.filter(estatus=estatus)
    if mostrar_contacto in {"true", "false"}:
        queryset = queryset.filter(mostrar_contacto=(mostrar_contacto == "true"))
    if contacto:
        queryset = queryset.filter(
            Q(telefono__icontains=contacto)
            | Q(whatsapp__icontains=contacto)
            | Q(email__icontains=contacto)
        )

    return render(
        request,
        "yonkes/list.html",
        {
            "active_module": "yonkes",
            "yonkes": queryset,
            "estatus_choices": Yonke.ESTATUS_CHOICES,
            "filters": {
                "q": q,
                "estatus": estatus,
                "mostrar_contacto": mostrar_contacto,
                "contacto": contacto,
            },
        },
    )


def yonke_detail(request, pk):
    yonke = get_object_or_404(Yonke, pk=pk)
    vehiculos_count = getattr(yonke, "vehiculos", None).count() if hasattr(yonke, "vehiculos") else None
    piezas_count = getattr(yonke, "piezas", None).count() if hasattr(yonke, "piezas") else None
    return render(
        request,
        "yonkes/detail.html",
        {
            "active_module": "yonkes",
            "yonke": yonke,
            "vehiculos_count": vehiculos_count,
            "piezas_count": piezas_count,
        },
    )


def yonke_create(request):
    form = YonkeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        yonke = form.save()
        return redirect("yonkes_html:yonkes-detail", pk=yonke.pk)
    return render(request, "yonkes/form.html", {"active_module": "yonkes", "form": form, "is_edit": False})


def yonke_edit(request, pk):
    yonke = get_object_or_404(Yonke, pk=pk)
    form = YonkeForm(request.POST or None, instance=yonke)
    if request.method == "POST" and form.is_valid():
        yonke = form.save()
        return redirect("yonkes_html:yonkes-detail", pk=yonke.pk)
    return render(
        request,
        "yonkes/form.html",
        {"active_module": "yonkes", "form": form, "is_edit": True, "yonke": yonke},
    )
