def test_imports():
    errors = []
    
    try:
        import fitz  # pymupdf
        print("✅ PyMuPDF OK")
    except Exception as exc:
        errors.append(f"❌ PyMuPDF failed: {exc}")

    try:
        import pdfplumber
        print("✅ pdfplumber OK")
    except Exception as exc:
        errors.append(f"❌ pdfplumber failed: {exc}")

    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy OK")
    except Exception as exc:
        errors.append(f"❌ spaCy failed: {exc}")

    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence-Transformers OK")
    except Exception as exc:
        errors.append(f"❌ Sentence-Transformers failed: {exc}")

    try:
        import streamlit
        print("✅ Streamlit OK")
    except Exception as exc:
        errors.append(f"❌ Streamlit failed: {exc}")

    try:
        from langdetect import detect
        print("✅ LangDetect OK")
    except Exception as exc:
        errors.append(f"❌ LangDetect failed: {exc}")

    if errors:
        print("\n⚠️ These failed:")
        for e in errors:
            print(e)
    else:
        print("\n🎉 Sab kuch ready hai! Step 2 pe jao.")

test_imports()