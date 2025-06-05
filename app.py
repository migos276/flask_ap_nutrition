from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import base64
import io
import os
from collections import defaultdict
import statistics
import json
from dateutil import parser
from PIL import Image as PILImage
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///allergie_detection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PlanAlimentaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    semaine_debut = db.Column(db.Date, nullable=False)  # Lundi de la semaine
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    repas_planifies = db.relationship('RepasPlanifie', backref='plan', lazy=True, cascade='all, delete-orphan')

class RepasPlanifie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan_alimentaire.id'), nullable=False)
    jour_semaine = db.Column(db.Integer, nullable=False)  # 0=Lundi, 6=Dimanche
    type_repas = db.Column(db.String(50), nullable=False)  # petit_dejeuner, dejeuner, diner, collation
    aliments_planifies = db.Column(db.Text, nullable=False)  # JSON des aliments
    calories_estimees = db.Column(db.Float)
    notes = db.Column(db.Text)

class Buffet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    nom_evenement = db.Column(db.String(200), nullable=False)
    date_evenement = db.Column(db.DateTime, nullable=False)
    nombre_invites = db.Column(db.Integer, nullable=False)
    budget_total = db.Column(db.Float)
    type_evenement = db.Column(db.String(100))  # mariage, anniversaire, etc.
    notes = db.Column(db.Text)
    statut = db.Column(db.String(50), default='planification')  # planification, confirme, termine
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    plats_buffet = db.relationship('PlatBuffet', backref='buffet', lazy=True, cascade='all, delete-orphan')

class PlatBuffet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buffet_id = db.Column(db.Integer, db.ForeignKey('buffet.id'), nullable=False)
    nom_plat = db.Column(db.String(200), nullable=False)
    categorie = db.Column(db.String(100))  # entree, plat_principal, dessert, boisson
    quantite_par_personne = db.Column(db.Float)  # en grammes ou unités
    cout_unitaire = db.Column(db.Float)
    allergenes = db.Column(db.Text)  # JSON des allergènes
    ingredients = db.Column(db.Text)  # JSON des ingrédients
    instructions_preparation = db.Column(db.Text)
    temps_preparation = db.Column(db.Integer)  # en minutes
    difficulte = db.Column(db.Integer)  # 1-5
    notes = db.Column(db.Text)
# Modèles de base de données
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    repas = db.relationship('Repas', backref='utilisateur', lazy=True, cascade='all, delete-orphan')
    symptomes = db.relationship('Symptome', backref='utilisateur', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('Image', backref='utilisateur', lazy=True, cascade='all, delete-orphan')
    plans_alimentaires = db.relationship('PlanAlimentaire', backref='utilisateur', lazy=True, cascade='all, delete-orphan')
    buffets = db.relationship('Buffet', backref='utilisateur', lazy=True, cascade='all, delete-orphan')



class Aliment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    ingredients = db.Column(db.Text)  # JSON string des ingrédients
    allergenes_courants = db.Column(db.Text)  # JSON string des allergènes
    calories_pour_100g = db.Column(db.Float)
    proteines_pour_100g = db.Column(db.Float)
    glucides_pour_100g = db.Column(db.Float)
    lipides_pour_100g = db.Column(db.Float)
    fibres_pour_100g = db.Column(db.Float)
    categorie = db.Column(db.String(50))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Repas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    date_heure = db.Column(db.DateTime, nullable=False)
    aliments = db.Column(db.Text, nullable=False)  # JSON string des aliments avec quantités
    description = db.Column(db.Text)
    
    # Relations
    images = db.relationship('Image', backref='repas', lazy=True, cascade='all, delete-orphan')
    
class Symptome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    date_heure = db.Column(db.DateTime, nullable=False)
    type_symptome = db.Column(db.String(100), nullable=False)
    severite = db.Column(db.Integer, nullable=False)  # 1-10
    description = db.Column(db.Text)
    
    # Relations
    images = db.relationship('Image', backref='symptome', lazy=True, cascade='all, delete-orphan')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    nom_fichier = db.Column(db.String(255), nullable=False)
    donnees_blob = db.Column(db.LargeBinary, nullable=False)  # Stockage en blob
    type_mime = db.Column(db.String(50), nullable=False)
    taille = db.Column(db.Integer)  # Taille en bytes
    largeur = db.Column(db.Integer)
    hauteur = db.Column(db.Integer)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    repas_id = db.Column(db.Integer, db.ForeignKey('repas.id'))
    symptome_id = db.Column(db.Integer, db.ForeignKey('symptome.id'))

# Classe pour l'analyse des allergies
class AnalyseurAllergies:
    def __init__(self):
        self.fenetre_temporelle_min = 2  # 2 heures
        self.fenetre_temporelle_max = 48  # 48 heures
        self.seuil_alerte = 30  # 30%
    
    def calculer_score_risque(self, utilisateur_id, aliment_nom):
        """Calcule le score de risque pour un aliment donné"""
        # Récupérer tous les repas contenant cet aliment
        repas_avec_aliment = []
        repas_utilisateur = Repas.query.filter_by(utilisateur_id=utilisateur_id).all()
        
        for repas in repas_utilisateur:
            try:
                aliments_repas = json.loads(repas.aliments)
                # Vérifier si l'aliment est présent (format: [{"nom": "aliment", "quantite": 100}])
                if isinstance(aliments_repas, list):
                    if any(aliment_nom.lower() in aliment.get('nom', '').lower() for aliment in aliments_repas):
                        repas_avec_aliment.append(repas)
                elif isinstance(aliments_repas, dict):
                    if any(aliment_nom.lower() in aliment.lower() for aliment in aliments_repas.keys()):
                        repas_avec_aliment.append(repas)
            except:
                continue
        
        if not repas_avec_aliment:
            return 0
        
        # Compter les symptômes après consommation
        symptomes_apres_consommation = 0
        
        for repas in repas_avec_aliment:
            symptomes = Symptome.query.filter_by(utilisateur_id=utilisateur_id).filter(
                Symptome.date_heure >= repas.date_heure + timedelta(hours=self.fenetre_temporelle_min),
                Symptome.date_heure <= repas.date_heure + timedelta(hours=self.fenetre_temporelle_max)
            ).all()
            
            if symptomes:
                symptomes_apres_consommation += 1
        
        # Calculer le score
        score = (symptomes_apres_consommation / len(repas_avec_aliment)) * 100
        return round(score, 2)
    
    def detecter_patterns(self, utilisateur_id):
        """Détecte les patterns d'allergies pour un utilisateur"""
        # Récupérer tous les aliments consommés
        aliments_uniques = set()
        repas_utilisateur = Repas.query.filter_by(utilisateur_id=utilisateur_id).all()
        
        for repas in repas_utilisateur:
            try:
                aliments_repas = json.loads(repas.aliments)
                if isinstance(aliments_repas, list):
                    aliments_uniques.update([aliment.get('nom', '') for aliment in aliments_repas])
                elif isinstance(aliments_repas, dict):
                    aliments_uniques.update(aliments_repas.keys())
            except:
                continue
        
        # Calculer les scores pour chaque aliment
        resultats = []
        for aliment in aliments_uniques:
            if aliment:  # Éviter les chaînes vides
                score = self.calculer_score_risque(utilisateur_id, aliment)
                if score > 0:
                    resultats.append({
                        'aliment': aliment,
                        'score_risque': score,
                        'niveau_alerte': 'ÉLEVÉ' if score >= self.seuil_alerte else 'MODÉRÉ' if score >= 15 else 'FAIBLE'
                    })
        
        # Trier par score décroissant
        resultats.sort(key=lambda x: x['score_risque'], reverse=True)
        return resultats
    
    def generer_rapport(self, utilisateur_id):
        """Génère un rapport complet d'analyse"""
        patterns = self.detecter_patterns(utilisateur_id)
        
        # Statistiques générales
        total_repas = Repas.query.filter_by(utilisateur_id=utilisateur_id).count()
        total_symptomes = Symptome.query.filter_by(utilisateur_id=utilisateur_id).count()
        
        # Recommandations
        recommandations = []
        aliments_suspects = [p for p in patterns if p['score_risque'] >= self.seuil_alerte]
        
        if aliments_suspects:
            recommandations.append("Évitez temporairement les aliments suivants : " + 
                                 ", ".join([a['aliment'] for a in aliments_suspects[:3]]))
            recommandations.append("Consultez un allergologue pour des tests spécifiques")
            recommandations.append("Tenez un journal détaillé de vos symptômes")
        else:
            recommandations.append("Aucun aliment suspect détecté avec un niveau de risque élevé")
            recommandations.append("Continuez à surveiller vos réactions alimentaires")
        
        return {
            'statistiques': {
                'total_repas': total_repas,
                'total_symptomes': total_symptomes,
                'periode_analyse': '30 derniers jours'
            },
            'aliments_suspects': patterns,
            'recommandations': recommandations,
            'date_rapport': datetime.utcnow().isoformat()
        }

# Initialisation de l'analyseur
analyseur = AnalyseurAllergies()

# Utilitaires pour les images
def traiter_image(data_base64, nom_fichier):
    """Traite une image base64 et retourne les informations"""
    try:
        # Décoder base64
        image_data = base64.b64decode(data_base64)
        
        # Ouvrir avec PIL pour obtenir les dimensions
        image = PILImage.open(io.BytesIO(image_data))
        largeur, hauteur = image.size
        
        # Optimiser l'image si elle est trop grande
        if largeur > 1920 or hauteur > 1080:
            image.thumbnail((1920, 1080), PILImage.Resampling.LANCZOS)
            
            # Reconvertir en bytes
            output = io.BytesIO()
            format_image = image.format if image.format else 'JPEG'
            image.save(output, format=format_image, quality=85, optimize=True)
            image_data = output.getvalue()
            largeur, hauteur = image.size
        
        return {
            'donnees_blob': image_data,
            'taille': len(image_data),
            'largeur': largeur,
            'hauteur': hauteur
        }
    except Exception as e:
        raise ValueError(f"Erreur lors du traitement de l'image: {str(e)}")

# Routes API pour les utilisateurs
@app.route('/api/utilisateurs', methods=['POST'])
def creer_utilisateur():
    """Créer un nouvel utilisateur"""
    data = request.get_json()
    
    if not data or not data.get('nom') or not data.get('email'):
        return jsonify({'erreur': 'Nom et email requis'}), 400
    
    # Vérifier si l'email existe déjà
    if Utilisateur.query.filter_by(email=data['email']).first():
        return jsonify({'erreur': 'Email déjà utilisé'}), 400
    
    utilisateur = Utilisateur(
        nom=data['nom'],
        email=data['email']
    )
    
    db.session.add(utilisateur)
    db.session.commit()
    
    return jsonify({
        'id': utilisateur.id,
        'nom': utilisateur.nom,
        'email': utilisateur.email,
        'date_creation': utilisateur.date_creation.isoformat()
    }), 201

@app.route('/api/utilisateurs/<int:utilisateur_id>', methods=['GET'])
def obtenir_utilisateur(utilisateur_id):
    """Obtenir les informations d'un utilisateur"""
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    
    return jsonify({
        'id': utilisateur.id,
        'nom': utilisateur.nom,
        'email': utilisateur.email,
        'date_creation': utilisateur.date_creation.isoformat()
    })

@app.route('/api/utilisateurs/<int:utilisateur_id>', methods=['PUT'])
def modifier_utilisateur(utilisateur_id):
    """Modifier un utilisateur"""
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'erreur': 'Données requises'}), 400
    
    # Vérifier l'unicité de l'email si modifié
    if data.get('email') and data['email'] != utilisateur.email:
        if Utilisateur.query.filter_by(email=data['email']).first():
            return jsonify({'erreur': 'Email déjà utilisé'}), 400
        utilisateur.email = data['email']
    
    if data.get('nom'):
        utilisateur.nom = data['nom']
    
    db.session.commit()
    
    return jsonify({
        'id': utilisateur.id,
        'nom': utilisateur.nom,
        'email': utilisateur.email,
        'date_creation': utilisateur.date_creation.isoformat()
    })

