import os

SRC = r"C:\Users\prett\Pretel-OS\buckets\business\projects\marketing-os\docs"
OUT = r"C:\Users\prett\Documents\pretel-os\buckets\business\projects\marketing-os\_corpus_extracted"

def extract_pdf(path):
    try:
        import fitz  # pymupdf - best text quality
        doc = fitz.open(path)
        t = "\n".join(p.get_text() for p in doc)
        doc.close()
        if t.strip():
            return t, "pymupdf"
    except Exception:
        pass
    try:
        import pypdf
        r = pypdf.PdfReader(path)
        return "\n".join((pg.extract_text() or "") for pg in r.pages), "pypdf"
    except Exception:
        return None, None

def extract_docx(path):
    try:
        import docx
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs), "docx"
    except Exception:
        return None, None

count = 0; total = 0; fail = []; engines = {}
for root, dirs, files in os.walk(SRC):
    for f in files:
        ext = f.lower().rsplit(".", 1)[-1] if "." in f else ""
        if ext not in ("pdf", "docx"):
            continue
        src = os.path.join(root, f)
        text, eng = (extract_pdf if ext == "pdf" else extract_docx)(src)
        rel = os.path.relpath(src, SRC)
        out = os.path.join(OUT, rel + ".txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if text and text.strip():
            with open(out, "w", encoding="utf-8") as w:
                w.write(text)
            count += 1; total += len(text); engines[eng] = engines.get(eng, 0) + 1
        else:
            fail.append(rel)

print("EXTRACTED:", count, "files | total chars:", total)
print("engines:", engines)
print("FAILURES:", len(fail))
for x in fail:
    print("  FAIL", x)
