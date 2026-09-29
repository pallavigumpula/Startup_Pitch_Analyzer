from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {"txt", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_storage):
    filename = file_storage.filename

    if not filename or not allowed_file(filename):
        raise ValueError("Unsupported file type. Please upload a .txt or .pdf file.")

    ext = filename.rsplit(".", 1)[1].lower()

    if ext == "txt":
        return file_storage.read().decode("utf-8", errors="ignore")

    try:
        reader = PdfReader(file_storage)
        pages = [page.extract_text() or "" for page in reader.pages]
    except PdfReadError:
        logger.exception(f"Failed to read PDF file: {filename}")
        raise ValueError("Couldn't read that PDF file. It may be corrupted or password-protected.")

    text = "\n".join(pages)

    if not text.strip():
        raise ValueError("Couldn't extract any text from that PDF.")

    return text
