#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Point d'entrée principal de l'application de recommandation de films CinéFlix.

Ce module est responsable de :
1. L'initialisation de l'environnement de l'application
2. La configuration du système de journalisation
3. La vérification et création des dossiers nécessaires
4. Le lancement de l'interface graphique

Auteurs: Moss'Ab Mirande-Ney et Arnaud Goddard
Date: Janvier 2025
"""

# Imports standards pour la gestion des fichiers et du système
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import tkinter as tk

# Import de l'interface graphique
from python.interface.gui import ApplicationPrincipale

# Configuration des chemins de base
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)

def configurer_journaux():
    """
    Configure le système de journalisation de l'application.
    
    Cette fonction :
    - Crée le dossier 'logs' s'il n'existe pas
    - Configure le format des logs (horodatage, niveau, message)
    - Met en place la sortie vers un fichier et la console
    """
    log_dir = Path(current_dir) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,  # Niveau de détail des logs
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app.log'),  # Sortie fichier
            logging.StreamHandler()  # Sortie console
        ]
    )

def verifier_configuration():
    """
    Vérifie et initialise la configuration de l'application.
    
    Cette fonction :
    - Crée les dossiers nécessaires (logs, config)
    - Initialise le fichier de configuration par défaut s'il n'existe pas
    - Définit les paramètres de base (thème, langue, etc.)
    """
    # Création des dossiers essentiels
    for dossier in ['logs', 'config']:
        (Path(current_dir) / dossier).mkdir(exist_ok=True)
    
    # Vérification et création du fichier de configuration
    config_file = Path(current_dir) / 'config' / 'config.json'
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                "theme": "dark",        # Thème par défaut
                "langue": "fr",         # Langue par défaut
                "max_recommandations": 5  # Nombre max de recommandations
            }, f, indent=4)

def main():
    """
    Fonction principale de l'application.
    
    Cette fonction :
    1. Configure l'environnement (logs, config)
    2. Initialise la fenêtre principale
    3. Lance l'interface graphique
    4. Gère les erreurs potentielles
    """
    try:
        # Étape 1 : Configuration de l'environnement
        configurer_journaux()
        verifier_configuration()
        
        # Étape 2 : Création de la fenêtre principale
        root = tk.Tk()
        root.title("CinéFlix")
        root.geometry("1200x800")  # Taille par défaut
        root.minsize(800, 600)     # Taille minimale
        
        # Étape 3 : Lancement de l'application
        app = ApplicationPrincipale(root)
        root.mainloop()
        
    except Exception as e:
        # Gestion des erreurs avec journalisation
        logging.error(f'Erreur: {str(e)}', exc_info=True)
        sys.exit(1)

# Point d'entrée du programme
if __name__ == "__main__":
    main()