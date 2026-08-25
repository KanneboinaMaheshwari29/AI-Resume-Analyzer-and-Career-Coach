import fitz

from app import (
    allowed_file,
    extract_pdf_text
)


def create_test_pdf():

    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        """
        Alex Morgan

        Professional Summary
        Computer Science graduate interested in Data Science.

        Skills
        Python, SQL, Machine Learning

        Education
        Bachelor of Technology in Computer Science.

        Projects
        Created a machine learning classification project.
        """
    )

    pdf_bytes = document.tobytes()

    document.close()

    return pdf_bytes


def test_pdf_extension():

    assert allowed_file("resume.pdf") is True
    assert allowed_file("resume.PDF") is True
    assert allowed_file("resume.docx") is False
    assert allowed_file("resume.txt") is False


def test_pdf_text_extraction():

    pdf_bytes = create_test_pdf()

    result = extract_pdf_text(pdf_bytes)

    assert result["success"] is True
    assert result["pageCount"] == 1
    assert "Alex Morgan" in result["text"]
    assert "Python" in result["text"]


def test_invalid_pdf():

    result = extract_pdf_text(
        b"This is not a real PDF file."
    )

    assert result["success"] is False