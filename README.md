v# API de Détection d'Allergies et de Gestion Alimentaire

Cette API Flask permet de gérer les utilisateurs, les repas, les aliments, les plans alimentaires, les symptômes, les images (stockage en BLOB), ainsi que l'organisation de buffets pour événements. Elle inclut également des fonctionnalités d'analyse intelligente des allergies et de génération de rapports nutritionnels.

## Fonctionnalités principales

- **Gestion des utilisateurs** (CRUD)
- **Gestion des aliments** (CRUD, recherche, catégories)
- **Suivi des repas** (avec aliments, quantités, description)
- **Suivi des symptômes** (type, sévérité, date, description)
- **Gestion des images** (upload, récupération, suppression, association à un repas/symptôme/utilisateur)
- **Analyse intelligente des allergies** (détection de patterns, score de risque, rapport)
- **Plans alimentaires hebdomadaires** (création, consultation, ajout de repas planifiés)
- **Organisation de buffets** (création d'événements, ajout de plats, calcul de quantités/couts, planning)
- **Rapports nutritionnels** (statistiques globales et individuelles)
- **Statistiques globales et dashboard utilisateur**

---

## Démarrage rapide
1. **Lancer l'API**
   ```bash
   docker-composer up
   ```

   L'API sera accessible sur `http://localhost:5000`.

---

## Structure des endpoints principaux

| Ressource                 | Endpoint                                              | Méthode(s)      | Description                                                                 |
|---------------------------|------------------------------------------------------|-----------------|-----------------------------------------------------------------------------|
| Utilisateurs              | /api/utilisateurs                                    | POST, GET, PUT, DELETE | CRUD utilisateur                                                  |
| Aliments                  | /api/aliments                                        | POST, GET, PUT, DELETE | CRUD aliments, recherche, filtres, catégories                    |
| Repas                     | /api/repas                                           | POST             | Ajouter un repas                                                           |
| Repas utilisateur         | /api/repas/<utilisateur_id>                          | GET              | Lister les repas d'un utilisateur                                           |
| Symptômes                 | /api/symptomes                                       | POST             | Ajouter un symptôme                                                        |
| Symptômes utilisateur     | /api/symptomes/<utilisateur_id>                      | GET              | Lister les symptômes d'un utilisateur                                      |
| Images                    | /api/images                                          | POST, DELETE     | Ajouter ou supprimer une image                                             |
| Images utilisateur        | /api/images/utilisateur/<utilisateur_id>             | GET              | Lister les images d'un utilisateur                                         |
| Analyse allergies         | /api/analyse/<utilisateur_id>                        | GET              | Générer un rapport d'analyse d'allergies                                   |
| Score risque aliment      | /api/score-risque/<utilisateur_id>/<aliment>         | GET              | Calculer le risque pour un aliment                                         |
| Dashboard utilisateur     | /api/dashboard/<utilisateur_id>                      | GET              | Récupérer toutes les stats d'un utilisateur                                |
| Plans alimentaires        | /api/plans-alimentaires                              | POST             | Créer un plan alimentaire                                                  |
| Plans utilisateur         | /api/plans-alimentaires/<utilisateur_id>             | GET              | Lister les plans d'un utilisateur                                          |
| Repas planifiés           | /api/plans-alimentaires/<plan_id>/repas              | POST             | Ajouter un repas planifié à un plan                                        |
| Planning semaine          | /api/plans-alimentaires/<plan_id>/semaine            | GET              | Voir le planning hebdomadaire d'un plan                                    |
| Liste de courses          | /api/plans-alimentaires/<plan_id>/liste-courses      | GET              | Générer une liste de courses pour un plan                                  |
| Buffets                   | /api/buffets                                         | POST             | Créer un nouvel événement buffet                                           |
| Buffets utilisateur       | /api/buffets/<utilisateur_id>                        | GET              | Obtenir les buffets d'un utilisateur                                       |
| Plats buffet              | /api/buffets/<buffet_id>/plats                      | POST             | Ajouter un plat à un buffet                                                |
| Détails buffet            | /api/buffets/<buffet_id>/details                     | GET              | Voir tous les détails d'un buffet                                          |
| Quantités buffet          | /api/buffets/<buffet_id>/quantites                   | GET              | Calculer les quantités totales nécessaires                                 |
| Planning préparation      | /api/buffets/<buffet_id>/planning                    | GET              | Générer un planning de préparation                                         |
| Statistiques globales     | /api/stats                                           | GET              | Statistiques globales de l'application                                     |
| Healthcheck               | /api/health                                          | GET              | Vérifier l'état de l'API                                                   |

---

## Simulation d'utilisation avec Postman

### 1. Création d'un utilisateur

- **Requête**
  - Méthode : `POST`
  - URL : `http://localhost:5000/api/utilisateurs`
  - Body (JSON):
    ```json
    {
      "nom": "Jean Dupont",
      "email": "jean.dupont@email.com"
    }
    ```
- **Réponse attendue**
    ```json
    {
      "id": 1,
      "nom": "Jean Dupont",
      "email": "jean.dupont@email.com",
      "date_creation": "2025-06-10T20:00:00.000000"
    }
    ```

### 2. Ajout d'un aliment

- **Requête**
  - Méthode : `POST`
  - URL : `http://localhost:5000/api/aliments`
  - Body (JSON):
    ```json
    {
      "nom": "Riz Basmati",
      "ingredients": ["riz"],
      "allergenes_courants": [],
      "calories_pour_100g": 130,
      "proteines_pour_100g": 2.5,
      "glucides_pour_100g": 28.0,
      "lipides_pour_100g": 0.3,
      "fibres_pour_100g": 0.4,
      "categorie": "Féculents"
    }
    ```
- **Réponse attendue**
    ```json
    {
      "id": 2,
      "nom": "Riz Basmati",
      ...
    }
    ```

### 3. Ajout d'un repas

- **Requête**
  - Méthode : `POST`
  - URL : `http://localhost:5000/api/repas`
  - Body (JSON):
    ```json
    {
      "utilisateur_id": 1,
      "aliments": [
        { "nom": "Riz Basmati", "quantite": 150 },
        { "nom": "Poulet rôti", "quantite": 100 }
      ],
      "description": "Déjeuner du midi"
    }
    ```
- **Réponse attendue**
    ```json
    {
      "id": 1,
      "utilisateur_id": 1,
      "date_heure": "...",
      "aliments": [
        { "nom": "Riz Basmati", "quantite": 150 },
        { "nom": "Poulet rôti", "quantite": 100 }
      ],
      "description": "Déjeuner du midi"
    }
    ```

### 4. Ajout d'un symptôme

- **Requête**
  - Méthode : `POST`
  - URL : `http://localhost:5000/api/symptomes`
  - Body (JSON):
    ```json
    {
      "utilisateur_id": 1,
      "type_symptome": "Éruption cutanée",
      "severite": 6,
      "description": "Rougeur sur la peau après le repas de midi"
    }
    ```
- **Réponse attendue**
    ```json
    {
      "id": 1,
      "utilisateur_id": 1,
      "type_symptome": "Éruption cutanée",
      "severite": 6,
      ...
    }
    ```

### 5. Analyse intelligente des allergies

- **Requête**
  - Méthode : `GET`
  - URL : `http://localhost:5000/api/analyse/1`
- **Réponse attendue**
    ```json
    {
      "statistiques": { ... },
      "aliments_suspects": [ ... ],
      "recommandations": [ ... ],
      "date_rapport": "..."
    }
    ```

### 6. Ajout d'une image (base64)

- **Requête**
- pour obtenir le code de l'image en base 64 utiliser le code html dans le projet principal 
  - Méthode : `POST`
  - URL : `http://localhost:5000/api/images`
  - Body (JSON):
    ```json
    {
      "nom_fichier": "symptome_photo.jpg",
      "donnees_base64": "<base64 de l'image>",
      "type_mime": "image/jpeg",
      "utilisateur_id": 1,
      "symptome_id": 1
    }
    ```
- **Réponse attendue**
    ```json
    {
      "id": 1,
      "uuid": "...",
      "nom_fichier": "symptome_photo.jpg",
      ...
    }
    ```

### 7. Génération d'un plan alimentaire

- **Requête**
  - Méthode : `POST`
  - URL : `http://localhost:5000/api/plans-alimentaires`
  - Body (JSON):
    ```json
    {
      "utilisateur_id": 1,
      "nom": "Semaine équilibrée",
      "semaine_debut": "2025-06-09"
    }
    ```
- **Réponse attendue**
    ```json
    {
      "id": 1,
      "utilisateur_id": 1,
      "nom": "Semaine équilibrée",
      ...
    }
    ```

---

## Tester avec Postman

1. Ouvrez Postman.
2. Créez une nouvelle Collection, ajoutez les requêtes ci-dessus avec la méthode et le body appropriés.
3. Lancez les tests en adaptant les IDs selon le retour des réponses précédentes si nécessaire.

---

## Notes

- Toutes les routes acceptent et renvoient du JSON.
- Les erreurs renvoient un champ `"erreur"` dans la réponse.
- Certains endpoints nécessitent des IDs existants (utilisateur, aliment, etc.).
- Pour les images, encodez le fichier en base64 avant l'envoi.

---



# Simulation complète d'utilisation de l'API avec Postman

Ce scénario simule un utilisateur fictif "Sophie Martin" qui va tester toutes les fonctionnalités principales de l'API, étape par étape, via des requêtes Postman.  
Pour chaque opération, les paramètres, le body et la réponse attendue sont précisés.

---

## 1. Création d'un utilisateur

**POST** `/api/utilisateurs`

```json
{
  "nom": "Sophie Martin",
  "email": "sophie.martin@email.com"
}
```
**Réponse attendue**
```json
{
  "id": 1,
  "nom": "Sophie Martin",
  "email": "sophie.martin@email.com",
  "date_creation": "2025-06-10T21:11:00.000000"
}
```

---

## 2. Ajout d'aliments

**POST** `/api/aliments`

```json
{
  "nom": "Poulet rôti",
  "ingredients": ["poulet", "épices"],
  "allergenes_courants": [],
  "calories_pour_100g": 165,
  "proteines_pour_100g": 31,
  "glucides_pour_100g": 0,
  "lipides_pour_100g": 3.6,
  "fibres_pour_100g": 0,
  "categorie": "Viandes"
}
```

**POST** `/api/aliments`

```json
{
  "nom": "Riz Basmati",
  "ingredients": ["riz"],
  "allergenes_courants": [],
  "calories_pour_100g": 130,
  "proteines_pour_100g": 2.5,
  "glucides_pour_100g": 28.0,
  "lipides_pour_100g": 0.3,
  "fibres_pour_100g": 0.4,
  "categorie": "Féculents"
}
```

---

## 3. Création et consultation de repas

**POST** `/api/repas`
```json
{
  "utilisateur_id": 1,
  "aliments": [
    { "nom": "Poulet rôti", "quantite": 120 },
    { "nom": "Riz Basmati", "quantite": 150 }
  ],
  "description": "Déjeuner équilibré"
}
```

**GET** `/api/repas/1`

---

## 4. Création et consultation de symptômes

**POST** `/api/symptomes`
```json
{
  "utilisateur_id": 1,
  "type_symptome": "Maux de ventre",
  "severite": 5,
  "description": "Douleurs peu après le déjeuner"
}
```

**GET** `/api/symptomes/1`

---

## 5. Ajout d'une image (exemple d'image en base64)

**POST** `/api/images`

```json
{
  "nom_fichier": "douleur.jpg",
  "donnees_base64": "<base64 de votre image>",
  "type_mime": "image/jpeg",
  "utilisateur_id": 1,
  "symptome_id": 1
}
```

**GET** `/api/images/utilisateur/1`

---

## 6. Analyse intelligente des allergies

**GET** `/api/analyse/1`

---

## 7. Calcul du score de risque pour un aliment

**GET** `/api/score-risque/1/Poulet rôti`

---

## 8. Statistiques/nutrition - Dashboard utilisateur

**GET** `/api/dashboard/1`

---

## 9. Création d'un plan alimentaire hebdomadaire

**POST** `/api/plans-alimentaires`
```json
{
  "utilisateur_id": 1,
  "nom": "Plan semaine healthy",
  "semaine_debut": "2025-06-09"
}
```

**GET** `/api/plans-alimentaires/1`

---

## 10. Ajout de repas planifiés au plan

**POST** `/api/plans-alimentaires/1/repas`
```json
{
  "jour_semaine": 0,
  "type_repas": "dejeuner",
  "aliments_planifies": [
    { "nom": "Poulet rôti", "quantite": 100 },
    { "nom": "Riz Basmati", "quantite": 120 }
  ],
  "calories_estimees": 250
}
```

---

## 11. Consultation du planning de la semaine

**GET** `/api/plans-alimentaires/1/semaine`

---

## 12. Génération de la liste de courses

**GET** `/api/plans-alimentaires/1/liste-courses`

---

## 13. Création d'un buffet événementiel

**POST** `/api/buffets`
```json
{
  "utilisateur_id": 1,
  "nom_evenement": "Anniversaire de Sophie",
  "date_evenement": "2025-06-15T19:00:00",
  "nombre_invites": 10,
  "budget_total": 100,
  "type_evenement": "anniversaire"
}
```

**GET** `/api/buffets/1`

---

## 14. Ajout d'un plat au buffet

**POST** `/api/buffets/1/plats`
```json
{
  "nom_plat": "Poulet rôti",
  "categorie": "plat_principal",
  "quantite_par_personne": 120,
  "cout_unitaire": 2.5,
  "allergenes": [],
  "ingredients": [
    { "nom": "Poulet", "quantite": 120 }
  ],
  "instructions_preparation": "Faire rôtir le poulet avec des épices",
  "temps_preparation": 60,
  "difficulte": 2
}
```

---

## 15. Détails et planning du buffet

**GET** `/api/buffets/1/details`

**GET** `/api/buffets/1/quantites`

**GET** `/api/buffets/1/planning`

---

## 16. Statistiques globales & healthcheck

**GET** `/api/health`

**GET** `/api/stats`

---

# Notes pour les tests Postman

- Pensez à adapter les IDs (`utilisateur_id`, `plan_id`, `buffet_id`, etc.) selon les réponses reçues aux opérations précédentes.
- Pour uploader une image, utilisez un outil ou script pour obtenir la chaîne base64 à partir d'une image réelle.
- Ajoutez chaque requête à une Collection pour pouvoir rejouer le scénario complet.
- Analysez les réponses à chaque étape pour vérifier la cohérence des données.

---
## Licence

Projet open-source à but éducatif.