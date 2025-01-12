/**
 * @file similarite.h
 * @brief Définition des structures et fonctions pour le calcul de similarité
 */

#ifndef SIMILARITE_H
#define SIMILARITE_H

#include <stdio.h>
#include <stdlib.h>

// Structure pour représenter un film
typedef struct {
    int id;
    char titre[100];
    float note;
} Film;

// Structure pour représenter un utilisateur
typedef struct {
    int id;
    Film* films_vus;
    int nb_films_vus;
} Utilisateur;

// Fonctions principales
float calculer_similarite_jaccard(Utilisateur* user1, Utilisateur* user2);
Film* recommander_films(Utilisateur* user, Utilisateur** users, int nb_users, int* nb_recommandations);

#endif // SIMILARITE_H