@app.route('/api/utilisateurs/<int:utilisateur_id>', methods=['DELETE'])
def supprimer_utilisateur(utilisateur_id):
    """Supprimer un utilisateur et toutes ses données"""
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    
    db.session.delete(utilisateur)
    db.session.commit()
    
    return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200

# Routes CRUD pour les aliments
@app.route('/api/aliments', methods=['POST'])
def creer_aliment():
    """Créer un nouvel aliment"""
    data = request.get_json()
    
    if not data or not data.get('nom'):
        return jsonify({'erreur': 'Nom de l\'aliment requis'}), 400
    
    # Vérifier l'unicité du nom
    if Aliment.query.filter_by(nom=data['nom']).first():
        return jsonify({'erreur': 'Un aliment avec ce nom existe déjà'}), 400
    
    aliment = Aliment(
        nom=data['nom'],
        ingredients=json.dumps(data.get('ingredients', [])),
        allergenes_courants=json.dumps(data.get('allergenes_courants', [])),
        calories_pour_100g=data.get('calories_pour_100g'),
        proteines_pour_100g=data.get('proteines_pour_100g'),
        glucides_pour_100g=data.get('glucides_pour_100g'),
        lipides_pour_100g=data.get('lipides_pour_100g'),
        fibres_pour_100g=data.get('fibres_pour_100g'),
        categorie=data.get('categorie')
    )
    
    db.session.add(aliment)
    db.session.commit()
    
    return jsonify({
        'id': aliment.id,
        'nom': aliment.nom,
        'ingredients': json.loads(aliment.ingredients),
        'allergenes_courants': json.loads(aliment.allergenes_courants),
        'calories_pour_100g': aliment.calories_pour_100g,
        'proteines_pour_100g': aliment.proteines_pour_100g,
        'glucides_pour_100g': aliment.glucides_pour_100g,
        'lipides_pour_100g': aliment.lipides_pour_100g,
        'fibres_pour_100g': aliment.fibres_pour_100g,
        'categorie': aliment.categorie,
        'date_creation': aliment.date_creation.isoformat(),
        'date_modification': aliment.date_modification.isoformat()
    }), 201

