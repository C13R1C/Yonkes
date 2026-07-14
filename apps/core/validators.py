from pathlib import Path
from zipfile import BadZipFile, ZipFile

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_UPLOAD_SIZE = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MAX_IMAGE_DIMENSION = 8000
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
ALLOWED_XLSX_EXTENSION = ".xlsx"


def _file_size(uploaded_file):
    size = getattr(uploaded_file, "size", None)
    if size is not None:
        return size
    position = uploaded_file.tell()
    uploaded_file.seek(0, 2)
    size = uploaded_file.tell()
    uploaded_file.seek(position)
    return size


def validate_uploaded_image(uploaded_file):
    if not uploaded_file:
        return
    name = getattr(uploaded_file, "name", "")
    if Path(name).suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Formato de imagen no permitido. Usa JPG, PNG o WEBP.")
    if _file_size(uploaded_file) > MAX_UPLOAD_SIZE:
        raise ValidationError("La imagen no puede superar 5 MB.")

    position = uploaded_file.tell()
    try:
        uploaded_file.seek(0)
        try:
            with Image.open(uploaded_file) as image:
                image.verify()
                image_format = image.format
        except (UnidentifiedImageError, OSError) as exc:
            raise ValidationError("El archivo no es una imagen válida o está corrupto.") from exc

        if image_format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError("El contenido de la imagen no coincide con un formato permitido.")

        uploaded_file.seek(0)
        with Image.open(uploaded_file) as image:
            width, height = image.size
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION or width * height > MAX_IMAGE_PIXELS:
                raise ValidationError("Las dimensiones de la imagen exceden el máximo permitido.")
    finally:
        uploaded_file.seek(position)


def validate_uploaded_xlsx(uploaded_file):
    if not uploaded_file:
        return
    name = getattr(uploaded_file, "name", "")
    if Path(name).suffix.lower() != ALLOWED_XLSX_EXTENSION:
        raise ValidationError("Solo se permiten archivos XLSX.")
    size = _file_size(uploaded_file)
    if size <= 0:
        raise ValidationError("El archivo no puede estar vacío.")
    if size > MAX_UPLOAD_SIZE:
        raise ValidationError("El archivo no puede superar 5 MB.")

    position = uploaded_file.tell()
    try:
        uploaded_file.seek(0)
        try:
            with ZipFile(uploaded_file) as archive:
                names = set(archive.namelist())
                if "[Content_Types].xml" not in names or not any(name.startswith("xl/") for name in names):
                    raise ValidationError("El archivo XLSX no tiene una estructura válida.")
        except BadZipFile as exc:
            raise ValidationError("El archivo XLSX no tiene una estructura válida.") from exc
    finally:
        uploaded_file.seek(position)
