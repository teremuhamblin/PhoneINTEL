###### GUIDES.md >> markdown 
###### Outils OSINT, Piratage éthique, Cybersécurité, Réseautage, Programmation, Outils de force brute, Outils de bombardement, Outils de phishing, Utilitaires Linux, Personnalisation, Distributions Linux, 

---

>Passer au contenu
- 》》 *Application*
   - Web
   - Termux

---

# PhoneIntel
- 》》 dans le terminal
– *outil de collecte d’informations sur les numéros de téléphone*.

**PhoneIntel** est un *outil OSINT simple* qui peut *recueillir des informations publiques sur les numéros de téléphone*. Il fournit différentes commandes pour *rechercher des numéros de téléphone, générer des pers de recherche, ouvrir les résultats dans un navigateur et utiliser des fonctionnalités optionnelles de l’API Neutrino*. PhoneIntel est *utile pour apprendre à connaître les numéros de téléphone, l’OSINT, et la collecte d’informations à partir du terminal*.

- 》》 Fonctionnalités de l’outil *PhoneIntel* :
```text
- Obtenez des informations sur un numéro de téléphone.
- Recherchez des numéros de téléphone et des SMS.
- Générez des nerds de recherche.
- Ouvrez les résultats de recherche dans un navigateur.
- Utilisez un fichier d’entrée pour plusieurs recherches.
- Utilisez des fonctionnalités optionnelles de l’API Neutrino.
- Commande d’installation PhoneIntel
   - Il suffit d’une seule commande pour installer PhoneIntel. Assurez-vous que Python est installé sur votre système, puis exécutez la commande pip suivante dans le terminal pour installer l’outil.
```

### Installation.
》》 **pip install phoneintel**
- PhoneIntel est désormais installé et prêt à être utilisé.

### Commandes d’utilisation
Après avoir installé PhoneIntel, vous pouvez *utiliser différentes commandes pour rechercher des numéros de téléphone et accéder aux fonctionnalités disponibles*.

>>Obtenez des informations sur un numéro de téléphone.

**phoneintel --info +14155552671**
- Obtenez les coordonnées téléphoniques et utilisez l’option carte.

---

**phoneintel --info +14155552671 --map**
- Cherchez un numéro de téléphone.

---

**phoneintel --search +14155552671**
- Recherchez à l’aide d’une chaîne de texte.

---

**phoneintel --search --string "John Doe"**
- Recherchez à l’aide d’un fichier d’entrée.

---

**phoneintel --search --input numbers.txt**
- Recherchez avec les informations de l’API Neutrino.

---

**phoneintel --search +14155552671 --neutrino-api**
- Cherchez avec l’option carte.

---

**phoneintel --search +14155552671 --map**
- Créez des geeks des réseaux sociaux.

---

**phoneintel --dorks +14155552671 --type social_networks**
- Générez des geeks sur les forums.

---

**phoneintel --dorks +14155552671 --type forums**
- Générez des petites annonces, des idiots.

---

**phoneintel --dorks +14155552671 --type classifieds**
- Créez des geeks du e-commerce.

---

**phoneintel --dorks +14155552671 --type ecommerce**
- Générez des nerds d’actualités.

---

**phoneintel --dorks +14155552671 --type news**
- Créez des blogueurs de geeks.

---

**phoneintel --dorks +14155552671 --type blogs**
- Générez des nerds sur le chantier.

---

**phoneintel --dorks +14155552671 --type job_sites**
- Générez des nerds de sites collés.

---

**phoneintel --dorks +14155552671 --type pastes**
- Générez des geeks de réputation.

---

**phoneintel --dorks +14155552671 --type reputation**
- Générez des geeks d’annuaire téléphonique.

---

**phoneintel --dorks +14155552671 --type phone_directories**
- Faites des gens chercher, des geeks.

---

**phoneintel --dorks +14155552671 --type people_search**
- Générez tous les geeks disponibles.

---

**phoneintel --dorks +14155552671 --type all**
- Générez des geeks avec l’option carte.

---

**phoneintel --dorks +14155552671 --type all --map**
- Générez des dorks en utilisant les informations API de Neutrino.

---

**phoneintel --dorks +14155552671 --type all --neutrino-api**
- Ouvre les résultats de recherche de numéro de téléphone dans un navigateur.

---

**phoneintel --browser +14155552671**
- Utilisez la commande navigateur avec les informations de l’API Neutrino.

---

**phoneintel --browser +14155552671 --neutrino-api**
- Utilisez la commande navigateur avec l’option carte.

---

**phoneintel --browser +14155552671 --map**
- Connectez-vous à l’API Neutrino.

---

**phoneintel --neutrino --login --id YOUR_API_ID --key YOUR_API_KEY**
- Afficher les identifiants API Neutrino enregistrés.

---

**phoneintel --neutrino --show**
- Traitez un numéro de téléphone à l’aide de l’API Neutrino.

---

**phoneintel --neutrino +14155552671**
- Utilisez l’API Neutrino avec l’option de map.

---

**phoneintel --neutrino +14155552671 --map**
- Montrez les crédits.

---

**phoneintel --credits**
- Montrez la clause de non-responsabilité.

---

**phoneintel --disclaimer**
- Choisissez la commande dont vous avez besoin, entrez les informations requises, et PhoneIntel exécutera l’opération sélectionnée et affichera les résultats.

### Présentation de PhoneIntel
PhoneIntel propose un *moyen simple d’explorer les informations sur les numéros de téléphone et les options de recherche depuis le terminal*.
- *Il est facile à installer et inclut différentes commandes pour apprendre à connaître les OSINT de numéro de téléphone*.