@app.route('/api/aliments', methods=['GET'])
def lister_aliments():
    """Lister tous les aliments avec pagination et filtres"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    categorie = request.args.get('categorie')
    recherche = request.args.get('recherche')
    
    query = Aliment.query
    
    # Filtrer par catégorie
    if categorie:
        query = query.filter(Aliment.categorie == categorie)
    
    # Recherche par nom
    if recherche:
        query = query.filter(Aliment.nom.contains(recherche))
    
    # Pagination
    aliments_pagines = query.order_by(Aliment.nom).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'aliments': [{
            'id': a.id,
            'nom': a.nom,
            'ingredients': json.loads(a.ingredients) if a.ingredients else [],
            'allergenes_courants': json.loads(a.allergenes_courants) if a.allergenes_courants else [],
            'calories_pour_100g': a.calories_pour_100g,
            'proteines_pour_100g': a.proteines_pour_100g,
            'glucides_pour_100g': a.glucides_pour_100g,
            'lipides_pour_100g': a.lipides_pour_100g,
            'fibres_pour_100g': a.fibres_pour_100g,
            'categorie': a.categorie,
            'date_creation': a.date_creation.isoformat(),
            'date_modification': a.date_modification.isoformat()
        } for a in aliments_pagines.items],
        'pagination': {
            'page': page,
            'pages': aliments_pagines.pages,
            'per_page': per_page,
            'total': aliments_pagines.total,
            'has_next': aliments_pagines.has_next,
            'has_prev': aliments_pagines.has_prev
        }
    })

@app.route('/api/aliments/<int:aliment_id>', methods=['GET'])
def obtenir_aliment(aliment_id):
    """Obtenir un aliment par son ID"""
    aliment = Aliment.query.get_or_404(aliment_id)
    
    return jsonify({
        'id': aliment.id,
        'nom': aliment.nom,
        'ingredients': json.loads(aliment.ingredients) if aliment.ingredients else [],
        'allergenes_courants': json.loads(aliment.allergenes_courants) if aliment.allergenes_courants else [],
        'calories_pour_100g': aliment.calories_pour_100g,
        'proteines_pour_100g': aliment.proteines_pour_100g,
        'glucides_pour_100g': aliment.glucides_pour_100g,
        'lipides_pour_100g': aliment.lipides_pour_100g,
        'fibres_pour_100g': aliment.fibres_pour_100g,
        'categorie': aliment.categorie,
        'date_creation': aliment.date_creation.isoformat(),
        'date_modification': aliment.date_modification.isoformat()
    })

@app.route('/api/aliments/<int:aliment_id>', methods=['PUT'])
def modifier_aliment(aliment_id):
    """Modifier un aliment"""
    aliment = Aliment.query.get_or_404(aliment_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'erreur': 'Données requises'}), 400
    
    # Vérifier l'unicité du nom si modifié
    if data.get('nom') and data['nom'] != aliment.nom:
        if Aliment.query.filter_by(nom=data['nom']).first():
            return jsonify({'erreur': 'Un aliment avec ce nom existe déjà'}), 400
        aliment.nom = data['nom']
    
    # Mettre à jour les champs
    if 'ingredients' in data:
        aliment.ingredients = json.dumps(data['ingredients'])
    if 'allergenes_courants' in data:
        aliment.allergenes_courants = json.dumps(data['allergenes_courants'])
    if 'calories_pour_100g' in data:
        aliment.calories_pour_100g = data['calories_pour_100g']
    if 'proteines_pour_100g' in data:
        aliment.proteines_pour_100g = data['proteines_pour_100g']
    if 'glucides_pour_100g' in data:
        aliment.glucides_pour_100g = data['glucides_pour_100g']
    if 'lipides_pour_100g' in data:
        aliment.lipides_pour_100g = data['lipides_pour_100g']
    if 'fibres_pour_100g' in data:
        aliment.fibres_pour_100g = data['fibres_pour_100g']
    if 'categorie' in data:
        aliment.categorie = data['categorie']
    
    aliment.date_modification = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'id': aliment.id,
        'nom': aliment.nom,
        'ingredients': json.loads(aliment.ingredients) if aliment.ingredients else [],
        'allergenes_courants': json.loads(aliment.allergenes_courants) if aliment.allergenes_courants else [],
        'calories_pour_100g': aliment.calories_pour_100g,
        'proteines_pour_100g': aliment.proteines_pour_100g,
        'glucides_pour_100g': aliment.glucides_pour_100g,
        'lipides_pour_100g': aliment.lipides_pour_100g,
        'fibres_pour_100g': aliment.fibres_pour_100g,
        'categorie': aliment.categorie,
        'date_creation': aliment.date_creation.isoformat(),
        'date_modification': aliment.date_modification.isoformat()
    })

@app.route('/api/aliments/<int:aliment_id>', methods=['DELETE'])
def supprimer_aliment(aliment_id):
    """Supprimer un aliment"""
    aliment = Aliment.query.get_or_404(aliment_id)
    
    db.session.delete(aliment)
    db.session.commit()
    
    return jsonify({'message': f'Aliment "{aliment.nom}" supprimé avec succès'}), 200

@app.route('/api/aliments/categories', methods=['GET'])
def lister_categories():
    """Lister toutes les catégories d'aliments"""
    categories = db.session.query(Aliment.categorie).distinct().filter(
        Aliment.categorie.isnot(None)
    ).all()
    
    return jsonify({
        'categories': [cat[0] for cat in categories if cat[0]]
    })

@app.route('/api/aliments/recherche', methods=['GET'])
def rechercher_aliments():
    """Recherche avancée d'aliments"""
    terme = request.args.get('q', '')
    if not terme:
        return jsonify({'erreur': 'Terme de recherche requis'}), 400
    
    # Recherche dans le nom et les ingrédients
    aliments = Aliment.query.filter(
        db.or_(
            Aliment.nom.contains(terme),
            Aliment.ingredients.contains(terme)
        )
    ).limit(10).all()
    
    return jsonify({
        'resultats': [{
            'id': a.id,
            'nom': a.nom,
            'categorie': a.categorie,
            'ingredients': json.loads(a.ingredients) if a.ingredients else []
        } for a in aliments]
    })

# Routes pour les images avec gestion blob
@app.route('/api/images', methods=['POST'])
def ajouter_image():
    """Ajouter une image avec stockage en blob"""
    data = request.get_json()
    
    if not data or not data.get('nom_fichier') or not data.get('donnees_base64') or not data.get('type_mime'):
        return jsonify({'erreur': 'nom_fichier, donnees_base64 et type_mime requis'}), 400
    
    try:
        # Traiter l'image
        info_image = traiter_image(data['donnees_base64'], data['nom_fichier'])
        
        # Créer l'enregistrement
        image = Image(
            nom_fichier=data['nom_fichier'],
            donnees_blob=info_image['donnees_blob'],
            type_mime=data['type_mime'],
            taille=info_image['taille'],
            largeur=info_image['largeur'],
            hauteur=info_image['hauteur'],
            utilisateur_id=data.get('utilisateur_id'),
            repas_id=data.get('repas_id'),
            symptome_id=data.get('symptome_id')
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'id': image.id,
            'uuid': image.uuid,
            'nom_fichier': image.nom_fichier,
            'type_mime': image.type_mime,
            'taille': image.taille,
            'largeur': image.largeur,
            'hauteur': image.hauteur,
            'date_creation': image.date_creation.isoformat(),
            'utilisateur_id': image.utilisateur_id,
            'repas_id': image.repas_id,
            'symptome_id': image.symptome_id
        }), 201
        
    except ValueError as e:
        return jsonify({'erreur': str(e)}), 400
    except Exception as e:
        return jsonify({'erreur': f'Erreur lors de l\'ajout de l\'image: {str(e)}'}), 500

