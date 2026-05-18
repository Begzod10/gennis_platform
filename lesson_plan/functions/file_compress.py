"""
Size-cap + lossless compression for lesson-plan uploads.

If a file is over the limit, try a format-aware lossless rewrite:
- .docx / .xlsx  → re-zip the OOXML container with max DEFLATE
- .pdf           → rewrite content streams with pypdf / PyPDF2 (if installed)
- .txt           → collapse trailing whitespace and runs of blank lines

If the result still exceeds the limit, raise FileTooLargeError so the
view returns 413.
"""
from __future__ import annotations

import io
import re
import zipfile
from typing import Optional

from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile


MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB hard cap for lesson-plan files


class FileTooLargeError(Exception):
    """File is over the limit and cannot be compressed below it."""


def _wrap(name: str, data: bytes, content_type: Optional[str]) -> InMemoryUploadedFile:
    bio = io.BytesIO(data)
    bio.seek(0)
    return InMemoryUploadedFile(
        file=bio,
        field_name="file",
        name=name,
        content_type=content_type or "application/octet-stream",
        size=len(data),
        charset=None,
    )


def _read_all(uploaded: UploadedFile) -> bytes:
    try:
        uploaded.seek(0)
    except Exception:
        pass
    return uploaded.read()


def _recompress_ooxml(data: bytes) -> bytes:
    """Re-zip a .docx / .xlsx container with maximum DEFLATE compression."""
    src = io.BytesIO(data)
    dst = io.BytesIO()
    with zipfile.ZipFile(src, mode="r") as zin, zipfile.ZipFile(
        dst, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zout:
        for item in zin.infolist():
            zout.writestr(item, zin.read(item.filename))
    return dst.getvalue()


def _compress_txt(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="replace")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.encode("utf-8")


def _compress_pdf(data: bytes) -> Optional[bytes]:
    try:
        from pypdf import PdfReader, PdfWriter  # type: ignore
    except Exception:
        try:
            from PyPDF2 import PdfReader, PdfWriter  # type: ignore
        except Exception:
            return None

    reader = PdfReader(io.BytesIO(data))
    writer = PdfWriter()
    for page in reader.pages:
        try:
            page.compress_content_streams()
        except Exception:
            pass
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def compress_to_limit(
    uploaded: UploadedFile, max_bytes: int = MAX_UPLOAD_BYTES
) -> UploadedFile:
    """
    Return the upload untouched if it is already within max_bytes.
    Otherwise try a format-aware lossless compression and return a new
    InMemoryUploadedFile. Raises FileTooLargeError if it still doesn't fit.
    """
    size = getattr(uploaded, "size", None)
    if size is not None and size <= max_bytes:
        return uploaded

    name = uploaded.name or ""
    ext = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
    content_type = getattr(uploaded, "content_type", None)

    data = _read_all(uploaded)
    if len(data) <= max_bytes:
        return _wrap(name, data, content_type)

    try:
        if ext in (".docx", ".xlsx"):
            compressed = _recompress_ooxml(data)
        elif ext == ".txt":
            compressed = _compress_txt(data)
        elif ext == ".pdf":
            compressed = _compress_pdf(data)
        else:
            compressed = None
    except zipfile.BadZipFile:
        compressed = None
    except Exception:
        compressed = None

    if compressed is None or len(compressed) > max_bytes:
        raise FileTooLargeError(
            f"File is {len(data) / (1024 * 1024):.2f} MB; limit is "
            f"{max_bytes / (1024 * 1024):.0f} MB and it could not be compressed below the limit."
        )

    return _wrap(name, compressed, content_type)
