# 🚀 Guide d'Installation - Analyse Tanger Med

## 📋 Vue d'Ensemble

Ce guide détaille l'installation complète du projet d'analyse data-driven du trafic Tanger Med, depuis la configuration de l'environnement jusqu'au déploiement du dashboard Power BI.

## ⚡ Installation Rapide (Quick Start)

```bash
# 1. Cloner ou télécharger le projet
git clone [repository-url] tanger-med-analysis
cd tanger-med-analysis

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Exécuter l'analyse complète
python notebooks/main_analysis.py

# 4. Consulter les résultats
ls outputs/     # Analyses et graphiques
ls powerbi/     # Package Power BI
```

## 🔧 Installation Détaillée

### Étape 1: Prérequis Système

#### Système d'Exploitation
- **Windows**: 10/11 (64-bit)
- **macOS**: 10.15+ (Catalina ou plus récent)
- **Linux**: Ubuntu 18.04+, CentOS 7+, ou équivalent

#### Logiciels Requis
- **Python**: 3.8 ou plus récent
- **Power BI Desktop**: Version récente (pour le dashboard)
- **Navigateur Web**: Chrome, Firefox, Safari, ou Edge

#### Ressources Minimales
- **RAM**: 8 GB minimum, 16 GB recommandé
- **Stockage**: 2 GB d'espace libre
- **CPU**: Processeur 64-bit, 4 cœurs recommandé

### Étape 2: Configuration Python

#### Option A: Installation avec pip (Recommandée)

```bash
# Vérifier la version Python
python --version  # Doit être 3.8+

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances depuis requirements.txt
pip install -r requirements.txt

# Vérifier l'installation
python -c "import pandas, numpy, matplotlib, seaborn; print('✅ Installation réussie')"
```

#### Option B: Installation avec conda

```bash
# Créer un environnement conda
conda create -n tanger-med python=3.9
conda activate tanger-med

# Installer les packages conda
conda install pandas numpy matplotlib seaborn scipy statsmodels jupyter openpyxl

# Installer les packages pip restants
pip install plotly xlsxwriter scikit-learn

# Vérifier l'installation
python -c "import pandas, numpy, matplotlib, seaborn; print('✅ Installation réussie')"
```

#### Option C: Installation avec environnement virtuel

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Sur Windows:
venv\Scripts\activate
# Sur macOS/Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
python -c "import pandas, numpy, matplotlib, seaborn; print('✅ Installation réussie')"
```

### Étape 3: Configuration du Projet

#### Structure des Dossiers

```bash
# Créer la structure de dossiers
mkdir -p data outputs powerbi logs

