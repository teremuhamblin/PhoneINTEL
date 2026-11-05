###### install.md >> markdown
# 📱 PhoneIntel
### Installation & Configuration
- Automatisée sous Termux

Le projet intègre un script d'installation robuste et sécurisé (**`install.sh`**) conçu exclusivement pour l'environnement **Termux** sous Android.
- Il automatise le déploiement de **PhoneIntel** en garantissant l'isolation des dépendances et l'intégrité du système.

### Caractéristiques Techniques du Script
- 》》 **Vérification d'Environnement** : Détection stricte de l'environnement Termux (**`$TERMUX_VERSION`**) pour éviter toute exécution sur des systèmes non compatibles.


- 》》 **Isolation via Environnement Virtuel (venv)** : Installation de PhoneIntel dans un environnement virtuel Python isolé (**`$HOME/.venvs/phoneintel`**) pour prévenir les conflits avec les paquets globaux du système.


- 》》 **Gestion des Dépendances** : Mise à jour automatique des miroirs et paquets APT (**`python`, `python-pip`, `git`, `libffi`, `openssl`, `clang`, `make`**) avec vérification préalable.


- 》》 **Wrapper d'Exécution Global** : Création d'un script relais dans **`$HOME/.local/bin/phoneintel`** et injection automatique dans le **`$PATH`** du fichier **`.bashrc`**.

- 》》 **Gestion Stricte des Erreurs** : Utilisation de **`set -euo pipefail`** pour stopper immédiatement le script en cas d'échec d'une commande ou de variable non initialisée.

### Utilisation du Script
Pour lancer l'installation automatisée sur votre appareil Termux :
```bash
# Télécharger ou copier le script d'installation, puis :
chmod +x install.sh
./install.sh
```

>> **Une fois l'installation terminée, la commande globale phoneintel est directement accessible depuis n'importe quel répertoire du terminal**.

