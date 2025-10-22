from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


def _normalise(value: str) -> str:
    return value.strip().lower()


def _slugify(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    id: str
    filename: str
    title: str
    description: str | None = None

    @property
    def stem(self) -> str:
        return Path(self.filename).stem


DOCUMENTS: tuple[DocumentMetadata, ...] = (
    DocumentMetadata(
        id="fomc_statement",
        filename="01_fomc_statement_2025-09-17.html",
        title="FOMC Statement — September 17, 2025",
        description="Official statement outlining the Federal Reserve's policy decision and rationale.",
    ),
    DocumentMetadata(
        id="implementation_note",
        filename="02_implementation_note_2025-09-17.html",
        title="Implementation Note — September 17, 2025",
        description="Operational guidance on how the policy decision will be implemented across facilities.",
    ),
    DocumentMetadata(
        id="sep_tables_pdf",
        filename="03_sep_tables_2025-09-17.pdf",
        title="Summary of Economic Projections Tables (PDF)",
        description="PDF tables summarising participants' projections for key economic indicators.",
    ),
    DocumentMetadata(
        id="sep_tables_html",
        filename="04_sep_tables_2025-09-17.html",
        title="Summary of Economic Projections Tables (HTML)",
        description="HTML tables summarising participants' projections for key economic indicators.",
    ),
    DocumentMetadata(
        id="press_conference_transcript",
        filename="05_press_conference_transcript_2025-09-17.pdf",
        title="Press Conference Transcript — September 17, 2025",
        description="Chair Powell's press conference transcript following the September 2025 FOMC meeting.",
    ),
    DocumentMetadata(
        id="bls_cpi_august",
        filename="06_bls_cpi_2025-08.html",
        title="BLS Consumer Price Index — August 2025",
        description="Consumer Price Index report providing the latest inflation readings.",
    ),
    DocumentMetadata(
        id="bea_gdp_q2_second_estimate",
        filename="07_bea_gdp_q2_2025_second_estimate.pdf",
        title="BEA GDP Second Estimate — Q2 2025",
        description="Bureau of Economic Analysis second estimate of GDP for the second quarter of 2025.",
    ),
    DocumentMetadata(
        id="monetary_policy_report",
        filename="08_fed_mpr_2025-06.pdf",
        title="Monetary Policy Report — June 2025",
        description="Semiannual Monetary Policy Report submitted to Congress in June 2025.",
    ),
)
DOCUMENTS_BY_ID: dict[str, DocumentMetadata] = {doc.id: doc for doc in DOCUMENTS}

DOCUMENTS_BY_FILENAME: dict[str, DocumentMetadata] = {
    _normalise(doc.filename): doc for doc in DOCUMENTS
}

DOCUMENTS_BY_STEM: dict[str, DocumentMetadata] = {_normalise(doc.stem): doc for doc in DOCUMENTS}

DOCUMENTS_BY_SLUG: dict[str, DocumentMetadata] = {}
for document in DOCUMENTS:
    for candidate in {
        document.id,
        document.filename,
        document.stem,
        document.title,
        document.description or "",
    }:
        if candidate:
            DOCUMENTS_BY_SLUG.setdefault(_slugify(candidate), document)


def as_dicts(documents: Iterable[DocumentMetadata]) -> list[dict[str, str | None]]:
    return [asdict(document) for document in documents]


__all__ = [
    "DOCUMENTS",
    "DOCUMENTS_BY_FILENAME",
    "DOCUMENTS_BY_ID",
    "DOCUMENTS_BY_STEM",
    "DOCUMENTS_BY_SLUG",
    "DocumentMetadata",
    "as_dicts",
]
