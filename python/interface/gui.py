#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module contenant l'interface graphique principale de l'application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging

from ..catalogue.gestion import GestionCatalogue
from ..ventes.gestion_ventes import GestionVentes
from ..utilisateurs.gestion_utilisateurs import GestionUtilisateurs
from ..commentaires.gestion_commentaires import GestionCommentaires

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import dates as mdates
import json
import os
import numpy as np
import re
import uuid
import json
from pathlib import Path

class FenetreConnexion(tk.Toplevel):
    """Fenêtre de connexion/inscription."""
    
    def __init__(self, master, callback_connexion):
        super().__init__(master)
        self.title("Connexion - CinéFlix")
        self.geometry("400x600")
        
        # Configuration du style
        style = ttk.Style()
        style.configure('Custom.TFrame', background='#1e1e1e')
        style.configure('Custom.TLabel', 
                       background='#1e1e1e',
                       foreground='#ffffff',
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel',
                       background='#1e1e1e',
                       foreground='#ffffff',
                       font=('Segoe UI', 24))
        style.configure('Custom.TButton',
                       padding=10,
                       background='#007acc',
                       foreground='white')

        # Configuration de la fenêtre
        self.configure(bg='#1e1e1e')
        self.callback_connexion = callback_connexion
        self.gestion_utilisateurs = GestionUtilisateurs()
        self.mode_inscription = False
        
        # Frame principal
        main_frame = ttk.Frame(self, style='Custom.TFrame')
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Titre
        titre_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        titre_frame.pack(fill=tk.X, pady=(0, 40))
        self.titre_label = ttk.Label(titre_frame, text="Connexion", style='Title.TLabel')
        self.titre_label.pack(anchor='center')
        
        # Frame pour les champs de saisie
        self.form_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        self.form_frame.pack(fill=tk.X, padx=20)
        
        # Nom d'utilisateur
        username_label = ttk.Label(self.form_frame, text="Nom d'utilisateur:", style='Custom.TLabel')
        username_label.pack(anchor='w', pady=(0, 5))
        self.entry_username = tk.Entry(self.form_frame, 
                                     bg='#2d2d2d',
                                     fg='white',
                                     insertbackground='white',
                                     relief='flat',
                                     font=('Segoe UI', 10))
        self.entry_username.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Mot de passe
        password_label = ttk.Label(self.form_frame, text="Mot de passe:", style='Custom.TLabel')
        password_label.pack(anchor='w', pady=(0, 5))
        self.entry_password = tk.Entry(self.form_frame,
                                     show="•",
                                     bg='#2d2d2d',
                                     fg='white',
                                     insertbackground='white',
                                     relief='flat',
                                     font=('Segoe UI', 10))
        self.entry_password.pack(fill=tk.X, pady=(0, 25), ipady=5)
        
        # Email (caché par défaut)
        self.entry_email = tk.Entry(self.form_frame,
                                  bg='#2d2d2d',
                                  fg='white',
                                  insertbackground='white',
                                  relief='flat',
                                  font=('Segoe UI', 10))
        self.entry_email.pack_forget()
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill=tk.X, padx=20)
        
        # Bouton de connexion
        self.btn_connexion = tk.Button(button_frame,
                                     text="Se connecter",
                                     command=self.connexion,
                                     bg='#007acc',
                                     fg='white',
                                     font=('Segoe UI', 10),
                                     relief='flat',
                                     activebackground='#005999',
                                     activeforeground='white')
        self.btn_connexion.pack(fill=tk.X, pady=(0, 10))
        
        # Bouton créer un compte
        self.btn_switch = tk.Button(button_frame,
                                  text="Créer un compte",
                                  command=self.switch_mode,
                                  bg='#007acc',
                                  fg='white',
                                  font=('Segoe UI', 10),
                                  relief='flat',
                                  activebackground='#005999',
                                  activeforeground='white')
        self.btn_switch.pack(fill=tk.X)
        
        # Frame pour les exigences de mot de passe (caché par défaut)
        self.frame_exigences = ttk.Frame(main_frame, style='Custom.TFrame')
        self.frame_exigences.pack(fill=tk.X, pady=10)
        self.frame_exigences.pack_forget()
        
        # Labels pour les exigences
        self.exigences = {
            'longueur': ttk.Label(self.frame_exigences, text="❌ 8 caractères minimum", style='Custom.TLabel'),
            'majuscule': ttk.Label(self.frame_exigences, text="❌ Une majuscule", style='Custom.TLabel'),
            'minuscule': ttk.Label(self.frame_exigences, text="❌ Une minuscule", style='Custom.TLabel'),
            'chiffre': ttk.Label(self.frame_exigences, text="❌ Un chiffre", style='Custom.TLabel'),
            'special': ttk.Label(self.frame_exigences, text="❌ Un caractère spécial", style='Custom.TLabel')
        }
        
        for label in self.exigences.values():
            label.pack(anchor='w')
        
        # Centrer la fenêtre
        self.transient(master)
        self.grab_set()
        
        # Binding des événements
        self.entry_password.bind('<KeyRelease>', self.verifier_mdp_temps_reel)
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus())
        self.entry_password.bind('<Return>', lambda e: self.connexion())

    def on_entry_click(self, entry, default_text):
        """Gère le focus sur un champ de saisie."""
        if entry.get() == default_text:
            entry.delete(0, tk.END)
            if entry == self.entry_password:
                entry.config(show="•")
    
    def on_focus_out(self, entry, default_text):
        """Gère la perte de focus d'un champ de saisie."""
        if entry.get() == '':
            entry.insert(0, default_text)
            if entry == self.entry_password and entry.get() == default_text:
                entry.config(show="")
    
    def verifier_mdp_temps_reel(self, event=None):
        """Vérifie la force du mot de passe en temps réel."""
        if not self.mode_inscription:
            return
        
        password = self.entry_password.get()
        if password == "Mot de passe":
            return
        
        # Vérification de la longueur
        self.exigences['longueur'].config(
            text=("✅" if len(password) >= 8 else "❌") + " 8 caractères minimum"
        )
        
        # Vérification majuscule
        self.exigences['majuscule'].config(
            text=("✅" if re.search(r'[A-Z]', password) else "❌") + " Une majuscule"
        )
        
        # Vérification minuscule
        self.exigences['minuscule'].config(
            text=("✅" if re.search(r'[a-z]', password) else "❌") + " Une minuscule"
        )
        
        # Vérification chiffre
        self.exigences['chiffre'].config(
            text=("✅" if re.search(r'\d', password) else "❌") + " Un chiffre"
        )
        
        # Vérification caractère spécial
        self.exigences['special'].config(
            text=("✅" if re.search(r'[!@#$%^&*(),.?":{}|<>]', password) else "❌") + " Un caractère spécial"
        )
    
    def switch_mode(self):
        """Bascule entre mode connexion et inscription."""
        self.mode_inscription = not self.mode_inscription
        if self.mode_inscription:
            self.titre_label.config(text="Inscription")
            self.btn_connexion.config(text="S'inscrire")
            self.btn_switch.config(text="Déjà un compte ?")
            
            # Ajouter le champ email
            email_label = ttk.Label(self.form_frame, text="Email:", style='Custom.TLabel')
            email_label.pack(anchor='w', pady=(0, 5))
            self.entry_email.pack(fill=tk.X, pady=(0, 15), ipady=5)
            
            # Afficher les exigences
            self.frame_exigences.pack(fill=tk.X, pady=10)
            self.geometry("400x600")  # Agrandir la fenêtre pour les exigences
        else:
            self.titre_label.config(text="Connexion")
            self.btn_connexion.config(text="Se connecter")
            self.btn_switch.config(text="Créer un compte")
            self.entry_email.pack_forget()
            self.frame_exigences.pack_forget()
            self.geometry("400x400")  # Réduire la fenêtre
    
    def connexion(self):
        """Gère la connexion ou l'inscription."""
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        if self.mode_inscription:
            email = self.entry_email.get()
            succes, message = self.gestion_utilisateurs.creer_utilisateur(username, password, email)
        else:
            succes, message = self.gestion_utilisateurs.verifier_connexion(username, password)
        
        if succes:
            self.callback_connexion(username)
            self.destroy()
        else:
            messagebox.showerror("Erreur", message)

