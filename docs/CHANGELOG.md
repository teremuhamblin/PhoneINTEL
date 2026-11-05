# CHANGELOG.md

Toutes les modifications notables apportées au projet **PhoneIntel** seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère au [Versionnement Semantique](https://semver.org/lang/fr/).

---

## [2.0.0] - 2026-11-05

### Ajouté
- Refactorisation complète du code pour une structure modulaire et propre.
- Intégration d'un script d'installation automatisé et sécurisé dédié exclusivement à l'environnement **Termux**.
- Prise en charge de l'isolation des dépendances via un environnement virtuel Python (`venv`).
- Support étendu pour les requêtes de recherche groupées (batch processing via fichiers d'entrée) et l'API Neutrino.
- Documentation complète du projet (README, CONTRIBUTING, SECURITY, CHANGELOG).

### Modifié
- Amélioration de la gestion des erreurs réseau et des limites de requêtes.
- Optimisation des performances lors de la génération des dorks OSINT.

---

## [1.0.0] - Initial Release

### Ajouté
- Lancement initial de PhoneIntel sur le terminal.
- Fonctionnalités de recherche de base sur les numéros de téléphone.
- Intégration des options de cartes, de dorks par catégories et de l'ouverture directe dans le navigateur.
