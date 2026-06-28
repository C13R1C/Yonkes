from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import can_create_inventory, is_admin_general, user_yonke, yonkes_queryset_for_user
from apps.yonkes.models import Yonke

from .forms import ImportacionExcelForm
from .models import ImportacionError, ImportacionExcel


@login_required(login_url="/login/")
def importaciones_list(request):
    if not can_create_inventory(request.user):
        raise PermissionDenied
    q = request.GET.get("q", "").strip()
    yonke = request.GET.get("yonke", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    estado = request.GET.get("estado", "").strip()

    queryset = ImportacionExcel.objects.select_related("yonke").order_by("-creado_en", "-id")
    if not is_admin_general(request.user):
        queryset = queryset.filter(yonke=user_yonke(request.user))

    if q:
        queryset = queryset.filter(Q(archivo__icontains=q) | Q(resultado__icontains=q))
    if yonke:
        queryset = queryset.filter(yonke_id=yonke)
    if tipo:
        queryset = queryset.filter(tipo_importacion=tipo)
    if estado:
        queryset = queryset.filter(estado=estado)

    return render(
        request,
        "importaciones/list.html",
        {
            "active_module": "importaciones",
            "importaciones": queryset,
            "yonkes": yonkes_queryset_for_user(Yonke.objects.all().order_by("nombre"), request.user),
            "tipo_choices": ImportacionExcel.TIPO_CHOICES,
            "estado_choices": ImportacionExcel.ESTADO_CHOICES,
            "filters": {"q": q, "yonke": yonke, "tipo": tipo, "estado": estado},
        },
    )


@login_required(login_url="/login/")
def importaciones_create(request):
    if not can_create_inventory(request.user):
        raise PermissionDenied
    form = ImportacionExcelForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        registro = form.save(commit=False)
        registro.usuario = request.user
        if not registro.yonke_id:
            registro.yonke = user_yonke(request.user)
        registro.save()
        return redirect("importaciones-detail", pk=registro.pk)

    return render(
        request,
        "importaciones/form.html",
        {
            "active_module": "importaciones",
            "form": form,
            "aviso_procesamiento": "El procesamiento automático de Excel aún no está implementado. Esta pantalla registra el archivo para procesamiento posterior.",
        },
    )


@login_required(login_url="/login/")
def importaciones_detail(request, pk):
    queryset = ImportacionExcel.objects.select_related("yonke")
    if not is_admin_general(request.user):
        queryset = queryset.filter(yonke=user_yonke(request.user))
    importacion = get_object_or_404(queryset, pk=pk)
    errores = ImportacionError.objects.filter(importacion=importacion).order_by("numero_fila", "id")

    return render(
        request,
        "importaciones/detail.html",
        {
            "active_module": "importaciones",
            "importacion": importacion,
            "errores": errores,
            "aviso_procesamiento": "El procesamiento automático de Excel aún no está implementado. Esta pantalla registra el archivo para procesamiento posterior.",
        },
    )
