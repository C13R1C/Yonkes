from django.contrib import admin
from .models import ImportacionExcel, ImportacionError


class ImportacionErrorInline(admin.TabularInline):
    model = ImportacionError
    extra = 0
    readonly_fields = ("numero_fila", "campo", "valor", "error", "creado_en")


@admin.register(ImportacionExcel)
class ImportacionExcelAdmin(admin.ModelAdmin):
    list_display = ("id", "yonke", "tipo_importacion", "estado", "total_filas", "filas_validas", "filas_con_error", "creado_en")
    list_filter = ("estado", "tipo_importacion", "yonke")
    search_fields = ("yonke__nombre",)
    inlines = [ImportacionErrorInline]


@admin.register(ImportacionError)
class ImportacionErrorAdmin(admin.ModelAdmin):
    list_display = ("id", "importacion", "numero_fila", "campo", "error", "creado_en")
    search_fields = ("campo", "valor", "error")
