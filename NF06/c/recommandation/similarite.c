/**
 * @file similarite.c
 * @brief Implémentation des fonctions de calcul de similarité
 */

#include "similarite.h"
#include <string.h>

float calculer_similarite_jaccard(Utilisateur* user1, Utilisateur* user2) {
    int intersection = 0;
    int union_films = 0;
    
    // Calcul de l'intersection
    for (int i = 0; i < user1->nb_films_vus; i++) {
        for (int j = 0; j < user2->nb_films_vus; j++) {
            if (user1->films_vus[i].id == user2->films_vus[j].id) {
                intersection++;
                break;
            }
        }
    }
    
    // Calcul de l'union
    union_films = user1->nb_films_vus + user2->nb_films_vus - intersection;
    
    // Calcul de la similarité de Jaccard
    if (union_films == 0) return 0.0f;
    return (float)intersection / union_films;
}

Film* recommander_films(Utilisateur* user, Utilisateur** users, int nb_users, int* nb_recommandations) {
    // Tableau pour stocker les films recommandés
    Film* recommandations = NULL;
    *nb_recommandations = 0;
    
    // Trouver l'utilisateur le plus similaire
    float max_similarite = 0.0f;
    Utilisateur* user_similaire = NULL;
    
    for (int i = 0; i < nb_users; i++) {
        if (users[i]->id == user->id) continue;
        
        float similarite = calculer_similarite_jaccard(user, users[i]);
        if (similarite > max_similarite) {
            max_similarite = similarite;
            user_similaire = users[i];
        }
    }
    
    // Si on trouve un utilisateur similaire, on recommande ses films
    if (user_similaire != NULL && max_similarite > 0.0f) {
        // Allouer de la mémoire pour les recommandations
        recommandations = malloc(sizeof(Film) * user_similaire->nb_films_vus);
        
        // Ajouter les films non vus par l'utilisateur
        for (int i = 0; i < user_similaire->nb_films_vus; i++) {
            int film_deja_vu = 0;
            
            // Vérifier si l'utilisateur a déjà vu ce film
            for (int j = 0; j < user->nb_films_vus; j++) {
                if (user_similaire->films_vus[i].id == user->films_vus[j].id) {
                    film_deja_vu = 1;
                    break;
                }
            }
            
            // Si le film n'a pas été vu, l'ajouter aux recommandations
            if (!film_deja_vu) {
                recommandations[*nb_recommandations] = user_similaire->films_vus[i];
                (*nb_recommandations)++;
            }
        }
    }
    
    return recommandations;
}