@app.route('/api/images/<int:image_id>', methods=['GET'])
def obtenir_image_info(image_id):
    """Obtenir les informations d'une image (sans les données blob)"""
    image = Image.query.get_or_404(image_id)
    
    return jsonify({
        'id': image.id,
        'uuid': image.uuid,
        'nom_fichier': image.nom_fichier,
        'type_mime': image.type_mime,
        'taille': image.taille,
        'largeur': image.largeur,
        'hauteur': image.hauteur,
        'date_creation': image.date_creation.isoformat(),
        'utilisateur_id': image.utilisateur_id,
        'repas_id': image.repas_id,
        'symptome_id': image.symptome_id
    })

@app.route('/api/images/<int:image_id>/blob', methods=['GET'])
def obtenir_image_blob(image_id):
    """Obtenir les données blob d'une image"""
    image = Image.query.get_or_404(image_id)
    
    return send_file(
        io.BytesIO(image.donnees_blob),
        mimetype=image.type_mime,
        as_attachment=False,
        download_name=image.nom_fichier
    )

@app.route('/api/images/uuid/<uuid_str>', methods=['GET'])
def obtenir_image_par_uuid(uuid_str):
    """Obtenir une image par son UUID"""
    image = Image.query.filter_by(uuid=uuid_str).first_or_404()
    
    return send_file(
        io.BytesIO(image.donnees_blob),
        mimetype=image.type_mime,
        as_attachment=False,
        download_name=image.nom_fichier
    )

@app.route('/api/images/<int:image_id>/base64', methods=['GET'])
def obtenir_image_base64(image_id):
    """Obtenir une image en format base64"""
    image = Image.query.get_or_404(image_id)
    
    image_base64 = base64.b64encode(image.donnees_blob).decode('utf-8')
    
    return jsonify({
        'id': image.id,
        'uuid': image.uuid,
        'nom_fichier': image.nom_fichier,
        'type_mime': image.type_mime,
        'donnees_base64': image_base64,
        'taille': image.taille,
        'largeur': image.largeur,
        'hauteur': image.hauteur
    })

@app.route('/api/images/<int:image_id>', methods=['DELETE'])
def supprimer_image(image_id):
    """Supprimer une image"""
    image = Image.query.get_or_404(image_id)
    
    db.session.delete(image)
    db.session.commit()
    
    return jsonify({'message': f'Image "{image.nom_fichier}" supprimée avec succès'}), 200

@app.route('/api/images/utilisateur/<int:utilisateur_id>', methods=['GET'])
def lister_images_utilisateur(utilisateur_id):
    """Lister les images d'un utilisateur"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    images_pagines = Image.query.filter_by(utilisateur_id=utilisateur_id).order_by(
        Image.date_creation.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'images': [{
            'id': img.id,
            'uuid': img.uuid,
            'nom_fichier': img.nom_fichier,
            'type_mime': img.type_mime,
            'taille': img.taille,
            'largeur': img.largeur,
            'hauteur': img.hauteur,
            'date_creation': img.date_creation.isoformat(),
            'repas_id': img.repas_id,
            'symptome_id': img.symptome_id
        } for img in images_pagines.items],
        'pagination': {
            'page': page,
            'pages': images_pagines.pages,
            'per_page': per_page,
            'total': images_pagines.total
        }
    })

@app.route('/api/images/repas/<int:repas_id>', methods=['GET'])
def lister_images_repas(repas_id):
    """Lister les images d'un repas"""
    images = Image.query.filter_by(repas_id=repas_id).order_by(Image.date_creation.desc()).all()
    
    return jsonify({
        'images': [{
            'id': img.id,
            'uuid': img.uuid,
            'nom_fichier': img.nom_fichier,
            'type_mime': img.type_mime,
            'taille': img.taille,
            'largeur': img.largeur,
            'hauteur': img.hauteur,
            'date_creation': img.date_creation.isoformat()
        } for img in images]
    })

@app.route('/api/images/symptome/<int:symptome_id>', methods=['GET'])
def lister_images_symptome(symptome_id):
    """Lister les images d'un symptôme"""
    images = Image.query.filter_by(symptome_id=symptome_id).order_by(Image.date_creation.desc()).all()
    
    return jsonify({
        'images': [{
            'id': img.id,
            'uuid': img.uuid,
            'nom_fichier': img.nom_fichier,
            'type_mime': img.type_mime,
            'taille': img.taille,
            'largeur': img.largeur,
            'hauteur': img.hauteur,
            'date_creation': img.date_creation.isoformat()
        } for img in images]
    })

# Routes d'analyse
@app.route('/api/analyse/<int:utilisateur_id>', methods=['GET'])
def analyser_allergies(utilisateur_id):
    """Analyser les allergies potentielles d'un utilisateur"""
    # Vérifier que l'utilisateur existe
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur:
        return jsonify({'erreur': 'Utilisateur non trouvé'}), 404
    
    # Générer le rapport d'analyse
    rapport = analyseur.generer_rapport(utilisateur_id)
    
    return jsonify(rapport)

@app.route('/api/score-risque/<int:utilisateur_id>/<aliment>', methods=['GET'])
def calculer_score_aliment(utilisateur_id, aliment):
    """Calculer le score de risque pour un aliment spécifique"""
    # Vérifier que l'utilisateur existe
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur:
        return jsonify({'erreur': 'Utilisateur non trouvé'}), 404
    
    score = analyseur.calculer_score_risque(utilisateur_id, aliment)
    
    return jsonify({
        'aliment': aliment,
        'score_risque': score,
        'niveau_alerte': 'ÉLEVÉ' if score >= 30 else 'MODÉRÉ' if score >= 15 else 'FAIBLE',
        'seuil_alerte': analyseur.seuil_alerte
    })

@app.route('/api/dashboard/<int:utilisateur_id>', methods=['GET'])
def dashboard_utilisateur(utilisateur_id):
    """Dashboard complet pour un utilisateur"""
    # Vérifier que l'utilisateur existe
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur:
        return jsonify({'erreur': 'Utilisateur non trouvé'}), 404
    
    # Statistiques de base
    total_repas = Repas.query.filter_by(utilisateur_id=utilisateur_id).count()
    total_symptomes = Symptome.query.filter_by(utilisateur_id=utilisateur_id).count()
    total_images = Image.query.filter_by(utilisateur_id=utilisateur_id).count()
    
    # Derniers repas
    derniers_repas = Repas.query.filter_by(utilisateur_id=utilisateur_id).order_by(
        Repas.date_heure.desc()
    ).limit(5).all()
    
    # Derniers symptômes
    derniers_symptomes = Symptome.query.filter_by(utilisateur_id=utilisateur_id).order_by(
        Symptome.date_heure.desc()
    ).limit(5).all()
    
    # Analyse des allergies
    rapport_allergies = analyseur.generer_rapport(utilisateur_id)
    
    # Statistiques nutritionnelles (basées sur les aliments consommés)
    stats_nutritionnelles = calculer_stats_nutritionnelles(utilisateur_id)
    
    return jsonify({
        'utilisateur': {
            'id': utilisateur.id,
            'nom': utilisateur.nom,
            'email': utilisateur.email
        },
        'statistiques': {
            'total_repas': total_repas,
            'total_symptomes': total_symptomes,
            'total_images': total_images
        },
        'derniers_repas': [{
            'id': r.id,
            'date_heure': r.date_heure.isoformat(),
            'aliments': json.loads(r.aliments),
            'description': r.description,
            'nb_images': len(r.images)
        } for r in derniers_repas],
        'derniers_symptomes': [{
            'id': s.id,
            'date_heure': s.date_heure.isoformat(),
            'type_symptome': s.type_symptome,
            'severite': s.severite,
            'description': s.description,
            'nb_images': len(s.images)
        } for s in derniers_symptomes],
        'analyse_allergies': rapport_allergies,
        'stats_nutritionnelles': stats_nutritionnelles
    })

