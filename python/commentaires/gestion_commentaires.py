#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des commentaires.
"""

import json
from datetime import datetime
from pathlib import Path

class GestionCommentaires:
    """Classe gérant les commentaires des films."""
    
    def __init__(self):
        """Initialise le gestionnaire de commentaires."""
        self.base_path = Path("donnees")
        self.fichier = self.base_path / "commentaires.json"
        self._charger_donnees()

    def _charger_donnees(self):
        """Charge les commentaires depuis le fichier JSON."""
        try:
            with open(self.fichier, 'r', encoding='utf-8') as f:
                self.commentaires = json.load(f)
        except FileNotFoundError:
            self.commentaires = {"comments": []}
            self._sauvegarder()

    def _sauvegarder(self):
        """Sauvegarde les commentaires dans le fichier JSON."""
        self.base_path.mkdir(exist_ok=True)
        with open(self.fichier, 'w', encoding='utf-8') as f:
            json.dump(self.commentaires, f, indent=4, ensure_ascii=False)

    def ajouter_commentaire(self, film_id, utilisateur, note, commentaire):
        """Ajoute un commentaire pour un film.
        
        Args:
            film_id (int): ID du film
            utilisateur (str): Nom de l'utilisateur
            note (int): Note donnée par l'utilisateur (1-5)
            commentaire (str): Texte du commentaire
        """
        # Générer un nouvel ID
        nouvel_id = max([c['id'] for c in self.commentaires['comments']], default=0) + 1
        
        # Créer le nouveau commentaire
        nouveau_commentaire = {
            "id": nouvel_id,
            "film_id": film_id,
            "utilisateur": utilisateur,
            "note": note,
            "commentaire": commentaire,
            "date": datetime.now().isoformat()
        }
        
        # Ajouter le commentaire
        self.commentaires['comments'].append(nouveau_commentaire)
        
        # Sauvegarder les commentaires
        self._sauvegarder()
        
        return True, "Commentaire ajouté avec succès"

    def obtenir_commentaires_film(self, film_id):
        """Récupère tous les commentaires pour un film donné."""
        return [c for c in self.commentaires['comments'] if c['film_id'] == film_id]

    def supprimer_commentaire(self, comment_id):
        """Supprime un commentaire par son ID."""
        self.commentaires["comments"] = [
            c for c in self.commentaires["comments"] if c["id"] != comment_id
        ]
        self._sauvegarder()

    def modifier_commentaire(self, commentaire_id, nouveau_texte, nouvelle_note):
        """Modifie un commentaire existant."""
        for comment in self.commentaires["comments"]:
            if comment["id"] == commentaire_id:
                comment["commentaire"] = nouveau_texte
                comment["note"] = nouvelle_note
                comment["date"] = datetime.now().isoformat()
                self._sauvegarder()
                return True
        return False

    def calculer_moyenne_notes(self, film_id):
        """Calcule la moyenne des notes pour un film."""
        commentaires = self.obtenir_commentaires_film(film_id)
        if not commentaires:
            return 0
        return sum(c["note"] for c in commentaires) / len(commentaires)
