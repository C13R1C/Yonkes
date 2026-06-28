from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import can_access_admin_area, can_manage_yonke, is_admin_general, is_dueno_yonke, is_empleado, user_yonke

from .forms import YonkeForm
from .models import Yonke


def _can_use_yonkes_directory(user):
    return bool(user and user.is_authenticated)


def _is_yonke_operator(user):
    return is_dueno_yonke(user) or is_empleado(user)


def _yonkes_directory_queryset(user):
    qs = Yonke.objects.all().order_by("nombre")
    if is_admin_general(user):
        return qs
    if _is_yonke_operator(user):
        current_yonke = user_yonke(user)
        public_q = Q(estatus="activo") | Q(mostrar_contacto=True)
        if current_yonke:
            public_q |= Q(pk=current_yonke.pk)
        return qs.filter(public_q).distinct()
    return qs.filter(estatus="activo", mostrar_contacto=True)


def _can_view_yonke_contact(user, yonke):
    if is_admin_general(user):
        return True
    current_yonke = user_yonke(user)
    if current_yonke and current_yonke.pk == yonke.pk:
        return True
    return bool(yonke.mostrar_contacto)


def _can_view_yonke_internal_data(user, yonke):
    return bool(is_admin_general(user) or can_manage_yonke(user, yonke))


@login_required(login_url="/login/")
def yonke_list(request):
    if not _can_use_yonkes_directory(request.user):
        raise PermissionDenied

    queryset = _yonkes_directory_queryset(request.user)

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
        if not is_admin_general(request.user):
            current_yonke = user_yonke(request.user)
            contact_visibility = Q(mostrar_contacto=True)
            if current_yonke:
                contact_visibility |= Q(pk=current_yonke.pk)
            queryset = queryset.filter(contact_visibility)
        queryset = queryset.filter(
            Q(telefono__icontains=contacto)
            | Q(whatsapp__icontains=contacto)
            | Q(email__icontains=contacto)
        )

    yonkes = list(queryset)
    for yonke_obj in yonkes:
        yonke_obj.can_edit_yonke = can_manage_yonke(request.user, yonke_obj)
        yonke_obj.can_view_contact = _can_view_yonke_contact(request.user, yonke_obj)

    return render(
        request,
        "yonkes/list.html",
        {
            "active_module": "yonkes",
            "yonkes": yonkes,
            "can_create_yonke": can_access_admin_area(request.user),
            "estatus_choices": Yonke.ESTATUS_CHOICES,
            "filters": {
                "q": q,
                "estatus": estatus,
                "mostrar_contacto": mostrar_contacto,
                "contacto": contacto,
            },
        },
    )


@login_required(login_url="/login/")
def yonke_detail(request, pk):
    if not _can_use_yonkes_directory(request.user):
        raise PermissionDenied

    yonke = get_object_or_404(_yonkes_directory_queryset(request.user), pk=pk)
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
            "can_edit_yonke": can_manage_yonke(request.user, yonke),
            "can_view_contact": _can_view_yonke_contact(request.user, yonke),
            "can_view_internal_data": _can_view_yonke_internal_data(request.user, yonke),
        },
    )


@login_required(login_url="/login/")
def yonke_create(request):
    if not is_admin_general(request.user):
        raise PermissionDenied
    form = YonkeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        yonke = form.save()
        messages.success(request, "Registro creado correctamente.")
        return redirect("yonkes_html:yonkes-detail", pk=yonke.pk)
    return render(request, "yonkes/form.html", {"active_module": "yonkes", "form": form, "is_edit": False})


@login_required(login_url="/login/")
def yonke_edit(request, pk):
    yonke = get_object_or_404(Yonke, pk=pk)
    if not can_manage_yonke(request.user, yonke):
        raise PermissionDenied
    form = YonkeForm(request.POST or None, instance=yonke)
    if request.method == "POST" and form.is_valid():
        yonke = form.save()
        messages.success(request, "Registro actualizado correctamente.")
        return redirect("yonkes_html:yonkes-detail", pk=yonke.pk)
    return render(
        request,
        "yonkes/form.html",
        {"active_module": "yonkes", "form": form, "is_edit": True, "yonke": yonke},
    )
