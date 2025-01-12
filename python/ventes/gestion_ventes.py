#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des ventes de films.
"""

import csv
import os
from datetime import datetime, timedelta
import random

class GestionVentes:
    """Classe gérant les opérations de vente."""
    
    def __init__(self, fichier_ventes="donnees/ventes.csv"):
        """Initialisation avec le chemin du fichier des ventes."""
        self.fichier_ventes = fichier_ventes
        self.ventes = []
        self.derniere_synchro = None
        
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(fichier_ventes), exist_ok=True)
        
        # Créer le fichier s'il n'existe pas
        if not os.path.exists(fichier_ventes):
            self._sauvegarder_ventes()
        
        self.charger_ventes()

    def enregistrer_vente(self, film_id, titre_film, quantite, prix_unitaire):
        """Enregistre une nouvelle vente."""
        # Générer un nouvel ID
        nouveau_id = max([vente['id'] for vente in self.ventes], default=0) + 1
        
        # Utiliser une date basée sur la dernière vente + quelques minutes
        if self.ventes:
            derniere_date = datetime.strptime(self.ventes[-1]['date'], "%Y-%m-%d %H:%M:%S")
            nouvelle_date = derniere_date + timedelta(minutes=random.randint(15, 60))
        else:
            nouvelle_date = datetime(2025, 1, 1, 9, 0)  # Commencer au 1er janvier 2025 à 9h
        
        vente = {
            'id': nouveau_id,
            'date': nouvelle_date.strftime("%Y-%m-%d %H:%M:%S"),
            'film_id': film_id,
            'titre_film': titre_film,
            'quantite': quantite,
            'prix_unitaire': prix_unitaire,
            'total': quantite * prix_unitaire
        }
        self.ventes.append(vente)
        self._sauvegarder_ventes()
        return vente

    def charger_ventes(self):
        """Charge l'historique des ventes depuis le fichier CSV."""
        try:
            with open(self.fichier_ventes, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                self.ventes = []
                for row in reader:
                    vente = {
                        'id': int(row['id']),
                        'date': row['date'],
                        'film_id': int(row['film_id']),
                        'titre_film': row['titre_film'],
                        'quantite': int(row['quantite']),
                        'prix_unitaire': float(row['prix_unitaire']),
                        'total': float(row['total'])
                    }
                    self.ventes.append(vente)
                    print(f"Chargement de la vente: {vente}")
        except FileNotFoundError:
            print(f"Le fichier {self.fichier_ventes} n'existe pas encore.")
        except Exception as e:
            print(f"Erreur lors du chargement des ventes: {str(e)}")    

    def _sauvegarder_ventes(self):
        """Sauvegarde les ventes dans le fichier CSV."""
        with open(self.fichier_ventes, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'date', 'film_id', 'titre_film', 'quantite', 
                         'prix_unitaire', 'total']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for vente in self.ventes:
                writer.writerow(vente)

    def calculer_revenu_total(self):
        """Calcule le revenu total de toutes les ventes."""
        return sum(vente['total'] for vente in self.ventes)

    def obtenir_rapport_ventes(self, date_debut=None, date_fin=None):
        """Génère un rapport des ventes pour une période donnée."""
        ventes_filtrees = self.ventes
        
        if date_debut:
            ventes_filtrees = [v for v in ventes_filtrees 
                             if datetime.strptime(v['date'], "%Y-%m-%d %H:%M:%S") >= date_debut]
        if date_fin:
            ventes_filtrees = [v for v in ventes_filtrees 
                             if datetime.strptime(v['date'], "%Y-%m-%d %H:%M:%S") <= date_fin]

        rapport = {
            'nombre_ventes': len(ventes_filtrees),
            'revenu_total': sum(v['total'] for v in ventes_filtrees),
            'ventes_par_film': {},
            'quantite_totale': sum(v['quantite'] for v in ventes_filtrees),
            'ventes_par_jour': {},
            'moyenne_vente': 0,
            'plus_grosse_vente': None,
            'films_plus_vendus': []
        }

        # Calcul des ventes par film et autres statistiques
        for vente in ventes_filtrees:
            # Ventes par film
            if vente['titre_film'] not in rapport['ventes_par_film']:
                rapport['ventes_par_film'][vente['titre_film']] = {
                    'quantite': 0,
                    'revenu': 0
                }
            rapport['ventes_par_film'][vente['titre_film']]['quantite'] += vente['quantite']
            rapport['ventes_par_film'][vente['titre_film']]['revenu'] += vente['total']
            
            # Ventes par jour
            date_jour = vente['date'].split()[0]
            if date_jour not in rapport['ventes_par_jour']:
                rapport['ventes_par_jour'][date_jour] = {
                    'nombre_ventes': 0,
                    'revenu': 0
                }
            rapport['ventes_par_jour'][date_jour]['nombre_ventes'] += 1
            rapport['ventes_par_jour'][date_jour]['revenu'] += vente['total']
            
            # Plus grosse vente
            if (not rapport['plus_grosse_vente'] or 
                vente['total'] > rapport['plus_grosse_vente']['total']):
                rapport['plus_grosse_vente'] = vente

        # Calcul de la moyenne des ventes
        if rapport['nombre_ventes'] > 0:
            rapport['moyenne_vente'] = rapport['revenu_total'] / rapport['nombre_ventes']

        # Films les plus vendus (top 3)
        films_tries = sorted(rapport['ventes_par_film'].items(), 
                           key=lambda x: x[1]['quantite'], 
                           reverse=True)
        rapport['films_plus_vendus'] = films_tries[:3]

        return rapport

    def annuler_vente(self, vente_id):
        """Annule une vente spécifique."""
        for i, vente in enumerate(self.ventes):
            if vente['id'] == vente_id:
                del self.ventes[i]
                self._sauvegarder_ventes()
                return True
        return False

    def reinitialiser_dates_ventes(self):
        """Réinitialise toutes les dates de vente à la date actuelle."""
        date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for vente in self.ventes:
            vente['date'] = date_actuelle
        self._sauvegarder_ventes()

    def mettre_a_jour_horloge(self):
        """Met à jour l'horloge interne avec l'heure système actuelle."""
        self.derniere_synchro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.derniere_synchro

    def filtrer_par_periode(self, debut=None, fin=None):
        """Filtre les ventes par période.
        
        Args:
            debut (datetime, optional): Date de début
            fin (datetime, optional): Date de fin. Si non spécifié, utilise la date actuelle.
        """
        if fin is None:
            fin = datetime.now()
        
        ventes_filtrees = self.ventes
        if debut:
            ventes_filtrees = [v for v in ventes_filtrees 
                             if datetime.strptime(v['date'], "%Y-%m-%d %H:%M:%S") >= debut]
        if fin:
            ventes_filtrees = [v for v in ventes_filtrees 
                             if datetime.strptime(v['date'], "%Y-%m-%d %H:%M:%S") <= fin]
        
        return ventes_filtrees

    def trier_par_date(self, descendant=True):
        """Trie les ventes par date."""
        return sorted(self.ventes, 
                     key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"), 
                     reverse=descendant)

    def generer_ventes_fictives(self, films):
        """Génère des ventes fictives à partir du 1er janvier 2025."""
        from datetime import datetime, timedelta
        import random

        # Vider les ventes existantes
        self.ventes = []
        
        # Date de début : 1er janvier 2025
        date_debut = datetime(2025, 1, 1)
        date_fin = datetime(2025, 1, 31)  # Générer pour tout le mois de janvier
        
        # Générer des ventes pour chaque jour
        current_date = date_debut
        while current_date <= date_fin:
            # Générer 3 à 8 ventes par jour
            nb_ventes = random.randint(3, 8)
            for _ in range(nb_ventes):
                # Choisir un film au hasard
                film = random.choice(films)
                
                # Générer une heure aléatoire pour la vente
                heure = random.randint(9, 21)  # Entre 9h et 21h
                minute = random.randint(0, 59)
                date_vente = current_date.replace(hour=heure, minute=minute)
                
                # Générer une quantité et un prix aléatoires
                quantite = random.randint(1, 5)  # Augmenter la quantité max possible
                prix_unitaire = random.uniform(8.99, 14.99)
                
                # Créer la vente
                vente = {
                    'id': len(self.ventes) + 1,
                    'date': date_vente.strftime("%Y-%m-%d %H:%M:%S"),
                    'film_id': film['id'],
                    'titre_film': film['titre'],
                    'quantite': quantite,
                    'prix_unitaire': round(prix_unitaire, 2),
                    'total': round(quantite * prix_unitaire, 2)
                }
                self.ventes.append(vente)
            
            current_date += timedelta(days=1)
        
        # Trier les ventes par date
        self.ventes.sort(key=lambda x: x['date'])
        
        # Sauvegarder les ventes générées
        self._sauvegarder_ventes()
