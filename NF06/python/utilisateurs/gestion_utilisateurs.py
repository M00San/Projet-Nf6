import json
from datetime import datetime
from pathlib import Path
import re
import logging

class GestionUtilisateurs:
    def __init__(self):
        self.base_path = Path("donnees")
        self.utilisateurs = {}
        self.notes = {}
        self.commentaires = {}
        self.gestion_catalogue = None  # Sera initialisé plus tard
        self._charger_donnees()

    def _charger_donnees(self):
        """Charge les données des utilisateurs depuis les fichiers JSON."""
        try:
            # Charger les utilisateurs
            with open(self.base_path / "utilisateurs.json", 'r', encoding='utf-8') as f:
                self.utilisateurs = json.load(f)
            
            # Charger les notes
            with open(self.base_path / "notes_utilisateurs.json", 'r', encoding='utf-8') as f:
                notes_brutes = json.load(f)
                self.notes = {}
                # Nettoyer et normaliser les notes
                for username, notes in notes_brutes.items():
                    self.notes[username] = {}
                    # Gérer le cas spécial où les notes sont dans un sous-dictionnaire "notes"
                    if "notes" in notes:
                        notes = notes["notes"]
                    for film_id, note_data in notes.items():
                        if isinstance(note_data, dict) and 'note' in note_data:
                            # Convertir la note sur une échelle de 1 à 5
                            note_originale = float(note_data['note'])
                            note_normalisee = round(note_originale / 2) if note_originale > 5 else round(note_originale)
                            self.notes[username][film_id] = {
                                'note': note_normalisee,
                                'date': note_data['date']
                            }
            
            # Charger les commentaires
            with open(self.base_path / "commentaires.json", 'r', encoding='utf-8') as f:
                self.commentaires = json.load(f)
        except FileNotFoundError as e:
            logging.error(f"Erreur lors du chargement des données: {e}")
            self.utilisateurs = {}
            self.notes = {}
            self.commentaires = {}

    def _sauvegarder_donnees(self):
        """Sauvegarde les données des utilisateurs dans les fichiers JSON."""
        try:
            # Sauvegarder les utilisateurs
            with open(self.base_path / "utilisateurs.json", 'w', encoding='utf-8') as f:
                json.dump(self.utilisateurs, f, indent=4, ensure_ascii=False)
            
            # Sauvegarder les notes
            with open(self.base_path / "notes_utilisateurs.json", 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=4, ensure_ascii=False)
            
            # Sauvegarder les commentaires
            with open(self.base_path / "commentaires.json", 'w', encoding='utf-8') as f:
                json.dump(self.commentaires, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des données: {e}")

    def verifier_force_mdp(self, password):
        """Vérifie la force du mot de passe."""
        # Vérification de la longueur minimale
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"

        # Vérification de la présence d'au moins une majuscule
        if not re.search(r'[A-Z]', password):
            return False, "Le mot de passe doit contenir au moins une majuscule"

        # Vérification de la présence d'au moins une minuscule
        if not re.search(r'[a-z]', password):
            return False, "Le mot de passe doit contenir au moins une minuscule"

        # Vérification de la présence d'au moins un chiffre
        if not re.search(r'\d', password):
            return False, "Le mot de passe doit contenir au moins un chiffre"

        # Vérification de la présence d'au moins un caractère spécial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Le mot de passe doit contenir au moins un caractère spécial"

        # Vérification des mots de passe courants
        common_passwords = {
            '123456', 'password', 'qwerty', 'abc123', 'admin123',
            'welcome', 'monkey123', 'football', 'password123', '12345678'
        }
        if password.lower() in common_passwords:
            return False, "Ce mot de passe est trop commun"

        return True, "Mot de passe valide"

    def set_gestion_catalogue(self, gestion_catalogue):
        """Définit l'instance de GestionCatalogue à utiliser."""
        self.gestion_catalogue = gestion_catalogue

    def calculer_moyenne_notes_film(self, film_id):
        """Calcule la moyenne des notes pour un film donné.
        
        Args:
            film_id (int): L'ID du film
            
        Returns:
            float: La moyenne des notes sur 5 étoiles
        """
        notes = []
        film_id_str = str(film_id)
        
        # Récupérer les notes des utilisateurs
        for user_notes in self.notes.values():
            if film_id_str in user_notes and 'note' in user_notes[film_id_str]:
                notes.append(user_notes[film_id_str]['note'])
        
        # Récupérer les notes des commentaires
        try:
            with open(self.base_path / "commentaires.json", 'r', encoding='utf-8') as f:
                commentaires = json.load(f)
                for commentaire in commentaires['comments']:  # Utiliser 'comments' au lieu de 'commentaires'
                    if commentaire['film_id'] == film_id:
                        # Convertir la note sur 5 si nécessaire
                        note = commentaire['note']
                        if note > 5:  # Si la note est sur 10
                            note = round(note / 2)
                        notes.append(note)
        except Exception as e:
            logging.error(f"Erreur lors de la lecture des commentaires: {e}")
        
        # Calculer la moyenne unique (sans doublons par utilisateur)
        if not notes:
            return 0
            
        # Calculer la moyenne
        moyenne = sum(notes) / len(notes)
        return moyenne

    def creer_utilisateur(self, username, password, email, role="user"):
        """Crée un nouvel utilisateur avec vérification du mot de passe."""
        if username in self.utilisateurs:
            return False, "Nom d'utilisateur déjà existant"
        
        # Forcer le rôle admin pour root
        if username == "root":
            role = "admin"
        
        # Ne pas vérifier le mot de passe pour l'utilisateur root
        if username != "root":
            # Vérification de la force du mot de passe
            password_valide, message = self.verifier_force_mdp(password)
            if not password_valide:
                return False, message
            
            # Vérification du format de l'email
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return False, "Format d'email invalide"
        
        self.utilisateurs[username] = {
            'password': password,  # Dans un vrai système, il faudrait hasher le mot de passe
            'email': email,
            'role': role,
            'date_creation': datetime.now().isoformat(),
            'derniere_connexion': None
        }
        self.notes[username] = {}
        self._sauvegarder_donnees()
        return True, "Compte créé avec succès"

    def supprimer_utilisateur(self, username):
        """Supprime un utilisateur."""
        if username in self.utilisateurs:
            del self.utilisateurs[username]
            if username in self.notes:
                del self.notes[username]
            self._sauvegarder_donnees()
            return True, "Utilisateur supprimé"
        return False, "Utilisateur non trouvé"

    def promouvoir_utilisateur(self, username):
        """Promouvoir un utilisateur en admin."""
        if username in self.utilisateurs and self.utilisateurs[username]['role'] == "user":
            self.utilisateurs[username]['role'] = "admin"
            self._sauvegarder_donnees()
            return True, "Utilisateur promu en admin"
        return False, "Promotion échouée"

    def verifier_connexion(self, username, password):
        """Vérifie les identifiants de connexion."""
        if username in self.utilisateurs and self.utilisateurs[username]['password'] == password:
            self.utilisateurs[username]['derniere_connexion'] = datetime.now().isoformat()
            self._sauvegarder_donnees()
            return True, self.utilisateurs[username]['role']
        return False, "Nom d'utilisateur ou mot de passe incorrect"

    def noter_film(self, username, film_id, note):
        """Enregistre la note d'un utilisateur pour un film.
        
        Args:
            username (str): Nom de l'utilisateur
            film_id (int): ID du film
            note (int): Note de 1 à 5 étoiles
        """
        if username not in self.notes:
            self.notes[username] = {}
        
        if not 1 <= note <= 5:
            return False, "La note doit être comprise entre 1 et 5 étoiles"
        
        # Convertir film_id en string pour le stockage
        film_id_str = str(film_id)
        
        # Enregistrer la note (sur 5 étoiles)
        self.notes[username][film_id_str] = {
            'note': note,
            'date': datetime.now().isoformat()
        }
        
        # Mettre à jour la note globale du film si possible
        if self.gestion_catalogue:
            nouvelle_moyenne = self.calculer_moyenne_notes_film(film_id)
            # Convertir la moyenne en note sur 10 pour le stockage dans films.csv
            note_sur_dix = round(nouvelle_moyenne * 2, 1)
            self.gestion_catalogue.mettre_a_jour_note_film(film_id, note_sur_dix)
        
        self._sauvegarder_donnees()
        return True, "Note enregistrée"

    def obtenir_notes_utilisateur(self, username):
        """Récupère toutes les notes d'un utilisateur."""
        return self.notes.get(username, {})

    def commenter_film(self, utilisateur, titre_film, commentaire):
        """Ajoute ou met à jour un commentaire pour un film."""
        if not titre_film in self.commentaires:
            self.commentaires[titre_film] = {}
            
        # Récupérer la note de l'utilisateur pour ce film
        note = self.notes.get(utilisateur, {}).get(titre_film, {}).get('note', 0)
            
        self.commentaires[titre_film][utilisateur] = {
            "texte": commentaire,
            "date": datetime.now().isoformat(),
            "note": note
        }
        self._sauvegarder_donnees()
        
    def obtenir_commentaires_film(self, titre_film):
        """Récupère tous les commentaires pour un film."""
        return self.commentaires.get(titre_film, {})