def calculer_stats_nutritionnelles(utilisateur_id):
    """Calculer les statistiques nutritionnelles d'un utilisateur"""
    # Récupérer les repas des 7 derniers jours
    date_limite = datetime.utcnow() - timedelta(days=7)
    repas_recents = Repas.query.filter(
        Repas.utilisateur_id == utilisateur_id,
        Repas.date_heure >= date_limite
    ).all()
    
    total_calories = 0
    total_proteines = 0
    total_glucides = 0
    total_lipides = 0
    total_fibres = 0
    jours_avec_repas = set()
    
    for repas in repas_recents:
        jours_avec_repas.add(repas.date_heure.date())
        try:
            aliments_repas = json.loads(repas.aliments)
            for aliment_data in aliments_repas:
                if isinstance(aliment_data, dict):
                    nom_aliment = aliment_data.get('nom', '')
                    quantite = aliment_data.get('quantite', 100)  # en grammes
                    
                    # Rechercher l'aliment dans la base
                    aliment = Aliment.query.filter_by(nom=nom_aliment).first()
                    if aliment:
                        facteur = quantite / 100  # Facteur de conversion pour 100g
                        if aliment.calories_pour_100g:
                            total_calories += aliment.calories_pour_100g * facteur
                        if aliment.proteines_pour_100g:
                            total_proteines += aliment.proteines_pour_100g * facteur
                        if aliment.glucides_pour_100g:
                            total_glucides += aliment.glucides_pour_100g * facteur
                        if aliment.lipides_pour_100g:
                            total_lipides += aliment.lipides_pour_100g * facteur
                        if aliment.fibres_pour_100g:
                            total_fibres += aliment.fibres_pour_100g * facteur
        except:
            continue
    
    nb_jours = len(jours_avec_repas) or 1  # Éviter la division par zéro
    
    return {
        'periode': '7 derniers jours',
        'nb_jours_avec_repas': len(jours_avec_repas),
        'moyennes_par_jour': {
            'calories': round(total_calories / nb_jours, 1),
            'proteines': round(total_proteines / nb_jours, 1),
            'glucides': round(total_glucides / nb_jours, 1),
            'lipides': round(total_lipides / nb_jours, 1),
            'fibres': round(total_fibres / nb_jours, 1)
        },
        'totaux': {
            'calories': round(total_calories, 1),
            'proteines': round(total_proteines, 1),
            'glucides': round(total_glucides, 1),
            'lipides': round(total_lipides, 1),
            'fibres': round(total_fibres, 1)
        }
    }

# Routes utilitaires
@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API"""
    # Vérifier la connexion à la base de données
    try:
        db.session.execute('SELECT 1')
        db_status = 'OK'
    except:
        db_status = 'ERROR'
    
    return jsonify({
        'status': 'OK',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'features': [
            'Gestion utilisateurs',
            'CRUD aliments complet',
            'Gestion repas et symptômes',
            'Stockage images en blob',
            'Analyse allergies',
            'Statistiques nutritionnelles'
        ]
    })

@app.route('/api/stats', methods=['GET'])
def statistiques_globales():
    """Statistiques globales de l'application"""
    return jsonify({
        'utilisateurs': Utilisateur.query.count(),
        'aliments': Aliment.query.count(),
        'repas': Repas.query.count(),
        'symptomes': Symptome.query.count(),
        'images': Image.query.count(),
        'taille_totale_images': db.session.query(db.func.sum(Image.taille)).scalar() or 0
    })

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    return jsonify({'erreur': 'Ressource non trouvée'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'erreur': 'Requête invalide'}), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'erreur': 'Erreur interne du serveur'}), 500

# Initialisation de la base de données
def init_database():
    """Initialise la base de données avec des données de base"""
    db.create_all()
    
    # Ajouter quelques aliments de base s'ils n'existent pas
    if Aliment.query.count() == 0:
        aliments_base = [
           [
  {
    "nom": "Biryani de poulet",
    "ingredients": ["riz basmati", "poulet", "yaourt", "oignons", "garam masala", "safran", "ghee", "menthe", "coriandre"],
    "allergenes_courants": ["lactose", "gluten (épices)"],
    "calories_pour_100g": 185,
    "proteines_pour_100g": 12.5,
    "glucides_pour_100g": 18.2,
    "lipides_pour_100g": 7.8,
    "fibres_pour_100g": 1.2,
    "categorie": "Plats principaux"
  },
  {
    "nom": "Karahi de mouton",
    "ingredients": ["mouton", "tomates", "gingembre", "ail", "piments verts", "huile", "coriandre", "cumin", "garam masala"],
    "allergenes_courants": [],
    "calories_pour_100g": 265,
    "proteines_pour_100g": 22.8,
    "glucides_pour_100g": 4.5,
    "lipides_pour_100g": 17.3,
    "fibres_pour_100g": 1.8,
    "categorie": "Plats principaux"
  },
  {
    "nom": "Daal chawal (lentilles au riz)",
    "ingredients": ["lentilles masoor", "riz basmati", "curcuma", "oignons", "ail", "gingembre", "tomates", "ghee"],
    "allergenes_courants": ["lactose (ghee)"],
    "calories_pour_100g": 142,
    "proteines_pour_100g": 8.3,
    "glucides_pour_100g": 22.1,
    "lipides_pour_100g": 2.9,
    "fibres_pour_100g": 4.7,
    "categorie": "Plats végétariens"
  },
  {
    "nom": "Chapati (pain pakistanais)",
    "ingredients": ["farine de blé complet", "eau", "sel", "huile"],
    "allergenes_courants": ["gluten"],
    "calories_pour_100g": 297,
    "proteines_pour_100g": 11.8,
    "glucides_pour_100g": 56.4,
    "lipides_pour_100g": 4.1,
    "fibres_pour_100g": 9.6,
    "categorie": "Pains et accompagnements"
  },
  {
    "nom": "Seekh kebab",
    "ingredients": ["bœuf haché", "oignons", "ail", "gingembre", "coriandre", "menthe", "piments", "garam masala", "cumin"],
    "allergenes_courants": [],
    "calories_pour_100g": 312,
    "proteines_pour_100g": 24.7,
    "glucides_pour_100g": 3.2,
    "lipides_pour_100g": 22.1,
    "fibres_pour_100g": 0.8,
    "categorie": "Grillades"
  }
]
        ]
        
        for aliment_data in aliments_base:
            aliment = Aliment(
                nom=aliment_data['nom'],
                ingredients=json.dumps(aliment_data['ingredients']),
                allergenes_courants=json.dumps(aliment_data['allergenes_courants']),
                calories_pour_100g=aliment_data['calories_pour_100g'],
                proteines_pour_100g=aliment_data['proteines_pour_100g'],
                glucides_pour_100g=aliment_data['glucides_pour_100g'],
                lipides_pour_100g=aliment_data['lipides_pour_100g'],
                fibres_pour_100g=aliment_data['fibres_pour_100g'],
                categorie=aliment_data['categorie']
            )
            db.session.add(aliment)
        
        db.session.commit()
        print("Base de données initialisée avec des aliments de base")
