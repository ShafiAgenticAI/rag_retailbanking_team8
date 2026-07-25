import requests

SERVER = "http://127.0.0.1:8000"


def ask_compliance_engine(question, input_json=None):

    payload = {"question": question, "input_json": input_json}

    response = requests.post(f"{SERVER}/api/v1/query", json=payload)

    response.raise_for_status()

    return response.json()


def ingest_pdf(pdf_file):

    files = {"file": (pdf_file.name, pdf_file, "application/pdf")}

    response = requests.post(f"{SERVER}/upload/pdf", files=files)

    response.raise_for_status()

    return response.json()