# Vérifier la structure
ls -la
# Doit afficher: src/, notebooks/, data/, outputs/, powerbi/, requirements.txt, README.md
```

#### Permissions (Linux/macOS)

```bash
# Donner les permissions d'exécution
chmod +x notebooks/main_analysis.py
chmod +x scripts/*.sh  # Si des scripts shell sont présents

# Vérifier les permissions
ls -la notebooks/main_analysis.py
```

#### Variables d'Environnement

```bash
# Ajouter le projet au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Pour rendre permanent (Linux/macOS)
echo 'export PYTHONPATH="${PYTHONPATH}:'$(pwd)'/src"' >> ~/.bashrc
source ~/.bashrc

# Sur Windows (PowerShell)
$env:PYTHONPATH += ";$(Get-Location)\src"
```

### Étape 4: Test de l'Installation

#### Test Rapide

```bash
# Test d'import des modules
python -c "
from src.data_preprocessing import TangerMedDataProcessor
from src.eda_analysis import TangerMedEDA
from src.kpi_analysis import TangerMedKPIAnalyzer
from src.statistical_analysis import TangerMedStatisticalAnalyzer
from src.powerbi_dashboard import PowerBIDashboardPrep
print('✅ Tous les modules importés avec succès')
"
```

#### Test avec Données d'Exemple

```bash
# Exécuter avec des données d'exemple
python -c "
from src.data_preprocessing import create_sample_data
import os
os.makedirs('data', exist_ok=True)
sample_data = create_sample_data(1000, 'data/test_data.csv')
print(f'✅ Données d\\'exemple créées: {len(sample_data)} lignes')
"
```

#### Test Complet

```bash
# Exécuter l'analyse complète (peut prendre quelques minutes)
python notebooks/main_analysis.py

# Vérifier les sorties
ls outputs/    # Doit contenir des fichiers CSV, PNG, XLSX
ls powerbi/    # Doit contenir des fichiers CSV, TXT, JSON, MD
```

## 📊 Configuration Power BI

### Étape 1: Installation Power BI Desktop

#### Téléchargement
1. Aller sur [powerbi.microsoft.com](https://powerbi.microsoft.com)
2. Télécharger **Power BI Desktop** (gratuit)
3. Installer avec les options par défaut

#### Vérification
1. Ouvrir Power BI Desktop
2. Vérifier la version (doit être récente)
3. Fermer Power BI Desktop

### Étape 2: Préparation des Données Power BI

```bash
# S'assurer que le package Power BI est créé
python -c "
from src.powerbi_dashboard import PowerBIDashboardPrep
from src.data_preprocessing import TangerMedDataProcessor, create_sample_data
import pandas as pd

# Créer des données d'exemple si nécessaire
sample_data = create_sample_data(5000, 'data/sample_data.csv')

# Préprocessing
processor = TangerMedDataProcessor()
cleaned_data = processor.full_preprocessing('data/sample_data.csv')

# Créer le package Power BI
powerbi_prep = PowerBIDashboardPrep(cleaned_data)
powerbi_prep.create_complete_powerbi_package('powerbi/')

print('✅ Package Power BI créé')
"
```

### Étape 3: Import dans Power BI

1. **Ouvrir Power BI Desktop**

2. **Importer les Données**
   ```
   Obtenir des données > Texte/CSV
   Naviguer vers le dossier powerbi/
   Importer dans cet ordre:
   - dim_date.csv
   - dim_company.csv  
   - dim_berth.csv
   - dim_time.csv
   - fact_traffic.csv
   ```

3. **Créer les Relations**
   ```
   Aller dans l'onglet "Modèle"
   Créer les relations selon relationships.json:
   - fact_traffic[date_key] → dim_date[date_key]
   - fact_traffic[company_key] → dim_company[company_key]
   - fact_traffic[berth_key] → dim_berth[berth_key]
   - fact_traffic[time_slot_key] → dim_time[time_slot_key]
   ```

4. **Ajouter les Mesures DAX**
   ```
   Ouvrir dax_measures.txt
   Pour chaque mesure:
   - Clic droit sur fact_traffic > Nouvelle mesure
   - Copier-coller la formule DAX
   - Renommer la mesure
   ```

5. **Créer les Pages**
   ```
   Suivre la structure dans dashboard_structure.json
   Créer 5 pages selon PowerBI_Guide.md
   ```

## 🔧 Configuration Avancée

### Configuration pour Gros Datasets

```python
# Modifier dans src/data_preprocessing.py
CHUNK_SIZE = 10000  # Réduire si problèmes de mémoire
MAX_MEMORY_GB = 8   # Ajuster selon votre système

# Configuration pandas pour gros datasets
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 20)
```

### Configuration Logging

```python
# Créer un fichier de configuration logging
import logging
import os

# Créer le dossier logs
os.makedirs('logs', exist_ok=True)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tanger_med.log'),
        logging.StreamHandler()
    ]
)
```

### Configuration Matplotlib (Français)

```python
# Ajouter au début de vos scripts
import matplotlib.pyplot as plt
import locale

# Configuration pour affichage en français
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux/macOS
except:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')  # Windows
    except:
        pass  # Garder la configuration par défaut

# Configuration matplotlib
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
```

## 🐛 Résolution des Problèmes Courants

### Problème: Import Error

**Erreur**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Vérifier le PYTHONPATH
echo $PYTHONPATH  # Linux/macOS
echo $env:PYTHONPATH  # Windows PowerShell

# Ajouter le chemin src
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/macOS
$env:PYTHONPATH += ";$(Get-Location)\src"     # Windows PowerShell

# Ou exécuter depuis le répertoire racine
cd /path/to/tanger-med-analysis
python -c "import sys; sys.path.append('src'); from data_preprocessing import *"
```

### Problème: Dépendances Manquantes

**Erreur**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**:
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt

# Vérifier les versions
pip list | grep -E "(pandas|numpy|matplotlib|seaborn)"

# Si problème persistant, utiliser conda
conda install pandas numpy matplotlib seaborn scipy statsmodels
```

### Problème: Erreur de Mémoire

**Erreur**: `MemoryError` ou système qui rame

**Solution**:
```python
# Réduire la taille des données d'exemple
sample_data = create_sample_data(5000, 'data/sample_data.csv')  # Au lieu de 35000

# Utiliser des types optimisés
OPTIMIZED_DTYPES = {
    'pax': 'int32',
    'vehicules_legers': 'int16',
    'poids_lourds': 'int16',
    'temps_attente': 'float32',
    'temps_transit': 'float32'
}

# Traiter par chunks
chunk_size = 1000  # Ajuster selon votre RAM
```

### Problème: Graphiques ne s'affichent pas

**Erreur**: Graphiques vides ou erreurs matplotlib

**Solution**:
```python
# Configuration backend matplotlib
import matplotlib
matplotlib.use('Agg')  # Pour environnement sans écran
# ou
matplotlib.use('TkAgg')  # Pour environnement avec écran

# Vérifier l'installation
python -c "import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.savefig('test.png'); print('✅ Matplotlib OK')"
```

### Problème: Power BI - Relations non créées

**Erreur**: Relations automatiques échouent dans Power BI

**Solution**:
1. Vérifier que les colonnes clés existent dans les deux tables
2. S'assurer que les types de données correspondent
3. Créer manuellement les relations :
   ```
   Modèle > Gérer les relations > Nouvelle relation
   Sélectionner les tables et colonnes correspondantes
   Cardinalité: Plusieurs à un (N:1)
   Direction du filtre croisé: Unique
   ```

### Problème: Mesures DAX Incorrectes

**Erreur**: Erreurs dans les formules DAX

**Solution**:
1. Vérifier la syntaxe DAX (sensible à la casse)
2. S'assurer que les noms de tables/colonnes correspondent
3. Utiliser l'éditeur DAX de Power BI pour validation
4. Commencer par les mesures simples puis ajouter les complexes

## 📱 Installation Mobile/Tablette

### Power BI Mobile

1. **Télécharger l'application**
   - iOS: App Store > "Microsoft Power BI"
   - Android: Google Play > "Microsoft Power BI"

2. **Configuration**
   - Se connecter avec compte Microsoft
   - Synchroniser les rapports depuis Power BI Service

3. **Accès aux Dashboards**
   - Publier d'abord le rapport depuis Power BI Desktop
   - Accéder via l'application mobile

## 🔄 Mise à Jour et Maintenance

### Mise à Jour des Dépendances

```bash
# Vérifier les versions actuelles
pip list --outdated

# Mettre à jour toutes les dépendances
pip install --upgrade -r requirements.txt

# Ou mise à jour sélective
pip install --upgrade pandas numpy matplotlib seaborn
```

### Mise à Jour du Code

```bash
# Sauvegarder les modifications locales
cp -r outputs/ outputs_backup/
cp -r powerbi/ powerbi_backup/

# Mettre à jour le code (git ou téléchargement)
git pull origin main
# ou télécharger et remplacer les fichiers

# Retester l'installation
python notebooks/main_analysis.py
```

### Nettoyage Périodique

```bash
# Nettoyer les fichiers temporaires
rm -rf __pycache__/
rm -rf src/__pycache__/
rm -rf .pytest_cache/

# Nettoyer les anciens outputs (optionnel)
rm -rf outputs_old/
rm -rf logs/*.log.old
```

## 📞 Support et Aide

### Ressources Documentaires

- **README.md**: Vue d'ensemble et utilisation
- **DOCUMENTATION.md**: Documentation technique détaillée
- **powerbi/PowerBI_Guide.md**: Guide spécifique Power BI
- **Code source**: Commentaires dans chaque module

### Diagnostic Automatique

```bash
# Script de diagnostic
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import pandas as pd
    print(f'✅ Pandas: {pd.__version__}')
except ImportError:
    print('❌ Pandas: Non installé')

try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except ImportError:
    print('❌ NumPy: Non installé')

try:
    import matplotlib
    print(f'✅ Matplotlib: {matplotlib.__version__}')
except ImportError:
    print('❌ Matplotlib: Non installé')

try:
    import seaborn as sns
    print(f'✅ Seaborn: {sns.__version__}')
except ImportError:
    print('❌ Seaborn: Non installé')

import os
print(f'Répertoire courant: {os.getcwd()}')
print(f'Structure: {os.listdir(\".\")}')
"
```

### Contact Support

Pour assistance technique:
1. Vérifier cette documentation
2. Exécuter le diagnostic automatique
3. Consulter les logs dans `logs/tanger_med.log`
4. Contacter l'équipe de développement avec les informations du diagnostic

---

## ✅ Checklist d'Installation

- [ ] Python 3.8+ installé
- [ ] Dépendances Python installées (`pip install -r requirements.txt`)
- [ ] Structure de dossiers créée (`data/`, `outputs/`, `powerbi/`)
- [ ] PYTHONPATH configuré
- [ ] Test d'import des modules réussi
- [ ] Données d'exemple générées
- [ ] Analyse complète exécutée
- [ ] Package Power BI créé
- [ ] Power BI Desktop installé
- [ ] Données importées dans Power BI
- [ ] Relations créées dans Power BI
- [ ] Mesures DAX ajoutées
- [ ] Dashboard Power BI fonctionnel

**🎉 Installation Complète! Vous êtes prêt à analyser les données Tanger Med!**