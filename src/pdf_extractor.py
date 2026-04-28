import fitz  # PyMuPDF
import pdfplumber
import os


def extract_text_pymupdf(pdf_path):
    """
    PyMuPDF se text extract karta hai.
    Fast hai, basic resumes ke liye best.
    """
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"PyMuPDF error: {e}")
    return text.strip()


def extract_text_pdfplumber(pdf_path):
    """
    pdfplumber se text extract karta hai.
    Tables aur complex layouts ke liye better.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber error: {e}")
    return text.strip()


def extract_with_layout(pdf_path):
    """
    Layout-aware extraction — har element ki
    position bhi save karta hai (top, left coordinates).
    Helpful for understanding resume structure.
    """
    elements = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                words = page.extract_words()
                for word in words:
                    elements.append({
                        "page": page_num + 1,
                        "text": word["text"],
                        "x0": round(word["x0"], 2),      # left position
                        "top": round(word["top"], 2),     # top position
                        "x1": round(word["x1"], 2),
                        "bottom": round(word["bottom"], 2)
                    })
    except Exception as e:
        print(f"Layout extraction error: {e}")
    return elements


def extract_resume(pdf_path):
    """
    Main function — dono methods try karta hai,
    jo better result de woh return karta hai.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ File nahi mili: {pdf_path}")
        return None

    print(f"📄 Processing: {os.path.basename(pdf_path)}")

    # Pehle PyMuPDF try karo
    text_pymupdf = extract_text_pymupdf(pdf_path)

    # Phir pdfplumber try karo
    text_pdfplumber = extract_text_pdfplumber(pdf_path)

    # Jo zyada text deta hai woh use karo
    if len(text_pymupdf) >= len(text_pdfplumber):
        final_text = text_pymupdf
        method_used = "PyMuPDF"
    else:
        final_text = text_pdfplumber
        method_used = "pdfplumber"

    print(f"✅ Extracted {len(final_text)} characters using {method_used}")

    return {
        "file_name": os.path.basename(pdf_path),
        "file_path": pdf_path,
        "raw_text": final_text,
        "word_count": len(final_text.split()),
        "method_used": method_used
    }


def extract_all_resumes(folder_path):
    """
    Ek poore folder ke saare PDFs process karta hai.
    """
    results = []

    if not os.path.exists(folder_path):
        print(f"❌ Folder nahi mila: {folder_path}")
        return results

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

    if not pdf_files:
        print("⚠️ Koi PDF nahi mila folder mein!")
        return results

    print(f"\n📁 {len(pdf_files)} PDFs mile — processing shuru...\n")

    for pdf_file in pdf_files:
        full_path = os.path.join(folder_path, pdf_file)
        result = extract_resume(full_path)
        if result:
            results.append(result)

    print(f"\n✅ Total {len(results)} resumes successfully extracted!\n")
    return results


# ── TEST ──
if __name__ == "__main__":
    import sys

    # Single PDF test
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = extract_resume(pdf_path)
        if result:
            print("\n--- Extracted Text (first 500 chars) ---")
            print(result["raw_text"][:500])
            print(f"\nWord count: {result['word_count']}")
    else:
        # Folder test
        folder = "data/resumes"
        results = extract_all_resumes(folder)
        if results:
            print("--- First Resume Preview ---")
            print(results[0]["raw_text"][:500])