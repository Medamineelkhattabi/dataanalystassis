#!/usr/bin/env python3
"""
Analyse Complète du Trafic Tanger Med - Marhaba 2022-2023
Script principal d'exécution de toutes les analyses
"""

import sys
import os
sys.path.append('../src')

# Imports des modules personnalisés
from data_preprocessing import TangerMedDataProcessor, create_sample_data
from eda_analysis import TangerMedEDA
from kpi_analysis import TangerMedKPIAnalyzer
from statistical_analysis import TangerMedStatisticalAnalyzer
from powerbi_dashboard import PowerBIDashboardPrep

# Imports standards
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime
import json

def main():
    """Fonction principale d'exécution de l'analyse complète"""
    
    print("🚀 DÉBUT DE L'ANALYSE COMPLÈTE TANGER MED")
    print("=" * 60)
    print(f"📅 Date d'exécution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    warnings.filterwarnings('ignore')
    plt.style.use('seaborn-v0_8')
    
    # Créer les dossiers de sortie
    os.makedirs('../outputs', exist_ok=True)
    os.makedirs('../powerbi', exist_ok=True)
    os.makedirs('../data', exist_ok=True)
    
    # =============================================================================
    # 1. DATA PREPROCESSING & CLEANING
    # =============================================================================
    print("\n🧹 ÉTAPE 1: PREPROCESSING & CLEANING")
    print("-" * 40)
    
    # Initialiser le processeur
    processor = TangerMedDataProcessor()
    
    # Créer des données d'exemple (remplacez par vos vraies données)
    print("📊 Création des données d'exemple...")
    sample_data = create_sample_data(35000, '../data/sample_tanger_med_data.csv')
    data_file = '../data/sample_tanger_med_data.csv'
    
    # Prétraitement complet
    print("🔄 Prétraitement des données...")
    cleaned_data = processor.full_preprocessing(data_file)
    
    # Résumé des données
    summary = processor.get_data_summary()
    print(f"✅ Données nettoyées: {summary['shape'][0]:,} observations")
    print(f"📊 Total passagers: {summary['total_pax']:,}")
    print(f"🚗 Total véhicules légers: {summary['total_vehicules_legers']:,}")
    print(f"🚛 Total poids lourds: {summary['total_poids_lourds']:,}")
    
    # Sauvegarder
    processor.save_cleaned_data('../outputs/cleaned_tanger_med_data.csv')
    
    # =============================================================================
    # 2. EXPLORATORY DATA ANALYSIS (EDA)
    # =============================================================================
    print("\n📈 ÉTAPE 2: EXPLORATORY DATA ANALYSIS")
    print("-" * 40)
    
    # Initialiser l'analyseur EDA
    eda_analyzer = TangerMedEDA(cleaned_data)
    
    # Générer toutes les analyses EDA
    print("📊 Génération des statistiques descriptives...")
    descriptive_stats = eda_analyzer.generate_descriptive_stats('../outputs/descriptive_stats.txt')
    
    print("📊 Création des graphiques...")
    eda_analyzer.plot_distributions('../outputs')
    eda_analyzer.plot_categorical_analysis('../outputs')
    eda_analyzer.plot_time_series('../outputs')
    eda_analyzer.plot_correlation_heatmap('../outputs')
    eda_analyzer.plot_company_analysis('../outputs')
    eda_analyzer.plot_berth_utilization('../outputs')
    
    print("✅ Analyse EDA terminée!")
    
    # =============================================================================
    # 3. KPI ANALYSIS (UNCTAD-INSPIRED)
    # =============================================================================
    print("\n🎯 ÉTAPE 3: KPI ANALYSIS")
    print("-" * 40)
    
    # Initialiser l'analyseur KPI
    kpi_analyzer = TangerMedKPIAnalyzer(cleaned_data)
    
    # Calculer tous les KPI
    print("📊 Calcul des KPI de performance...")
    all_kpis = kpi_analyzer.calculate_all_kpis()
    
    # Afficher les KPI principaux
    if 'passenger_throughput' in all_kpis:
        pt = all_kpis['passenger_throughput']
        print(f"🚢 Débit passagers moyen/jour: {pt.get('avg_pax_per_day', 0):,.0f}")
        print(f"📈 Pic journalier: {pt.get('max_pax_per_day', 0):,}")
    
    if 'waiting_times' in all_kpis:
        wt = all_kpis['waiting_times']
        print(f"⏱️ Temps d'attente moyen: {wt.get('avg_waiting_time', 0):.1f} min")
        print(f"🔴 Opérations > 60min: {wt.get('pct_waiting_over_60min', 0):.1f}%")
    
    if 'seasonal_performance' in all_kpis:
        sp = all_kpis['seasonal_performance']
        print(f"🏖️ Augmentation Marhaba: +{sp.get('marhaba_increase_pax', 0):.1f}%")
    
    # Créer les graphiques KPI
    print("📊 Création du dashboard KPI...")
    kpi_analyzer.plot_kpi_dashboard('../outputs')
    
    # Sauvegarder le rapport KPI
    kpi_analyzer.save_kpi_report('../outputs')
    
    print("✅ Analyse KPI terminée!")
    
    # =============================================================================
    # 4. STATISTICAL ANALYSIS
    # =============================================================================
    print("\n🔬 ÉTAPE 4: STATISTICAL ANALYSIS")
    print("-" * 40)
    
    # Initialiser l'analyseur statistique
    stat_analyzer = TangerMedStatisticalAnalyzer(cleaned_data)
    
    # Générer le rapport statistique complet
    print("📊 Génération des analyses statistiques...")
    statistical_report = stat_analyzer.comprehensive_statistical_report()
    
    # Compter les résultats significatifs
    significant_anovas = 0
    if 'anova' in statistical_report:
        for dep_var, indep_results in statistical_report['anova'].items():
            for indep_var, result in indep_results.items():
                if result['is_significant']:
                    significant_anovas += 1
    
    total_correlations = 0
    if 'correlation' in statistical_report:
        for method in ['pearson', 'spearman']:
            if method in statistical_report['correlation']:
                total_correlations += len(statistical_report['correlation'][method]['significant_correlations'])
    
    print(f"📊 Tests ANOVA significatifs: {significant_anovas}")
    print(f"📊 Corrélations significatives: {total_correlations}")
    
    # Créer les graphiques statistiques
    print("📊 Création des graphiques statistiques...")
    stat_analyzer.plot_statistical_results('../outputs')
    
    # Sauvegarder l'analyse complète
    stat_analyzer.save_complete_analysis('../outputs')
    
    print("✅ Analyse statistique terminée!")
    
    # =============================================================================
    # 5. POWER BI DASHBOARD PREPARATION
    # =============================================================================
    print("\n📊 ÉTAPE 5: POWER BI DASHBOARD")
    print("-" * 40)
    
    # Initialiser la préparation Power BI
    powerbi_prep = PowerBIDashboardPrep(cleaned_data)
    
    # Créer le package complet Power BI
    print("📊 Création du package Power BI...")
    powerbi_prep.create_complete_powerbi_package('../powerbi')
    
    print(f"📊 Tables créées: {len(powerbi_prep.dashboard_tables)}")
    print(f"📈 Mesures DAX: {len(powerbi_prep.measures)}")
    print(f"🔗 Relations: {len(powerbi_prep.relationships)}")
    print(f"📱 Pages dashboard: {len(powerbi_prep.dashboard_structure['pages'])}")
    
    print("✅ Package Power BI créé!")
    
    # =============================================================================
    # 6. SYNTHESIS & RECOMMENDATIONS
    # =============================================================================
    print("\n💡 ÉTAPE 6: SYNTHÈSE & RECOMMANDATIONS")
    print("-" * 40)
    
    # Créer un rapport de synthèse
    synthesis_report = {
        'metadata': {
            'date_creation': datetime.now().isoformat(),
            'periode_analyse': summary['periode'],
            'total_observations': summary['shape'][0],
            'version': '1.0'
        },
        'kpi_principaux': {
            'total_passagers': summary['total_pax'],
            'total_vehicules_legers': summary['total_vehicules_legers'],
            'total_poids_lourds': summary['total_poids_lourds'],
            'compagnies_actives': summary['compagnies'],
            'postes_utilises': summary['postes']
        },
        'resultats_statistiques': {
            'anova_significatives': significant_anovas,
            'correlations_significatives': total_correlations
        }
    }
    
    # Générer des recommandations
    recommendations = []
    
    # Recommandations basées sur les temps d'attente
    if 'waiting_times' in all_kpis:
        wt = all_kpis['waiting_times']
        avg_waiting = wt.get('avg_waiting_time', 0)
        pct_over_60 = wt.get('pct_waiting_over_60min', 0)
        
        if avg_waiting > 45:
            recommendations.append({
                'priorite': 'HAUTE',
                'domaine': 'Temps d\'attente',
                'probleme': f'Temps d\'attente moyen élevé: {avg_waiting:.1f}min',
                'actions': [
                    'Optimiser les processus d\'embarquement',
                    'Renforcer les équipes pendant les pics',
                    'Améliorer la coordination entre postes'
                ]
            })
        
        if pct_over_60 > 20:
            recommendations.append({
                'priorite': 'MOYENNE',
                'domaine': 'Efficacité opérationnelle',
                'probleme': f'{pct_over_60:.1f}% des opérations > 60min',
                'actions': [
                    'Identifier les causes de retards',
                    'Mettre en place des alertes temps réel',
                    'Développer des plans de contingence'
                ]
            })
    
    # Recommandations saisonnières
    if 'seasonal_performance' in all_kpis:
        sp = all_kpis['seasonal_performance']
        marhaba_increase = sp.get('marhaba_increase_pax', 0)
        
        if marhaba_increase > 50:
            recommendations.append({
                'priorite': 'HAUTE',
                'domaine': 'Préparation saisonnière',
                'probleme': f'Forte augmentation Marhaba: +{marhaba_increase:.1f}%',
                'actions': [
                    'Renforcer les capacités en période estivale',
                    'Planifier les ressources humaines',
                    'Optimiser la gestion des flux'
                ]
            })
    
    # Recommandations technologiques
    recommendations.append({
        'priorite': 'MOYENNE',
        'domaine': 'Digitalisation',
        'probleme': 'Besoin d\'outils de monitoring en temps réel',
        'actions': [
            'Implémenter le dashboard Power BI créé',
            'Automatiser la collecte de données',
            'Former les équipes aux outils analytiques'
        ]
    })
    
    synthesis_report['recommendations'] = recommendations
    
    # Sauvegarder le rapport de synthèse
    with open('../outputs/synthesis_report.json', 'w', encoding='utf-8') as f:
        json.dump(synthesis_report, f, indent=2, ensure_ascii=False)
    
    # Afficher les recommandations
    print("💡 RECOMMANDATIONS PRINCIPALES:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. 🎯 {rec['domaine']} (Priorité: {rec['priorite']})")
        print(f"   Problème: {rec['probleme']}")
        print("   Actions recommandées:")
        for action in rec['actions']:
            print(f"   • {action}")
    
    # =============================================================================
    # 7. RÉSUMÉ FINAL
    # =============================================================================
    print("\n🎉 ANALYSE COMPLÈTE TERMINÉE!")
    print("=" * 60)
    
    # Compter les fichiers générés
    output_files = []
    for root, dirs, files in os.walk('../outputs'):
        for file in files:
            if file.endswith(('.csv', '.xlsx', '.png', '.txt', '.json')):
                output_files.append(file)
    
    for root, dirs, files in os.walk('../powerbi'):
        for file in files:
            if file.endswith(('.csv', '.txt', '.json', '.md')):
                output_files.append(f"powerbi/{file}")
    
    print(f"📊 RÉSULTATS GÉNÉRÉS:")
    print(f"  • Données nettoyées: {summary['shape'][0]:,} observations")
    print(f"  • Total fichiers: {len(output_files)}")
    print(f"  • KPI calculés: {len(all_kpis)} catégories")
    print(f"  • Tests statistiques: {significant_anovas + total_correlations} significatifs")
    print(f"  • Tables Power BI: {len(powerbi_prep.dashboard_tables)}")
    print(f"  • Recommandations: {len(recommendations)}")
    
    print(f"\n📁 DOSSIERS DE SORTIE:")
    print(f"  • ../outputs/ - Analyses, graphiques, rapports")
    print(f"  • ../powerbi/ - Package Power BI complet")
    print(f"  • ../data/ - Données nettoyées")
    
    print(f"\n🚀 PROCHAINES ÉTAPES:")
    print(f"  1. Déployer le dashboard Power BI")
    print(f"  2. Former les équipes aux outils")
    print(f"  3. Implémenter les recommandations")
    print(f"  4. Mettre en place le monitoring continu")
    
    print(f"\n✅ ANALYSE TANGER MED COMPLÈTE - SUCCÈS!")
    
    return synthesis_report

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n🎯 Rapport de synthèse sauvegardé: ../outputs/synthesis_report.json")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()