@app.route('/api/repas', methods=['POST'])
def ajouter_repas():
    """Ajouter un nouveau repas"""
    data = request.get_json()
    
    if not data or not data.get('utilisateur_id') or not data.get('aliments'):
        return jsonify({'erreur': 'utilisateur_id et aliments requis'}), 400
    
    # Vérifier que l'utilisateur existe
    utilisateur = Utilisateur.query.get(data['utilisateur_id'])
    if not utilisateur:
        return jsonify({'erreur': 'Utilisateur non trouvé'}), 404
    
    # Parse la date ou utilise maintenant
    date_heure = datetime.utcnow()
    if data.get('date_heure'):
        try:
            date_heure = parser.parse(data['date_heure'])
        except:
            pass
    
    repas = Repas(
        utilisateur_id=data['utilisateur_id'],
        date_heure=date_heure,
        aliments=json.dumps(data['aliments']),
        description=data.get('description', '')
    )
    
    db.session.add(repas)
    db.session.commit()
    
    return jsonify({
        'id': repas.id,
        'utilisateur_id': repas.utilisateur_id,
        'date_heure': repas.date_heure.isoformat(),
        'aliments': json.loads(repas.aliments),
        'description': repas.description
    }), 201

@app.route('/api/repas/<int:utilisateur_id>', methods=['GET'])
def lister_repas(utilisateur_id):
    """Lister les repas d'un utilisateur"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    repas_pagines = Repas.query.filter_by(utilisateur_id=utilisateur_id).order_by(
        Repas.date_heure.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'repas': [{
            'id': r.id,
            'date_heure': r.date_heure.isoformat(),
            'aliments': json.loads(r.aliments),
            'description': r.description,
            'nb_images': len(r.images)
        } for r in repas_pagines.items],
        'pagination': {
            'page': page,
            'pages': repas_pagines.pages,
            'per_page': per_page,
            'total': repas_pagines.total
        }
    })

# Routes pour les symptômes
@app.route('/api/symptomes', methods=['POST'])
def ajouter_symptome():
    """Ajouter un nouveau symptôme"""
    data = request.get_json()
    
    if not data or not data.get('utilisateur_id') or not data.get('type_symptome') or not data.get('severite'):
        return jsonify({'erreur': 'utilisateur_id, type_symptome et severite requis'}), 400
    
    # Vérifier que l'utilisateur existe
    utilisateur = Utilisateur.query.get(data['utilisateur_id'])
    if not utilisateur:
        return jsonify({'erreur': 'Utilisateur non trouvé'}), 404
    
    # Parse la date ou utilise maintenant
    date_heure = datetime.utcnow()
    if data.get('date_heure'):
        try:
            date_heure = parser.parse(data['date_heure'])
        except:
            pass
    
    symptome = Symptome(
        utilisateur_id=data['utilisateur_id'],
        date_heure=date_heure,
        type_symptome=data['type_symptome'],
        severite=int(data['severite']),
        description=data.get('description', '')
    )
    
    db.session.add(symptome)
    db.session.commit()
    
    return jsonify({
        'id': symptome.id,
        'utilisateur_id': symptome.utilisateur_id,
        'date_heure': symptome.date_heure.isoformat(),
        'type_symptome': symptome.type_symptome,
        'severite': symptome.severite,
        'description': symptome.description
    }), 201

@app.route('/api/symptomes/<int:utilisateur_id>', methods=['GET'])
def lister_symptomes(utilisateur_id):
    """Lister les symptômes d'un utilisateur"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    symptomes_pagines = Symptome.query.filter_by(utilisateur_id=utilisateur_id).order_by(
        Symptome.date_heure.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'symptomes': [{
            'id': s.id,
            'date_heure': s.date_heure.isoformat(),
            'type_symptome': s.type_symptome,
            'severite': s.severite,
            'description': s.description,
            'nb_images': len(s.images)
        } for s in symptomes_pagines.items],
        'pagination': {
            'page': page,
            'pages': symptomes_pagines.pages,
            'per_page': per_page,
            'total': symptomes_pagines.total
        }
    })
# POUR LES PLANIFICATIONS ALIMENTAIRES
@app.route('/api/plans-alimentaires', methods=['POST'])
def creer_plan_alimentaire():
    """Créer un nouveau plan alimentaire hebdomadaire"""
    data = request.get_json()
    if not data or not data.get('utilisateur_id') or not data.get('nom') or not data.get('semaine_debut'):
        return jsonify({'erreur': 'utilisateur_id, nom et semaine_debut requis'}), 400
    
    try:
        semaine_debut = parser.parse(data['semaine_debut']).date()
        # S'assurer que c'est un lundi
        jours_depuis_lundi = semaine_debut.weekday()
        semaine_debut = semaine_debut - timedelta(days=jours_depuis_lundi)
    except:
        return jsonify({'erreur': 'Format de date invalide pour semaine_debut'}), 400
    
    plan = PlanAlimentaire(
        utilisateur_id=data['utilisateur_id'],
        nom=data['nom'],
        semaine_debut=semaine_debut,
        actif=data.get('actif', True)
    )
    
    db.session.add(plan)
    db.session.commit()
    
    return jsonify({
        'id': plan.id,
        'utilisateur_id': plan.utilisateur_id,
        'nom': plan.nom,
        'semaine_debut': plan.semaine_debut.isoformat(),
        'actif': plan.actif,
        'date_creation': plan.date_creation.isoformat()
    }), 201

@app.route('/api/plans-alimentaires/<int:utilisateur_id>', methods=['GET'])
def obtenir_plans_alimentaires(utilisateur_id):
    """Obtenir tous les plans alimentaires d'un utilisateur"""
    actif_seulement = request.args.get('actif', 'false').lower() == 'true'
    
    query = PlanAlimentaire.query.filter_by(utilisateur_id=utilisateur_id)
    if actif_seulement:
        query = query.filter_by(actif=True)
    
    plans = query.order_by(PlanAlimentaire.semaine_debut.desc()).all()
    
    return jsonify([{
        'id': plan.id,
        'nom': plan.nom,
        'semaine_debut': plan.semaine_debut.isoformat(),
        'actif': plan.actif,
        'date_creation': plan.date_creation.isoformat(),
        'nombre_repas': len(plan.repas_planifies)
    } for plan in plans])

