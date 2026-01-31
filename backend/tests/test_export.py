import asyncio
from pathlib import Path
from app.services.export.pdf import generate_pdf
from app.services.export.docx import generate_docx
from app.services.export.txt import generate_txt

async def test_all_exports():
    print("🧪 Démarrage du test des exports...")
    
    # Données fictives pour le test
    test_data = {
        "title": "Test de Génération SmartScribe",
        "content": (
            "# Introduction\nCeci est un test.\n\n"
            "## Section Importance\n> ⚠️ Ceci est une alerte rouge.\n\n"
            "- Point 1\n- Point 2\n"
            "\nNote terminée."
        )
    }

    formats = {
        "pdf": generate_pdf,
        "docx": generate_docx,
        "txt": generate_txt
    }

    for fmt, func in formats.items():
        try:
            print(f"⏳ Test export {fmt}...")
            path, size = await func(test_data, filename=f"test_file.{fmt}")
            print(f"✅ Succès {fmt} : {path} ({size} octets)")
        except Exception as e:
            print(f"❌ Échec {fmt} : {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_all_exports())