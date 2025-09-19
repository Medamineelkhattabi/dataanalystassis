"""
Module de Préparation Dashboard Power BI pour Tanger Med
Préparation des données et recommandations pour Power BI
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import calendar

logger = logging.getLogger(__name__)

class PowerBIDashboardPrep:
    """
    Classe pour préparer les données et structures pour Power BI
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.dashboard_tables = {}
        self.measures = {}
        self.relationships = []
        self.dashboard_structure = {}
        
    def create_fact_table(self) -> pd.DataFrame:
        """
        Crée la table de faits principale pour Power BI
        
        Returns:
            pd.DataFrame: Table de faits
        """
        logger.info("Création de la table de faits principale...")
        
        fact_table = self.data.copy()
        
        # Ajouter des clés pour les dimensions
        fact_table['date_key'] = fact_table['date'].dt.strftime('%Y%m%d') if 'date' in fact_table.columns else None
        fact_table['company_key'] = fact_table['compagnie_maritime'].astype(str) if 'compagnie_maritime' in fact_table.columns else None
        fact_table['berth_key'] = fact_table['poste'].astype(str) if 'poste' in fact_table.columns else None
        fact_table['direction_key'] = fact_table['sens'].astype(str) if 'sens' in fact_table.columns else None
        fact_table['time_slot_key'] = fact_table['plage_horaire'].astype(str) if 'plage_horaire' in fact_table.columns else None
        
        # Ajouter un ID unique pour chaque fait
        fact_table['fact_id'] = range(1, len(fact_table) + 1)
        
        # Sélectionner les colonnes pour la table de faits
        fact_columns = [
            'fact_id', 'date_key', 'company_key', 'berth_key', 'direction_key', 'time_slot_key',
            'pax', 'vehicules_legers', 'poids_lourds', 'temps_attente', 'temps_transit',
            'is_marhaba'
        ]
        
        # Filtrer les colonnes existantes
        fact_columns = [col for col in fact_columns if col in fact_table.columns]
        fact_table_final = fact_table[fact_columns]
        
        self.dashboard_tables['fact_traffic'] = fact_table_final
        return fact_table_final
    
    def create_date_dimension(self) -> pd.DataFrame:
        """
        Crée la dimension Date
        
        Returns:
            pd.DataFrame: Table dimension Date
        """
        logger.info("Création de la dimension Date...")
        
        if 'date' not in self.data.columns:
            logger.warning("Colonne date non trouvée")
            return pd.DataFrame()
        
        # Obtenir la plage de dates
        min_date = self.data['date'].min()
        max_date = self.data['date'].max()
        
        # Créer la plage complète de dates
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        date_dim = pd.DataFrame({
            'date_key': date_range.strftime('%Y%m%d'),
            'date': date_range,
            'annee': date_range.year,
            'mois_num': date_range.month,
            'mois_nom': date_range.strftime('%B'),
            'mois_nom_court': date_range.strftime('%b'),
            'jour': date_range.day,
            'jour_semaine_num': date_range.dayofweek,
            'jour_semaine_nom': date_range.strftime('%A'),
            'jour_semaine_nom_court': date_range.strftime('%a'),
            'trimestre': date_range.quarter,
            'semaine_annee': date_range.isocalendar().week,
            'is_marhaba': date_range.month.isin([6, 7, 8, 9]),
            'periode': ['Marhaba' if month in [6, 7, 8, 9] else 'Hors-Marhaba' 
                       for month in date_range.month],
            'is_weekend': date_range.dayofweek.isin([5, 6]),
            'jour_annee': date_range.dayofyear
        })
        
        # Noms en français
        mois_fr = {
            'January': 'Janvier', 'February': 'Février', 'March': 'Mars',
            'April': 'Avril', 'May': 'Mai', 'June': 'Juin',
            'July': 'Juillet', 'August': 'Août', 'September': 'Septembre',
            'October': 'Octobre', 'November': 'Novembre', 'December': 'Décembre'
        }
        
        jours_fr = {
            'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
            'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'
        }
        
        date_dim['mois_nom'] = date_dim['mois_nom'].replace(mois_fr)
        date_dim['jour_semaine_nom'] = date_dim['jour_semaine_nom'].replace(jours_fr)
        
        self.dashboard_tables['dim_date'] = date_dim
        return date_dim
    
    def create_company_dimension(self) -> pd.DataFrame:
        """
        Crée la dimension Compagnie Maritime
        
        Returns:
            pd.DataFrame: Table dimension Compagnie
        """
        logger.info("Création de la dimension Compagnie...")
        
        if 'compagnie_maritime' not in self.data.columns:
            logger.warning("Colonne compagnie_maritime non trouvée")
            return pd.DataFrame()
        
        # Statistiques par compagnie
        company_stats = self.data.groupby('compagnie_maritime').agg({
            'pax': ['sum', 'mean', 'count'],
            'vehicules_legers': 'sum',
            'poids_lourds': 'sum',
            'temps_attente': 'mean',
            'temps_transit': 'mean'
        }).round(2)
        
        # Aplatir les colonnes multi-niveaux
        company_stats.columns = [f'{col[0]}_{col[1]}' if col[1] != '' else col[0] 
                                for col in company_stats.columns]
        
        company_dim = pd.DataFrame({
            'company_key': company_stats.index.astype(str),
            'compagnie_maritime': company_stats.index,
            'total_pax': company_stats['pax_sum'],
            'avg_pax_per_operation': company_stats['pax_mean'],
            'total_operations': company_stats['pax_count'],
            'total_vehicules_legers': company_stats['vehicules_legers'],
            'total_poids_lourds': company_stats['poids_lourds'],
            'avg_temps_attente': company_stats['temps_attente'],
            'avg_temps_transit': company_stats['temps_transit']
        })
        
        # Calculer la part de marché
        total_pax = company_dim['total_pax'].sum()
        company_dim['part_marche_pct'] = (company_dim['total_pax'] / total_pax * 100).round(2)
        
        # Catégoriser les compagnies par taille
        company_dim['categorie_taille'] = pd.cut(
            company_dim['part_marche_pct'],
            bins=[0, 5, 15, 30, 100],
            labels=['Petite', 'Moyenne', 'Grande', 'Majeure'],
            include_lowest=True
        )
        
        self.dashboard_tables['dim_company'] = company_dim
        return company_dim
    
    def create_berth_dimension(self) -> pd.DataFrame:
        """
        Crée la dimension Poste/Quai
        
        Returns:
            pd.DataFrame: Table dimension Poste
        """
        logger.info("Création de la dimension Poste...")
        
        if 'poste' not in self.data.columns:
            logger.warning("Colonne poste non trouvée")
            return pd.DataFrame()
        
        # Statistiques par poste
        berth_stats = self.data.groupby('poste').agg({
            'pax': ['sum', 'mean', 'count'],
            'vehicules_legers': 'sum',
            'poids_lourds': 'sum',
            'temps_attente': 'mean',
            'temps_transit': 'mean'
        }).round(2)
        
        # Aplatir les colonnes
        berth_stats.columns = [f'{col[0]}_{col[1]}' if col[1] != '' else col[0] 
                              for col in berth_stats.columns]
        
        berth_dim = pd.DataFrame({
            'berth_key': berth_stats.index.astype(str),
            'poste': berth_stats.index,
            'total_pax': berth_stats['pax_sum'],
            'avg_pax_per_operation': berth_stats['pax_mean'],
            'total_operations': berth_stats['pax_count'],
            'total_vehicules_legers': berth_stats['vehicules_legers'],
            'total_poids_lourds': berth_stats['poids_lourds'],
            'avg_temps_attente': berth_stats['temps_attente'],
            'avg_temps_transit': berth_stats['temps_transit']
        })
        
        # Calculer le taux d'utilisation relatif
        max_operations = berth_dim['total_operations'].max()
        berth_dim['taux_utilisation_relatif'] = (berth_dim['total_operations'] / max_operations * 100).round(2)
        
        # Catégoriser l'efficacité des postes
        berth_dim['efficacite_categorie'] = pd.cut(
            berth_dim['avg_pax_per_operation'],
            bins=3,
            labels=['Faible', 'Moyenne', 'Élevée'],
            include_lowest=True
        )
        
        self.dashboard_tables['dim_berth'] = berth_dim
        return berth_dim
    
    def create_time_dimension(self) -> pd.DataFrame:
        """
        Crée la dimension Créneau Horaire
        
        Returns:
            pd.DataFrame: Table dimension Temps
        """
        logger.info("Création de la dimension Créneau Horaire...")
        
        if 'plage_horaire' not in self.data.columns:
            logger.warning("Colonne plage_horaire non trouvée")
            return pd.DataFrame()
        
        # Statistiques par créneau horaire
        time_stats = self.data.groupby('plage_horaire').agg({
            'pax': ['sum', 'mean', 'count'],
            'vehicules_legers': 'sum',
            'poids_lourds': 'sum',
            'temps_attente': 'mean'
        }).round(2)
        
        # Aplatir les colonnes
        time_stats.columns = [f'{col[0]}_{col[1]}' if col[1] != '' else col[0] 
                             for col in time_stats.columns]
        
        time_dim = pd.DataFrame({
            'time_slot_key': time_stats.index.astype(str),
            'plage_horaire': time_stats.index,
            'total_pax': time_stats['pax_sum'],
            'avg_pax_per_operation': time_stats['pax_mean'],
            'total_operations': time_stats['pax_count'],
            'avg_temps_attente': time_stats['temps_attente']
        })
        
        # Ajouter des informations sur les créneaux
        def categorize_time_slot(slot):
            if isinstance(slot, str):
                if '00-06' in slot or '06' in slot.split('-')[0]:
                    return 'Nuit/Matin'
                elif '06-12' in slot or '12' in slot.split('-')[1]:
                    return 'Matin'
                elif '12-18' in slot or '18' in slot.split('-')[1]:
                    return 'Après-midi'
                else:
                    return 'Soir/Nuit'
            return 'Inconnu'
        
        time_dim['periode_jour'] = time_dim['plage_horaire'].apply(categorize_time_slot)
        
        # Catégoriser l'activité
        time_dim['niveau_activite'] = pd.cut(
            time_dim['total_pax'],
            bins=3,
            labels=['Faible', 'Moyen', 'Élevé'],
            include_lowest=True
        )
        
        self.dashboard_tables['dim_time'] = time_dim
        return time_dim
    
    def create_aggregated_tables(self) -> Dict[str, pd.DataFrame]:
        """
        Crée des tables agrégées pour améliorer les performances du dashboard
        
        Returns:
            Dict[str, pd.DataFrame]: Tables agrégées
        """
        logger.info("Création des tables agrégées...")
        
        aggregated_tables = {}
        
        # 1. Agrégation mensuelle
        if 'date' in self.data.columns:
            monthly_agg = self.data.groupby([
                self.data['date'].dt.year,
                self.data['date'].dt.month,
                'compagnie_maritime'
            ]).agg({
                'pax': 'sum',
                'vehicules_legers': 'sum',
                'poids_lourds': 'sum',
                'temps_attente': 'mean',
                'temps_transit': 'mean'
            }).reset_index()
            
            monthly_agg.columns = ['annee', 'mois', 'compagnie_maritime', 'total_pax', 
                                  'total_vehicules_legers', 'total_poids_lourds', 
                                  'avg_temps_attente', 'avg_temps_transit']
            
            # Ajouter des informations temporelles
            monthly_agg['date_key'] = monthly_agg['annee'].astype(str) + monthly_agg['mois'].astype(str).str.zfill(2)
            monthly_agg['mois_nom'] = monthly_agg['mois'].apply(lambda x: calendar.month_name[x])
            monthly_agg['is_marhaba'] = monthly_agg['mois'].isin([6, 7, 8, 9])
            
            aggregated_tables['monthly_summary'] = monthly_agg
        
        # 2. Agrégation par compagnie et poste
        if 'compagnie_maritime' in self.data.columns and 'poste' in self.data.columns:
            company_berth_agg = self.data.groupby(['compagnie_maritime', 'poste']).agg({
                'pax': ['sum', 'count'],
                'vehicules_legers': 'sum',
                'poids_lourds': 'sum',
                'temps_attente': 'mean'
            }).reset_index()
            
            # Aplatir les colonnes
            company_berth_agg.columns = ['compagnie_maritime', 'poste', 'total_pax', 'total_operations',
                                        'total_vehicules_legers', 'total_poids_lourds', 'avg_temps_attente']
            
            aggregated_tables['company_berth_summary'] = company_berth_agg
        
        # 3. Résumé des KPI par période
        if 'is_marhaba' in self.data.columns:
            period_kpi = self.data.groupby('is_marhaba').agg({
                'pax': ['sum', 'mean', 'count'],
                'vehicules_legers': ['sum', 'mean'],
                'poids_lourds': ['sum', 'mean'],
                'temps_attente': ['mean', 'median'],
                'temps_transit': ['mean', 'median']
            }).reset_index()
            
            # Aplatir et renommer
            period_kpi.columns = ['is_marhaba', 'total_pax', 'avg_pax', 'total_operations',
                                 'total_vehicules_legers', 'avg_vehicules_legers',
                                 'total_poids_lourds', 'avg_poids_lourds',
                                 'avg_temps_attente', 'median_temps_attente',
                                 'avg_temps_transit', 'median_temps_transit']
            
            period_kpi['periode'] = period_kpi['is_marhaba'].map({True: 'Marhaba', False: 'Hors-Marhaba'})
            
            aggregated_tables['period_kpi_summary'] = period_kpi
        
        # Sauvegarder dans les tables du dashboard
        for name, table in aggregated_tables.items():
            self.dashboard_tables[name] = table
        
        return aggregated_tables
    
    def create_dax_measures(self) -> Dict[str, str]:
        """
        Génère les mesures DAX pour Power BI
        
        Returns:
            Dict[str, str]: Mesures DAX
        """
        logger.info("Création des mesures DAX...")
        
        dax_measures = {
            # Mesures de base
            'Total Passagers': 'SUM(fact_traffic[pax])',
            'Total Véhicules Légers': 'SUM(fact_traffic[vehicules_legers])',
            'Total Poids Lourds': 'SUM(fact_traffic[poids_lourds])',
            'Total Opérations': 'COUNT(fact_traffic[fact_id])',
            
            # Moyennes
            'Moyenne PAX par Opération': 'AVERAGE(fact_traffic[pax])',
            'Temps Attente Moyen': 'AVERAGE(fact_traffic[temps_attente])',
            'Temps Transit Moyen': 'AVERAGE(fact_traffic[temps_transit])',
            
            # Mesures de comparaison
            'PAX Année Précédente': '''
                CALCULATE(
                    [Total Passagers],
                    SAMEPERIODLASTYEAR(dim_date[date])
                )
            ''',
            
            'Croissance PAX (%)': '''
                VAR CurrentYear = [Total Passagers]
                VAR PreviousYear = [PAX Année Précédente]
                RETURN
                IF(
                    PreviousYear <> 0,
                    (CurrentYear - PreviousYear) / PreviousYear * 100,
                    BLANK()
                )
            ''',
            
            # Mesures Marhaba
            'PAX Marhaba': '''
                CALCULATE(
                    [Total Passagers],
                    dim_date[is_marhaba] = TRUE
                )
            ''',
            
            'PAX Hors Marhaba': '''
                CALCULATE(
                    [Total Passagers],
                    dim_date[is_marhaba] = FALSE
                )
            ''',
            
            'Augmentation Marhaba (%)': '''
                VAR MahabaPAX = [PAX Marhaba]
                VAR NormalPAX = [PAX Hors Marhaba]
                RETURN
                IF(
                    NormalPAX <> 0,
                    (MahabaPAX - NormalPAX) / NormalPAX * 100,
                    BLANK()
                )
            ''',
            
            # Mesures de performance
            'Taux Occupation Moyen': '''
                DIVIDE(
                    [Total Passagers],
                    [Total Opérations],
                    0
                )
            ''',
            
            'Efficacité Poste': '''
                DIVIDE(
                    [Total Passagers],
                    DISTINCTCOUNT(fact_traffic[berth_key]),
                    0
                )
            ''',
            
            # Mesures de temps
            'Temps Rotation Moyen': '''
                AVERAGE(fact_traffic[temps_attente]) + AVERAGE(fact_traffic[temps_transit])
            ''',
            
            'Opérations > 60min Attente (%)': '''
                VAR TotalOperations = [Total Opérations]
                VAR LongWaitOperations = 
                    CALCULATE(
                        COUNT(fact_traffic[fact_id]),
                        fact_traffic[temps_attente] > 60
                    )
                RETURN
                IF(
                    TotalOperations > 0,
                    LongWaitOperations / TotalOperations * 100,
                    0
                )
            ''',
            
            # Mesures de ranking
            'Rang Compagnie PAX': '''
                RANKX(
                    ALL(dim_company[compagnie_maritime]),
                    [Total Passagers],
                    ,
                    DESC
                )
            ''',
            
            'Part de Marché (%)': '''
                VAR CompanyPAX = [Total Passagers]
                VAR TotalMarketPAX = 
                    CALCULATE(
                        [Total Passagers],
                        ALL(dim_company)
                    )
                RETURN
                IF(
                    TotalMarketPAX > 0,
                    CompanyPAX / TotalMarketPAX * 100,
                    0
                )
            ''',
            
            # Mesures conditionnelles
            'Couleur Performance': '''
                VAR Performance = [Moyenne PAX par Opération]
                VAR Benchmark = 
                    CALCULATE(
                        AVERAGE(fact_traffic[pax]),
                        ALL()
                    )
                RETURN
                SWITCH(
                    TRUE(),
                    Performance >= Benchmark * 1.1, "Vert",
                    Performance >= Benchmark * 0.9, "Orange",
                    "Rouge"
                )
            ''',
            
            # Mesures de tendance
            'Tendance 3 Mois': '''
                VAR CurrentPeriod = [Total Passagers]
                VAR PreviousPeriod = 
                    CALCULATE(
                        [Total Passagers],
                        DATEADD(dim_date[date], -3, MONTH)
                    )
                RETURN
                IF(
                    AND(CurrentPeriod > 0, PreviousPeriod > 0),
                    IF(CurrentPeriod > PreviousPeriod, "↗", 
                       IF(CurrentPeriod < PreviousPeriod, "↘", "→")),
                    "—"
                )
            '''
        }
        
        self.measures = dax_measures
        return dax_measures
    
    def define_relationships(self) -> List[Dict]:
        """
        Définit les relations entre les tables
        
        Returns:
            List[Dict]: Relations entre tables
        """
        logger.info("Définition des relations entre tables...")
        
        relationships = [
            {
                'from_table': 'fact_traffic',
                'from_column': 'date_key',
                'to_table': 'dim_date',
                'to_column': 'date_key',
                'cardinality': 'many_to_one',
                'cross_filter': 'single'
            },
            {
                'from_table': 'fact_traffic',
                'from_column': 'company_key',
                'to_table': 'dim_company',
                'to_column': 'company_key',
                'cardinality': 'many_to_one',
                'cross_filter': 'single'
            },
            {
                'from_table': 'fact_traffic',
                'from_column': 'berth_key',
                'to_table': 'dim_berth',
                'to_column': 'berth_key',
                'cardinality': 'many_to_one',
                'cross_filter': 'single'
            },
            {
                'from_table': 'fact_traffic',
                'from_column': 'time_slot_key',
                'to_table': 'dim_time',
                'to_column': 'time_slot_key',
                'cardinality': 'many_to_one',
                'cross_filter': 'single'
            }
        ]
        
        self.relationships = relationships
        return relationships
    
    def create_dashboard_structure(self) -> Dict:
        """
        Définit la structure recommandée du dashboard
        
        Returns:
            Dict: Structure du dashboard
        """
        logger.info("Création de la structure du dashboard...")
        
        dashboard_structure = {
            'pages': [
                {
                    'name': 'Vue d\'Ensemble',
                    'description': 'KPI principaux et tendances générales',
                    'visuals': [
                        {
                            'type': 'card',
                            'title': 'Total Passagers',
                            'measure': 'Total Passagers',
                            'format': '#,##0'
                        },
                        {
                            'type': 'card',
                            'title': 'Total Véhicules',
                            'measure': 'Total Véhicules Légers',
                            'format': '#,##0'
                        },
                        {
                            'type': 'card',
                            'title': 'Temps Attente Moyen',
                            'measure': 'Temps Attente Moyen',
                            'format': '#0.0 "min"'
                        },
                        {
                            'type': 'card',
                            'title': 'Croissance vs N-1',
                            'measure': 'Croissance PAX (%)',
                            'format': '+#0.0%;-#0.0%;#0.0%'
                        },
                        {
                            'type': 'line_chart',
                            'title': 'Évolution Mensuelle du Trafic',
                            'x_axis': 'dim_date[mois_nom]',
                            'y_axis': 'Total Passagers',
                            'legend': 'dim_date[annee]'
                        },
                        {
                            'type': 'column_chart',
                            'title': 'Trafic par Compagnie',
                            'x_axis': 'dim_company[compagnie_maritime]',
                            'y_axis': 'Total Passagers',
                            'sort_by': 'Total Passagers DESC'
                        },
                        {
                            'type': 'donut_chart',
                            'title': 'Part de Marché',
                            'legend': 'dim_company[compagnie_maritime]',
                            'values': 'Part de Marché (%)'
                        },
                        {
                            'type': 'gauge',
                            'title': 'Performance vs Objectif',
                            'value': 'Total Passagers',
                            'target': '5000000',  # À ajuster selon les objectifs
                            'min': '0',
                            'max': '6000000'
                        }
                    ],
                    'filters': [
                        'dim_date[annee]',
                        'dim_date[periode]',
                        'dim_company[compagnie_maritime]'
                    ]
                },
                {
                    'name': 'Analyse Temporelle',
                    'description': 'Analyse des patterns temporels et saisonniers',
                    'visuals': [
                        {
                            'type': 'matrix',
                            'title': 'Trafic par Mois et Année',
                            'rows': 'dim_date[mois_nom]',
                            'columns': 'dim_date[annee]',
                            'values': 'Total Passagers'
                        },
                        {
                            'type': 'column_chart',
                            'title': 'Comparaison Marhaba vs Normal',
                            'x_axis': 'dim_date[periode]',
                            'y_axis': ['Total Passagers', 'Temps Attente Moyen']
                        },
                        {
                            'type': 'line_chart',
                            'title': 'Tendance Hebdomadaire',
                            'x_axis': 'dim_date[jour_semaine_nom]',
                            'y_axis': 'Moyenne PAX par Opération'
                        },
                        {
                            'type': 'heatmap',
                            'title': 'Heatmap Mois vs Jour Semaine',
                            'x_axis': 'dim_date[jour_semaine_nom]',
                            'y_axis': 'dim_date[mois_nom]',
                            'values': 'Total Passagers'
                        },
                        {
                            'type': 'area_chart',
                            'title': 'Distribution par Créneau Horaire',
                            'x_axis': 'dim_time[plage_horaire]',
                            'y_axis': 'Total Passagers'
                        }
                    ],
                    'filters': [
                        'dim_date[annee]',
                        'dim_date[trimestre]',
                        'dim_date[is_marhaba]'
                    ]
                },
                {
                    'name': 'Performance Compagnies',
                    'description': 'Analyse détaillée par compagnie maritime',
                    'visuals': [
                        {
                            'type': 'table',
                            'title': 'Tableau de Bord Compagnies',
                            'columns': [
                                'dim_company[compagnie_maritime]',
                                'Total Passagers',
                                'Part de Marché (%)',
                                'Moyenne PAX par Opération',
                                'Temps Attente Moyen',
                                'Rang Compagnie PAX'
                            ]
                        },
                        {
                            'type': 'scatter_chart',
                            'title': 'Efficacité vs Volume',
                            'x_axis': 'Total Passagers',
                            'y_axis': 'Moyenne PAX par Opération',
                            'legend': 'dim_company[compagnie_maritime]',
                            'size': 'Total Opérations'
                        },
                        {
                            'type': 'waterfall_chart',
                            'title': 'Contribution au Trafic Total',
                            'category': 'dim_company[compagnie_maritime]',
                            'y_axis': 'Total Passagers'
                        },
                        {
                            'type': 'bar_chart',
                            'title': 'Temps d\'Attente par Compagnie',
                            'x_axis': 'Temps Attente Moyen',
                            'y_axis': 'dim_company[compagnie_maritime]',
                            'sort_by': 'Temps Attente Moyen ASC'
                        }
                    ],
                    'filters': [
                        'dim_company[categorie_taille]',
                        'dim_date[periode]'
                    ]
                },
                {
                    'name': 'Utilisation Postes',
                    'description': 'Analyse de l\'utilisation et performance des postes',
                    'visuals': [
                        {
                            'type': 'column_chart',
                            'title': 'Opérations par Poste',
                            'x_axis': 'dim_berth[poste]',
                            'y_axis': 'Total Opérations'
                        },
                        {
                            'type': 'matrix',
                            'title': 'Trafic Poste vs Compagnie',
                            'rows': 'dim_berth[poste]',
                            'columns': 'dim_company[compagnie_maritime]',
                            'values': 'Total Passagers'
                        },
                        {
                            'type': 'gauge_chart',
                            'title': 'Taux d\'Utilisation par Poste',
                            'category': 'dim_berth[poste]',
                            'value': 'dim_berth[taux_utilisation_relatif]'
                        },
                        {
                            'type': 'bubble_chart',
                            'title': 'Efficacité vs Utilisation',
                            'x_axis': 'dim_berth[taux_utilisation_relatif]',
                            'y_axis': 'dim_berth[avg_pax_per_operation]',
                            'size': 'Total Passagers',
                            'legend': 'dim_berth[poste]'
                        }
                    ],
                    'filters': [
                        'dim_berth[efficacite_categorie]',
                        'dim_date[periode]'
                    ]
                },
                {
                    'name': 'Analyse Opérationnelle',
                    'description': 'KPI opérationnels et temps de traitement',
                    'visuals': [
                        {
                            'type': 'histogram',
                            'title': 'Distribution Temps d\'Attente',
                            'x_axis': 'fact_traffic[temps_attente]',
                            'bins': 20
                        },
                        {
                            'type': 'box_plot',
                            'title': 'Temps d\'Attente par Compagnie',
                            'category': 'dim_company[compagnie_maritime]',
                            'y_axis': 'fact_traffic[temps_attente]'
                        },
                        {
                            'type': 'line_chart',
                            'title': 'Évolution Temps Rotation',
                            'x_axis': 'dim_date[date]',
                            'y_axis': 'Temps Rotation Moyen'
                        },
                        {
                            'type': 'funnel_chart',
                            'title': 'Répartition Temps d\'Attente',
                            'categories': ['< 30min', '30-60min', '60-120min', '> 120min'],
                            'values': 'Total Opérations'
                        }
                    ],
                    'filters': [
                        'dim_company[compagnie_maritime]',
                        'dim_berth[poste]',
                        'dim_time[periode_jour]'
                    ]
                }
            ],
            'global_filters': [
                {
                    'name': 'Sélecteur Période',
                    'type': 'date_range',
                    'field': 'dim_date[date]'
                },
                {
                    'name': 'Filtre Compagnie',
                    'type': 'multi_select',
                    'field': 'dim_company[compagnie_maritime]'
                },
                {
                    'name': 'Période Marhaba',
                    'type': 'toggle',
                    'field': 'dim_date[is_marhaba]'
                }
            ]
        }
        
        self.dashboard_structure = dashboard_structure
        return dashboard_structure
    
    def export_powerbi_data(self, output_dir: str = '/workspace/powerbi') -> None:
        """
        Exporte toutes les données préparées pour Power BI
        
        Args:
            output_dir (str): Répertoire de sortie
        """
        logger.info("Export des données pour Power BI...")
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Créer toutes les tables si pas déjà fait
        if not self.dashboard_tables:
            self.create_fact_table()
            self.create_date_dimension()
            self.create_company_dimension()
            self.create_berth_dimension()
            self.create_time_dimension()
            self.create_aggregated_tables()
        
        # Exporter chaque table
        for table_name, table_data in self.dashboard_tables.items():
            file_path = f"{output_dir}/{table_name}.csv"
            table_data.to_csv(file_path, index=False, encoding='utf-8-sig')
            logger.info(f"Table exportée: {file_path}")
        
        # Exporter les mesures DAX
        if not self.measures:
            self.create_dax_measures()
        
        with open(f"{output_dir}/dax_measures.txt", 'w', encoding='utf-8') as f:
            f.write("=== MESURES DAX POUR POWER BI ===\n\n")
            for measure_name, dax_formula in self.measures.items():
                f.write(f"Nom de la mesure: {measure_name}\n")
                f.write(f"Formule DAX:\n{dax_formula}\n")
                f.write("-" * 50 + "\n\n")
        
        # Exporter les relations
        if not self.relationships:
            self.define_relationships()
        
        with open(f"{output_dir}/relationships.json", 'w', encoding='utf-8') as f:
            json.dump(self.relationships, f, indent=2, ensure_ascii=False)
        
        # Exporter la structure du dashboard
        if not self.dashboard_structure:
            self.create_dashboard_structure()
        
        with open(f"{output_dir}/dashboard_structure.json", 'w', encoding='utf-8') as f:
            json.dump(self.dashboard_structure, f, indent=2, ensure_ascii=False)
        
        # Créer un guide d'utilisation
        self._create_powerbi_guide(output_dir)
        
        logger.info(f"Export Power BI terminé dans: {output_dir}")
    
    def _create_powerbi_guide(self, output_dir: str) -> None:
        """Crée un guide d'utilisation pour Power BI"""
        guide_content = """
# GUIDE D'UTILISATION POWER BI - TANGER MED DASHBOARD

## 1. IMPORT DES DONNÉES

### Étapes d'import:
1. Ouvrir Power BI Desktop
2. Cliquer sur "Obtenir des données" > "Texte/CSV"
3. Importer les fichiers dans cet ordre:
   - dim_date.csv (Dimension Date)
   - dim_company.csv (Dimension Compagnie)
   - dim_berth.csv (Dimension Poste)
   - dim_time.csv (Dimension Créneau)
   - fact_traffic.csv (Table de Faits)
   - Tables agrégées (monthly_summary.csv, etc.)

### Configuration des types de données:
- Dates: Format Date/Heure
- Clés: Texte
- Mesures numériques: Nombre décimal
- Booléens: Vrai/Faux

## 2. CRÉATION DES RELATIONS

Aller dans l'onglet "Modèle" et créer les relations suivantes:
- fact_traffic[date_key] → dim_date[date_key] (N:1)
- fact_traffic[company_key] → dim_company[company_key] (N:1)
- fact_traffic[berth_key] → dim_berth[berth_key] (N:1)
- fact_traffic[time_slot_key] → dim_time[time_slot_key] (N:1)

## 3. CRÉATION DES MESURES DAX

Copier-coller les mesures du fichier dax_measures.txt dans Power BI:
1. Clic droit sur la table fact_traffic
2. "Nouvelle mesure"
3. Coller la formule DAX
4. Renommer la mesure

## 4. STRUCTURE DU DASHBOARD

Créer 5 pages comme défini dans dashboard_structure.json:

### Page 1: Vue d'Ensemble
- 4 cartes KPI en haut
- Graphique en lignes pour l'évolution mensuelle
- Graphique en colonnes pour le trafic par compagnie
- Graphique en secteurs pour les parts de marché
- Jauge de performance

### Page 2: Analyse Temporelle
- Matrice mois/année
- Comparaison Marhaba vs Normal
- Tendances hebdomadaires
- Heatmap temporelle

### Page 3: Performance Compagnies
- Tableau de bord détaillé
- Nuage de points efficacité/volume
- Graphique en cascade
- Temps d'attente par compagnie

### Page 4: Utilisation Postes
- Opérations par poste
- Matrice poste/compagnie
- Jauges d'utilisation
- Analyse efficacité/utilisation

### Page 5: Analyse Opérationnelle
- Distribution des temps d'attente
- Box plots par compagnie
- Évolution des temps de rotation
- Répartition par seuils de temps

## 5. FILTRES ET INTERACTIONS

### Filtres globaux:
- Sélecteur de période (date range)
- Filtre multi-sélection compagnies
- Toggle Marhaba/Normal

### Interactions entre visuels:
- Activer le filtrage croisé
- Configurer les interactions selon les besoins

## 6. FORMATAGE ET DESIGN

### Couleurs recommandées:
- Bleu principal: #1f77b4
- Orange accent: #ff7f0e
- Vert positif: #2ca02c
- Rouge négatif: #d62728

### Polices:
- Titres: Segoe UI Bold, 14pt
- Texte: Segoe UI, 10pt
- Valeurs: Segoe UI, 12pt

## 7. PUBLICATION ET PARTAGE

1. Enregistrer le fichier .pbix
2. Publier sur Power BI Service
3. Configurer l'actualisation automatique des données
4. Partager avec les utilisateurs appropriés

## 8. MAINTENANCE

- Actualiser les données régulièrement
- Vérifier les performances des requêtes
- Ajuster les mesures selon les besoins métier
- Surveiller l'utilisation du dashboard

## CONTACT SUPPORT

Pour toute question technique, consulter la documentation Power BI officielle
ou contacter l'équipe de développement.
        """
        
        with open(f"{output_dir}/PowerBI_Guide.md", 'w', encoding='utf-8') as f:
            f.write(guide_content)
    
    def create_complete_powerbi_package(self, output_dir: str = '/workspace/powerbi') -> None:
        """
        Crée un package complet pour Power BI
        
        Args:
            output_dir (str): Répertoire de sortie
        """
        logger.info("Création du package Power BI complet...")
        
        # Créer toutes les composantes
        self.create_fact_table()
        self.create_date_dimension()
        self.create_company_dimension()
        self.create_berth_dimension()
        self.create_time_dimension()
        self.create_aggregated_tables()
        self.create_dax_measures()
        self.define_relationships()
        self.create_dashboard_structure()
        
        # Exporter tout
        self.export_powerbi_data(output_dir)
        
        logger.info(f"Package Power BI complet créé dans: {output_dir}")


if __name__ == "__main__":
    # Exemple d'utilisation
    from data_preprocessing import TangerMedDataProcessor, create_sample_data
    
    # Créer des données d'exemple
    sample_data = create_sample_data(5000, '/workspace/data/sample_tanger_med_data.csv')
    
    # Prétraitement
    processor = TangerMedDataProcessor()
    cleaned_data = processor.full_preprocessing('/workspace/data/sample_tanger_med_data.csv')
    
    # Préparation Power BI
    powerbi_prep = PowerBIDashboardPrep(cleaned_data)
    
    # Créer le package complet
    powerbi_prep.create_complete_powerbi_package()
    
    print("Package Power BI créé! Consultez /workspace/powerbi pour tous les fichiers.")