class FenetreDetailsFilm(tk.Toplevel):
    """Fenêtre popup pour afficher les détails d'un film."""
    
    def __init__(self, master, film, gestion_utilisateurs, utilisateur_connecte):
        super().__init__(master)
        self.film = film
        self.gestion_utilisateurs = gestion_utilisateurs
        self.utilisateur_connecte = utilisateur_connecte
        self.gestion_commentaires = GestionCommentaires()
        
        # Configuration de la fenêtre
        self.title(f"{film['titre']} - Détails")
        self.geometry("1000x800")
        self.configure(bg='#1e1e1e')
        
        # Style pour les commentaires
        style = ttk.Style()
        style.configure("Commentaire.TFrame", background='#2d2d2d')
        style.configure("CommentaireHeader.TLabel", 
                       background='#2d2d2d',
                       foreground='#ffffff',
                       font=('Segoe UI', 10, 'bold'))
        style.configure("CommentaireNote.TLabel", 
                       background='#2d2d2d',
                       foreground='#ffffff',
                       font=('Segoe UI', 10))
        style.configure("CommentaireTexte.TLabel", 
                       background='#2d2d2d',
                       foreground='#ffffff',
                       font=('Segoe UI', 10),
                       wraplength=500)
        
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame gauche pour l'affiche et les infos
        frame_gauche = ttk.Frame(main_frame)
        frame_gauche.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Affiche du film (placeholder blanc pour l'instant)
        canvas_affiche = tk.Canvas(frame_gauche, width=300, height=450, bg='white')
        canvas_affiche.pack(pady=(0, 10))
        
        # Informations du film
        info_frame = ttk.Frame(frame_gauche)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text=film['titre'], 
                 font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text=f"Réalisé par {film['realisateur']}",
                 font=('Segoe UI', 12)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Genre: {film['genre']}",
                 font=('Segoe UI', 10)).pack(anchor='w')
        ttk.Label(info_frame, text=f"Année: {film['annee']}",
                 font=('Segoe UI', 10)).pack(anchor='w')
        
        # Frame droite pour la note et les commentaires
        frame_droite = ttk.Frame(main_frame)
        frame_droite.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Note moyenne
        note_moyenne = film['note']  # La note est déjà sur 10 dans le film
        self.label_note_globale = ttk.Label(frame_droite, 
                                          text=f"Note globale: {note_moyenne}/10", 
                                          font=('Segoe UI', 12, 'bold'))
        self.label_note_globale.pack(anchor='w')
        
        # Affichage des étoiles pour la note moyenne
        note_etoiles = note_moyenne / 2
        etoiles_moyenne = "★" * int(note_etoiles) + "☆" * (5 - int(note_etoiles))
        self.label_etoiles_moyenne = ttk.Label(frame_droite, 
                                             text=etoiles_moyenne, 
                                             font=('Segoe UI', 20))
        self.label_etoiles_moyenne.pack(anchor='w', pady=(0, 20))
        
        # Votre note
        ttk.Label(frame_droite, text="Votre note:", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        
        # Frame pour les boutons d'étoiles
        self.frame_etoiles = ttk.Frame(frame_droite)
        self.frame_etoiles.pack(fill=tk.X)
        
        self.note_utilisateur = tk.IntVar()
        
        # Récupérer la note existante de l'utilisateur (déjà sur 5 étoiles)
        notes_utilisateur = self.gestion_utilisateurs.notes.get(self.utilisateur_connecte, {})
        note_existante = notes_utilisateur.get(str(film['id']), {}).get('note', 0)
        self.note_utilisateur.set(note_existante)
        
        # Créer les boutons d'étoiles
        for i in range(5):
            btn = ttk.Button(self.frame_etoiles, text="★" if i < note_existante else "☆",
                           command=lambda x=i: self.noter_film(x + 1))
            btn.pack(side=tk.LEFT)
        
        # Séparateur
        ttk.Separator(frame_droite, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Votre commentaire
        ttk.Label(frame_droite, text="Ajouter un commentaire:", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.text_commentaire = tk.Text(frame_droite, height=4, 
                                      bg='#2d2d2d', fg='white',
                                      font=('Segoe UI', 10))
        self.text_commentaire.pack(fill=tk.X, pady=(0, 10))
        
        # Bouton Enregistrer
        ttk.Button(frame_droite, text="Enregistrer",
                  command=self.sauvegarder).pack(anchor='e', pady=(0, 20))
        
        # Séparateur
        ttk.Separator(frame_droite, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Autres commentaires
        ttk.Label(frame_droite, text="Commentaires des utilisateurs", 
                 font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Canvas et scrollbar pour les commentaires
        self.canvas_commentaires = tk.Canvas(frame_droite, bg='#1e1e1e', 
                                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_droite, orient="vertical", 
                                command=self.canvas_commentaires.yview)
        
        # Frame pour contenir tous les commentaires
        self.frame_tous_commentaires = ttk.Frame(self.canvas_commentaires)
        
        # Configuration du canvas
        self.canvas_commentaires.configure(yscrollcommand=scrollbar.set)
        self.canvas_commentaires.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ajouter le frame au canvas
        self.canvas_window = self.canvas_commentaires.create_window(
            (0, 0), window=self.frame_tous_commentaires, anchor="nw"
        )
        
        # Configurer le scroll
        self.frame_tous_commentaires.bind("<Configure>", self.on_frame_configure)
        self.canvas_commentaires.bind("<Configure>", self.on_canvas_configure)
        
        # Charger les commentaires existants
        self.charger_commentaires()
        
        # Centrer la fenêtre par rapport au parent
        self.transient(master)
        self.grab_set()
    
    def on_frame_configure(self, event=None):
        """Mettre à jour le scrollregion quand la taille du frame change."""
        self.canvas_commentaires.configure(scrollregion=self.canvas_commentaires.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Mettre à jour la largeur du frame quand le canvas change."""
        self.canvas_commentaires.itemconfig(self.canvas_window, width=event.width)
    
    def noter_film(self, note):
        """Met à jour l'affichage des étoiles et enregistre la note."""
        # Mettre à jour la note dans l'interface
        self.note_utilisateur.set(note)
        
        # Mettre à jour l'affichage des boutons d'étoiles
        for widget in self.frame_etoiles.winfo_children():
            widget.destroy()
        
        for i in range(5):
            btn = ttk.Button(self.frame_etoiles, text="★" if i < note else "☆",
                           command=lambda x=i: self.noter_film(x + 1))
            btn.pack(side=tk.LEFT)
        
        # Enregistrer la note
        self.gestion_utilisateurs.noter_film(self.utilisateur_connecte, self.film['id'], note)
        
        # Recharger les données du film depuis le catalogue
        for film in self.gestion_utilisateurs.gestion_catalogue.films:
            if film['id'] == self.film['id']:
                self.film = film
                break
        
        # Mettre à jour l'affichage de la note moyenne
        note_moyenne = self.film['note']  # La note est sur 10 dans le film
        self.label_note_globale.configure(text=f"Note globale: {note_moyenne}/10")
        
        # Mettre à jour les étoiles de la note moyenne
        note_etoiles = note_moyenne / 2
        etoiles_moyenne = "★" * int(note_etoiles) + "☆" * (5 - int(note_etoiles))
        self.label_etoiles_moyenne.configure(text=etoiles_moyenne)

    def charger_commentaires(self):
        """Charge et affiche les commentaires existants."""
        # Effacer les commentaires existants
        for widget in self.frame_tous_commentaires.winfo_children():
            widget.destroy()
        
        # Récupérer les commentaires pour ce film
        commentaires = self.gestion_commentaires.obtenir_commentaires_film(self.film['id'])
        
        if not commentaires:
            ttk.Label(self.frame_tous_commentaires, 
                     text="Aucun commentaire pour ce film",
                     style="CommentaireTexte.TLabel").pack(pady=10)
            return
        
        # Afficher chaque commentaire
        for commentaire in commentaires:
            frame_commentaire = ttk.Frame(self.frame_tous_commentaires, 
                                        style="Commentaire.TFrame")
            frame_commentaire.pack(fill=tk.X, pady=5, padx=5)
            
            # En-tête du commentaire (utilisateur et date)
            frame_header = ttk.Frame(frame_commentaire, style="Commentaire.TFrame")
            frame_header.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame_header, 
                     text=commentaire['utilisateur'],
                     style="CommentaireHeader.TLabel").pack(side=tk.LEFT)
            
            # Convertir la date ISO en objet datetime
            date = datetime.fromisoformat(commentaire['date'])
            date_str = date.strftime("%d/%m/%Y %H:%M")
            
            ttk.Label(frame_header,
                     text=date_str,
                     style="CommentaireHeader.TLabel").pack(side=tk.RIGHT)
            
            # Note en étoiles
            note = commentaire['note']
            if note > 5:  # Convertir la note sur 5 si nécessaire
                note = round(note / 2)
            etoiles = "★" * note + "☆" * (5 - note)
            ttk.Label(frame_commentaire,
                     text=etoiles,
                     style="CommentaireNote.TLabel").pack(anchor='w', padx=5)
            
            # Texte du commentaire
            ttk.Label(frame_commentaire,
                     text=commentaire['commentaire'],
                     style="CommentaireTexte.TLabel").pack(anchor='w', padx=5, pady=(0, 5))
            
            # Séparateur entre les commentaires
            ttk.Separator(self.frame_tous_commentaires, 
                         orient='horizontal').pack(fill=tk.X, pady=5)

    def sauvegarder(self):
        """Sauvegarde la note et le commentaire."""
        commentaire = self.text_commentaire.get("1.0", tk.END).strip()
        note = self.note_utilisateur.get()
        
        if commentaire:
            # Ajouter le commentaire avec la note
            self.gestion_commentaires.ajouter_commentaire(
                self.film['id'],
                self.utilisateur_connecte,
                note,  # La note est déjà sur 5 étoiles
                commentaire
            )
            
            # Recharger les commentaires
            self.charger_commentaires()
            
            # Effacer le champ de commentaire
            self.text_commentaire.delete("1.0", tk.END)
        
        # Enregistrer la note dans les notes utilisateur
        self.gestion_utilisateurs.noter_film(
            self.utilisateur_connecte,
            self.film['id'],
            note
        )
        
        # Recharger les données du film depuis le catalogue
        for film in self.gestion_utilisateurs.gestion_catalogue.films:
            if film['id'] == self.film['id']:
                self.film = film
                break
        
        # Mettre à jour l'affichage de la note moyenne
        note_moyenne = self.film['note']  # La note est sur 10 dans le film
        self.label_note_globale.configure(text=f"Note globale: {note_moyenne}/10")
        
        # Mettre à jour les étoiles de la note moyenne
        note_etoiles = note_moyenne / 2
        etoiles_moyenne = "★" * int(note_etoiles) + "☆" * (5 - int(note_etoiles))
        self.label_etoiles_moyenne.configure(text=etoiles_moyenne)

class ApplicationPrincipale(tk.Frame):
    """Classe principale de l'interface graphique."""
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("CinéFlix - Système de Recommandation")
        self.master.geometry("1200x800")
        self.master.configure(bg='#1E1E1E')
        
        # Initialisation des gestionnaires
        self.catalogue = GestionCatalogue()
        self.ventes = GestionVentes()
        self.gestion_utilisateurs = GestionUtilisateurs()
        self.utilisateur_connecte = None
        
        # Connecter GestionCatalogue à GestionUtilisateurs
        self.gestion_utilisateurs.set_gestion_catalogue(self.catalogue)
        
        # Générer des ventes fictives si aucune vente n'existe
        if not self.ventes.ventes:
            self.ventes.generer_ventes_fictives(self.catalogue.films)
        
        # Synchroniser l'horloge
        self.derniere_synchro = self.catalogue.mettre_a_jour_horloge()
        self.derniere_synchro_ventes = self.ventes.mettre_a_jour_horloge()
        
        # Timer pour la mise à jour de l'horloge (toutes les minutes)
        self.master.after(60000, self.synchroniser_horloge)
        
        # Créer l'utilisateur root s'il n'existe pas
        succes, _ = self.gestion_utilisateurs.verifier_connexion("root", "toor")
        if not succes:
            self.gestion_utilisateurs.creer_utilisateur("root", "toor", "root@cineflix.com", role="admin")
            # Ajouter quelques notes pour l'utilisateur root
            films_notes = {
                "Inception": 5,
                "The Dark Knight": 5,
                "Pulp Fiction": 4,
                "The Godfather": 5,
                "Matrix": 4
            }
            for titre, note in films_notes.items():
                self.gestion_utilisateurs.noter_film("root", titre, note)
        
        # Afficher la fenêtre de connexion
        self.afficher_connexion()
    
    def afficher_connexion(self):
        """Affiche la fenêtre de connexion."""
        # Détruire toute fenêtre de connexion existante
        for widget in self.master.winfo_children():
            if isinstance(widget, FenetreConnexion):
                widget.destroy()
                
        fenetre_connexion = FenetreConnexion(self.master, self.connexion_reussie)
        fenetre_connexion.protocol("WM_DELETE_WINDOW", lambda: self.fermeture_fenetre_connexion(fenetre_connexion))
        fenetre_connexion.transient(self.master)
        fenetre_connexion.grab_set()
    
    def fermeture_fenetre_connexion(self, fenetre):
        """Gère la fermeture de la fenêtre de connexion."""
        reponse = tk.messagebox.askyesno(
            "Quitter",
            "Voulez-vous vraiment quitter l'application ?",
            parent=fenetre
        )
        if reponse:
            self.master.quit()
        else:
            fenetre.focus_set()

    def connexion_reussie(self, username):
        """Callback appelé après une connexion réussie."""
        self.utilisateur_connecte = username
        self.configurer_style()
        self.pack(fill=tk.BOTH, expand=True)
        self.creer_widgets()
        
        # Mettre à jour les listes accessibles à tous les utilisateurs
        self.mettre_a_jour_liste_films()
        self.mettre_a_jour_recommandations()
        
        # Mettre à jour les listes réservées à l'admin
        if self.est_admin():
            self.mettre_a_jour_liste_ventes()
            self.rafraichir_stats()
    
    def est_admin(self):
        """Vérifie si l'utilisateur actuel a les droits d'administration."""
        return self.gestion_utilisateurs.utilisateurs.get(self.utilisateur_connecte, {}).get('role') == 'admin'

    def configurer_style(self):
        """Configure le style de l'interface pour un design moderne et épuré."""
        style = ttk.Style()
        style.theme_use('default')

        # Palette de couleurs moderne et professionnelle
        COLORS = {
            'bg': '#1E1E1E',  # Fond sombre
            'primary': '#007AFF',  # Bleu vif
            'secondary': '#2D2D2D',  # Gris foncé
            'text': '#FFFFFF',  # Texte blanc
            'accent': '#FF3B30',  # Rouge pour les actions importantes
            'success': '#34C759',  # Vert pour les confirmations
            'warning': '#FF9500'  # Orange pour les avertissements
        }

        # Style global
        style.configure('.',
            background=COLORS['bg'],
            foreground=COLORS['text'],
            font=('Segoe UI', 10),
            relief='flat')

        # Style des fenêtres
        style.configure('TFrame',
            background=COLORS['bg'])

        # Style des onglets
        style.configure('TNotebook',
            background=COLORS['bg'],
            padding=5)
        style.configure('TNotebook.Tab',
            padding=[20, 10],
            background=COLORS['secondary'],
            foreground=COLORS['text'])
        style.map('TNotebook.Tab',
            background=[('selected', COLORS['primary'])],
            foreground=[('selected', COLORS['text'])])

        # Style des boutons
        style.configure('TButton',
            background=COLORS['primary'],
            foreground=COLORS['text'],
            padding=[15, 8],
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            borderwidth=0)
        style.map('TButton',
            background=[('active', '#0056b3')],
            relief=[('pressed', 'flat')])

        # Style des entrées
        style.configure('TEntry',
            fieldbackground=COLORS['secondary'],
            foreground=COLORS['text'],
            padding=[10, 8],
            relief='flat',
            borderwidth=1)
        style.map('TEntry',
            fieldbackground=[('focus', COLORS['secondary'])],
            bordercolor=[('focus', COLORS['primary'])])

        # Style des combobox
        style.configure('TCombobox',
            background=COLORS['secondary'],
            fieldbackground=COLORS['secondary'],
            foreground=COLORS['text'],
            padding=[8, 6],
            relief='flat',
            borderwidth=1)
        style.map('TCombobox',
            fieldbackground=[('readonly', COLORS['secondary'])],
            selectbackground=[('readonly', COLORS['primary'])])

        # Style de la liste
        style.configure('Treeview',
            background=COLORS['secondary'],
            foreground=COLORS['text'],
            fieldbackground=COLORS['secondary'],
            rowheight=40,
            relief='flat',
            borderwidth=0,
            font=('Segoe UI', 10))
        style.configure('Treeview.Heading',
            background=COLORS['bg'],
            foreground=COLORS['text'],
            relief='flat',
            font=('Segoe UI', 10, 'bold'))
        style.map('Treeview',
            background=[('selected', COLORS['primary'])],
            foreground=[('selected', COLORS['text'])])

        # Style des labels
        style.configure('TLabel',
            background=COLORS['bg'],
            foreground=COLORS['text'],
            font=('Segoe UI', 10))

        # Style pour l'affichage de l'utilisateur
        style.configure('User.TLabel',
                       font=('Segoe UI', 14, 'bold'),  # Augmenté la taille et mis en gras
                       foreground='#007ACC',
                       background='#2D2D2D',
                       padding=(15, 8))  # Augmenté le padding

        # Style pour le bouton de déconnexion
        style.configure('Logout.TButton',
                       font=('Segoe UI', 12, 'bold'),  # Augmenté la taille et mis en gras
                       padding=(20, 10))  # Augmenté le padding

        return COLORS

    def creer_widgets(self):
        """Crée les widgets de l'interface avec un design moderne."""
        self.pack(fill=tk.BOTH, expand=True)
        
        # Configuration du style
        self.configurer_style()
        
        # Frame pour le bouton de déconnexion et l'utilisateur connecté
        frame_user = ttk.Frame(self)
        frame_user.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame stylisé pour l'utilisateur
        user_display = ttk.Frame(frame_user, style='TFrame')
        user_display.pack(side=tk.LEFT, padx=(0, 10))
        
        # Label pour afficher l'utilisateur connecté avec style amélioré
        label_user = ttk.Label(user_display, 
                             text=f"👤 {self.utilisateur_connecte}", 
                             style='User.TLabel')
        label_user.pack(side=tk.LEFT)
        
        # Bouton de déconnexion stylisé
        bouton_deconnexion = ttk.Button(frame_user, 
                                      text="Déconnexion", 
                                      command=self.deconnexion,
                                      style='Logout.TButton')
        bouton_deconnexion.pack(side=tk.RIGHT)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Création des onglets
        self.tab_accueil = ttk.Frame(self.notebook)
        self.tab_films = ttk.Frame(self.notebook)
        self.tab_ventes = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)
        self.tab_moderation = ttk.Frame(self.notebook)
        
        # Ajout des onglets au notebook
        self.notebook.add(self.tab_accueil, text='Accueil')
        self.notebook.add(self.tab_films, text='Catalogue')
        
        # Ajout des onglets réservés aux administrateurs
        if self.est_admin():
            self.notebook.add(self.tab_ventes, text='Ventes')
            self.notebook.add(self.tab_stats, text='Statistiques')
            self.notebook.add(self.tab_moderation, text='Modération')
            
            # Création des widgets pour les onglets admin
            self.creer_widgets_ventes()
            self.creer_widgets_stats()
            self.creer_widgets_moderation()
        
        # Créer les widgets pour les onglets de base
        self.creer_widgets_accueil()
        self.creer_widgets_films()
    
    def creer_widgets_accueil(self):
        """Crée les widgets pour l'onglet Accueil."""
        # Frame principale
        main_frame = ttk.Frame(self.tab_accueil)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Message de bienvenue
        if self.utilisateur_connecte:
            welcome_text = f"Bienvenue {self.utilisateur_connecte} !"
        else:
            welcome_text = "Bienvenue sur CinéFlix !"
        
        # Créer un label personnalisé avec tk.Label au lieu de ttk.Label pour plus de contrôle
        welcome_label = tk.Label(main_frame, 
                               text=welcome_text,
                               font=('Segoe UI', 24, 'bold'),  # Taille réduite mais toujours en gras
                               fg='white',
                               bg='#1E1E1E')
        welcome_label.pack(pady=(10, 30))  # Moins d'espace vertical
        
        # Frame pour les recommandations
        self.frame_recommandations = ttk.Frame(main_frame)
        self.frame_recommandations.pack(fill=tk.BOTH, expand=True)
        
        # Titre des recommandations avec un style plus élégant
        titre_recommandations = tk.Label(self.frame_recommandations,
                                       text="Films recommandés pour vous",
                                       font=('Segoe UI', 20),  # Plus grand qu'avant
                                       fg='#4A9EFF',  # Bleu clair pour le contraste
                                       bg='#1E1E1E')
        titre_recommandations.pack(pady=(0, 20))  # Plus d'espace en bas
        
        # Liste des recommandations
        self.tree_recommandations = ttk.Treeview(self.frame_recommandations, 
                                                columns=('Titre', 'Genre', 'Note', 'Année', 'Score'),
                                                show='headings',
                                                height=10)
        
        # Configuration des colonnes
        self.tree_recommandations.heading('Titre', text='Titre')
        self.tree_recommandations.heading('Genre', text='Genre')
        self.tree_recommandations.heading('Note', text='Note')
        self.tree_recommandations.heading('Année', text='Année')
        self.tree_recommandations.heading('Score', text='Score')
        
        # Ajuster la largeur des colonnes
        self.tree_recommandations.column('Titre', width=200)
        self.tree_recommandations.column('Genre', width=100)
        self.tree_recommandations.column('Note', width=50)
        self.tree_recommandations.column('Année', width=70)
        self.tree_recommandations.column('Score', width=70)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(self.frame_recommandations, 
                                orient=tk.VERTICAL, 
                                command=self.tree_recommandations.yview)
        self.tree_recommandations.configure(yscrollcommand=scrollbar.set)
        
        # Placement des widgets
        self.tree_recommandations.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Ajouter le binding pour le double-clic
        self.tree_recommandations.bind('<Double-Button-1>', self.afficher_details_film)
        
        # Mettre à jour les recommandations
        if self.utilisateur_connecte:
            self.mettre_a_jour_recommandations()
    
    def creer_widgets_films(self):
        """Crée les widgets pour l'onglet Films."""
        frame_films = ttk.Frame(self.tab_films)
        frame_films.pack(fill=tk.BOTH, expand=True)
        
        # Frame pour les filtres
        frame_filtres = ttk.LabelFrame(frame_films, text='Filtres')
        frame_filtres.pack(fill=tk.X, padx=20, pady=10)
        
        # Filtre par titre
        ttk.Label(frame_filtres, text='Titre:').grid(row=0, column=0, padx=5, pady=5)
        self.entry_titre = ttk.Entry(frame_filtres, width=30)
        self.entry_titre.insert(0, "")
        self.entry_titre.grid(row=0, column=1, padx=5, pady=5)
        self.entry_titre.bind('<KeyRelease>', self.filtrer_films)
        
        # Filtre par genre
        ttk.Label(frame_filtres, text='Genre:').grid(row=0, column=2, padx=5, pady=5)
        self.combo_genre = ttk.Combobox(frame_filtres, values=['Tous'] + sorted(list(set(film['genre'] for film in self.catalogue.films))))
        self.combo_genre.set('Tous')
        self.combo_genre.grid(row=0, column=3, padx=5, pady=5)
        self.combo_genre.bind('<<ComboboxSelected>>', self.filtrer_films)
        
        # Filtre par note
        ttk.Label(frame_filtres, text='Note:').grid(row=1, column=0, padx=5, pady=5)
        self.combo_note = ttk.Combobox(frame_filtres, values=[
            'Toutes',
            'Excellents (≥ 9)',
            'Très bons (≥ 7)',
            'Bons (≥ 5)',
            'Moyens (< 5)'
        ])
        self.combo_note.set('Toutes')
        self.combo_note.grid(row=1, column=1, padx=5, pady=5)
        self.combo_note.bind('<<ComboboxSelected>>', self.filtrer_films)
        
        # Filtre par année
        ttk.Label(frame_filtres, text='Période:').grid(row=1, column=2, padx=5, pady=5)
        self.combo_annee = ttk.Combobox(frame_filtres, values=[
            'Toutes',
            'Films récents (2010+)',
            'Années 2000',
            'Années 90',
            'Années 80',
            'Films classiques (<1980)'
        ])
        self.combo_annee.set('Toutes')
        self.combo_annee.grid(row=1, column=3, padx=5, pady=5)
        self.combo_annee.bind('<<ComboboxSelected>>', self.filtrer_films)
        
        # Liste des films avec tri
        self.tree_films = ttk.Treeview(frame_films, columns=('Titre', 'Réalisateur', 'Genre', 'Année', 'Note', 'Date d\'ajout'),
                                     show='headings', height=15)
        
        # Configuration des colonnes avec tri
        colonnes = {
            'Titre': (300, lambda: self.trier_films('Titre')),
            'Réalisateur': (200, lambda: self.trier_films('Réalisateur')),
            'Genre': (150, lambda: self.trier_films('Genre')),
            'Année': (100, lambda: self.trier_films('Année')),
            'Note': (100, lambda: self.trier_films('Note')),
            'Date d\'ajout': (150, lambda: self.trier_films('Date d\'ajout'))
        }
        
        # Variables pour le tri
        self.tri_actuel = {'colonne': None, 'ordre': 'asc'}
        
        for col, (width, command) in colonnes.items():
            self.tree_films.heading(col, text=col, command=command)
            self.tree_films.column(col, width=width, anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_films, orient=tk.VERTICAL, command=self.tree_films.yview)
        self.tree_films.configure(yscrollcommand=scrollbar.set)
        
        # Placement de la liste et scrollbar
        self.tree_films.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=10)
        
        # Ajouter le binding pour le double-clic
        self.tree_films.bind('<Double-Button-1>', self.afficher_details_film)
        
        # Frame des boutons - uniquement pour l'administrateur
        if self.est_admin():
            frame_actions = ttk.Frame(frame_films)
            frame_actions.pack(fill=tk.X, padx=20, pady=(0, 10))
            
            ttk.Button(frame_actions, text="+ Ajouter un film", 
                      command=self.afficher_dialogue_ajout_film).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame_actions, text="✎ Modifier", 
                      command=self.modifier_film_selectionne).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame_actions, text="✕ Supprimer", 
                      command=self.supprimer_film_selectionne).pack(side=tk.LEFT, padx=5)
    
    def filtrer_films(self, *args):
        """Filtre la liste des films selon les critères."""
        recherche = self.entry_titre.get().lower()
        genre = self.combo_genre.get()
        note = self.combo_note.get()
        periode = self.combo_annee.get()
        
        # Effacer la liste actuelle
        for item in self.tree_films.get_children():
            self.tree_films.delete(item)
        
        # Filtrer les films
        for film in self.catalogue.films:
            if (recherche in film['titre'].lower() or recherche in film['realisateur'].lower()):
                # Filtre par genre
                if genre == 'Tous' or genre == film['genre']:
                    # Filtre par note
                    note_ok = (note == 'Toutes' or
                             (note == 'Excellents (≥ 9)' and film['note'] >= 9) or
                             (note == 'Très bons (≥ 7)' and film['note'] >= 7) or
                             (note == 'Bons (≥ 5)' and film['note'] >= 5) or
                             (note == 'Moyens (< 5)' and film['note'] < 5))
                    
                    # Filtre par période
                    annee_ok = (periode == 'Toutes' or
                              (periode == 'Films récents (2010+)' and film['annee'] >= 2010) or
                              (periode == 'Années 2000' and 2000 <= film['annee'] <= 2009) or
                              (periode == 'Années 90' and 1990 <= film['annee'] <= 1999) or
                              (periode == 'Années 80' and 1980 <= film['annee'] <= 1989) or
                              (periode == 'Films classiques (<1980)' and film['annee'] < 1980))
                    
                    if note_ok and annee_ok:
                        self.tree_films.insert('', 'end', values=(
                            film['titre'],
                            film['realisateur'],
                            film['genre'],
                            film['annee'],
                            film['note'],
                            film['date_ajout'].split('T')[0]
                        ))
        
        # Si un tri est actif, réappliquer le tri
        if self.tri_actuel['colonne']:
            self.trier_films(self.tri_actuel['colonne'])

    def trier_films(self, colonne):
        """Trie les films selon la colonne sélectionnée."""
        items = [(self.tree_films.set(item, colonne), item) for item in self.tree_films.get_children('')]
        
        # Inverser l'ordre si on clique sur la même colonne
        if self.tri_actuel['colonne'] == colonne:
            self.tri_actuel['ordre'] = 'desc' if self.tri_actuel['ordre'] == 'asc' else 'asc'
        else:
            self.tri_actuel['colonne'] = colonne
            self.tri_actuel['ordre'] = 'asc'
        
        # Trier selon le type de données
        if colonne in ['Année', 'Note']:
            items.sort(key=lambda x: float(x[0]) if x[0] else 0, 
                      reverse=(self.tri_actuel['ordre'] == 'desc'))
        else:
            items.sort(key=lambda x: x[0].lower(), 
                      reverse=(self.tri_actuel['ordre'] == 'desc'))
        
        # Réorganiser les items
        for idx, (val, item) in enumerate(items):
            self.tree_films.move(item, '', idx)
        
        # Mettre à jour les en-têtes pour montrer l'ordre de tri
        for col in self.tree_films['columns']:
            if col == colonne:
                arrow = '↓' if self.tri_actuel['ordre'] == 'desc' else '↑'
                self.tree_films.heading(col, text=f'{col} {arrow}')
            else:
                self.tree_films.heading(col, text=col)
    
    def creer_widgets_ventes(self):
        """Crée les widgets pour l'onglet Ventes."""
        # Frame pour nouvelle vente
        frame_nouvelle_vente = ttk.LabelFrame(self.tab_ventes, text="Nouvelle Vente")
        frame_nouvelle_vente.pack(fill=tk.X, padx=20, pady=10)
        
        # Formulaire de vente
        frame_form = ttk.Frame(frame_nouvelle_vente)
        frame_form.pack(padx=20, pady=10)
        
        # Film
        ttk.Label(frame_form, text="Film:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_films = ttk.Combobox(frame_form, width=40, state='readonly')
        self.combo_films['values'] = [f['titre'] for f in self.catalogue.films]
        self.combo_films.grid(row=0, column=1, padx=5, pady=5)
        
        # Quantité
        ttk.Label(frame_form, text="Quantité:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_quantite = ttk.Entry(frame_form, width=10)
        self.entry_quantite.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Prix
        ttk.Label(frame_form, text="Prix unitaire (€):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_prix = ttk.Entry(frame_form, width=10)
        self.entry_prix.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Bouton enregistrer
        ttk.Button(frame_form, text="Enregistrer la vente", 
                  command=self.enregistrer_vente).grid(row=3, column=0, columnspan=2, pady=15)

        # Liste des ventes
        self.tree_ventes = ttk.Treeview(self.tab_ventes, 
                                      columns=('ID', 'Date', 'Film', 'Quantité', 'Prix Unit.', 'Total'),
                                      show='headings',
                                      height=15)
        
        # Configuration des colonnes
        colonnes_ventes = {
            'ID': 80,
            'Date': 150,
            'Film': 300,
            'Quantité': 100,
            'Prix Unit.': 100,
            'Total': 100
        }
        
        for col, width in colonnes_ventes.items():
            self.tree_ventes.heading(col, text=col)
            self.tree_ventes.column(col, width=width, anchor='w')
        
        # Ajout de la scrollbar
        scrollbar_ventes = ttk.Scrollbar(self.tab_ventes, orient=tk.VERTICAL, command=self.tree_ventes.yview)
        self.tree_ventes.configure(yscrollcommand=scrollbar_ventes.set)
        
        # Placement de la liste et scrollbar
        self.tree_ventes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
        scrollbar_ventes.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20))

        # Ajouter le binding pour le double-clic
        self.tree_ventes.bind('<Double-Button-1>', self.afficher_details_film_vente)
    
    def creer_widgets_stats(self):
        """Crée les widgets pour l'onglet Statistiques."""
        # Frame principale pour les statistiques
        self.frame_stats_main = ttk.Frame(self.tab_stats)
        self.frame_stats_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bouton de rafraîchissement en haut
        refresh_button = ttk.Button(self.frame_stats_main, text="Rafraîchir", command=self.rafraichir_stats)
        refresh_button.pack(pady=5)

        # Créer les conteneurs pour les statistiques
        self.stats_container = ttk.Frame(self.frame_stats_main)
        self.stats_container.pack(fill=tk.BOTH, expand=True)

        # Afficher les statistiques initiales
        self.rafraichir_stats()

        # Configurer le rafraîchissement automatique (toutes les 5 minutes)
        self.after(300000, self.rafraichir_stats)

    def rafraichir_stats(self):
        """Rafraîchit les statistiques affichées."""
        try:
            if hasattr(self, 'stats_container') and self.stats_container.winfo_exists():
                for widget in self.stats_container.winfo_children():
                    widget.destroy()
                self.afficher_statistiques()
        except Exception as e:
            print(f"Erreur lors du rafraîchissement des stats : {str(e)}")
            # En cas d'erreur, afficher un message
            error_label = ttk.Label(self.stats_container, 
                                  text=f"Erreur lors du rafraîchissement des statistiques : {str(e)}",
                                  style='Custom.TLabel')
            error_label.pack(pady=20)
    
    def afficher_statistiques(self):
        """Affiche les statistiques directement dans la fenêtre principale."""
        try:
            # Nettoyer le conteneur existant
            if hasattr(self, 'stats_container'):
                for widget in self.stats_container.winfo_children():
                    widget.destroy()
            
            # Frame principal pour les statistiques
            main_stats_frame = ttk.Frame(self.stats_container, style='Custom.TFrame')
            main_stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Frame pour les statistiques textuelles
            text_stats_frame = ttk.Frame(main_stats_frame, style='Custom.TFrame')
            text_stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
            
            # Calculer les statistiques globales
            total_films = len(self.catalogue.films)
            total_ventes = sum(float(vente['quantite']) for vente in self.ventes.ventes)
            total_users = len(self.gestion_utilisateurs.utilisateurs)  # Correction ici
            # Notes moyennes globales
            all_notes = []
            for film in self.catalogue.films:
                if film.get('notes'):
                    notes = [float(note) for note in film['notes'].values() if str(note).replace('.', '').isdigit()]
                    if notes:
                        all_notes.extend(notes)
            note_moyenne_globale = sum(all_notes) / len(all_notes) if all_notes else 0
            
            # Obtenir la date actuelle
            date_actuelle = datetime.now()
            debut_mois = date_actuelle.replace(day=1)
            
            # Statistiques des films
            films_ce_mois = len(self.catalogue.filtrer_par_periode(debut_mois.isoformat()))
            
            # Statistiques des ventes
            ventes_ce_mois = self.ventes.filtrer_par_periode(debut=debut_mois)
            total_ventes_mois = sum(float(v['total']) for v in ventes_ce_mois)
            
            # Afficher les statistiques textuelles
            stats_text = [
                f"Nombre total de films: {total_films}",
                f"Films ajoutés ce mois: {films_ce_mois}",
                f"Volume total des ventes: {total_ventes:.0f} €",
                f"Ventes ce mois: {total_ventes_mois:.0f} €",
                f"Nombre total d'utilisateurs: {total_users}",
                f"Note moyenne globale: {note_moyenne_globale:.1f}/10",
                f"Dernière synchronisation: {self.derniere_synchro.split('T')[0]}"
            ]
            
            for text in stats_text:
                label = ttk.Label(text_stats_frame, text=text, style='Custom.TLabel')
                label.pack(side=tk.LEFT, padx=20)
            
            # Style personnalisé pour les graphiques
            plt.style.use('default')
            
            # Création d'une figure avec 2 lignes et 2 colonnes
            fig = Figure(figsize=(12, 8), facecolor='white')
            
            # Configuration des sous-graphiques avec plus d'espace
            gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
            
            # Configuration des sous-graphiques
            ax1 = fig.add_subplot(gs[0, 0])  # Graphique des genres
            ax2 = fig.add_subplot(gs[0, 1])  # Graphique des notes moyennes
            ax3 = fig.add_subplot(gs[1, :])  # Graphique des tendances

            # 1. Graphique des genres (camembert)
            genres = {}
            for film in self.catalogue.films:
                genre = film['genre']
                genres[genre] = genres.get(genre, 0) + 1
            
            if genres:
                genres_tries = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5])
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
                wedges, texts, autotexts = ax1.pie(genres_tries.values(), 
                                                 labels=genres_tries.keys(),
                                                 colors=colors,
                                                 autopct='%1.1f%%',
                                                 startangle=90)
                ax1.set_title('Top 5 des Genres les Plus Populaires', pad=20)

            # 2. Graphique des notes moyennes (barres horizontales)
            notes_moyennes = {}
            for film in self.catalogue.films:
                # Récupérer toutes les notes pour ce film de tous les utilisateurs
                notes = []
                for username in self.gestion_utilisateurs.utilisateurs:
                    notes_utilisateur = self.gestion_utilisateurs.obtenir_notes_utilisateur(username)
                    if film['titre'] in notes_utilisateur:
                        # Convertir la note de 1-5 en 1-10
                        note = notes_utilisateur[film['titre']].get('note', 0) * 2
                        notes.append(note)
                
                if notes:  # Si le film a des notes
                    notes_moyennes[film['titre']] = sum(notes) / len(notes)

            if notes_moyennes:
                films_tries = dict(sorted(notes_moyennes.items(), key=lambda x: x[1], reverse=True)[:5])
                
                y_pos = range(len(films_tries))
                bars = ax2.barh(y_pos, list(films_tries.values()), color='#45B7D1')
                
                # Ajuster les labels et les valeurs
                ax2.set_yticks(y_pos)
                ax2.set_yticklabels(list(films_tries.keys()))
                ax2.set_xlim(0, 10)
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    width = bar.get_width()
                    ax2.text(width, bar.get_y() + bar.get_height()/2,
                            f'{width:.1f}',
                            ha='left', va='center',
                            fontweight='bold')
                
                ax2.set_title('Top 5 des Films les Mieux Notés', pad=20)
            else:
                ax2.text(0.5, 0.5, 'Aucune note disponible',
                        ha='center', va='center',
                        transform=ax2.transAxes)
                ax2.set_title('Top 5 des Films les Mieux Notés', pad=20)

            # 3. Graphique des tendances (ligne)
            dates_ventes = {}
            for vente in self.ventes.ventes:
                # Convertir la date en objet datetime
                date_obj = datetime.strptime(vente['date'].split(' ')[0], '%Y-%m-%d')
                dates_ventes[date_obj] = dates_ventes.get(date_obj, 0) + float(vente['quantite'])
            
            if dates_ventes:
                dates_triees = dict(sorted(dates_ventes.items()))
                
                # Créer le graphique des tendances avec plus d'espace pour les dates
                fig.subplots_adjust(bottom=0.2)  # Ajuster l'espace en bas
                
                # Tracer le graphique avec les objets datetime
                ax3.plot(list(dates_triees.keys()), 
                        list(dates_triees.values()),
                        marker='o',
                        color='#45B7D1',
                        linewidth=2)
                
                ax3.set_title('Tendance des Ventes', pad=20)
                
                # Formater les dates sur l'axe x
                ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                
                # Rotation des dates pour une meilleure lisibilité
                plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
                
                # Ajouter une grille pour faciliter la lecture
                ax3.grid(True, linestyle='--', alpha=0.7)
            
            # Frame pour contenir le graphique
            frame_graph = ttk.Frame(main_stats_frame, style='Custom.TFrame')
            frame_graph.pack(fill=tk.BOTH, expand=True)
            
            # Créer le canvas Tkinter
            canvas = FigureCanvasTkAgg(fig, master=frame_graph)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # S'assurer que le graphique est dessiné
            canvas.draw()
            
        except Exception as e:
            print(f"Erreur lors de l'affichage des statistiques : {str(e)}")
            error_label = ttk.Label(self.stats_container,
                                  text=f"Erreur lors de l'affichage des statistiques : {str(e)}",
                                  style='Custom.TLabel')
            error_label.pack(pady=20)
    
    def mettre_a_jour_liste_films(self):
        """Met à jour la liste des films dans l'interface."""
        # Vérifier si tree_films existe
        if not hasattr(self, 'tree_films'):
            return
            
        # Effacer la liste actuelle
        for item in self.tree_films.get_children():
            self.tree_films.delete(item)
        
        # Mettre à jour avec les nouveaux films
        for film in self.catalogue.films:
            self.tree_films.insert('', 'end', values=(
                film['titre'],
                film['realisateur'],
                film['genre'],
                film['annee'],
                film['note'],
                film['date_ajout'].split('T')[0]
            ))
    
    def mettre_a_jour_liste_ventes(self):
        """Met à jour la liste des ventes affichée."""
        # Effacer la liste actuelle
        for item in self.tree_ventes.get_children():
            self.tree_ventes.delete(item)
        
        # Ajouter les ventes à la liste
        for vente in self.ventes.ventes:
            self.tree_ventes.insert('', 'end', values=(
                vente['id'],
                vente['date'],
                vente['titre_film'],
                vente['quantite'],
                f"{float(vente['prix_unitaire']):.2f} €",
                f"{float(vente['quantite']) * float(vente['prix_unitaire']):.2f} €"
            ))

    def afficher_statistiques(self):
        """Affiche les statistiques directement dans la fenêtre principale."""
        try:
            # Nettoyer le conteneur existant
            if hasattr(self, 'stats_container'):
                for widget in self.stats_container.winfo_children():
                    widget.destroy()
            
            # Frame principal pour les statistiques
            main_stats_frame = ttk.Frame(self.stats_container, style='Custom.TFrame')
            main_stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Frame pour les statistiques textuelles
            text_stats_frame = ttk.Frame(main_stats_frame, style='Custom.TFrame')
            text_stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
            
            # Calculer les statistiques globales
            total_films = len(self.catalogue.films)
            total_ventes = sum(float(vente['quantite']) for vente in self.ventes.ventes)
            total_users = len(self.gestion_utilisateurs.utilisateurs)  # Correction ici
            # Notes moyennes globales
            all_notes = []
            for film in self.catalogue.films:
                if film.get('notes'):
                    notes = [float(note) for note in film['notes'].values() if str(note).replace('.', '').isdigit()]
                    if notes:
                        all_notes.extend(notes)
            note_moyenne_globale = sum(all_notes) / len(all_notes) if all_notes else 0
            
            # Obtenir la date actuelle
            date_actuelle = datetime.now()
            debut_mois = date_actuelle.replace(day=1)
            
            # Statistiques des films
            films_ce_mois = len(self.catalogue.filtrer_par_periode(debut_mois.isoformat()))
            
            # Statistiques des ventes
            ventes_ce_mois = self.ventes.filtrer_par_periode(debut=debut_mois)
            total_ventes_mois = sum(float(v['total']) for v in ventes_ce_mois)
            
            # Afficher les statistiques textuelles
            stats_text = [
                f"Nombre total de films: {total_films}",
                f"Films ajoutés ce mois: {films_ce_mois}",
                f"Volume total des ventes: {total_ventes:.0f} €",
                f"Ventes ce mois: {total_ventes_mois:.0f} €",
                f"Nombre total d'utilisateurs: {total_users}",
                f"Note moyenne globale: {note_moyenne_globale:.1f}/10",
                f"Dernière synchronisation: {self.derniere_synchro.split('T')[0]}"
            ]
            
            for text in stats_text:
                label = ttk.Label(text_stats_frame, text=text, style='Custom.TLabel')
                label.pack(side=tk.LEFT, padx=20)
            
            # Style personnalisé pour les graphiques
            plt.style.use('default')
            
            # Création d'une figure avec 2 lignes et 2 colonnes
            fig = Figure(figsize=(12, 8), facecolor='white')
            
            # Configuration des sous-graphiques avec plus d'espace
            gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
            
            # Configuration des sous-graphiques
            ax1 = fig.add_subplot(gs[0, 0])  # Graphique des genres
            ax2 = fig.add_subplot(gs[0, 1])  # Graphique des notes moyennes
            ax3 = fig.add_subplot(gs[1, :])  # Graphique des tendances

            # 1. Graphique des genres (camembert)
            genres = {}
            for film in self.catalogue.films:
                genre = film['genre']
                genres[genre] = genres.get(genre, 0) + 1
            
            if genres:
                genres_tries = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5])
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
                wedges, texts, autotexts = ax1.pie(genres_tries.values(), 
                                                 labels=genres_tries.keys(),
                                                 colors=colors,
                                                 autopct='%1.1f%%',
                                                 startangle=90)
                ax1.set_title('Top 5 des Genres les Plus Populaires', pad=20)

            # 2. Graphique des notes moyennes (barres horizontales)
            notes_moyennes = {}
            for film in self.catalogue.films:
                # Récupérer toutes les notes pour ce film de tous les utilisateurs
                notes = []
                for username in self.gestion_utilisateurs.utilisateurs:
                    notes_utilisateur = self.gestion_utilisateurs.obtenir_notes_utilisateur(username)
                    if film['titre'] in notes_utilisateur:
                        # Convertir la note de 1-5 en 1-10
                        note = notes_utilisateur[film['titre']].get('note', 0) * 2
                        notes.append(note)
                
                if notes:  # Si le film a des notes
                    notes_moyennes[film['titre']] = sum(notes) / len(notes)

            if notes_moyennes:
                films_tries = dict(sorted(notes_moyennes.items(), key=lambda x: x[1], reverse=True)[:5])
                
                y_pos = range(len(films_tries))
                bars = ax2.barh(y_pos, list(films_tries.values()), color='#45B7D1')
                
                # Ajuster les labels et les valeurs
                ax2.set_yticks(y_pos)
                ax2.set_yticklabels(list(films_tries.keys()))
                ax2.set_xlim(0, 10)
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    width = bar.get_width()
                    ax2.text(width, bar.get_y() + bar.get_height()/2,
                            f'{width:.1f}',
                            ha='left', va='center',
                            fontweight='bold')
                
                ax2.set_title('Top 5 des Films les Mieux Notés', pad=20)
            else:
                ax2.text(0.5, 0.5, 'Aucune note disponible',
                        ha='center', va='center',
                        transform=ax2.transAxes)
                ax2.set_title('Top 5 des Films les Mieux Notés', pad=20)

            # 3. Graphique des tendances (ligne)
            dates_ventes = {}
            for vente in self.ventes.ventes:
                # Convertir la date en objet datetime
                date_obj = datetime.strptime(vente['date'].split(' ')[0], '%Y-%m-%d')
                dates_ventes[date_obj] = dates_ventes.get(date_obj, 0) + float(vente['quantite'])
            
            if dates_ventes:
                dates_triees = dict(sorted(dates_ventes.items()))
                
                # Créer le graphique des tendances avec plus d'espace pour les dates
                fig.subplots_adjust(bottom=0.2)  # Ajuster l'espace en bas
                
                # Tracer le graphique avec les objets datetime
                ax3.plot(list(dates_triees.keys()), 
                        list(dates_triees.values()),
                        marker='o',
                        color='#45B7D1',
                        linewidth=2)
                
                ax3.set_title('Tendance des Ventes', pad=20)
                
                # Formater les dates sur l'axe x
                ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                
                # Rotation des dates pour une meilleure lisibilité
                plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
                
                # Ajouter une grille pour faciliter la lecture
                ax3.grid(True, linestyle='--', alpha=0.7)
            
            # Frame pour contenir le graphique
            frame_graph = ttk.Frame(main_stats_frame, style='Custom.TFrame')
            frame_graph.pack(fill=tk.BOTH, expand=True)
            
            # Créer le canvas Tkinter
            canvas = FigureCanvasTkAgg(fig, master=frame_graph)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # S'assurer que le graphique est dessiné
            canvas.draw()
            
        except Exception as e:
            print(f"Erreur lors de l'affichage des statistiques : {str(e)}")
            error_label = ttk.Label(self.stats_container,
                                  text=f"Erreur lors de l'affichage des statistiques : {str(e)}",
                                  style='Custom.TLabel')
            error_label.pack(pady=20)
    
    def mettre_a_jour_recommandations(self):
        """Met à jour les recommandations basées sur les notes de l'utilisateur."""
        if not self.utilisateur_connecte:
            return
            
        # Effacer les recommandations existantes
        for item in self.tree_recommandations.get_children():
            self.tree_recommandations.delete(item)
            
        # Récupérer les notes de l'utilisateur
        notes_utilisateur = {}
        for film in self.catalogue.films:
            if film.get('notes') and self.utilisateur_connecte in film['notes']:
                notes_utilisateur[film['titre']] = film['notes'][self.utilisateur_connecte]
        
        # Si l'utilisateur n'a pas encore noté de films, afficher les films les mieux notés
        if not notes_utilisateur:
            films_scores = [(film, film.get('note', 0)) for film in self.catalogue.films]
            films_scores.sort(key=lambda x: x[1], reverse=True)
            for film, score in films_scores[:10]:
                self.tree_recommandations.insert('', 'end', values=(
                    film['titre'],
                    film['genre'],
                    film.get('note', 'N/A'),
                    film.get('annee', 'N/A'),
                    f"{score:.1f}"
                ))
            return
            
        # Calculer les recommandations basées sur les genres préférés
        genres_preferes = {}
        for film in self.catalogue.films:
            if film['titre'] in notes_utilisateur:
                note = notes_utilisateur[film['titre']]
                genre = film['genre']
                if genre not in genres_preferes:
                    genres_preferes[genre] = []
                genres_preferes[genre].append(note)
        
        # Calculer la moyenne des notes par genre
        moyennes_genres = {}
        for genre, notes in genres_preferes.items():
            moyennes_genres[genre] = sum(notes) / len(notes)
        
        # Calculer un score pour chaque film non vu
        films_scores = []
        for film in self.catalogue.films:
            if film['titre'] not in notes_utilisateur:
                # Le score est basé sur :
                # 1. La préférence pour le genre (50%)
                # 2. La note moyenne du film (50%)
                score_genre = moyennes_genres.get(film['genre'], 0)
                note_film = film.get('note', 0)
                score = (score_genre * 0.5) + (note_film * 0.5)
                films_scores.append((film, score))
        
        # Trier les films par score et afficher les 10 meilleurs
        films_scores.sort(key=lambda x: x[1], reverse=True)
        for film, score in films_scores[:10]:
            self.tree_recommandations.insert('', 'end', values=(
                film['titre'],
                film['genre'],
                film.get('note', 'N/A'),
                film.get('annee', 'N/A'),
                f"{score:.1f}"
            ))
        
        # Ajouter le gestionnaire d'événements pour le double-clic
        self.tree_recommandations.bind('<Double-Button-1>', self.afficher_details_film)
    
    def creer_widgets_moderation(self):
        """Crée les widgets pour l'onglet Modération (admin uniquement)."""
        # Tableau des utilisateurs
        columns = ('Nom', 'Email', 'Rôle', 'Date de Création', 'Dernière Connexion')
        self.table_utilisateurs = ttk.Treeview(self.tab_moderation, columns=columns, show='headings')
        self.table_utilisateurs.heading('Nom', text='Nom')
        self.table_utilisateurs.heading('Email', text='Email')
        self.table_utilisateurs.heading('Rôle', text='Rôle')
        self.table_utilisateurs.heading('Date de Création', text='Date de Création')
        self.table_utilisateurs.heading('Dernière Connexion', text='Dernière Connexion')
        self.table_utilisateurs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Boutons d'action
        btn_frame = ttk.Frame(self.tab_moderation)
        btn_frame.pack(pady=10)

        btn_supprimer = ttk.Button(btn_frame, text="Supprimer Utilisateur", command=self.supprimer_utilisateur)
        btn_supprimer.pack(side=tk.LEFT, padx=5)

        btn_promouvoir = ttk.Button(btn_frame, text="Promouvoir en Admin", command=self.promouvoir_utilisateur)
        btn_promouvoir.pack(side=tk.LEFT, padx=5)

        # Charger les utilisateurs
        self.charger_utilisateurs()

    def charger_utilisateurs(self):
        """Charge la liste des utilisateurs dans le tableau de modération."""
        for utilisateur in self.table_utilisateurs.get_children():
            self.table_utilisateurs.delete(utilisateur)
        for nom, infos in self.gestion_utilisateurs.utilisateurs.items():
            self.table_utilisateurs.insert('', tk.END, values=(nom, infos['email'], infos['role'], infos.get('date_creation', 'N/A'), infos.get('derniere_connexion', 'N/A')))

    def supprimer_utilisateur(self):
        """Supprime l'utilisateur sélectionné."""
        selected_item = self.table_utilisateurs.selection()
        if selected_item:
            utilisateur = self.table_utilisateurs.item(selected_item)['values'][0]
            if utilisateur != 'root':  # Ne pas supprimer l'admin principal
                succes, message = self.gestion_utilisateurs.supprimer_utilisateur(utilisateur)
                messagebox.showinfo("Suppression", message)
                self.charger_utilisateurs()
            else:
                messagebox.showwarning("Action Interdite", "Impossible de supprimer l'utilisateur root.")

    def promouvoir_utilisateur(self):
        """Promeut l'utilisateur sélectionné en admin."""
        selected_item = self.table_utilisateurs.selection()
        if selected_item:
            utilisateur = self.table_utilisateurs.item(selected_item)['values'][0]
            succes, message = self.gestion_utilisateurs.promouvoir_utilisateur(utilisateur)
            messagebox.showinfo("Promotion", message)
            self.charger_utilisateurs()
    
    def afficher_details_film(self, event):
        """Affiche la fenêtre de détails pour le film sélectionné."""
        tree = event.widget
        item = tree.selection()[0]
        titre = tree.item(item)['values'][0]
        
        # Trouver le film dans le catalogue
        film = next((f for f in self.catalogue.films if f['titre'] == titre), None)
        if film:
            FenetreDetailsFilm(self, film, self.gestion_utilisateurs, self.utilisateur_connecte)
    
    def afficher_details_film_vente(self, event):
        """Affiche les détails d'un film à partir de l'onglet ventes."""
        item = self.tree_ventes.selection()[0]
        film_titre = self.tree_ventes.item(item)['values'][1]  # Le titre est dans la deuxième colonne (index 1)
        film = self.catalogue.obtenir_film_par_titre(film_titre)
        if film:
            FenetreDetailsFilm(self.master, film, self.gestion_utilisateurs, self.utilisateur_connecte)
    
    def afficher_dialogue_ajout_film(self):
        """Affiche une fenêtre de dialogue pour ajouter un nouveau film."""
        dialogue = tk.Toplevel(self)
        dialogue.title("Ajouter un Film")
        dialogue.geometry("400x500")
        
        # Style du dialogue
        dialogue.configure(bg='#1E1E1E')
        frame = ttk.Frame(dialogue)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Champs de saisie
        champs = [
            ('Titre:', 'titre', ''),
            ('Réalisateur:', 'realisateur', ''),
            ('Année:', 'annee', '2024'),
            ('Genre:', 'genre', ''),
            ('Note:', 'note', '0'),
            ('Acteurs (séparés par |):', 'acteurs', '')
        ]
        
        entries = {}
        for i, (label, key, default) in enumerate(champs):
            ttk.Label(frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(frame, width=40)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry
        
        def valider():
            try:
                film = {
                    'titre': entries['titre'].get().strip(),
                    'realisateur': entries['realisateur'].get().strip(),
                    'annee': int(entries['annee'].get()),
                    'genre': entries['genre'].get().strip(),
                    'note': float(entries['note'].get()),
                    'acteurs': [a.strip() for a in entries['acteurs'].get().split('|') if a.strip()],
                    'date_ajout': datetime.now().strftime('%Y-%m-%d'),
                    'notes': []
                }
                
                if not film['titre'] or not film['realisateur']:
                    messagebox.showerror("Erreur", "Le titre et le réalisateur sont obligatoires.")
                    return
                
                self.catalogue.ajouter_film(film)
                self.mettre_a_jour_liste_films()
                dialogue.destroy()
                messagebox.showinfo("Succès", "Film ajouté avec succès!")
                
            except ValueError as e:
                messagebox.showerror("Erreur", f"Erreur de saisie : {str(e)}")
        
        # Boutons
        frame_boutons = ttk.Frame(frame)
        frame_boutons.grid(row=len(champs), column=0, columnspan=2, pady=20)
        
        ttk.Button(frame_boutons, text="Valider", command=valider).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_boutons, text="Annuler", command=dialogue.destroy).pack(side=tk.LEFT, padx=5)

    def modifier_film_selectionne(self):
        """Modifie le film sélectionné."""
        selection = self.tree_films.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un film à modifier.")
            return
        
        # Récupérer le film sélectionné
        item = self.tree_films.item(selection[0])
        titre = item['values'][0]
        film = next((f for f in self.catalogue.films if f['titre'] == titre), None)
        
        if not film:
            messagebox.showerror("Erreur", "Film non trouvé.")
            return
        
        # Créer la fenêtre de dialogue
        dialogue = tk.Toplevel(self)
        dialogue.title("Modifier le Film")
        dialogue.geometry("400x500")
        dialogue.configure(bg='#1E1E1E')
        
        frame = ttk.Frame(dialogue)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Champs de saisie
        entries = {}
        row = 0
        
        # Titre
        ttk.Label(frame, text="Titre:").grid(row=row, column=0, padx=5, pady=5)
        entries['titre'] = ttk.Entry(frame, width=40)
        entries['titre'].insert(0, film['titre'])
        entries['titre'].grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        # Réalisateur
        ttk.Label(frame, text="Réalisateur:").grid(row=row, column=0, padx=5, pady=5)
        entries['realisateur'] = ttk.Entry(frame, width=40)
        entries['realisateur'].insert(0, film['realisateur'])
        entries['realisateur'].grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        # Année
        ttk.Label(frame, text="Année:").grid(row=row, column=0, padx=5, pady=5)
        entries['annee'] = ttk.Entry(frame, width=40)
        entries['annee'].insert(0, str(film['annee']))
        entries['annee'].grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        # Genre
        ttk.Label(frame, text="Genre:").grid(row=row, column=0, padx=5, pady=5)
        entries['genre'] = ttk.Entry(frame, width=40)
        entries['genre'].insert(0, film['genre'])
        entries['genre'].grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        # Note
        ttk.Label(frame, text="Note:").grid(row=row, column=0, padx=5, pady=5)
        entries['note'] = ttk.Entry(frame, width=40)
        entries['note'].insert(0, str(film['note']))
        entries['note'].grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        # Acteurs
        ttk.Label(frame, text="Acteurs (séparés par |):").grid(row=row, column=0, padx=5, pady=5)
        entries['acteurs'] = ttk.Entry(frame, width=40)
        entries['acteurs'].insert(0, '|'.join(film['acteurs']))
        entries['acteurs'].grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        def valider_modification():
            try:
                film_modifie = {
                    'titre': entries['titre'].get().strip(),
                    'realisateur': entries['realisateur'].get().strip(),
                    'annee': int(entries['annee'].get()),
                    'genre': entries['genre'].get().strip(),
                    'note': float(entries['note'].get()),
                    'acteurs': [a.strip() for a in entries['acteurs'].get().split('|') if a.strip()],
                    'date_ajout': film['date_ajout'],
                    'notes': film.get('notes', [])
                }
                
                if not film_modifie['titre'] or not film_modifie['realisateur']:
                    messagebox.showerror("Erreur", "Le titre et le réalisateur sont obligatoires.")
                    return
                
                self.catalogue.modifier_film(film['id'], film_modifie)
                self.mettre_a_jour_liste_films()
                dialogue.destroy()
                messagebox.showinfo("Succès", "Film modifié avec succès!")
                
            except ValueError as e:
                messagebox.showerror("Erreur", f"Erreur de saisie : {str(e)}")
        
        # Boutons
        frame_boutons = ttk.Frame(frame)
        frame_boutons.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(frame_boutons, text="Valider", command=valider_modification).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_boutons, text="Annuler", command=dialogue.destroy).pack(side=tk.LEFT, padx=5)

    def supprimer_film_selectionne(self):
        """Supprime le film sélectionné."""
        selection = self.tree_films.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un film à supprimer.")
            return
        
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce film ?"):
            item = self.tree_films.item(selection[0])
            titre = item['values'][0]
            film = next((f for f in self.catalogue.films if f['titre'] == titre), None)
            
            if film:
                self.catalogue.supprimer_film(film['id'])
                self.mettre_a_jour_liste_films()
                messagebox.showinfo("Succès", "Film supprimé avec succès!")
            else:
                messagebox.showerror("Erreur", "Film non trouvé.")

    def enregistrer_vente(self):
        """Enregistre une nouvelle vente."""
        try:
            # Récupérer le film sélectionné
            titre_film = self.combo_films.get()
            if not titre_film:
                messagebox.showerror("Erreur", "Veuillez sélectionner un film.")
                return
            
            film = next((f for f in self.catalogue.films if f['titre'] == titre_film), None)
            if not film:
                messagebox.showerror("Erreur", "Film non trouvé.")
                return
            
            # Valider la quantité
            try:
                quantite = int(self.entry_quantite.get())
                if quantite <= 0:
                    raise ValueError("La quantité doit être positive.")
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer une quantité valide.")
                return
            
            # Valider le prix
            try:
                prix = float(self.entry_prix.get())
                if prix <= 0:
                    raise ValueError("Le prix doit être positif.")
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer un prix valide.")
                return
            
            # Enregistrer la vente via GestionVentes
            vente = self.ventes.enregistrer_vente(film['id'], film['titre'], quantite, prix)
            
            # Recharger les ventes pour mettre à jour l'affichage
            self.ventes.charger_ventes()
            self.mettre_a_jour_liste_ventes()
            
            # Réinitialiser les champs
            self.combo_films.set('')
            self.entry_quantite.delete(0, tk.END)
            self.entry_prix.delete(0, tk.END)
            
            messagebox.showinfo("Succès", "Vente enregistrée avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {str(e)}")

    def mettre_a_jour_liste_ventes(self):
        """Met à jour la liste des ventes affichée."""
        # Effacer la liste actuelle
        for item in self.tree_ventes.get_children():
            self.tree_ventes.delete(item)
        
        # Ajouter les ventes à la liste
        for vente in self.ventes.ventes:
            self.tree_ventes.insert('', 'end', values=(
                vente['id'],
                vente['date'],
                vente['titre_film'],
                vente['quantite'],
                f"{float(vente['prix_unitaire']):.2f} €",
                f"{float(vente['quantite']) * float(vente['prix_unitaire']):.2f} €"
            ))

    def deconnexion(self):
        """Gère la déconnexion de l'utilisateur."""
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            self.utilisateur_connecte = None
            # Détruire tous les widgets
            for widget in self.winfo_children():
                widget.destroy()
            # Afficher la fenêtre de connexion
            self.afficher_connexion()

    def synchroniser_horloge(self):
        """Met à jour l'horloge et rafraîchit les données si nécessaire."""
        nouvelle_synchro = self.catalogue.mettre_a_jour_horloge()
        nouvelle_synchro_ventes = self.ventes.mettre_a_jour_horloge()
        
        if nouvelle_synchro != self.derniere_synchro or nouvelle_synchro_ventes != self.derniere_synchro_ventes:
            self.derniere_synchro = nouvelle_synchro
            self.derniere_synchro_ventes = nouvelle_synchro_ventes
            self.rafraichir_stats()
            self.mettre_a_jour_liste_films()
            self.mettre_a_jour_liste_ventes()
        
        # Programmer la prochaine synchronisation
        self.master.after(60000, self.synchroniser_horloge)

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationPrincipale(master=root)
    app.mainloop()
