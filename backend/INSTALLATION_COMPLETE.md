# 📦 Guide d'installation complet - SmartScribe Backend

## 🎯 Vue d'ensemble

Ce guide vous permettra d'installer toutes les dépendances nécessaires pour faire fonctionner l'application SmartScribe.

---

## 📋 Table des matières

1. [Prérequis système](#prérequis-système)
2. [Installation Python et environnement virtuel](#installation-python-et-environnement-virtuel)
3. [Dépendances Python](#dépendances-python)
4. [Dépendances système (Windows)](#dépendances-système-windows)
5. [Configuration des services externes](#configuration-des-services-externes)
6. [Installation des outils IA](#installation-des-outils-ia)
7. [Configuration de l'environnement](#configuration-de-lenvironnement)
8. [Vérification de l'installation](#vérification-de-linstallation)

---

## 🔧 Prérequis système

### Système d'exploitation
- **Windows 10/11** (ou Linux/Mac)
- **Python 3.12** ou supérieur
- **Git** (pour cloner le projet si nécessaire)

### Espace disque requis
- Minimum **10 GB** d'espace libre (pour les modèles IA et dépendances)

### RAM recommandée
- Minimum **8 GB** (16 GB recommandé pour les modèles IA locaux)

---

## 🐍 Installation Python et environnement virtuel

### 1. Vérifier Python
```bash
python --version
# Doit afficher Python 3.12.x ou supérieur
```

### 2. Créer un environnement virtuel
```bash
cd backend
python -m venv venv
```

### 3. Activer l'environnement virtuel

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

---

## 📦 Dépendances Python

### Installation via requirements.txt

Créez un fichier `requirements.txt` complet avec toutes les dépendances :

```bash
pip install -r requirements.txt
```

### Liste complète des dépendances Python

#### 🔹 Framework et API
```
fastapi==0.128.0
uvicorn[standard]==0.40.0
python-multipart==0.0.21
pydantic==2.12.5
pydantic-settings==2.12.0
pydantic-core==2.41.5
```

#### 🔹 Base de données
```
motor==3.7.1          # MongoDB async driver
pymongo==4.16.0       # MongoDB driver
```

#### 🔹 Cache et tâches asynchrones
```
redis==7.1.0
celery==5.6.2
kombu==5.6.2
billiard==4.2.4
```

#### 🔹 Authentification et sécurité
```
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
cryptography==46.0.3
```

#### 🔹 Traitement audio/vidéo
```
librosa==0.11.0       # Analyse audio
soundfile==0.13.1     # Lecture/écriture audio
pydub==0.25.1         # Manipulation audio
noisereduce==3.0.3    # Réduction de bruit
soxr==1.0.0           # Resampling audio
opencv-python==4.8.1  # Traitement vidéo (cv2)
opencv-contrib-python==4.8.1  # Extensions OpenCV
```

#### 🔹 OCR et traitement d'images
```
pytesseract==0.3.10   # OCR (nécessite Tesseract installé)
Pillow==12.1.0        # Manipulation d'images
paddlepaddle==2.5.0   # Optionnel: pour PaddleOCR
paddleocr==2.7.0      # Optionnel: OCR alternatif
```

#### 🔹 Export de documents
```
reportlab==4.4.7      # Génération PDF
python-docx==1.2.0    # Génération DOCX
```

#### 🔹 IA et Machine Learning
```
openai-whisper==20250625  # Transcription vocale
torch==2.9.1          # PyTorch (pour modèles IA)
transformers==4.35.0  # Modèles HuggingFace
unsloth[colab-new]==2024.8  # Fine-tuning rapide
accelerate==0.25.0    # Accélération training
bitsandbytes==0.41.3  # Quantification 4-bit
trl==0.7.4            # Training RLHF
peft==0.7.1           # Parameter-Efficient Fine-Tuning
```

#### 🔹 Clients IA Cloud
```
groq==0.4.1           # Client Groq API
openai==1.12.0        # Client OpenAI (optionnel)
anthropic==0.18.1     # Client Anthropic Claude (optionnel)
```

#### 🔹 Utilitaires
```
python-dotenv==1.2.1  # Gestion variables d'environnement
requests==2.32.5      # Requêtes HTTP
aiohttp==3.9.1        # Requêtes HTTP async
email-validator==2.3.0
```

#### 🔹 Développement et tests
```
pytest==9.0.2
pytest-asyncio==0.21.1
httpx==0.25.2         # Client HTTP pour tests
```

#### 🔹 Logging et monitoring
```
colorama==0.4.6       # Couleurs dans les logs
```

---

## 🖥️ Dépendances système (Windows)

### 1. FFmpeg (Traitement audio/vidéo)

**Téléchargement:**
- Téléchargez depuis: https://ffmpeg.org/download.html
- Ou via Chocolatey: `choco install ffmpeg`
- Ou via winget: `winget install ffmpeg`

**Vérification:**
```bash
ffmpeg -version
```

**Ajouter au PATH:**
Ajoutez le chemin d'installation de FFmpeg à votre variable d'environnement PATH.

### 2. Tesseract OCR

**Téléchargement:**
- Téléchargez depuis: https://github.com/UB-Mannheim/tesseract/wiki
- Installez la version Windows avec support français

**Installation:**
1. Téléchargez `tesseract-ocr-w64-setup-5.x.x.exe`
2. Installez dans `C:\Program Files\Tesseract-OCR`
3. Ajoutez au PATH: `C:\Program Files\Tesseract-OCR`

**Vérification:**
```bash
tesseract --version
```

**Langues supplémentaires:**
```bash
# Téléchargez les fichiers de langue français depuis:
# https://github.com/tesseract-ocr/tessdata
# Placez-les dans: C:\Program Files\Tesseract-OCR\tessdata
```

### 3. Visual C++ Redistributable

**Nécessaire pour certaines bibliothèques Python:**
- Téléchargez depuis: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Installez le package "Microsoft Visual C++ 2015-2022 Redistributable"

---

## ☁️ Configuration des services externes

### 1. MongoDB

**Option A: Installation locale**
```bash
# Via Chocolatey
choco install mongodb

# Ou téléchargez depuis: https://www.mongodb.com/try/download/community
```

**Option B: MongoDB Atlas (Cloud)**
1. Créez un compte sur https://www.mongodb.com/cloud/atlas
2. Créez un cluster gratuit
3. Récupérez la chaîne de connexion

### 2. Redis

**Option A: Installation locale**
```bash
# Via Chocolatey
choco install redis-64

# Ou téléchargez depuis: https://github.com/microsoftarchive/redis/releases
```

**Option B: Redis Cloud**
1. Créez un compte sur https://redis.com/try-free/
2. Créez une base de données
3. Récupérez l'URL de connexion

### 3. Services IA Cloud (Optionnels)

#### Groq API
1. Créez un compte sur https://console.groq.com
2. Générez une clé API
3. Ajoutez-la dans `.env`

#### OpenAI API (Optionnel)
1. Créez un compte sur https://platform.openai.com
2. Générez une clé API
3. Ajoutez-la dans `.env`

---

## 🤖 Installation des outils IA

### 1. Ollama (Modèles IA locaux)

**Installation:**
```bash
# Téléchargez depuis: https://ollama.ai/download
# Ou via winget
winget install Ollama.Ollama
```

**Vérification:**
```bash
ollama --version
```

**Télécharger des modèles:**
```bash
# Modèle recommandé pour le français
ollama pull llama3.2:3b
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

### 2. PyTorch avec CUDA (Optionnel - pour GPU)

**Si vous avez une carte NVIDIA:**
```bash
# Vérifiez votre version CUDA
nvidia-smi

# Installez PyTorch avec CUDA (exemple pour CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Sans GPU (CPU uniquement):**
```bash
pip install torch torchvision torchaudio
```

---

## ⚙️ Configuration de l'environnement

### 1. Créer le fichier `.env`

Créez un fichier `.env` à la racine du dossier `backend`:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB_NAME=smartscribe

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API Keys (IA Cloud)
GROQ_API_KEY=votre_cle_groq_ici
OPENAI_API_KEY=votre_cle_openai_ici  # Optionnel

# Chemins
UPLOAD_PATH=./uploads
STORAGE_PATH=./storage
EXPORTS_PATH=./exports
LOGS_PATH=./logs

# Sécurité
SECRET_KEY=votre_secret_key_tres_longue_et_aleatoire_ici
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Configuration serveur
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Tesseract (Windows)
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# Ollama (si utilisé)
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Générer une SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## ✅ Vérification de l'installation

### 1. Script de vérification

Créez un fichier `check_installation.py`:

```python
import sys

def check_imports():
    """Vérifie que toutes les dépendances sont installées"""
    imports = [
        'fastapi', 'uvicorn', 'motor', 'pymongo',
        'redis', 'celery', 'bcrypt', 'jose',
        'librosa', 'cv2', 'pytesseract', 'PIL',
        'reportlab', 'docx', 'torch', 'transformers',
        'groq', 'openai', 'whisper'
    ]
    
    missing = []
    for module in imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MANQUANT")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️ Modules manquants: {', '.join(missing)}")
        return False
    else:
        print("\n✅ Toutes les dépendances sont installées!")
        return True

if __name__ == "__main__":
    check_imports()
```

**Exécuter:**
```bash
python check_installation.py
```

### 2. Vérifier les outils système

```bash
# FFmpeg
ffmpeg -version

# Tesseract
tesseract --version

# MongoDB (si installé localement)
mongod --version

# Redis (si installé localement)
redis-cli --version

# Ollama (si installé)
ollama --version
```

### 3. Tester la connexion MongoDB

```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_mongo():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connecté!")
    except Exception as e:
        print(f"❌ Erreur MongoDB: {e}")
    finally:
        client.close()

asyncio.run(test_mongo())
```

### 4. Tester la connexion Redis

```python
import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✅ Redis connecté!")
except Exception as e:
    print(f"❌ Erreur Redis: {e}")
```

---

## 🚀 Démarrage de l'application

### 1. Démarrer MongoDB (si local)
```bash
mongod
```

### 2. Démarrer Redis (si local)
```bash
redis-server
```

### 3. Démarrer Ollama (si utilisé)
```bash
ollama serve
```

### 4. Démarrer le worker Celery
```bash
celery -A app.core.celery_app worker --loglevel=info
```

### 5. Démarrer l'API FastAPI
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ou directement:
```bash
python -m app.main
```

---

## 📝 Notes importantes

### Problèmes courants

1. **Erreur Tesseract:**
   - Vérifiez que Tesseract est dans le PATH
   - Ou définissez `TESSERACT_CMD` dans `.env`

2. **Erreur FFmpeg:**
   - Vérifiez que FFmpeg est dans le PATH
   - Redémarrez le terminal après installation

3. **Erreur PyTorch/CUDA:**
   - Installez la version CPU si vous n'avez pas de GPU NVIDIA
   - Vérifiez la compatibilité CUDA

4. **Erreur MongoDB:**
   - Vérifiez que MongoDB est démarré
   - Vérifiez l'URL de connexion dans `.env`

5. **Erreur Redis:**
   - Vérifiez que Redis est démarré
   - Vérifiez l'URL de connexion dans `.env`

### Optimisations

- **Pour GPU NVIDIA:** Installez PyTorch avec CUDA pour accélérer les modèles IA
- **Pour CPU uniquement:** Utilisez des modèles quantifiés (4-bit) avec bitsandbytes
- **Pour production:** Utilisez MongoDB Atlas et Redis Cloud au lieu de services locaux

---

## 📚 Ressources supplémentaires

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Celery](https://docs.celeryproject.org/)
- [Documentation MongoDB](https://www.mongodb.com/docs/)
- [Documentation Redis](https://redis.io/docs/)
- [Documentation Ollama](https://ollama.ai/docs)
- [Documentation PyTorch](https://pytorch.org/docs/)

---

## ✅ Checklist finale

- [ ] Python 3.12+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Toutes les dépendances Python installées
- [ ] FFmpeg installé et dans le PATH
- [ ] Tesseract installé et dans le PATH
- [ ] MongoDB installé/configuré
- [ ] Redis installé/configuré
- [ ] Fichier `.env` créé et configuré
- [ ] Ollama installé (optionnel)
- [ ] PyTorch installé (optionnel)
- [ ] Tous les tests de vérification passés
- [ ] Application démarre sans erreur

---

**🎉 Félicitations! Votre environnement est maintenant prêt pour développer SmartScribe!**
