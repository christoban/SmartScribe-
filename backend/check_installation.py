"""
Script de vérification de l'installation
Vérifie que toutes les dépendances sont correctement installées
"""
import sys

def check_imports():
    """Vérifie que toutes les dépendances sont installées"""
    
    # Liste des modules à vérifier
    imports = {
        # Framework
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'websockets': 'WebSockets',
        
        # Validation
        'pydantic': 'Pydantic',
        'pydantic_settings': 'Pydantic Settings',
        
        # Base de données
        'motor': 'Motor (MongoDB async)',
        'pymongo': 'PyMongo',
        
        # Cache et tâches
        'redis': 'Redis',
        'celery': 'Celery',
        
        # Sécurité
        'jose': 'Python-JOSE',
        'passlib': 'Passlib',
        'bcrypt': 'Bcrypt',
        'cryptography': 'Cryptography',
        
        # Audio
        'librosa': 'Librosa',
        'soundfile': 'SoundFile',
        'pydub': 'PyDub',
        'noisereduce': 'NoiseReduce',
        'soxr': 'Soxr',
        
        # Vidéo/Images
        'cv2': 'OpenCV',
        'PIL': 'Pillow',
        'pytesseract': 'PyTesseract',
        
        # OCR (optionnel)
        'paddleocr': 'PaddleOCR (optionnel)',
        
        # Export
        'reportlab': 'ReportLab (PDF)',
        'docx': 'Python-DOCX',
        
        # IA Core
        'whisper': 'OpenAI Whisper',
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'accelerate': 'Accelerate',
        'bitsandbytes': 'BitsAndBytes',
        'trl': 'TRL',
        'peft': 'PEFT',
        
        # Clients IA
        'groq': 'Groq',
        'openai': 'OpenAI',
        
        # Utilitaires
        'dotenv': 'Python-Dotenv',
        'requests': 'Requests',
        'aiohttp': 'AioHTTP',
        'email_validator': 'Email Validator',
        
        # Numérique
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        
        # Tests
        'pytest': 'Pytest',
        'httpx': 'HTTPX',
        
        # Logging
        'colorama': 'Colorama',
    }
    
    print("🔍 Vérification des dépendances Python...\n")
    print("=" * 60)
    
    missing = []
    optional_missing = []
    
    for module, name in imports.items():
        try:
            # Gestion des imports spéciaux
            if module == 'cv2':
                import cv2
            elif module == 'PIL':
                from PIL import Image
            elif module == 'docx':
                import docx
            elif module == 'dotenv':
                import dotenv
            elif module == 'email_validator':
                import email_validator
            else:
                __import__(module)
            
            print(f"✅ {name:30} ({module})")
        except ImportError:
            if module in ['paddleocr', 'unsloth']:
                print(f"⚠️  {name:30} ({module}) - OPTIONNEL")
                optional_missing.append(module)
            else:
                print(f"❌ {name:30} ({module}) - MANQUANT")
                missing.append(module)
        except Exception as e:
            print(f"⚠️  {name:30} ({module}) - ERREUR: {str(e)[:50]}")
    
    print("=" * 60)
    
    # Résumé
    if missing:
        print(f"\n❌ {len(missing)} module(s) manquant(s):")
        for mod in missing:
            print(f"   - {mod}")
        print("\n💡 Installez-les avec: pip install -r requirements.txt")
        return False
    else:
        print(f"\n✅ Toutes les dépendances principales sont installées!")
        
        if optional_missing:
            print(f"\n⚠️  {len(optional_missing)} module(s) optionnel(s) manquant(s):")
            for mod in optional_missing:
                print(f"   - {mod}")
            print("   (Ces modules sont optionnels et ne sont pas requis pour le fonctionnement de base)")
        
        return True

def check_system_tools():
    """Vérifie les outils système"""
    import subprocess
    import shutil
    
    print("\n🔍 Vérification des outils système...\n")
    print("=" * 60)
    
    tools = {
        'ffmpeg': 'FFmpeg (traitement audio/vidéo)',
        'tesseract': 'Tesseract OCR',
        'mongod': 'MongoDB (optionnel si vous utilisez Atlas)',
        'redis-server': 'Redis (optionnel si vous utilisez Redis Cloud)',
        'ollama': 'Ollama (optionnel, pour modèles IA locaux)',
    }
    
    missing_tools = []
    
    for tool, name in tools.items():
        if shutil.which(tool):
            print(f"✅ {name:40} ({tool})")
        else:
            if tool in ['mongod', 'redis-server', 'ollama']:
                print(f"⚠️  {name:40} ({tool}) - OPTIONNEL")
            else:
                print(f"❌ {name:40} ({tool}) - MANQUANT")
                if tool not in ['mongod', 'redis-server', 'ollama']:
                    missing_tools.append(tool)
    
    print("=" * 60)
    
    if missing_tools:
        print(f"\n❌ {len(missing_tools)} outil(s) système manquant(s):")
        for tool in missing_tools:
            print(f"   - {tool}")
        print("\n💡 Consultez INSTALLATION_COMPLETE.md pour les instructions d'installation")
        return False
    else:
        print("\n✅ Tous les outils système requis sont installés!")
        return True

def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("  SmartScribe - Vérification de l'installation")
    print("=" * 60 + "\n")
    
    python_ok = check_imports()
    system_ok = check_system_tools()
    
    print("\n" + "=" * 60)
    if python_ok and system_ok:
        print("🎉 Tous les prérequis sont installés!")
        print("   Vous pouvez maintenant démarrer l'application.")
        return 0
    else:
        print("⚠️  Certains prérequis manquent.")
        print("   Consultez INSTALLATION_COMPLETE.md pour plus d'informations.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
