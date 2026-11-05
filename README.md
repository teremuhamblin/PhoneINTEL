# PhoneIntel

[![PyPI version](https://img.shields.io/pypi/v/phoneintel.svg)](https://pypi.org/project/phoneintel/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-grey.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-grey.svg)](LICENSE)

**PhoneIntel** est un outil OSINT (Open Source Intelligence) léger en ligne de commande, conçu pour collecter des informations publiques sur les numéros de téléphone. Il prend en charge le traitement par lots, la génération automatisée de dorks de recherche, l'intégration du navigateur et l'utilisation optionnelle de l'API Neutrino.

## Fonctionnalités

- **Recherche de numéros** : Récupérez des informations détaillées sur l'opérateur, la localisation et les métadonnées.
- **Recherches et Dorks** : Générez des requêtes de recherche OSINT ciblées sur plusieurs catégories (réseaux sociaux, forums, e-commerce, sites de notes collées, etc.).
- **Traitement par lots** : Utilisez un fichier texte pour analyser plusieurs numéros en une seule fois.
- **Intégration d'API** : Connectez l'API Neutrino pour une validation avancée des opérateurs et des localisations.
- **Support du navigateur et des cartes** : Ouvrez directement les résultats de recherche dans votre navigateur par défaut ou affichez des coordonnées cartographiques.

---

## Installation

Assurez-vous que Python 3.8+ est installé sur votre système, puis installez l'outil via pip :

```bash
pip install phoneintel
