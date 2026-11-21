<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:020617,35:0c4a6e,70:0284c7,100:38bdf8&height=180&section=header&text=𝗜𝗡𝗦𝗧𝗔𝗟𝗟𝗔𝗧𝗜𝗢𝗡&fontSize=48&fontColor=f0f9ff&stroke=7dd3fc&strokeWidth=1.2&fontAlignY=38&desc=𝗣𝗛𝗢𝗡𝗘𝗜𝗡𝗧𝗘𝗟%20%C2%B7%20𝗧𝗘𝗥𝗠𝗨𝗫%20%C2%B7%20𝗟𝗜𝗡𝗨𝗫%20%C2%B7%20𝗺𝗮𝗰𝗢𝗦&descSize=15&descAlignY=63&descColor=bae6fd&animation=fadeIn" width="100%" alt="Install PhoneIntel Banner" />

<p>
  <img src="https://img.shields.io/badge/ANDROID_16-TERMUX_%F0%9F%AB%86-38BDF8?style=for-the-badge&labelColor=0F172A&logo=android&logoColor=7DD3FC" alt="Termux" />
  <img src="https://img.shields.io/badge/LINUX-DEBIAN_%2F_ARCH_%2F_FEDORA-7DD3FC?style=for-the-badge&labelColor=0F172A&logo=linux&logoColor=38BDF8" alt="Linux" />
  <img src="https://img.shields.io/badge/VENV-PEP_668_SAFE-0EA5E9?style=for-the-badge&labelColor=0F172A&logo=python&logoColor=BAE6FD" alt="PEP 668 Safe" />
</p>

</div>

---

## ⚡ 1. Installation Automatisée (Recommandée)

Le script **`install.sh`** détecte automatiquement votre OS (**Termux Android 16**, **Debian/Ubuntu/Kali**, **Arch**, **Fedora**, **macOS**), crée un environnement virtuel isolé (`~/.venvs/phoneintel`) conforme **PEP 668**, et configure la commande globale `phoneintel`.

```bash
git clone https://github.com/teremuhamblin/PhoneINTEL.git
cd PhoneINTEL
bash install.sh
```

### Options utiles de `install.sh`

| Option | Rôle |
| :--- | :--- |
| `bash install.sh --local` | Installe depuis votre code source local (`src/phoneintel.py`) |
| `bash install.sh --pypi` | Installe le paquet officiel depuis PyPI |
| `bash install.sh --dev` | Installe en plus `pytest`, `pytest-cov`, `ruff`, `mypy`, `bandit` |
| `bash install.sh -y` | Exécution non-interactive (CI / scripts) |

---

## 🤖 2. Installation Spécifique Termux (Android 16)

```bash
pkg update && pkg upgrade -y
pkg install -y python git
git clone https://github.com/teremuhamblin/PhoneINTEL.git
cd PhoneINTEL
bash install.sh -y
```

> [!TIP]
> Si la commande `phoneintel` n'est pas reconnue immédiatement après l'installation, rechargez votre shell :
> `export PATH="$HOME/.local/bin:$PATH"`

---

## 🧹 3. Désinstallation

```bash
# Supprimer le lanceur et le venv isolé
bash uninstall.sh

# Supprimer aussi les logs d'installation
bash uninstall.sh --purge
```
