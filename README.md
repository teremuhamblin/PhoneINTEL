###### README.md >> markdown

# PhoneIntel

[![PyPI version](https://img.shields.io/pypi/v/phoneintel.svg)](https://pypi.org/project/phoneintel/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)


**PhoneIntel** est un outil OSINT (*Open Source Intelligence*) léger en ligne de commande, **conçu pour collecter des informations publiques sur les numéros de téléphone**.
- *Il prend en charge le traitement par lots, la génération automatisée de dorks de recherche, l'intégration du navigateur et l'utilisation optionnelle de l'API Neutrino*.

### Fonctionnalités
```text
- **Recherche de numéros** : Récupérez des informations détaillées sur l'opérateur, la localisation et les métadonnées.
- **Recherches et Dorks** : Générez des requêtes de recherche OSINT ciblées sur plusieurs catégories (réseaux sociaux, forums, e-commerce, sites de notes collées, etc.).
- **Traitement par lots** : Utilisez un fichier texte pour analyser plusieurs numéros en une seule fois.
- **Intégration d'API** : Connectez l'API Neutrino pour une validation avancée des opérateurs et des localisations.
- **Support du navigateur et des cartes** : Ouvrez directement les résultats de recherche dans votre navigateur par défaut ou affichez des coordonnées cartographiques.
```

---
---

### Installation
Assurez-vous que **Python 3.8+** est installé sur votre système, *puis installez l'outil via* **pip** :

```bash
pip install phoneintel
```

### Utilisation et Commandes
#### 1. Recherche et informations de base
###### Obtenir des informations générales sur un numéro
- 》》 **phoneintel --info +14155552671**

###### Obtenir des informations avec l'option carte
- 》》 **phoneintel --info +14155552671 --map**

#### 2. Recherches et Entrées par lots
###### Recherche standard
- 》》 **phoneintel --search +14155552671**

###### Recherche à l'aide d'une chaîne de texte
- 》》 **phoneintel --search --string "John Doe"**

###### Traitement par lots via un fichier d'entrée
- 》》 **phoneintel --search --input numbers.txt**

###### Recherche utilisant l'API Neutrino
- 》》 **phoneintel --search +14155552671 --neutrino-api**

#### 3. Génération de Dorks OSINT
​Générez des requêtes de reconnaissance ciblées sur différentes plateformes :
###### Cibler des catégories spécifiques (social_networks, forums, pastes, ecommerce, news, etc.)
- 》》 **phoneintel --dorks +14155552671 --type social_networks**
- 》》 **phoneintel --dorks +14155552671 --type forums**
- 》》 **phoneintel --dorks +14155552671 --type pastes**

###### Générer tous les types de dorks disponibles
- 》》 **phoneintel --dorks +14155552671 --type all**
- 》》 **phoneintel --dorks +14155552671 --type all --map**
- 》》 **phoneintel --dorks +14155552671 --type all --neutrino-api**

#### 4. Intégration du Navigateur et de l'API
###### Ouvrir les résultats directement dans un navigateur
- 》》 **phoneintel --browser +14155552671**
- 》》 **phoneintel --browser +14155552671 --neutrino-api**

###### Configurer les identifiants de l'API Neutrino
- 》》 **phoneintel --neutrino --login --id VOTRE_ID_API --key VOTRE_CLE_API
phoneintel --neutrino --show**

###### Traiter un numéro via l'API Neutrino avec l'option carte
- 》》 **phoneintel --neutrino +14155552671 --map**

#### 5. Commandes Utilitaires
###### Afficher les crédits
- 》》 **phoneintel --credits**

###### Afficher la clause de non-responsabilité
- 》》 **phoneintel --disclaimer**

### Avertissement
```text
​PhoneIntel est destiné à des fins éducatives et à des évaluations de sécurité autorisées uniquement. Les utilisateurs sont seuls responsables du respect des lois locales et des réglementations en matière de confidentialité. Les auteurs décline toute responsabilité en cas de mauvaise utilisation.
```

### ​Licence
- ​**Distribué sous la licence BSD3**.
   - 》》 *Voir le fichier LICENSE pour plus de détails*.












