"""
Module d'Analyse des KPI Tanger Med
Calcul des indicateurs de performance inspirés par UNCTAD
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
import logging
from datetime import datetime, timedelta

# Configuration
warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class TangerMedKPIAnalyzer:
    """
    Classe pour l'analyse des KPI de performance portuaire Tanger Med
    Basée sur les standards UNCTAD pour l'évaluation des ports
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.kpis = {}
        self._validate_data()
    
    def _validate_data(self):
        """Valide la présence des colonnes nécessaires"""
        required_cols = ['pax', 'vehicules_legers', 'poids_lourds']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        
        if missing_cols:
            logger.warning(f"Colonnes manquantes pour les KPI: {missing_cols}")
        
        # Vérifier la colonne date
        if 'date' not in self.data.columns:
            logger.warning("Colonne 'date' manquante - certains KPI temporels ne seront pas calculés")
    
    def calculate_passenger_throughput_kpis(self) -> Dict:
        """
        Calcule les KPI de débit passagers
        
        Returns:
            Dict: KPI de débit passagers
        """
        logger.info("Calcul des KPI de débit passagers...")
        
        kpis = {}
        
        # 1. Débit passagers total
        kpis['total_pax'] = self.data['pax'].sum()
        
        # 2. Débit passagers moyen par opération
        kpis['avg_pax_per_operation'] = self.data['pax'].mean()
        
        # 3. Débit passagers médian
        kpis['median_pax_per_operation'] = self.data['pax'].median()
        
        # 4. Débit passagers par jour (si date disponible)
        if 'date' in self.data.columns:
            daily_pax = self.data.groupby('date')['pax'].sum()
            kpis['avg_pax_per_day'] = daily_pax.mean()
            kpis['max_pax_per_day'] = daily_pax.max()
            kpis['min_pax_per_day'] = daily_pax.min()
            kpis['std_pax_per_day'] = daily_pax.std()
        
        # 5. Débit passagers par heure (si plage horaire disponible)
        if 'plage_horaire' in self.data.columns:
            hourly_pax = self.data.groupby('plage_horaire')['pax'].sum()
            kpis['pax_by_time_slot'] = dict(hourly_pax)
            kpis['peak_hour_pax'] = hourly_pax.max()
            kpis['peak_hour_slot'] = hourly_pax.idxmax()
        
        # 6. Coefficient de variation du trafic passagers
        kpis['pax_coefficient_of_variation'] = self.data['pax'].std() / self.data['pax'].mean() if self.data['pax'].mean() > 0 else 0
        
        return kpis
    
    def calculate_vehicle_throughput_kpis(self) -> Dict:
        """
        Calcule les KPI de débit véhicules
        
        Returns:
            Dict: KPI de débit véhicules
        """
        logger.info("Calcul des KPI de débit véhicules...")
        
        kpis = {}
        
        # 1. Débit total véhicules légers
        kpis['total_light_vehicles'] = self.data['vehicules_legers'].sum()
        kpis['avg_light_vehicles_per_operation'] = self.data['vehicules_legers'].mean()
        
        # 2. Débit total poids lourds
        kpis['total_heavy_vehicles'] = self.data['poids_lourds'].sum()
        kpis['avg_heavy_vehicles_per_operation'] = self.data['poids_lourds'].mean()
        
        # 3. Ratio véhicules légers / poids lourds
        total_light = self.data['vehicules_legers'].sum()
        total_heavy = self.data['poids_lourds'].sum()
        kpis['light_to_heavy_ratio'] = total_light / total_heavy if total_heavy > 0 else float('inf')
        
        # 4. Véhicules par passager (efficacité du transport)
        total_vehicles = total_light + total_heavy
        total_pax = self.data['pax'].sum()
        kpis['vehicles_per_passenger'] = total_vehicles / total_pax if total_pax > 0 else 0
        
        # 5. Débit véhicules par jour
        if 'date' in self.data.columns:
            daily_light = self.data.groupby('date')['vehicules_legers'].sum()
            daily_heavy = self.data.groupby('date')['poids_lourds'].sum()
            
            kpis['avg_light_vehicles_per_day'] = daily_light.mean()
            kpis['avg_heavy_vehicles_per_day'] = daily_heavy.mean()
            kpis['max_light_vehicles_per_day'] = daily_light.max()
            kpis['max_heavy_vehicles_per_day'] = daily_heavy.max()
        
        # 6. Coefficient de variation
        kpis['light_vehicles_cv'] = self.data['vehicules_legers'].std() / self.data['vehicules_legers'].mean() if self.data['vehicules_legers'].mean() > 0 else 0
        kpis['heavy_vehicles_cv'] = self.data['poids_lourds'].std() / self.data['poids_lourds'].mean() if self.data['poids_lourds'].mean() > 0 else 0
        
        return kpis
    
    def calculate_waiting_time_kpis(self) -> Dict:
        """
        Calcule les KPI de temps d'attente
        
        Returns:
            Dict: KPI de temps d'attente
        """
        logger.info("Calcul des KPI de temps d'attente...")
        
        kpis = {}
        
        if 'temps_attente' in self.data.columns:
            waiting_times = self.data['temps_attente'].dropna()
            
            if len(waiting_times) > 0:
                # 1. Temps d'attente moyen
                kpis['avg_waiting_time'] = waiting_times.mean()
                
                # 2. Temps d'attente médian
                kpis['median_waiting_time'] = waiting_times.median()
                
                # 3. Temps d'attente maximum
                kpis['max_waiting_time'] = waiting_times.max()
                
                # 4. Temps d'attente minimum
                kpis['min_waiting_time'] = waiting_times.min()
                
                # 5. Écart-type des temps d'attente
                kpis['std_waiting_time'] = waiting_times.std()
                
                # 6. Percentiles des temps d'attente
                kpis['waiting_time_p95'] = waiting_times.quantile(0.95)
                kpis['waiting_time_p75'] = waiting_times.quantile(0.75)
                kpis['waiting_time_p25'] = waiting_times.quantile(0.25)
                
                # 7. Pourcentage d'opérations avec attente > seuils
                kpis['pct_waiting_over_30min'] = (waiting_times > 30).mean() * 100
                kpis['pct_waiting_over_60min'] = (waiting_times > 60).mean() * 100
                kpis['pct_waiting_over_120min'] = (waiting_times > 120).mean() * 100
                
                # 8. Temps d'attente par compagnie
                if 'compagnie_maritime' in self.data.columns:
                    waiting_by_company = self.data.groupby('compagnie_maritime')['temps_attente'].mean()
                    kpis['waiting_time_by_company'] = dict(waiting_by_company)
                    kpis['best_company_waiting'] = waiting_by_company.idxmin()
                    kpis['worst_company_waiting'] = waiting_by_company.idxmax()
        
        return kpis
    
    def calculate_transit_time_kpis(self) -> Dict:
        """
        Calcule les KPI de temps de transit
        
        Returns:
            Dict: KPI de temps de transit
        """
        logger.info("Calcul des KPI de temps de transit...")
        
        kpis = {}
        
        if 'temps_transit' in self.data.columns:
            transit_times = self.data['temps_transit'].dropna()
            
            if len(transit_times) > 0:
                # 1. Temps de transit moyen
                kpis['avg_transit_time'] = transit_times.mean()
                
                # 2. Temps de transit médian
                kpis['median_transit_time'] = transit_times.median()
                
                # 3. Temps de transit par compagnie
                if 'compagnie_maritime' in self.data.columns:
                    transit_by_company = self.data.groupby('compagnie_maritime')['temps_transit'].mean()
                    kpis['transit_time_by_company'] = dict(transit_by_company)
                    kpis['fastest_company_transit'] = transit_by_company.idxmin()
                    kpis['slowest_company_transit'] = transit_by_company.idxmax()
                
                # 4. Temps de rotation (attente + transit)
                if 'temps_attente' in self.data.columns:
                    turnaround_time = self.data['temps_attente'].fillna(0) + self.data['temps_transit'].fillna(0)
                    kpis['avg_turnaround_time'] = turnaround_time.mean()
                    kpis['median_turnaround_time'] = turnaround_time.median()
        
        return kpis
    
    def calculate_berth_utilization_kpis(self) -> Dict:
        """
        Calcule les KPI d'utilisation des postes
        
        Returns:
            Dict: KPI d'utilisation des postes
        """
        logger.info("Calcul des KPI d'utilisation des postes...")
        
        kpis = {}
        
        if 'poste' in self.data.columns:
            # 1. Nombre d'opérations par poste
            operations_by_berth = self.data.groupby('poste').size()
            kpis['operations_by_berth'] = dict(operations_by_berth)
            
            # 2. Poste le plus utilisé
            kpis['most_used_berth'] = operations_by_berth.idxmax()
            kpis['most_used_berth_operations'] = operations_by_berth.max()
            
            # 3. Poste le moins utilisé
            kpis['least_used_berth'] = operations_by_berth.idxmin()
            kpis['least_used_berth_operations'] = operations_by_berth.min()
            
            # 4. Taux d'utilisation équilibré (coefficient de variation)
            kpis['berth_utilization_cv'] = operations_by_berth.std() / operations_by_berth.mean()
            
            # 5. Trafic passagers par poste
            pax_by_berth = self.data.groupby('poste')['pax'].sum()
            kpis['pax_by_berth'] = dict(pax_by_berth)
            
            # 6. Efficacité par poste (PAX par opération)
            efficiency_by_berth = self.data.groupby('poste')['pax'].mean()
            kpis['efficiency_by_berth'] = dict(efficiency_by_berth)
            kpis['most_efficient_berth'] = efficiency_by_berth.idxmax()
            
            # 7. Temps d'attente par poste
            if 'temps_attente' in self.data.columns:
                waiting_by_berth = self.data.groupby('poste')['temps_attente'].mean()
                kpis['waiting_time_by_berth'] = dict(waiting_by_berth)
                kpis['fastest_berth'] = waiting_by_berth.idxmin()
                kpis['slowest_berth'] = waiting_by_berth.idxmax()
        
        return kpis
    
    def calculate_company_performance_kpis(self) -> Dict:
        """
        Calcule les KPI de performance par compagnie
        
        Returns:
            Dict: KPI de performance par compagnie
        """
        logger.info("Calcul des KPI de performance par compagnie...")
        
        kpis = {}
        
        if 'compagnie_maritime' in self.data.columns:
            # 1. Part de marché par compagnie (en termes de passagers)
            pax_by_company = self.data.groupby('compagnie_maritime')['pax'].sum()
            total_pax = pax_by_company.sum()
            market_share = (pax_by_company / total_pax * 100) if total_pax > 0 else pax_by_company * 0
            kpis['market_share_by_company'] = dict(market_share)
            kpis['market_leader'] = market_share.idxmax()
            kpis['market_leader_share'] = market_share.max()
            
            # 2. Nombre d'opérations par compagnie
            operations_by_company = self.data.groupby('compagnie_maritime').size()
            kpis['operations_by_company'] = dict(operations_by_company)
            
            # 3. Efficacité par compagnie (PAX par opération)
            efficiency_by_company = self.data.groupby('compagnie_maritime')['pax'].mean()
            kpis['efficiency_by_company'] = dict(efficiency_by_company)
            kpis['most_efficient_company'] = efficiency_by_company.idxmax()
            
            # 4. Régularité du trafic par compagnie
            pax_std_by_company = self.data.groupby('compagnie_maritime')['pax'].std()
            pax_mean_by_company = self.data.groupby('compagnie_maritime')['pax'].mean()
            regularity = pax_std_by_company / pax_mean_by_company
            kpis['regularity_by_company'] = dict(regularity)
            kpis['most_regular_company'] = regularity.idxmin()
            
            # 5. Performance véhicules par compagnie
            vehicles_by_company = self.data.groupby('compagnie_maritime')[['vehicules_legers', 'poids_lourds']].sum()
            kpis['vehicles_by_company'] = vehicles_by_company.to_dict()
        
        return kpis
    
    def calculate_seasonal_kpis(self) -> Dict:
        """
        Calcule les KPI saisonniers (Marhaba vs Normal)
        
        Returns:
            Dict: KPI saisonniers
        """
        logger.info("Calcul des KPI saisonniers...")
        
        kpis = {}
        
        if 'is_marhaba' in self.data.columns:
            # 1. Comparaison trafic Marhaba vs Normal
            marhaba_stats = self.data.groupby('is_marhaba')[['pax', 'vehicules_legers', 'poids_lourds']].agg(['sum', 'mean', 'count'])
            
            # Trafic total
            normal_pax = marhaba_stats.loc[False, ('pax', 'sum')] if False in marhaba_stats.index else 0
            marhaba_pax = marhaba_stats.loc[True, ('pax', 'sum')] if True in marhaba_stats.index else 0
            
            kpis['normal_period_pax'] = normal_pax
            kpis['marhaba_period_pax'] = marhaba_pax
            kpis['marhaba_increase_pax'] = ((marhaba_pax - normal_pax) / normal_pax * 100) if normal_pax > 0 else 0
            
            # Trafic moyen par opération
            normal_avg = marhaba_stats.loc[False, ('pax', 'mean')] if False in marhaba_stats.index else 0
            marhaba_avg = marhaba_stats.loc[True, ('pax', 'mean')] if True in marhaba_stats.index else 0
            
            kpis['normal_avg_pax_per_op'] = normal_avg
            kpis['marhaba_avg_pax_per_op'] = marhaba_avg
            kpis['marhaba_avg_increase'] = ((marhaba_avg - normal_avg) / normal_avg * 100) if normal_avg > 0 else 0
            
            # 2. Intensité saisonnière
            if 'date' in self.data.columns:
                # Calculer l'intensité par mois
                monthly_pax = self.data.groupby([self.data['date'].dt.month, 'is_marhaba'])['pax'].sum().unstack(fill_value=0)
                if True in monthly_pax.columns and False in monthly_pax.columns:
                    seasonal_intensity = monthly_pax[True] / (monthly_pax[True] + monthly_pax[False]) * 100
                    kpis['seasonal_intensity_by_month'] = dict(seasonal_intensity)
                    kpis['peak_seasonal_month'] = seasonal_intensity.idxmax()
            
            # 3. Temps d'attente saisonnier
            if 'temps_attente' in self.data.columns:
                waiting_seasonal = self.data.groupby('is_marhaba')['temps_attente'].mean()
                kpis['normal_waiting_time'] = waiting_seasonal.get(False, 0)
                kpis['marhaba_waiting_time'] = waiting_seasonal.get(True, 0)
                
                if waiting_seasonal.get(False, 0) > 0:
                    kpis['marhaba_waiting_increase'] = ((waiting_seasonal.get(True, 0) - waiting_seasonal.get(False, 0)) / 
                                                      waiting_seasonal.get(False, 0) * 100)
        
        return kpis
    
    def calculate_operational_efficiency_kpis(self) -> Dict:
        """
        Calcule les KPI d'efficacité opérationnelle
        
        Returns:
            Dict: KPI d'efficacité opérationnelle
        """
        logger.info("Calcul des KPI d'efficacité opérationnelle...")
        
        kpis = {}
        
        # 1. Ratio passagers/véhicules (efficacité du transport)
        total_pax = self.data['pax'].sum()
        total_vehicles = self.data['vehicules_legers'].sum() + self.data['poids_lourds'].sum()
        kpis['passengers_per_vehicle'] = total_pax / total_vehicles if total_vehicles > 0 else 0
        
        # 2. Taux d'occupation moyen par traversée
        avg_pax_per_crossing = self.data['pax'].mean()
        avg_vehicles_per_crossing = (self.data['vehicules_legers'] + self.data['poids_lourds']).mean()
        kpis['avg_pax_per_crossing'] = avg_pax_per_crossing
        kpis['avg_vehicles_per_crossing'] = avg_vehicles_per_crossing
        
        # 3. Variabilité du trafic (indicateur de prévisibilité)
        pax_cv = self.data['pax'].std() / self.data['pax'].mean() if self.data['pax'].mean() > 0 else 0
        vehicles_cv = (self.data['vehicules_legers'] + self.data['poids_lourds']).std() / (self.data['vehicules_legers'] + self.data['poids_lourds']).mean()
        kpis['traffic_predictability_pax'] = 1 / (1 + pax_cv)  # Plus proche de 1 = plus prévisible
        kpis['traffic_predictability_vehicles'] = 1 / (1 + vehicles_cv)
        
        # 4. Efficacité par créneau horaire
        if 'plage_horaire' in self.data.columns:
            efficiency_by_slot = self.data.groupby('plage_horaire')['pax'].sum()
            total_slots = len(efficiency_by_slot)
            kpis['hourly_efficiency'] = dict(efficiency_by_slot)
            kpis['most_efficient_time_slot'] = efficiency_by_slot.idxmax()
            kpis['least_efficient_time_slot'] = efficiency_by_slot.idxmin()
            
            # Équilibrage des créneaux
            slot_balance = efficiency_by_slot.std() / efficiency_by_slot.mean()
            kpis['time_slot_balance'] = 1 / (1 + slot_balance)  # Plus proche de 1 = mieux équilibré
        
        # 5. Performance par sens (entrée/sortie)
        if 'sens' in self.data.columns:
            perf_by_direction = self.data.groupby('sens')[['pax', 'vehicules_legers', 'poids_lourds']].sum()
            kpis['performance_by_direction'] = perf_by_direction.to_dict()
            
            # Équilibrage entrée/sortie
            if 'ENTRÉE' in perf_by_direction.index and 'SORTIE' in perf_by_direction.index:
                entree_pax = perf_by_direction.loc['ENTRÉE', 'pax']
                sortie_pax = perf_by_direction.loc['SORTIE', 'pax']
                kpis['entry_exit_balance'] = min(entree_pax, sortie_pax) / max(entree_pax, sortie_pax) if max(entree_pax, sortie_pax) > 0 else 0
        
        return kpis
    
    def calculate_all_kpis(self) -> Dict:
        """
        Calcule tous les KPI
        
        Returns:
            Dict: Tous les KPI organisés par catégorie
        """
        logger.info("Calcul de tous les KPI...")
        
        all_kpis = {
            'passenger_throughput': self.calculate_passenger_throughput_kpis(),
            'vehicle_throughput': self.calculate_vehicle_throughput_kpis(),
            'waiting_times': self.calculate_waiting_time_kpis(),
            'transit_times': self.calculate_transit_time_kpis(),
            'berth_utilization': self.calculate_berth_utilization_kpis(),
            'company_performance': self.calculate_company_performance_kpis(),
            'seasonal_performance': self.calculate_seasonal_kpis(),
            'operational_efficiency': self.calculate_operational_efficiency_kpis()
        }
        
        self.kpis = all_kpis
        return all_kpis
    
    def create_kpi_dashboard_summary(self) -> pd.DataFrame:
        """
        Crée un résumé des KPI principaux pour le dashboard
        
        Returns:
            pd.DataFrame: Résumé des KPI principaux
        """
        if not self.kpis:
            self.calculate_all_kpis()
        
        # Sélectionner les KPI les plus importants
        key_kpis = []
        
        # KPI passagers
        if 'passenger_throughput' in self.kpis:
            pt = self.kpis['passenger_throughput']
            key_kpis.extend([
                {'Catégorie': 'Trafic Passagers', 'KPI': 'Total Passagers', 'Valeur': pt.get('total_pax', 0), 'Unité': 'passagers'},
                {'Catégorie': 'Trafic Passagers', 'KPI': 'Moyenne par jour', 'Valeur': pt.get('avg_pax_per_day', 0), 'Unité': 'passagers/jour'},
                {'Catégorie': 'Trafic Passagers', 'KPI': 'Pic journalier', 'Valeur': pt.get('max_pax_per_day', 0), 'Unité': 'passagers'},
            ])
        
        # KPI véhicules
        if 'vehicle_throughput' in self.kpis:
            vt = self.kpis['vehicle_throughput']
            key_kpis.extend([
                {'Catégorie': 'Trafic Véhicules', 'KPI': 'Total Véhicules Légers', 'Valeur': vt.get('total_light_vehicles', 0), 'Unité': 'véhicules'},
                {'Catégorie': 'Trafic Véhicules', 'KPI': 'Total Poids Lourds', 'Valeur': vt.get('total_heavy_vehicles', 0), 'Unité': 'véhicules'},
                {'Catégorie': 'Trafic Véhicules', 'KPI': 'Ratio Légers/Lourds', 'Valeur': vt.get('light_to_heavy_ratio', 0), 'Unité': 'ratio'},
            ])
        
        # KPI temps d'attente
        if 'waiting_times' in self.kpis:
            wt = self.kpis['waiting_times']
            key_kpis.extend([
                {'Catégorie': 'Temps d\'Attente', 'KPI': 'Temps Moyen', 'Valeur': wt.get('avg_waiting_time', 0), 'Unité': 'minutes'},
                {'Catégorie': 'Temps d\'Attente', 'KPI': 'Temps Médian', 'Valeur': wt.get('median_waiting_time', 0), 'Unité': 'minutes'},
                {'Catégorie': 'Temps d\'Attente', 'KPI': '% > 60min', 'Valeur': wt.get('pct_waiting_over_60min', 0), 'Unité': '%'},
            ])
        
        # KPI performance compagnies
        if 'company_performance' in self.kpis:
            cp = self.kpis['company_performance']
            key_kpis.extend([
                {'Catégorie': 'Performance Compagnies', 'KPI': 'Leader du marché', 'Valeur': cp.get('market_leader', 'N/A'), 'Unité': 'compagnie'},
                {'Catégorie': 'Performance Compagnies', 'KPI': 'Part de marché leader', 'Valeur': cp.get('market_leader_share', 0), 'Unité': '%'},
                {'Catégorie': 'Performance Compagnies', 'KPI': 'Compagnie la plus efficace', 'Valeur': cp.get('most_efficient_company', 'N/A'), 'Unité': 'compagnie'},
            ])
        
        # KPI saisonniers
        if 'seasonal_performance' in self.kpis:
            sp = self.kpis['seasonal_performance']
            key_kpis.extend([
                {'Catégorie': 'Performance Saisonnière', 'KPI': 'Augmentation Marhaba (PAX)', 'Valeur': sp.get('marhaba_increase_pax', 0), 'Unité': '%'},
                {'Catégorie': 'Performance Saisonnière', 'KPI': 'Augmentation temps attente Marhaba', 'Valeur': sp.get('marhaba_waiting_increase', 0), 'Unité': '%'},
            ])
        
        return pd.DataFrame(key_kpis)
    
    def plot_kpi_dashboard(self, save_dir: str = None) -> None:
        """
        Crée les graphiques pour le dashboard KPI
        
        Args:
            save_dir (str): Répertoire pour sauvegarder les graphiques
        """
        logger.info("Création du dashboard KPI...")
        
        if not self.kpis:
            self.calculate_all_kpis()
        
        # 1. KPI principaux - Vue d'ensemble
        self._plot_main_kpis(save_dir)
        
        # 2. Performance par compagnie
        self._plot_company_kpis(save_dir)
        
        # 3. Utilisation des postes
        self._plot_berth_kpis(save_dir)
        
        # 4. Performance saisonnière
        self._plot_seasonal_kpis(save_dir)
        
        # 5. Temps d'attente et efficacité
        self._plot_efficiency_kpis(save_dir)
    
    def _plot_main_kpis(self, save_dir: str = None) -> None:
        """Graphiques des KPI principaux"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('KPI Principaux - Tanger Med', fontsize=16)
        
        # 1. Trafic total par type
        ax1 = axes[0, 0]
        if 'passenger_throughput' in self.kpis and 'vehicle_throughput' in self.kpis:
            categories = ['Passagers', 'Véhicules Légers', 'Poids Lourds']
            values = [
                self.kpis['passenger_throughput'].get('total_pax', 0),
                self.kpis['vehicle_throughput'].get('total_light_vehicles', 0),
                self.kpis['vehicle_throughput'].get('total_heavy_vehicles', 0)
            ]
            
            bars = ax1.bar(categories, values, color=['skyblue', 'lightgreen', 'coral'])
            ax1.set_title('Trafic Total par Type')
            ax1.set_ylabel('Nombre total')
            
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:,.0f}', ha='center', va='bottom')
        
        # 2. Temps d'attente - distribution
        ax2 = axes[0, 1]
        if 'waiting_times' in self.kpis:
            wt = self.kpis['waiting_times']
            categories = ['Moyenne', 'Médiane', 'P95']
            values = [
                wt.get('avg_waiting_time', 0),
                wt.get('median_waiting_time', 0),
                wt.get('waiting_time_p95', 0)
            ]
            
            bars = ax2.bar(categories, values, color=['orange', 'yellow', 'red'])
            ax2.set_title('Temps d\'Attente (minutes)')
            ax2.set_ylabel('Minutes')
            
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.1f}', ha='center', va='bottom')
        
        # 3. Performance saisonnière
        ax3 = axes[1, 0]
        if 'seasonal_performance' in self.kpis:
            sp = self.kpis['seasonal_performance']
            categories = ['Normal', 'Marhaba']
            values = [
                sp.get('normal_period_pax', 0),
                sp.get('marhaba_period_pax', 0)
            ]
            
            bars = ax3.bar(categories, values, color=['lightblue', 'darkblue'])
            ax3.set_title('Trafic Passagers par Période')
            ax3.set_ylabel('Nombre de passagers')
            
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:,.0f}', ha='center', va='bottom')
        
        # 4. Efficacité opérationnelle
        ax4 = axes[1, 1]
        if 'operational_efficiency' in self.kpis:
            oe = self.kpis['operational_efficiency']
            categories = ['Passagers/Véhicule', 'Prévisibilité Trafic']
            values = [
                oe.get('passengers_per_vehicle', 0),
                oe.get('traffic_predictability_pax', 0) * 100  # Convertir en pourcentage
            ]
            
            bars = ax4.bar(categories, values, color=['purple', 'green'])
            ax4.set_title('Indicateurs d\'Efficacité')
            ax4.set_ylabel('Valeur')
            
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/main_kpis.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_company_kpis(self, save_dir: str = None) -> None:
        """Graphiques des KPI par compagnie"""
        if 'company_performance' not in self.kpis:
            return
        
        cp = self.kpis['company_performance']
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Performance par Compagnie Maritime', fontsize=16)
        
        # 1. Part de marché
        ax1 = axes[0]
        if 'market_share_by_company' in cp:
            market_share = cp['market_share_by_company']
            companies = list(market_share.keys())
            shares = list(market_share.values())
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(companies)))
            wedges, texts, autotexts = ax1.pie(shares, labels=companies, autopct='%1.1f%%',
                                              colors=colors, startangle=90)
            ax1.set_title('Part de Marché (% Passagers)')
        
        # 2. Efficacité par compagnie
        ax2 = axes[1]
        if 'efficiency_by_company' in cp:
            efficiency = cp['efficiency_by_company']
            companies = list(efficiency.keys())
            eff_values = list(efficiency.values())
            
            bars = ax2.bar(companies, eff_values, color=plt.cm.viridis(np.linspace(0, 1, len(companies))))
            ax2.set_title('Efficacité (PAX moyen par opération)')
            ax2.set_ylabel('Passagers par opération')
            ax2.set_xticklabels(companies, rotation=45, ha='right')
            
            for bar, value in zip(bars, eff_values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/company_kpis.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_berth_kpis(self, save_dir: str = None) -> None:
        """Graphiques des KPI d'utilisation des postes"""
        if 'berth_utilization' not in self.kpis:
            return
        
        bu = self.kpis['berth_utilization']
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Utilisation des Postes', fontsize=16)
        
        # 1. Opérations par poste
        ax1 = axes[0]
        if 'operations_by_berth' in bu:
            operations = bu['operations_by_berth']
            berths = list(operations.keys())
            ops_values = list(operations.values())
            
            bars = ax1.bar(berths, ops_values, color='lightcoral')
            ax1.set_title('Nombre d\'Opérations par Poste')
            ax1.set_xlabel('Poste')
            ax1.set_ylabel('Nombre d\'opérations')
            
            for bar, value in zip(bars, ops_values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value}', ha='center', va='bottom')
        
        # 2. Temps d'attente par poste
        ax2 = axes[1]
        if 'waiting_time_by_berth' in bu:
            waiting = bu['waiting_time_by_berth']
            berths = list(waiting.keys())
            waiting_values = list(waiting.values())
            
            bars = ax2.bar(berths, waiting_values, color='gold')
            ax2.set_title('Temps d\'Attente Moyen par Poste')
            ax2.set_xlabel('Poste')
            ax2.set_ylabel('Minutes')
            
            for bar, value in zip(bars, waiting_values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/berth_kpis.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_seasonal_kpis(self, save_dir: str = None) -> None:
        """Graphiques des KPI saisonniers"""
        if 'seasonal_performance' not in self.kpis:
            return
        
        sp = self.kpis['seasonal_performance']
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Performance Saisonnière - Marhaba vs Normal', fontsize=16)
        
        # 1. Comparaison trafic
        ax1 = axes[0]
        categories = ['Période Normale', 'Période Marhaba']
        pax_values = [sp.get('normal_period_pax', 0), sp.get('marhaba_period_pax', 0)]
        
        bars = ax1.bar(categories, pax_values, color=['lightblue', 'darkblue'])
        ax1.set_title('Trafic Passagers Total')
        ax1.set_ylabel('Nombre de passagers')
        
        for bar, value in zip(bars, pax_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:,.0f}', ha='center', va='bottom')
        
        # Ajouter le pourcentage d'augmentation
        if pax_values[0] > 0:
            increase = ((pax_values[1] - pax_values[0]) / pax_values[0]) * 100
            ax1.text(0.5, 0.95, f'Augmentation: {increase:.1f}%', 
                    transform=ax1.transAxes, ha='center', va='top',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 2. Comparaison temps d'attente
        ax2 = axes[1]
        waiting_values = [sp.get('normal_waiting_time', 0), sp.get('marhaba_waiting_time', 0)]
        
        bars = ax2.bar(categories, waiting_values, color=['lightgreen', 'red'])
        ax2.set_title('Temps d\'Attente Moyen')
        ax2.set_ylabel('Minutes')
        
        for bar, value in zip(bars, waiting_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/seasonal_kpis.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_efficiency_kpis(self, save_dir: str = None) -> None:
        """Graphiques des KPI d'efficacité"""
        if 'operational_efficiency' not in self.kpis:
            return
        
        oe = self.kpis['operational_efficiency']
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Indicateurs d\'Efficacité Opérationnelle', fontsize=16)
        
        # 1. Efficacité par créneau horaire
        ax1 = axes[0]
        if 'hourly_efficiency' in oe:
            hourly = oe['hourly_efficiency']
            slots = list(hourly.keys())
            efficiency_values = list(hourly.values())
            
            bars = ax1.bar(slots, efficiency_values, color='lightgreen')
            ax1.set_title('Trafic par Créneau Horaire')
            ax1.set_xlabel('Créneau')
            ax1.set_ylabel('Nombre de passagers')
            
            for bar, value in zip(bars, efficiency_values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:,.0f}', ha='center', va='bottom')
        
        # 2. Performance par sens
        ax2 = axes[1]
        if 'performance_by_direction' in oe and 'pax' in oe['performance_by_direction']:
            direction_pax = oe['performance_by_direction']['pax']
            directions = list(direction_pax.keys())
            pax_values = list(direction_pax.values())
            
            bars = ax2.bar(directions, pax_values, color=['orange', 'purple'])
            ax2.set_title('Trafic par Sens')
            ax2.set_xlabel('Sens')
            ax2.set_ylabel('Nombre de passagers')
            
            for bar, value in zip(bars, pax_values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:,.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/efficiency_kpis.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def export_kpis_to_excel(self, file_path: str) -> None:
        """
        Exporte tous les KPI vers un fichier Excel
        
        Args:
            file_path (str): Chemin du fichier Excel de sortie
        """
        logger.info("Export des KPI vers Excel...")
        
        if not self.kpis:
            self.calculate_all_kpis()
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Feuille de résumé
            summary_df = self.create_kpi_dashboard_summary()
            summary_df.to_excel(writer, sheet_name='Résumé KPI', index=False)
            
            # Feuilles détaillées pour chaque catégorie
            for category, kpis in self.kpis.items():
                # Convertir les KPI en DataFrame
                kpi_data = []
                for kpi_name, kpi_value in kpis.items():
                    if isinstance(kpi_value, dict):
                        for sub_key, sub_value in kpi_value.items():
                            kpi_data.append({
                                'KPI': f"{kpi_name}_{sub_key}",
                                'Valeur': sub_value
                            })
                    else:
                        kpi_data.append({
                            'KPI': kpi_name,
                            'Valeur': kpi_value
                        })
                
                if kpi_data:
                    category_df = pd.DataFrame(kpi_data)
                    category_df.to_excel(writer, sheet_name=category.replace('_', ' ').title(), index=False)
        
        logger.info(f"KPI exportés vers: {file_path}")
    
    def save_kpi_report(self, output_dir: str = '/workspace/outputs') -> None:
        """
        Sauvegarde un rapport complet des KPI
        
        Args:
            output_dir (str): Répertoire de sortie
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Calculer tous les KPI
        self.calculate_all_kpis()
        
        # Créer les graphiques
        self.plot_kpi_dashboard(output_dir)
        
        # Exporter vers Excel
        self.export_kpis_to_excel(f'{output_dir}/kpis_tanger_med.xlsx')
        
        # Créer un résumé texte
        summary = self.create_kpi_dashboard_summary()
        summary.to_csv(f'{output_dir}/kpi_summary.csv', index=False, encoding='utf-8')
        
        logger.info(f"Rapport KPI complet sauvegardé dans: {output_dir}")


if __name__ == "__main__":
    # Exemple d'utilisation
    from data_preprocessing import TangerMedDataProcessor, create_sample_data
    
    # Créer des données d'exemple
    sample_data = create_sample_data(5000, '/workspace/data/sample_tanger_med_data.csv')
    
    # Prétraitement
    processor = TangerMedDataProcessor()
    cleaned_data = processor.full_preprocessing('/workspace/data/sample_tanger_med_data.csv')
    
    # Analyse KPI
    kpi_analyzer = TangerMedKPIAnalyzer(cleaned_data)
    
    # Générer le rapport complet
    kpi_analyzer.save_kpi_report()
    
    print("Analyse KPI terminée! Consultez /workspace/outputs pour les résultats.")