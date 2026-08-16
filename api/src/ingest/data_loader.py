import re
from pathlib import Path

from langchain_core.documents import Document

from .pdf_parser import parse_resume

# Full pattern - English + German + all variations
SECTION_HEADERS = [
    # Summary / Profile
    r"summary", r"professional summary", r"executive summary", r"career summary",
    r"profile", r"professional profile", r"career profile", r"personal profile",
    r"objective", r"career objective", r"job objective",
    r"zusammenfassung", r"profil", r"berufliches profil", r"kurzprofil", r"karriereziel",

    # Skills
    r"skills", r"technical skills", r"key skills", r"core skills", r"key competencies",
    r"competencies", r"core competencies", r"areas of expertise", r"expertise",
    r"technical proficiencies", r"tech stack", r"technologies", r"technical expertise",
    r"fähigkeiten", r"kenntnisse", r"fachkenntnisse", r"technische fähigkeiten",
    r"technische kenntnisse", r"kompetenzen", r"kernkompetenzen", r"qualifikationen",
    r"fertigkeiten", r"edv-?kenntnisse",

    # Experience
    r"experience", r"work experience", r"professional experience", r"employment history",
    r"work history", r"career history", r"professional background", r"work",
    r"employment", r"professional experience",
    r"berufserfahrung", r"beruflicher werdegang", r"arbeitserfahrung", r"berufspraxis",
    r"berufslaufbahn", r"werdegang", r"beruflicher werdegang",

    # Education
    r"education", r"academic background", r"academic qualifications", r"educational background",
    r"academic history", r"qualifications",
    r"ausbildung", r"akademischer hintergrund", r"studium", r"schulbildung",
    r"akademische laufbahn", r"schulische laufbahn",

    # Projects
    r"projects", r"personal projects", r"academic projects", r"key projects", r"relevant projects",
    r"projekte", r"eigene projekte",

    # Certs / Awards / Others
    r"certifications", r"certificates", r"licenses", r"courses", r"training",
    r"zertifikate", r"zertifizierungen", r"bescheinigungen", r"weiterbildungen",
    r"achievements", r"accomplishments", r"awards", r"honors", r"auszeichnungen",
    r"publications", r"research", r"patents", r"publikationen",
    r"languages", r"language proficiency", r"sprachen", r"sprachkenntnisse",
    r"volunteer", r"volunteer experience", r"interests", r"hobbies", r"references"
]

# Build one big regex - this is what you asked for
section_pattern = r"(?im)^\s*(?:" + "|".join(SECTION_HEADERS) + r")\b.*$"
# Compiled version for splitting
SECTION_REGEX = re.compile(section_pattern, re.IGNORECASE | re.MULTILINE)

# For re.split() - keep the header as a delimiter
SPLIT_PATTERN = r"(?im)^\s*((?:" + "|".join(SECTION_HEADERS) + r")\b.*$)"

class DataLoader:
    def __init__(self, data_dir : Path):
        self.data_dir = data_dir
        if not self.data_dir.exists():
            raise ValueError("Data directory not found!")
        self._documents: list[Document] = self._load_docs()
    
    def _load_docs(self) -> list[Document]:
        docs: list[Document] = []
        for resume in list(self.data_dir.rglob("*.pdf")):
            doc = parse_resume(resume)
            doc.metadata['source'] = str(resume)
            docs.append(doc)
        return docs
    
    def split_documents(self):
        docs = self._load_docs()
        final_chunks = []

        for doc in docs:
            text = doc.page_content
            # Split while keeping headers
            parts = re.split(SPLIT_PATTERN, text)

            for i in range(1, len(parts), 2):
                header = parts[i].strip().lower()
                content = parts[i+1].strip() if i+1 < len(parts) else ""
                if len(content) < 30:
                    continue

                # Auto-detect type from header
                if any(k in header for k in ["skill", "tech", "fähig", "kenntnis"]):
                    ctype = "skills"
                elif any(k in header for k in ["erfahrung", "experience", "employment", "werdegang"]):
                    ctype = "experience"
                elif any(k in header for k in ["ausbildung", "education", "studium"]):
                    ctype = "education"
                elif "projekt" in header or "project" in header:
                    ctype = "projects"
                else:
                    ctype = "other"

                final_chunks.append(Document(
                    page_content=f"{header.upper()}: {content}",
                    metadata={**doc.metadata, "chunk_type": ctype}
                ))

        return final_chunks