@app.route('/api/plans-alimentaires/<int:plan_id>/repas', methods=['POST'])
def ajouter_repas_planifie(plan_id):
    """Ajouter un repas planifié à un plan"""
    data = request.get_json()
    if not data or not all(k in data for k in ['jour_semaine', 'type_repas', 'aliments_planifies']):
        return jsonify({'erreur': 'jour_semaine, type_repas et aliments_planifies requis'}), 400
    
    # Vérifier que le plan existe
    plan = PlanAlimentaire.query.get_or_404(plan_id)
    
    # Valider jour_semaine (0-6)
    if not (0 <= data['jour_semaine'] <= 6):
        return jsonify({'erreur': 'jour_semaine doit être entre 0 et 6'}), 400
    
    # Valider type_repas
    types_valides = ['petit_dejeuner', 'dejeuner', 'diner', 'collation']
    if data['type_repas'] not in types_valides:
        return jsonify({'erreur': f'type_repas doit être un de: {types_valides}'}), 400
    
    try:
        aliments_json = json.dumps(data['aliments_planifies'])
    except:
        return jsonify({'erreur': 'Format JSON invalide pour aliments_planifies'}), 400
    
    repas = RepasPlanifie(
        plan_id=plan_id,
        jour_semaine=data['jour_semaine'],
        type_repas=data['type_repas'],
        aliments_planifies=aliments_json,
        calories_estimees=data.get('calories_estimees'),
        notes=data.get('notes', '')
    )
    
    db.session.add(repas)
    db.session.commit()
    
    return jsonify({
        'id': repas.id,
        'plan_id': repas.plan_id,
        'jour_semaine': repas.jour_semaine,
        'type_repas': repas.type_repas,
        'aliments_planifies': json.loads(repas.aliments_planifies),
        'calories_estimees': repas.calories_estimees,
        'notes': repas.notes
    }), 201

@app.route('/api/plans-alimentaires/<int:plan_id>/semaine', methods=['GET'])
def obtenir_planning_semaine(plan_id):
    """Obtenir le planning complet d'une semaine"""
    plan = PlanAlimentaire.query.get_or_404(plan_id)
    repas = RepasPlanifie.query.filter_by(plan_id=plan_id).all()
    
    # Organiser par jour et type de repas
    planning = defaultdict(lambda: defaultdict(list))
    noms_jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    for repas_item in repas:
        jour_nom = noms_jours[repas_item.jour_semaine]
        planning[jour_nom][repas_item.type_repas].append({
            'id': repas_item.id,
            'aliments': json.loads(repas_item.aliments_planifies),
            'calories_estimees': repas_item.calories_estimees,
            'notes': repas_item.notes
        })
    
    return jsonify({
        'plan': {
            'id': plan.id,
            'nom': plan.nom,
            'semaine_debut': plan.semaine_debut.isoformat()
        },
        'planning': dict(planning)
    })

@app.route('/api/plans-alimentaires/<int:plan_id>/liste-courses', methods=['GET'])
def generer_liste_courses(plan_id):
    """Générer une liste de courses basée sur le plan alimentaire"""
    plan = PlanAlimentaire.query.get_or_404(plan_id)
    repas = RepasPlanifie.query.filter_by(plan_id=plan_id).all()
    
    # Agréger tous les ingrédients
    ingredients = defaultdict(float)
    
    for repas_item in repas:
        try:
            aliments = json.loads(repas_item.aliments_planifies)
            for aliment in aliments:
                nom = aliment.get('nom', '')
                quantite = aliment.get('quantite', 0)
                if nom:
                    ingredients[nom] += quantite
        except:
            continue
    
    # Organiser par catégorie (basique)
    categories = {
        'legumes': ['tomate', 'carotte', 'oignon', 'salade', 'courgette', 'aubergine', 'poivron'],
        'fruits': ['pomme', 'banane', 'orange', 'fraise', 'raisin'],
        'viandes': ['boeuf', 'porc', 'agneau', 'veau', 'poulet', 'dinde'],
        'poissons': ['saumon', 'thon', 'sardine', 'cabillaud', 'truite'],
        'feculents': ['riz', 'pâtes', 'pomme de terre', 'pain', 'quinoa'],
        'produits_laitiers': ['lait', 'yaourt', 'fromage', 'beurre', 'crème']
    }
    
    liste_organisee = defaultdict(list)
    autres = []
    
    for ingredient, quantite in ingredients.items():
        categorise = False
        for categorie, mots_cles in categories.items():
            if any(mot in ingredient.lower() for mot in mots_cles):
                liste_organisee[categorie].append({
                    'nom': ingredient,
                    'quantite': quantite
                })
                categorise = True
                break
        
        if not categorise:
            autres.append({
                'nom': ingredient,
                'quantite': quantite
            })
    
    if autres:
        liste_organisee['autres'] = autres
    
    return jsonify({
        'plan_nom': plan.nom,
        'semaine': plan.semaine_debut.isoformat(),
        'liste_courses': dict(liste_organisee),
        'total_articles': len(ingredients)
    })

# ==================== ROUTES POUR LA GESTION DE BUFFET ====================

@app.route('/api/buffets', methods=['POST'])
def creer_buffet():
    """Créer un nouveau buffet pour un événement"""
    data = request.get_json()
    required_fields = ['utilisateur_id', 'nom_evenement', 'date_evenement', 'nombre_invites']
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({'erreur': f'Champs requis: {required_fields}'}), 400
    
    try:
        date_evenement = parser.parse(data['date_evenement'])
    except:
        return jsonify({'erreur': 'Format de date invalide pour date_evenement'}), 400
    
    buffet = Buffet(
        utilisateur_id=data['utilisateur_id'],
        nom_evenement=data['nom_evenement'],
        date_evenement=date_evenement,
        nombre_invites=data['nombre_invites'],
        budget_total=data.get('budget_total'),
        type_evenement=data.get('type_evenement', ''),
        notes=data.get('notes', ''),
        statut=data.get('statut', 'planification')
    )
    
    db.session.add(buffet)
    db.session.commit()
    
    return jsonify({
        'id': buffet.id,
        'utilisateur_id': buffet.utilisateur_id,
        'nom_evenement': buffet.nom_evenement,
        'date_evenement': buffet.date_evenement.isoformat(),
        'nombre_invites': buffet.nombre_invites,
        'budget_total': buffet.budget_total,
        'type_evenement': buffet.type_evenement,
        'statut': buffet.statut,
        'date_creation': buffet.date_creation.isoformat()
    }), 201

@app.route('/api/buffets/<int:utilisateur_id>', methods=['GET'])
def obtenir_buffets_utilisateur(utilisateur_id):
    """Obtenir tous les buffets d'un utilisateur"""
    buffets = Buffet.query.filter_by(utilisateur_id=utilisateur_id).order_by(Buffet.date_evenement.desc()).all()
    
    return jsonify([{
        'id': buffet.id,
        'nom_evenement': buffet.nom_evenement,
        'date_evenement': buffet.date_evenement.isoformat(),
        'nombre_invites': buffet.nombre_invites,
        'budget_total': buffet.budget_total,
        'type_evenement': buffet.type_evenement,
        'statut': buffet.statut,
        'nombre_plats': len(buffet.plats_buffet),
        'date_creation': buffet.date_creation.isoformat()
    } for buffet in buffets])

