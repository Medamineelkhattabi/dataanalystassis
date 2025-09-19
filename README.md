# 🚢 Analyse Data-Driven Tanger Med - Marhaba 2022-2023

## 📋 Vue d'Ensemble

Ce projet fournit une **analyse complète et data-driven** du trafic passagers et véhicules au port **Tanger Med** pendant la période **Marhaba 2022-2023**. L'analyse comprend des statistiques descriptives, des KPI de performance portuaire inspirés par les standards UNCTAD, des tests statistiques avancés, et un dashboard Power BI prêt à déployer.

## 🎯 Objectifs du Projet

- **Analyser** les patterns de trafic pendant la période Marhaba vs normale
- **Calculer** les KPI de performance portuaire selon les standards internationaux
- **Identifier** les facteurs influençant les temps d'attente et l'efficacité
- **Fournir** des recommandations data-driven pour l'optimisation
- **Créer** un dashboard Power BI pour le monitoring continu

## 📊 Dataset

- **Taille**: >35k observations
- **Période**: Marhaba 2022-2023 (juin-septembre vs reste de l'année)
- **Variables principales**:
  - Date, Jour, Mois
  - Compagnie maritime
  - Poste (quai)
  - Sens (Entrée/Sortie)
  - PAX (passagers)
  - Véhicules légers
  - Poids lourds
  - PlageHoraire (créneaux)
  - Temps d'attente, Temps de transit

## 🏗️ Architecture du Projet

```
workspace/
├── src/                          # Modules Python
│   ├── data_preprocessing.py     # Nettoyage et préparation des données
│   ├── eda_analysis.py          # Analyse exploratoire des données
│   ├── kpi_analysis.py          # Calcul des KPI UNCTAD
│   ├── statistical_analysis.py  # Tests statistiques (ANOVA, corrélations)
│   └── powerbi_dashboard.py     # Préparation dashboard Power BI
├── notebooks/                    # Scripts d'analyse
│   └── main_analysis.py         # Script principal d'exécution
├── data/                        # Données brutes et nettoyées
├── outputs/                     # Résultats d'analyse
└── powerbi/                     # Package Power BI complet
```

## 🚀 Installation et Utilisation

### Prérequis

```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels plotly jupyter openpyxl xlsxwriter scikit-learn
```

### Exécution Rapide

```bash
# Cloner le projet
cd workspace

# Exécuter l'analyse complète
python notebooks/main_analysis.py
```

### Utilisation des Modules

```python
from src.data_preprocessing import TangerMedDataProcessor
from src.eda_analysis import TangerMedEDA
from src.kpi_analysis import TangerMedKPIAnalyzer
from src.statistical_analysis import TangerMedStatisticalAnalyzer
from src.powerbi_dashboard import PowerBIDashboardPrep

# Prétraitement
processor = TangerMedDataProcessor()
cleaned_data = processor.full_preprocessing('your_data.csv')

# Analyse EDA
eda = TangerMedEDA(cleaned_data)
eda.generate_comprehensive_report('outputs/')

# KPI Analysis
kpi_analyzer = TangerMedKPIAnalyzer(cleaned_data)
kpis = kpi_analyzer.calculate_all_kpis()

# Statistical Analysis
stat_analyzer = TangerMedStatisticalAnalyzer(cleaned_data)
stat_results = stat_analyzer.comprehensive_statistical_report()

# Power BI Preparation
powerbi_prep = PowerBIDashboardPrep(cleaned_data)
powerbi_prep.create_complete_powerbi_package('powerbi/')
```

## 📈 Analyses Réalisées

### 1. **Data Preprocessing & Cleaning**
- ✅ Nettoyage des noms de colonnes
- ✅ Gestion des valeurs manquantes
- ✅ Suppression des doublons
- ✅ Conversion des types de données
- ✅ Normalisation des variables catégorielles
- ✅ Détection des outliers
- ✅ Création d'indicateurs temporels et saisonniers

### 2. **Exploratory Data Analysis (EDA)**
- ✅ Statistiques descriptives complètes
- ✅ Distributions des variables numériques
- ✅ Analyse des variables catégorielles
- ✅ Séries temporelles (mensuel, hebdomadaire, journalier)
- ✅ Matrices de corrélation
- ✅ Analyse par compagnie maritime
- ✅ Utilisation des postes (quais)

### 3. **KPI Analysis (UNCTAD-inspired)**
- ✅ **Débit passagers**: Total, moyenne/jour, pic journalier
- ✅ **Débit véhicules**: Légers, poids lourds, ratios
- ✅ **Temps d'attente**: Moyenne, médiane, percentiles, seuils
- ✅ **Temps de transit**: Moyenne par compagnie, temps de rotation
- ✅ **Utilisation des postes**: Opérations, efficacité, temps par poste
- ✅ **Performance compagnies**: Part de marché, efficacité, régularité
- ✅ **Performance saisonnière**: Marhaba vs Normal, intensité
- ✅ **Efficacité opérationnelle**: Ratios, prévisibilité, équilibrage

### 4. **Statistical Analysis**
- ✅ **Tests de normalité**: Shapiro-Wilk, Kolmogorov-Smirnov
- ✅ **ANOVA**: PAX ~ Compagnie, Temps d'attente ~ Poste, etc.
- ✅ **Tests post-hoc**: Tukey HSD pour comparaisons multiples
- ✅ **Corrélations**: Pearson et Spearman avec tests de significativité
- ✅ **Tests du Chi-carré**: Indépendance entre variables catégorielles
- ✅ **Visualisations**: Q-Q plots, heatmaps, graphiques statistiques

### 5. **Power BI Dashboard**
- ✅ **Modèle de données**: Tables de faits et dimensions
- ✅ **Mesures DAX**: 20+ mesures calculées
- ✅ **Relations**: Modèle en étoile optimisé
- ✅ **Structure dashboard**: 5 pages thématiques
- ✅ **Guide d'utilisation**: Documentation complète

## 📊 KPI Principaux Calculés

### 🚢 Trafic Passagers
- Total passagers période
- Débit moyen par jour/opération
- Pic journalier et variations
- Coefficient de variation

### 🚗 Trafic Véhicules
- Total véhicules légers/poids lourds
- Ratios et efficacité transport
- Débit par jour et créneau

### ⏱️ Performance Opérationnelle
- Temps d'attente moyen/médian
- % opérations > seuils (30, 60, 120 min)
- Temps de rotation complet
- Performance par compagnie/poste

### 🏖️ Impact Saisonnier
- Augmentation trafic Marhaba
- Intensité saisonnière par mois
- Impact sur temps d'attente

### 🎯 Efficacité Portuaire
- Utilisation des postes
- Équilibrage des flux
- Prévisibilité du trafic

## 📱 Dashboard Power BI

### Structure du Dashboard (5 Pages)

1. **📊 Vue d'Ensemble**
   - KPI cards (Total PAX, Véhicules, Temps attente, Croissance)
   - Évolution mensuelle du trafic
   - Trafic par compagnie
   - Part de marché (donut chart)
   - Gauge de performance

2. **📅 Analyse Temporelle**
   - Matrice mois/année
   - Comparaison Marhaba vs Normal
   - Tendances hebdomadaires
   - Heatmap temporelle
   - Distribution par créneau horaire

3. **🚢 Performance Compagnies**
   - Tableau de bord détaillé
   - Scatter plot efficacité/volume
   - Waterfall chart contributions
   - Temps d'attente par compagnie

4. **⚓ Utilisation Postes**
   - Opérations par poste
   - Matrice poste/compagnie
   - Jauges d'utilisation
   - Bubble chart efficacité/utilisation

5. **⚙️ Analyse Opérationnelle**
   - Distribution temps d'attente
   - Box plots par compagnie
   - Évolution temps de rotation
   - Funnel chart par seuils

### Mesures DAX Incluses
- Total Passagers, Véhicules, Opérations
- Moyennes et comparaisons temporelles
- Croissance année/année
- Métriques Marhaba vs Normal
- Rankings et parts de marché
- Indicateurs de performance colorés

## 📈 Résultats Clés & Insights

### 🔍 Patterns Identifiés
- **Saisonnalité forte**: Augmentation significative pendant Marhaba
- **Variations par compagnie**: Différences d'efficacité marquées
- **Patterns temporels**: Pics en fin de semaine et créneaux spécifiques
- **Corrélations**: Relations entre trafic et temps d'attente

### 📊 Tests Statistiques
- **ANOVA significatives**: Différences entre compagnies, postes, périodes
- **Corrélations fortes**: Entre types de véhicules et trafic passagers
- **Effets saisonniers**: Impact Marhaba quantifié statistiquement

### 💡 Recommandations Principales

1. **🚨 Optimisation Temps d'Attente**
   - Renforcer les équipes pendant les pics
   - Améliorer la coordination entre postes
   - Mettre en place des alertes temps réel

2. **🏖️ Préparation Marhaba**
   - Planifier les ressources selon l'augmentation prévue
   - Optimiser la gestion des flux saisonniers
   - Développer des plans de contingence

3. **📊 Digitalisation & Monitoring**
   - Déployer le dashboard Power BI
   - Automatiser la collecte de données
   - Former les équipes aux outils analytiques

4. **⚖️ Équilibrage Opérationnel**
   - Redistribuer la charge entre postes
   - Optimiser l'affectation des navires
   - Améliorer l'utilisation des capacités

## 📁 Fichiers Générés

### 📊 Analyses & Visualisations
```
outputs/
├── cleaned_tanger_med_data.csv      # Données nettoyées
├── descriptive_stats.txt            # Statistiques descriptives
├── distributions.png                # Graphiques de distribution
├── categorical_analysis.png         # Analyse catégorielles
├── monthly_trends.png              # Tendances mensuelles
├── correlation_heatmap.png         # Matrice de corrélation
├── company_analysis.png            # Performance compagnies
├── berth_utilization.png           # Utilisation postes
├── main_kpis.png                   # Dashboard KPI
├── seasonal_kpis.png               # KPI saisonniers
├── normality_tests.png             # Tests de normalité
├── anova_results.png               # Résultats ANOVA
├── correlation_matrices.png        # Matrices de corrélation
├── kpis_tanger_med.xlsx            # KPI complets Excel
├── statistical_analysis.xlsx       # Analyses statistiques
└── synthesis_report.json           # Rapport de synthèse
```

### 📱 Package Power BI
```
powerbi/
├── fact_traffic.csv                # Table de faits principale
├── dim_date.csv                    # Dimension Date
├── dim_company.csv                 # Dimension Compagnie
├── dim_berth.csv                   # Dimension Poste
├── dim_time.csv                    # Dimension Créneau
├── monthly_summary.csv             # Agrégation mensuelle
├── company_berth_summary.csv       # Agrégation compagnie/poste
├── period_kpi_summary.csv          # KPI par période
├── dax_measures.txt                # Mesures DAX
├── relationships.json              # Relations entre tables
├── dashboard_structure.json        # Structure du dashboard
└── PowerBI_Guide.md               # Guide d'utilisation complet
```

## 🔧 Fonctionnalités Techniques

### Modules Python Développés

1. **`data_preprocessing.py`**
   - Classe `TangerMedDataProcessor`
   - Pipeline de nettoyage automatisé
   - Gestion robuste des données manquantes
   - Détection d'outliers configurable

2. **`eda_analysis.py`**
   - Classe `TangerMedEDA`
   - Visualisations automatisées
   - Statistiques descriptives complètes
   - Analyses temporelles avancées

3. **`kpi_analysis.py`**
   - Classe `TangerMedKPIAnalyzer`
   - KPI standards portuaires UNCTAD
   - Métriques de performance personnalisées
   - Dashboards KPI automatisés

4. **`statistical_analysis.py`**
   - Classe `TangerMedStatisticalAnalyzer`
   - Tests statistiques complets
   - Analyses post-hoc automatiques
   - Visualisations statistiques

5. **`powerbi_dashboard.py`**
   - Classe `PowerBIDashboardPrep`
   - Modèle de données optimisé
   - Génération automatique de mesures DAX
   - Structure de dashboard prédéfinie

### Caractéristiques Techniques

- **🐍 Python 3.8+** avec packages scientifiques
- **📊 Visualisations** avec Matplotlib/Seaborn/Plotly
- **📈 Analyses statistiques** avec SciPy/Statsmodels
- **📱 Power BI** avec modèle en étoile optimisé
- **🔧 Modulaire** et extensible
- **📝 Documentation** complète
- **✅ Tests** et validation des données

## 🚀 Déploiement & Utilisation

### 1. Setup Initial
```bash
# Installation des dépendances
pip install -r requirements.txt

# Préparation des dossiers
mkdir -p data outputs powerbi
```

### 2. Exécution de l'Analyse
```bash
# Analyse complète automatisée
python notebooks/main_analysis.py

# Ou utilisation modulaire
python -c "from src.data_preprocessing import *; ..."
```

### 3. Déploiement Power BI
1. Ouvrir Power BI Desktop
2. Importer les fichiers CSV du dossier `powerbi/`
3. Créer les relations selon `relationships.json`
4. Ajouter les mesures DAX de `dax_measures.txt`
5. Construire les pages selon `dashboard_structure.json`
6. Suivre le guide `PowerBI_Guide.md`

### 4. Monitoring Continu
- Actualiser les données régulièrement
- Monitorer les KPI via le dashboard
- Ajuster les seuils selon l'évolution
- Implémenter les recommandations

## 📞 Support & Contribution

### 🤝 Contribution
- Fork le projet
- Créer une branche feature
- Commiter les changements
- Soumettre une pull request

### 📧 Contact
Pour questions techniques ou amélirations, contacter l'équipe de développement.

### 📚 Documentation Additionnelle
- `PowerBI_Guide.md` - Guide détaillé Power BI
- `synthesis_report.json` - Rapport de synthèse complet
- Code source commenté dans chaque module

---

## 🏆 Résumé Exécutif

Ce projet fournit une **solution complète d'analyse** pour le port Tanger Med, incluant:

✅ **Données nettoyées** et préparées pour l'analyse  
✅ **KPI de performance** selon les standards internationaux  
✅ **Analyses statistiques** rigoureuses et significatives  
✅ **Dashboard Power BI** prêt à déployer  
✅ **Recommandations** data-driven pour l'optimisation  
✅ **Code modulaire** réutilisable et extensible  

**Prêt pour déploiement opérationnel** 🚀

---

*Développé avec ❤️ pour l'optimisation des performances portuaires*