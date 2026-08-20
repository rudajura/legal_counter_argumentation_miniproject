import asyncio
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI

load_dotenv()

from app.openai_client import (  # noqa: E402
    analyze_weaknesses,
    extract_fact_pattern,
    generate_counterarguments,
)
from app.pdf_extract import extract_text_from_pdf  # noqa: E402
from app.schemas import (  # noqa: E402
    AnalyzeResponse,
    CounterargumentsRequest,
    ExtractFactPatternResponse,
    WeaknessesResponse,
)
from app.sse import format_sse_event  # noqa: E402

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


def get_client() -> OpenAI:
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@app.post("/api/analyze/weaknesses", response_model=WeaknessesResponse)
async def analyze_weaknesses_endpoint(
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
    return {"weaknesses": weaknesses, "full_fact_pattern": full_fact_pattern}


@app.post("/api/extract/fact-pattern", response_model=ExtractFactPatternResponse)
async def extract_fact_pattern_endpoint(files: list[UploadFile] = File(...)):
    extracted_texts = []
    for uploaded_file in files:
        content = await uploaded_file.read()
        extracted_texts.append(extract_text_from_pdf(content))
    document_text = "\n\n".join(extracted_texts)

    client = get_client()
    fact_pattern = extract_fact_pattern(client, document_text)
    return {"fact_pattern": fact_pattern}


@app.post("/api/analyze/counterarguments", response_model=AnalyzeResponse)
async def generate_counterarguments_endpoint(body: CounterargumentsRequest):
    client = get_client()
    weaknesses = [w.model_dump() for w in body.weaknesses]
    result = generate_counterarguments(
        client, weaknesses, body.full_fact_pattern, body.argument
    )
    return result


@app.post("/api/analyze/stream")
async def analyze_stream_endpoint(
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

    async def event_generator():
        client = get_client()
        try:
            weaknesses = await asyncio.to_thread(
                analyze_weaknesses, client, full_fact_pattern, argument
            )
        except Exception as exc:
            yield format_sse_event(
                "error", {"message": str(exc), "phase": "weaknesses"}
            )
            return

        yield format_sse_event(
            "weaknesses",
            {"weaknesses": weaknesses, "full_fact_pattern": full_fact_pattern},
        )

        try:
            result = await asyncio.to_thread(
                generate_counterarguments,
                client,
                weaknesses,
                full_fact_pattern,
                argument,
            )
        except Exception as exc:
            yield format_sse_event(
                "error", {"message": str(exc), "phase": "counterarguments"}
            )
            return

        yield format_sse_event("result", result)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