@app.route('/api/buffets/<int:buffet_id>/plats', methods=['POST'])
def ajouter_plat_buffet(buffet_id):
    """Ajouter un plat au buffet"""
    data = request.get_json()
    if not data or not data.get('nom_plat'):
        return jsonify({'erreur': 'nom_plat requis'}), 400
    
    # Vérifier que le buffet existe
    buffet = Buffet.query.get_or_404(buffet_id)
    
    # Valider la catégorie
    categories_valides = ['entree', 'plat_principal', 'dessert', 'boisson', 'accompagnement']
    categorie = data.get('categorie', 'plat_principal')
    if categorie not in categories_valides:
        return jsonify({'erreur': f'categorie doit être un de: {categories_valides}'}), 400
    
    plat = PlatBuffet(
        buffet_id=buffet_id,
        nom_plat=data['nom_plat'],
        categorie=categorie,
        quantite_par_personne=data.get('quantite_par_personne', 0),
        cout_unitaire=data.get('cout_unitaire', 0),
        allergenes=json.dumps(data.get('allergenes', [])),
        ingredients=json.dumps(data.get('ingredients', [])),
        instructions_preparation=data.get('instructions_preparation', ''),
        temps_preparation=data.get('temps_preparation', 0),
        difficulte=data.get('difficulte', 1),
        notes=data.get('notes', '')
    )
    
    db.session.add(plat)
    db.session.commit()
    
    return jsonify({
        'id': plat.id,
        'buffet_id': plat.buffet_id,
        'nom_plat': plat.nom_plat,
        'categorie': plat.categorie,
        'quantite_par_personne': plat.quantite_par_personne,
        'cout_unitaire': plat.cout_unitaire,
        'allergenes': json.loads(plat.allergenes),
        'ingredients': json.loads(plat.ingredients),
        'instructions_preparation': plat.instructions_preparation,
        'temps_preparation': plat.temps_preparation,
        'difficulte': plat.difficulte,
        'notes': plat.notes
    }), 201

@app.route('/api/buffets/<int:buffet_id>/details', methods=['GET'])
def obtenir_details_buffet(buffet_id):
    """Obtenir les détails complets d'un buffet"""
    buffet = Buffet.query.get_or_404(buffet_id)
    plats = PlatBuffet.query.filter_by(buffet_id=buffet_id).all()
    
    # Organiser les plats par catégorie
    plats_par_categorie = defaultdict(list)
    cout_total = 0
    temps_total = 0
    
    for plat in plats:
        plat_info = {
            'id': plat.id,
            'nom_plat': plat.nom_plat,
            'quantite_par_personne': plat.quantite_par_personne,
            'cout_unitaire': plat.cout_unitaire,
            'cout_total': plat.cout_unitaire * buffet.nombre_invites if plat.cout_unitaire else 0,
            'allergenes': json.loads(plat.allergenes),
            'ingredients': json.loads(plat.ingredients),
            'instructions_preparation': plat.instructions_preparation,
            'temps_preparation': plat.temps_preparation,
            'difficulte': plat.difficulte,
            'notes': plat.notes
        }
        
        plats_par_categorie[plat.categorie].append(plat_info)
        cout_total += plat_info['cout_total']
        temps_total += plat.temps_preparation or 0
    
    return jsonify({
        'buffet': {
            'id': buffet.id,
            'nom_evenement': buffet.nom_evenement,
            'date_evenement': buffet.date_evenement.isoformat(),
            'nombre_invites': buffet.nombre_invites,
            'budget_total': buffet.budget_total,
            'type_evenement': buffet.type_evenement,
            'statut': buffet.statut,
            'notes': buffet.notes
        },
        'plats_par_categorie': dict(plats_par_categorie),
        'resume': {
            'nombre_plats': len(plats),
            'cout_estime': cout_total,
            'temps_preparation_total': temps_total,
            'cout_par_personne': cout_total / buffet.nombre_invites if buffet.nombre_invites > 0 else 0,
            'respect_budget': cout_total <= (buffet.budget_total or float('inf'))
        }
    })

@app.route('/api/buffets/<int:buffet_id>/quantites', methods=['GET'])
def calculer_quantites_buffet(buffet_id):
    """Calculer les quantités totales nécessaires pour le buffet"""
    buffet = Buffet.query.get_or_404(buffet_id)
    plats = PlatBuffet.query.filter_by(buffet_id=buffet_id).all()
    
    # Agréger tous les ingrédients
    ingredients_totaux = defaultdict(float)
    
    for plat in plats:
        try:
            ingredients = json.loads(plat.ingredients)
            for ingredient in ingredients:
                if isinstance(ingredient, dict):
                    nom = ingredient.get('nom', '')
                    quantite_unitaire = ingredient.get('quantite', 0)
                elif isinstance(ingredient, str):
                    nom = ingredient
                    quantite_unitaire = plat.quantite_par_personne or 100  # défaut 100g
                else:
                    continue
                
                if nom:
                    quantite_totale = quantite_unitaire * buffet.nombre_invites
                    ingredients_totaux[nom] += quantite_totale
        except:
            continue
    
    return jsonify({
        'buffet_nom': buffet.nom_evenement,
        'nombre_invites': buffet.nombre_invites,
        'ingredients_totaux': dict(ingredients_totaux),
        'date_evenement': buffet.date_evenement.isoformat()
    })

@app.route('/api/buffets/<int:buffet_id>/planning', methods=['GET'])
def generer_planning_preparation(buffet_id):
    """Générer un planning de préparation pour le buffet"""
    buffet = Buffet.query.get_or_404(buffet_id)
    plats = PlatBuffet.query.filter_by(buffet_id=buffet_id).order_by(PlatBuffet.temps_preparation.desc()).all()
    
    # Calculer les créneaux de préparation
    date_evenement = buffet.date_evenement
    planning = []
    
    for plat in plats:
        temps_prep = plat.temps_preparation or 30  # défaut 30 min
        heure_debut = date_evenement - timedelta(minutes=temps_prep)
        
        planning.append({
            'plat': plat.nom_plat,
            'categorie': plat.categorie,
            'heure_debut': heure_debut.isoformat(),
            'heure_fin': date_evenement.isoformat(),
            'duree_minutes': temps_prep,
            'difficulte': plat.difficulte,
            'instructions': plat.instructions_preparation,
            'ingredients_necessaires': json.loads(plat.ingredients)
        })
    
    # Recommandations générales
    recommandations = [
        "Préparez les plats les plus complexes en premier",
        "Gardez les plats froids au réfrigérateur jusqu'au service",
        "Préparez une liste de vérification pour chaque plat",
        "Prévoyez 20% de nourriture en plus pour les imprévus"
    ]
    
    return jsonify({
        'buffet_nom': buffet.nom_evenement,
        'date_evenement': buffet.date_evenement.isoformat(),
        'planning_preparation': planning,
        'temps_total_preparation': sum(plat.temps_preparation or 0 for plat in plats),
        'recommandations': recommandations
    })

if __name__ == '__main__':
    with app.app_context():
        init_database()
    
    print("=== Serveur Flask de Détection d'Allergies ===")
    print("Fonctionnalités disponibles:")
    print("- Gestion complète des utilisateurs (CRUD)")
    print("- Gestion complète des aliments (CRUD)")
    print("- Suivi des repas et symptômes")
    print("- Stockage d'images en blob optimisé")
    print("- Analyse intelligente des allergies")
    print("- Statistiques nutritionnelles")
    print("- Dashboard utilisateur")
    print("===============================================")
    
    app.run(debug=True, host='0.0.0.0', port=5000)