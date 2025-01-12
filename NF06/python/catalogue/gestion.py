#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion du catalogue de films.
"""

import csv
import os
from datetime import datetime

class GestionCatalogue:
    """Classe gérant les opérations sur le catalogue de films."""
    
    def __init__(self, fichier_catalogue="donnees/films.csv"):
        """Initialisation avec le chemin du fichier catalogue."""
        self.fichier_catalogue = fichier_catalogue
        self.films = []
        self.charger_catalogue()

    def ajouter_film(self, film_data):
        """Ajoute un nouveau film au catalogue.
        
        Args:
            film_data (dict): Dictionnaire contenant les données du film
                (titre, realisateur, annee, genre, note, acteurs)
        """
        # Vérifier les données requises
        required_fields = ['titre', 'realisateur', 'annee', 'genre', 'note', 'acteurs']
        for field in required_fields:
            if field not in film_data:
                raise ValueError(f"Le champ '{field}' est requis")

        # Générer un nouvel ID
        nouveau_id = max([film['id'] for film in self.films], default=0) + 1
        
        # Créer le film avec l'ID et la date d'ajout
        film = {
            'id': nouveau_id,
            'titre': film_data['titre'],
            'realisateur': film_data['realisateur'],
            'annee': int(film_data['annee']),
            'genre': film_data['genre'],
            'note': float(film_data['note']),
            'acteurs': film_data['acteurs'],
            'date_ajout': datetime.now().isoformat()  # Ajouter la date au format ISO
        }
        
        # Ajouter et sauvegarder
        self.films.append(film)
        self._sauvegarder_catalogue()
        return film

    def charger_catalogue(self):
        """Charge le catalogue depuis le fichier CSV."""
        try:
            with open(self.fichier_catalogue, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                self.films = []
                for row in reader:
                    film = {
                        'id': int(row['id']),
                        'titre': row['titre'],
                        'realisateur': row['realisateur'],
                        'annee': int(row['annee']),
                        'genre': row['genre'],
                        'note': float(row['note']),
                        'acteurs': row['acteurs'].split('|'),
                        'date_ajout': row.get('date_ajout', datetime.now().isoformat())  # Valeur par défaut pour les films existants
                    }
                    self.films.append(film)
        except FileNotFoundError:
            print(f"Le fichier {self.fichier_catalogue} n'existe pas encore.")

    def _sauvegarder_catalogue(self):
        """Sauvegarde le catalogue dans le fichier CSV."""
        with open(self.fichier_catalogue, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'titre', 'realisateur', 'annee', 'genre', 'note', 'acteurs', 'date_ajout']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for film in self.films:
                film_data = film.copy()
                film_data['acteurs'] = '|'.join(film_data['acteurs'])
                writer.writerow(film_data)

    def filtrer_par_genre(self, genre):
        """Filtre les films par genre."""
        return [f for f in self.films if f['genre'].lower() == genre.lower()]

    def filtrer_par_annee(self, annee):
        """Filtre les films par année."""
        return [f for f in self.films if f['annee'] == annee]

    def trier_par_note(self, descendant=True):
        """Trie les films par note."""
        return sorted(self.films, key=lambda x: x['note'], reverse=descendant)

    def trier_par_date_ajout(self, descendant=True):
        """Trie les films par date d'ajout."""
        return sorted(self.films, key=lambda x: x['date_ajout'], reverse=descendant)

    def filtrer_par_periode(self, debut, fin=None):
        """Filtre les films par période d'ajout.
        
        Args:
            debut (str): Date de début au format ISO
            fin (str, optional): Date de fin au format ISO. Si non spécifié, utilise la date actuelle.
        """
        if fin is None:
            fin = datetime.now().isoformat()
        
        return [f for f in self.films 
                if debut <= f['date_ajout'] <= fin]

    def reinitialiser_dates_ajout(self):
        """Réinitialise toutes les dates d'ajout à la date actuelle."""
        date_actuelle = datetime.now().isoformat()
        for film in self.films:
            film['date_ajout'] = date_actuelle
        self._sauvegarder_catalogue()

    def mettre_a_jour_horloge(self):
        """Met à jour l'horloge interne avec l'heure système actuelle."""
        self.derniere_synchro = datetime.now().isoformat()
        return self.derniere_synchro

    def obtenir_statistiques(self):
        """Génère des statistiques sur le catalogue."""
        stats = {
            'total_films': len(self.films),
            'films_par_genre': {},
            'films_par_annee': {},
            'note_moyenne': sum(f['note'] for f in self.films) / len(self.films) if self.films else 0
        }
        
        # Compter les films par genre
        for film in self.films:
            genre = film['genre']
            stats['films_par_genre'][genre] = stats['films_par_genre'].get(genre, 0) + 1
            
            annee = film['annee']
            stats['films_par_annee'][annee] = stats['films_par_annee'].get(annee, 0) + 1
        
        return stats

    def obtenir_film_par_titre(self, titre):
        """Obtient un film par son titre.
        
        Args:
            titre (str): Le titre du film à rechercher
            
        Returns:
            dict: Le film trouvé ou None si aucun film n'est trouvé
        """
        for film in self.films:
            if film['titre'].lower() == titre.lower():
                return film
        return None

    def rechercher_films(self, terme_recherche):
        """Recherche des films par titre, réalisateur ou acteurs."""
        terme_recherche = terme_recherche.lower()
        resultats = []
        
        for film in self.films:
            if (terme_recherche in film['titre'].lower() or
                terme_recherche in film['realisateur'].lower() or
                any(terme_recherche in acteur.lower() for acteur in film['acteurs'])):
                resultats.append(film)
                
        return resultats

    def mettre_a_jour_note_film(self, film_id, nouvelle_note):
        """Met à jour la note d'un film.
        
        Args:
            film_id (int): L'ID du film à mettre à jour
            nouvelle_note (float): La nouvelle note moyenne du film (sur 10)
        
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        for film in self.films:
            if film['id'] == film_id:
                # S'assurer que la note est sur 10
                if nouvelle_note > 5:
                    film['note'] = round(nouvelle_note, 1)
                else:
                    film['note'] = round(nouvelle_note * 2, 1)
                self._sauvegarder_catalogue()
                return True
        return False
