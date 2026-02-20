import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Brazilian Coffee PDF API",
    description="Serves PDF files from the knowledge base",
    version="1.0.0",
)

# Allow any origin so the frontend (wherever deployed) can link to PDFs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

PDF_DIR = Path(__file__).resolve().parent / "pdfs"


@app.get("/")
async def root():
    return {"status": "healthy", "service": "Brazilian Coffee PDF API"}


@app.get("/pdfs/{filename}")
async def serve_pdf(filename: str):
    """Serve a PDF file from the pdfs directory."""
    # Prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    pdf_path = PDF_DIR / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    logger.info(f"Serving PDF: {filename}")
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
