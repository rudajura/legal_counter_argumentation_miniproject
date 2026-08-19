import os

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.anthropic_client import analyze_weaknesses, generate_counterarguments  # noqa: E402
from app.pdf_extract import extract_text_from_pdf  # noqa: E402
from app.schemas import AnalyzeResponse  # noqa: E402

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def get_client() -> Anthropic:
    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    fact_pattern: str = Form(...),
    argument: str = Form(...),
    files: list[UploadFile] = File(default=[]),
):
    extracted_texts = []
    for uploaded_file in files:
        content = await uploaded_file.read()
        extracted_texts.append(extract_text_from_pdf(content))

    full_fact_pattern = fact_pattern
    if extracted_texts:
        full_fact_pattern += "\n\nPřílohy:\n" + "\n\n".join(extracted_texts)

    client = get_client()
    weaknesses = analyze_weaknesses(client, full_fact_pattern, argument)
    result = generate_counterarguments(
        client, weaknesses, full_fact_pattern, argument
    )
    return result
