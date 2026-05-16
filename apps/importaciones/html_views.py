from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.yonkes.models import Yonke

from .forms import ImportacionExcelForm
from .models import ImportacionError, ImportacionExcel


def importaciones_list(request):
    q = request.GET.get("q", "").strip()
    yonke = request.GET.get("yonke", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    estado = request.GET.get("estado", "").strip()

    queryset = ImportacionExcel.objects.select_related("yonke").order_by("-creado_en", "-id")

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
            "yonkes": Yonke.objects.all().order_by("nombre"),
            "tipo_choices": ImportacionExcel.TIPO_CHOICES,
            "estado_choices": ImportacionExcel.ESTADO_CHOICES,
            "filters": {"q": q, "yonke": yonke, "tipo": tipo, "estado": estado},
        },
    )


def importaciones_create(request):
    form = ImportacionExcelForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        registro = form.save()
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


def importaciones_detail(request, pk):
    importacion = get_object_or_404(ImportacionExcel.objects.select_related("yonke"), pk=pk)
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
