import os

from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def extract_text_from_docx(file_path):
    doc = Document(file_path)

    text = "\n".join(
        paragraph.text for paragraph in doc.paragraphs
    )

    return text.strip()


def extract_resume_text(file_path):
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension == ".docx":
        return extract_text_from_docx(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: '{extension}'. "
            "Please upload a .pdf or .docx file."
        )


if __name__ == "__main__":
    test_file = input(
        "Enter the path to a resume file (.pdf or .docx): "
    ).strip('"')

    if not os.path.exists(test_file):
        print(f"ERROR: File not found at: {test_file}")
        exit()

    try:
        extracted_text = extract_resume_text(test_file)

        print("\n--- EXTRACTED TEXT (first 500 characters) ---\n")
        print(extracted_text[:500])

        print(
            f"\n--- Total characters extracted: "
            f"{len(extracted_text)} ---"
        )

    except Exception as e:
        print(f"ERROR while extracting text: {e}")