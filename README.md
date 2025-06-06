# API de Détection d'Allergies Alimentaires 🍎⚕️

Une API REST complète développée en Flask pour le suivi alimentaire et la détection intelligente d'allergies alimentaires basée sur l'analyse des corrélations entre la consommation d'aliments et l'apparition de symptômes.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Technologies utilisées](#technologies-utilisées)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Endpoints API](#endpoints-api)
- [Analyse des allergies](#analyse-des-allergies)
- [Gestion des images](#gestion-des-images)
- [Tests](#tests)
- [Contribution](#contribution)
- [Licence](#licence)

## ✨ Fonctionnalités

### 🔹 Gestion des utilisateurs
- Création, modification, suppression d'utilisateurs
- Profils personnalisés avec historique complet

### 🔹 Base de données d'aliments
- CRUD complet pour la gestion des aliments
- Informations nutritionnelles détaillées
- Gestion des ingrédients et allergènes courants
- Catégorisation et recherche avancée

### 🔹 Suivi alimentaire
- Enregistrement des repas avec quantités
- Association d'images aux repas
- Historique détaillé de la consommation

### 🔹 Gestion des symptômes
- Enregistrement des symptômes avec niveaux de sévérité (1-10)
- Documentation photographique des réactions
- Horodatage précis

### 🔹 Analyse intelligente d'allergies
- **Algorithme de corrélation temporelle** : Analyse les liens entre consommation et symptômes
- **Fenêtre d'analyse configurable** : 2-48h après consommation
- **Scoring de risque** : Calcul de pourcentages de risque pour chaque aliment
- **Détection de patterns** : Identification automatique d'allergies potentielles
- **Système d'alertes** : Niveaux FAIBLE/MODÉRÉ/ÉLEVÉ

### 🔹 Gestion d'images optimisée
- Stockage en base de données (BLOB)
- Optimisation automatique (redimensionnement, compression)
- Support multi-formats (JPEG, PNG, GIF, WebP)
- Accès par UUID sécurisé

### 🔹 Dashboard et statistiques
- Vue d'ensemble personnalisée par utilisateur
- Statistiques nutritionnelles (moyennes sur 7 jours)
- Graphiques et tendances de consommation
- Rapport d'analyse complet

## 🛠 Technologies utilisées

- **Backend** : Python 3.8+ avec Flask
- **Base de données** : SQLite avec SQLAlchemy ORM
- **Traitement d'images** : Pillow (PIL)
- **Parsing de dates** : python-dateutil
- **API REST** : Flask-RESTful patterns
- **Stockage** : Base64 et BLOB pour les images

## 📦 Installation

### Prérequis

```bash
python >= 3.8
pip
```

### Installation rapide

1. **Cloner le projet**
```bash
git clone https://github.com/migos276/flask_ap_nutrition.git
cd flask_ap_nutrition
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install flask flask-sqlalchemy pillow python-dateutil
```

4. **Lancer l'application**
```bash
python app.py
```

L'API sera accessible sur `http://localhost:5000`

## ⚙️ Configuration

### Variables d'environnement

```bash
export FLASK_ENV=development          # Mode développement
export FLASK_DEBUG=True              # Mode debug
export DATABASE_URL=sqlite:///allergie_detection.db  # Base de données
```

### Configuration de l'analyseur

```python
# Dans la classe AnalyseurAllergies
fenetre_temporelle_min = 2   # Heures minimum après repas
fenetre_temporelle_max = 48  # Heures maximum après repas
seuil_alerte = 30           # Pourcentage pour alerte ÉLEVÉ
```

## 🚀 Utilisation REQUETES POSTMAN 

### Démarrage rapide

1. **Créer un utilisateur**
  -POST http://localhost:5000/api/utilisateurs 
  -Body 
  -raw
    {"nom": "Jean Dupont",
     "email": "jean@example.com"
     }

2. **Ajouter des aliments à la base**
  
   POST http://localhost:5000/api/aliments
  '{
    "nom": "Fromage de chèvre",
    "ingredients": ["lait de chèvre", "ferments"],
    "allergenes_courants": ["lactose", "caséine"],
    "calories_pour_100g": 364,
    "categorie": "Produits laitiers"
  }'
  Certains options dans ce POST sont optionnel car un utilisateur peut ne pas connaitre les allergenes courant dans une nourriture ou bien la cotegorie de la nourriture 

1. **Enregistrer un repas**

 POST http://localhost:5000/api/repas
  {
    "utilisateur_id": 1,
    "aliments": [
      {"nom": "Fromage de chèvre", "quantite": 50}
    ],
    "description": "Salade de chèvre au déjeuner"
  }'

1. **Signaler un symptôme**
 POST http://localhost:5000/api/symptomes 
 Body 
 raw
  {
    "utilisateur_id": 1,
    "type_symptome": "Maux de ventre",
    "severite": 6,
    "description": "Douleurs abdominales 3h après le repas"
  }

1. **Obtenir l'analyse d'allergies**

 http://localhost:5000/api/analyse/1
```

## 📡 Endpoints API

### 👤 Utilisateurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/utilisateurs` | Créer un utilisateur |
| GET | `/api/utilisateurs/{id}` | Obtenir un utilisateur |
| PUT | `/api/utilisateurs/{id}` | Modifier un utilisateur |
| DELETE | `/api/utilisateurs/{id}` | Supprimer un utilisateur |

### 🥕 Aliments

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/aliments` | Créer un aliment |
| GET | `/api/aliments` | Lister avec pagination |
| GET | `/api/aliments/{id}` | Obtenir un aliment |
| PUT | `/api/aliments/{id}` | Modifier un aliment |
| DELETE | `/api/aliments/{id}` | Supprimer un aliment |
| GET | `/api/aliments/categories` | Lister les catégories |
| GET | `/api/aliments/recherche?q={terme}` | Recherche avancée |

### 🍽️ Repas

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/repas` | Enregistrer un repas |
| GET | `/api/repas/{utilisateur_id}` | Lister les repas |

### 🤒 Symptômes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/symptomes` | Signaler un symptôme |
| GET | `/api/symptomes/{utilisateur_id}` | Lister les symptômes |

### 📸 Images

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/images` | Uploader une image |
| GET | `/api/images/{id}` | Info image |
| GET | `/api/images/{id}/blob` | Télécharger image |
| GET | `/api/images/uuid/{uuid}` | Image par UUID |
| GET | `/api/images/{id}/base64` | Image en base64 |
| DELETE | `/api/images/{id}` | Supprimer image |

### 📊 Analyse et Dashboard

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/analyse/{utilisateur_id}` | Rapport complet d'analyse |
| GET | `/api/score-risque/{utilisateur_id}/{aliment}` | Score pour un aliment |
| GET | `/api/dashboard/{utilisateur_id}` | Dashboard utilisateur |

### 🔧 Utilitaires

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | État de l'API |
| GET | `/api/stats` | Statistiques globales |

## 🧠 Analyse des allergies

### Algorithme de détection

L'algorithme analyse les corrélations temporelles entre :
- **Consommation d'aliments** (avec quantités)
- **Apparition de symptômes** (avec sévérité)

### Fenêtre d'analyse

```
Repas → [2h-48h] → Symptômes éventuels
```

### Calcul du score de risque

```python
score_risque = (nombre_symptomes_après_consommation / nombre_total_consommations) × 100
```

### Niveaux d'alerte

- **🔴 ÉLEVÉ** : Score ≥ 30% → Évitement recommandé
- **🟡 MODÉRÉ** : Score ≥ 15% → Surveillance accrue
- **🟢 FAIBLE** : Score < 15% → Pas d'inquiétude particulière

### Exemple de rapport

```json
{
  "statistiques": {
    "total_repas": 45,
    "total_symptomes": 12,
    "periode_analyse": "30 derniers jours"
  },
  "aliments_suspects": [
    {
      "aliment": "Lait entier",
      "score_risque": 75.0,
      "niveau_alerte": "ÉLEVÉ"
    },
    {
      "aliment": "Œuf de poule",
      "score_risque": 25.0,
      "niveau_alerte": "MODÉRÉ"
    }
  ],
  "recommandations": [
    "Évitez temporairement les aliments suivants : Lait entier",
    "Consultez un allergologue pour des tests spécifiques"
  ]
}
```

## 📱 Gestion des images

### Fonctionnalités

- **Stockage optimisé** : Compression automatique et redimensionnement
- **Formats supportés** : JPEG, PNG, GIF, WebP
- **Taille limite** : Redimensionnement automatique à 1920x1080 max
- **Métadonnées** : Extraction des dimensions, taille, type MIME

### Upload d'image
POST http://localhost:5000/api/images
  {
    "nom_fichier": "reaction_allergique.jpg",
    "donnees_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABg...",
    "type_mime": "image/jpeg",
    "utilisateur_id": 1,
    "symptome_id": 5
  }

### Accès aux images

- **Par ID** : `/api/images/123/blob`
- **Par UUID** : `/api/images/uuid/abc-123-def`
- **En base64** : `/api/images/123/base64`

## 🧪 Tests

### Tests manuels avec curl

```bash
# Test de santé de l'API
curl http://localhost:5000/api/health

# Test des statistiques
curl http://localhost:5000/api/stats

# Test dashboard utilisateur
curl http://localhost:5000/api/dashboard/1
```

### Données de test

L'application s'initialise automatiquement avec des aliments de base :
- Lait entier
- Œuf de poule  
- Pain de blé complet
- Arachides grillées
- Pomme
- Saumon atlantique

## 📊 Exemple de workflow complet

1. **Créer utilisateur** → Obtenir ID
2. **Enregistrer repas** → Avec photos éventuelles
3. **Signaler symptômes** → Avec niveau de sévérité
4. **Répéter** sur plusieurs jours/semaines
5. **Analyser** → Obtenir rapport automatique
6. **Consulter dashboard** → Vue d'ensemble

## 🔒 Sécurité

- Validation des données d'entrée
- Gestion d'erreurs robuste
- Images optimisées automatiquement
- UUID pour accès sécurisé aux images

## 🚧 Améliorations futures

- [ ] Authentification JWT
- [ ] API rate limiting
- [ ] Export de données (PDF, CSV)
- [ ] Notifications push
- [ ] Machine Learning avancé
- [ ] Intégration bases nutritionnelles
- [ ] Interface web complète

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Créer une issue GitHub
- Email : tchemoumiguel@gmail.com

# Requêtes Postman - Gestion de Buffet

## 1. Créer un nouveau buffet

**Méthode :** `POST`  
**URL :** `http://localhost:5000/api/buffets`  
**Headers :**
```
Content-Type: application/json
```

**Body (raw JSON) :**
```json
{
  "utilisateur_id": 1,
  "nom_evenement": "Anniversaire de Marie",
  "date_evenement": "2025-07-15T18:00:00",
  "nombre_invites": 25,
  "budget_total": 300.00,
  "type_evenement": "anniversaire",
  "notes": "Thème tropical, éviter les fruits de mer",
  "statut": "planification"
}
```

---

## 2. Obtenir tous les buffets d'un utilisateur

**Méthode :** `GET`  
**URL :** `http://localhost:5000/api/buffets/1`  
**Headers :** Aucun header spécifique requis

---

## 3. Ajouter un plat au buffet

**Méthode :** `POST`  
**URL :** `http://localhost:5000/api/buffets/1/plats`  
**Headers :**
```
Content-Type: application/json
```

**Body (raw JSON) :**
```json
{
  "nom_plat": "Salade de quinoa aux légumes",
  "categorie": "entree",
  "quantite_par_personne": 150,
  "cout_unitaire": 3.50,
  "allergenes": ["gluten"],
  "ingredients": [
    {
      "nom": "quinoa",
      "quantite": 50
    },
    {
      "nom": "tomates cerises",
      "quantite": 30
    },
    {
      "nom": "concombre",
      "quantite": 40
    }
  ],
  "instructions_preparation": "Cuire le quinoa, couper les légumes, mélanger avec vinaigrette",
  "temps_preparation": 45,
  "difficulte": 2,
  "notes": "Peut être préparé la veille"
}
```

**Exemple avec un plat principal :**
```json
{
  "nom_plat": "Poulet aux herbes de Provence",
  "categorie": "plat_principal",
  "quantite_par_personne": 200,
  "cout_unitaire": 8.00,
  "allergenes": [],
  "ingredients": [
    {
      "nom": "blanc de poulet",
      "quantite": 180
    },
    {
      "nom": "herbes de Provence",
      "quantite": 5
    },
    {
      "nom": "huile d'olive",
      "quantite": 10
    }
  ],
  "instructions_preparation": "Mariner le poulet 2h, cuire au four 180°C pendant 25 min",
  "temps_preparation": 30,
  "difficulte": 3,
  "notes": "Servir chaud"
}
```

---

## 4. Obtenir les détails complets d'un buffet

**Méthode :** `GET`  
**URL :** `http://localhost:5000/api/buffets/1/details`  
**Headers :** Aucun header spécifique requis

---

## 5. Calculer les quantités totales nécessaires

**Méthode :** `GET`  
**URL :** `http://localhost:5000/api/buffets/1/quantites`  
**Headers :** Aucun header spécifique requis

---

## 6. Générer un planning de préparation

**Méthode :** `GET`  
**URL :** `http://localhost:5000/api/buffets/1/planning`  
**Headers :** Aucun header spécifique requis

---

## Exemples de réponses attendues

### Réponse création de buffet (201 Created)
```json
{
  "id": 1,
  "utilisateur_id": 1,
  "nom_evenement": "Anniversaire de Marie",
  "date_evenement": "2025-07-15T18:00:00",
  "nombre_invites": 25,
  "budget_total": 300.0,
  "type_evenement": "anniversaire",
  "statut": "planification",
  "date_creation": "2025-06-05T14:30:00"
}
```

### Réponse liste des buffets (200 OK)
```json
[
  {
    "id": 1,
    "nom_evenement": "Anniversaire de Marie",
    "date_evenement": "2025-07-15T18:00:00",
    "nombre_invites": 25,
    "budget_total": 300.0,
    "type_evenement": "anniversaire",
    "statut": "planification",
    "nombre_plats": 3,
    "date_creation": "2025-06-05T14:30:00"
  }
]
```

---

## Cas d'erreur à tester

### Création de buffet sans champs requis
**Body :**
```json
{
  "nom_evenement": "Test"
}
```
**Réponse attendue (400 Bad Request) :**
```json
{
  "erreur": "Champs requis: ['utilisateur_id', 'nom_evenement', 'date_evenement', 'nombre_invites']"
}
```

### Ajout de plat avec catégorie invalide
**Body :**
```json
{
  "nom_plat": "Test",
  "categorie": "categorie_inexistante"
}
```
**Réponse attendue (400 Bad Request) :**
```json
{
  "erreur": "categorie doit être un de: ['entree', 'plat_principal', 'dessert', 'boisson', 'accompagnement']"
}
```

---

## Notes importantes

1. **Remplacez les IDs** dans les URLs par les IDs réels retournés par vos requêtes
2. **Ajustez l'URL de base** selon votre configuration (localhost:5000 par défaut)
3. **Les catégories valides** sont : `entree`, `plat_principal`, `dessert`, `boisson`, `accompagnement`
4. **Format de date** : ISO 8601 (YYYY-MM-DDTHH:MM:SS)
5. **Testez d'abord** la création d'un buffet avant d'ajouter des plats

## Ordre de test recommandé

1. Créer un buffet
2. Ajouter plusieurs plats (différentes catégories)
3. Obtenir les détails du buffet
4. Calculer les quantités
5. Générer le planning
6. Lister les buffets de l'utilisateur


pour tous probleme de conversion de l'image en base64 utiliser cette fonction python pour convertir votre image en bas64 

import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = "image/jpeg"  # ou png, gif, etc.
        return f"data:{mime_type};base64,{encoded}"

# Utilisation
base64_string = image_to_base64("mon_image.jpg")
print(base64_string)
https://www.youtube.com/watch?v=Zzjn_Jz-A2E