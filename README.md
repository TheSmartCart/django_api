# SmartCart API — Django REST Framework

![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.16.0-red?style=for-the-badge&logo=django)
![CI/CD](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

Ce dépôt contient le backend API de l'application **SmartCart**, développé avec Django 5.2 et Django REST Framework.

---

## Sommaire

- [1. Prérequis et Installation](#1-prérequis-et-installation)
  - [Installation de Python](#installation-de-python)
  - [Installation et Configuration de Visual Studio Code](#installation-et-configuration-de-visual-studio-code)
  - [Clonage du Projet](#clonage-du-projet)
  - [Création et Activation de l'Environnement Virtuel](#création-et-activation-de-lenvironnement-virtuel)
  - [Installation des Dépendances](#installation-des-dépendances)
- [2. Lancer le Projet en Mode Développeur](#2-lancer-le-projet-en-mode-développeur)
  - [Migrations de la Base de Données](#migrations-de-la-base-de-données)
  - [Création d'un Superutilisateur (Admin)](#création-dun-superutilisateur-admin)
  - [Démarrage du Serveur de Développement](#démarrage-du-serveur-de-développement)
  - [Exécution des Tests et Couverture de Code](#exécution-des-tests-et-couverture-de-code)
  - [Documentation Interactive de l'API (Swagger / ReDoc)](#documentation-interactive-de-lapi-swagger--redoc)
- [3. Déploiement Automatique (CI/CD)](#3-déploiement-automatique-cicd)
  - [Fonctionnement du Pipeline GitHub Actions](#fonctionnement-du-pipeline-github-actions)
  - [Configuration des Secrets GitHub](#configuration-des-secrets-github)

---

## 1. Prérequis et Installation

### Ce qu'il faut savoir

Pour toutes les commandes python, `python`est utilisé pour widows mais il faut modifier `python` par `python3`pour macOS.

### Installation de Python

Le projet utilise **Python 3.11**.
- **macOS** : `brew install python@3.11`
- **Windows** : Téléchargez l'installateur sur [python.org](https://www.python.org/downloads/) (n'oubliez pas de cocher *"Add Python to PATH"*).

Vérifiez l'installation avec :
```bash
python --version
```

---

### Installation et Configuration de Visual Studio Code

1. Téléchargez et installez **[Visual Studio Code](https://code.visualstudio.com/)**.
2. Installez les extensions VS Code recommandées pour Django & Python :
   - **Python** (`ms-python.python`) — Support complet du langage.
   - **Pylance** (`ms-python.vscode-pylance`) — Analyse statique et autocomplétion performante.
   - **Ruff** ou **Black Formatter** — Formatage automatique du code.

---

### Clonage du Projet

```bash
git clone <URL_DU_DEPOT_GIT>
cd django_api
```

---

### Création et Activation de l'Environnement Virtuel

Créez un environnement virtuel pour le projet :

- **macOS / Linux** :
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows** :
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  source venv/Scripts/activate
  ```

*(Une fois activé, votre terminal affichera `(venv)` au début de la ligne de commande).*

---

### Installation des Dépendances

Installez toutes les bibliothèques requises définies dans `requirements.txt` :

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Principales dépendances installées :
- `Django 5.2` : Framework Web backend.
- `djangorestframework 3.16.0` : Extension REST API.
- `djangorestframework-simplejwt 5.5.0` : Authentification basée sur les jetons JWT.
- `drf-spectacular` : Génération automatique des schémas OpenAPI 3.0 (Swagger & ReDoc).
- `pillow` : Gestion et traitement des fichiers images (ex: photos de profil, produits).
- `coverage 7.15.0` : Mesure de la couverture des tests unitaires.

---

## 2. Lancer le Projet en Mode Développeur

### Migrations de la Base de Données

Appliquez les migrations pour créer la structure de la base de données locale (`db.sqlite3`) :

```bash
python manage.py migrate
```

Si vous modifiez des modèles (`models.py`) au cours du développement :
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Création d'un Superutilisateur (Admin)

Pour accéder au panneau d'administration de Django (`/admin/`), créez un compte administrateur :

```bash
python manage.py createsuperuser
```
Suivez les instructions à l'écran.

---

### Démarrage du Serveur de Développement

Lancez le serveur local sur `http://127.0.0.1:8000/` :

```bash
python manage.py runserver
```

L'API est maintenant opérationnelle en mode développeur !

---

### Exécution des Tests et Couverture de Code

Le projet est configuré avec un seuil minimal de couverture de code de **80%** (exigé lors du déploiement CI/CD).

- **Lancer les tests unitaires** :
  ```bash
  python manage.py test
  ```

- **Lancer les tests avec rapport de couverture (Coverage)** :
  ```bash
  coverage run manage.py test
  coverage report --fail-under=80
  ```

- **Générer un rapport HTML détaillé de couverture** :
  ```bash
  coverage html
  ```
  Ouvrez htmlcov/index.html dans votre navigateur

---

### Documentation Interactive de l'API (Swagger / ReDoc)

La documentation est générée automatiquement et accessible lorsque le serveur tourne :

- **Swagger UI** : `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc** : `http://127.0.0.1:8000/api/schema/redoc/`
- **Schéma OpenAPI (JSON)** : `http://127.0.0.1:8000/api/schema/`
- **Interface d'administration Django** : `http://127.0.0.1:8000/admin/`

---

## 3. Déploiement Automatique (CI/CD)

Le projet intègre un pipeline complet d'intégration et de déploiement continus (CI/CD) géré par **GitHub Actions** (`.github/workflows/deploy.yml`).

```
Push sur `main`
       │
       ▼
┌──────────────┐
│  Job: test   │  ──► Exécution des tests Python 3.11 & vérification du coverage (>= 80%)
└──────┬───────┘
       │ (si succès)
       ▼
┌──────────────┐
│ Job: deploy  │  ──► Connexion SSH au VPS, git pull, venv, migrations, collectstatic & restart gunicorn
└──────┬───────┘
       │ (si succès)
       ▼
┌──────────────┐
│  Job: tag    │  ──► Extraction de API_VERSION et création automatique d'un Tag Git (ex: v1.0.0)
└──────────────┘
```

---

### Fonctionnement du Pipeline GitHub Actions

Chaque commit ou merge vers la branche principale **`main`** déclenche automatiquement le pipeline découpé en **3 Jobs** :

#### 1. Etape `test` (Unit tests)
- **Environnement** : `ubuntu-latest` avec Python 3.11.
- **Actions** :
  1. Récupération du code source (`actions/checkout@v4`).
  2. Installation des dépendances depuis `requirements.txt`.
  3. Exécution de la suite de tests unitaires via `coverage run manage.py test`.
  4. Vérification que la couverture globale de code est supérieure ou égale à **80%** (`coverage report --fail-under=80`). En cas d'échec, le pipeline s'arrête immédiatement et bloque le déploiement.

#### 2. Etape `deploy` (Deployment on a VPS)
- Exécutée uniquement si l'étape `test` a réussi.
- Connexion sécurisée au serveur VPS distant via SSH (`appleboy/ssh-action@v1.2.0`).
- **Commandes exécutées sur le VPS** :
  ```bash
  cd /var/www/django_api/django_api
  git fetch origin main
  git reset --hard origin/main
  source /var/www/django_api/venv/bin/activate
  pip install -r requirements.txt
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  sudo systemctl restart smartcart
  ```

#### 3. Etape `tag` (Creating the Tag)
- Exécutée uniquement si le déploiement a réussi.
- Récupère automatiquement le numéro de version `API_VERSION` configuré dans `smartcart/settings.py`.
- Crée et pousse automatiquement un tag Git sur le dépôt.

---

### Configuration des Secrets GitHub

Pour que le déploiement automatique sur le VPS fonctionne, les secrets suivants doivent être configurés dans le dépôt GitHub dans **Settings > Secrets and variables > Actions** :

| Nom du Secret | Description | Exemple / Valeur |
| :--- | :--- | :--- |
| `VPS_HOST` | Adresse IP ou nom de domaine du serveur VPS | `192.0.2.1` ou `api.smartcart.com` |
| `VPS_USER` | Nom de l'utilisateur SSH sur le VPS | `ubuntu` ou `root` |
| `VPS_SSH_KEY` | Clé SSH privée autorisée à se connecter au VPS | `-----BEGIN OPENSSH PRIVATE KEY----- ...` |

---

## Résumé des Commandes Utiles

| Action | Commande |
| :--- | :--- |
| **Activer le venv** | `source venv/bin/activate` |
| **Activer le venv (Windows)** | `.\venv\Scripts\Activate.ps1` |
| **Installer les dépendances** | `pip install -r requirements.txt` |
| **Appliquer les migrations** | `python manage.py migrate` |
| **Lancer le serveur dev** | `python manage.py runserver` |
| **Créer un administrateur** | `python manage.py createsuperuser` |
| **Lancer les tests avec couverture** | `coverage run manage.py test && coverage report --fail-under=80` |
