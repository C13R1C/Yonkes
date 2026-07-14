from io import BytesIO
from zipfile import ZipFile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from apps.core.validators import validate_uploaded_image, validate_uploaded_xlsx


def make_image(name="test.png", size=(10, 10), fmt="PNG", payload_size=None):
    data = BytesIO()
    Image.new("RGB", size, color="red").save(data, format=fmt)
    content = data.getvalue()
    if payload_size:
        content = content + (b"0" * payload_size)
    return SimpleUploadedFile(name, content, content_type="image/png")


def make_xlsx(name="test.xlsx", extra=b""):
    data = BytesIO()
    with ZipFile(data, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types></Types>")
        archive.writestr("xl/workbook.xml", "<workbook></workbook>")
    return SimpleUploadedFile(name, data.getvalue() + extra, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


class UploadValidatorTests(SimpleTestCase):
    def test_valid_image_accepted(self):
        validate_uploaded_image(make_image())

    def test_corrupt_and_executable_renamed_images_rejected(self):
        with self.assertRaises(ValidationError):
            validate_uploaded_image(SimpleUploadedFile("bad.png", b"not an image", content_type="image/png"))
        with self.assertRaises(ValidationError):
            validate_uploaded_image(SimpleUploadedFile("evil.jpg", b"MZ" + b"0" * 100, content_type="image/jpeg"))

    def test_oversized_image_rejected(self):
        with self.assertRaises(ValidationError):
            validate_uploaded_image(make_image(payload_size=5 * 1024 * 1024))

    def test_valid_xlsx_accepted(self):
        validate_uploaded_xlsx(make_xlsx())

    def test_invalid_empty_and_oversized_xlsx_rejected(self):
        for upload in [
            SimpleUploadedFile("evil.xlsx", b"MZ" + b"0" * 100),
            SimpleUploadedFile("empty.xlsx", b""),
            make_xlsx(extra=b"0" * (5 * 1024 * 1024)),
        ]:
            with self.assertRaises(ValidationError):
                validate_uploaded_xlsx(upload)
