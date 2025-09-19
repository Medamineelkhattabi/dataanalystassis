"""
Module d'Analyse Exploratoire des Données (EDA) pour Tanger Med
Statistiques descriptives, visualisations et analyses temporelles
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
import warnings
import logging
from datetime import datetime
import calendar

# Configuration
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration matplotlib pour le français
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

class TangerMedEDA:
    """
    Classe pour l'analyse exploratoire des données Tanger Med
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.numeric_columns = self._get_numeric_columns()
        self.categorical_columns = self._get_categorical_columns()
        self.date_column = self._get_date_column()
        
    def _get_numeric_columns(self) -> List[str]:
        """Identifie les colonnes numériques"""
        numeric_cols = []
        potential_cols = ['pax', 'vehicules_legers', 'poids_lourds', 'temps_attente', 'temps_transit']
        for col in potential_cols:
            if col in self.data.columns:
                numeric_cols.append(col)
        return numeric_cols
    
    def _get_categorical_columns(self) -> List[str]:
        """Identifie les colonnes catégorielles"""
        categorical_cols = []
        potential_cols = ['compagnie_maritime', 'poste', 'sens', 'plage_horaire', 'periode']
        for col in potential_cols:
            if col in self.data.columns:
                categorical_cols.append(col)
        return categorical_cols
    
    def _get_date_column(self) -> Optional[str]:
        """Identifie la colonne date"""
        date_cols = ['date', 'Date']
        for col in date_cols:
            if col in self.data.columns:
                return col
        return None
    
    def generate_descriptive_stats(self, save_path: str = None) -> Dict:
        """
        Génère les statistiques descriptives complètes
        
        Args:
            save_path (str): Chemin pour sauvegarder les résultats
            
        Returns:
            Dict: Statistiques descriptives
        """
        logger.info("Génération des statistiques descriptives...")
        
        stats = {}
        
        # 1. Informations générales
        stats['general'] = {
            'total_observations': len(self.data),
            'periode': f"{self.data[self.date_column].min()} à {self.data[self.date_column].max()}" if self.date_column else "Non disponible",
            'colonnes': list(self.data.columns),
            'types_donnees': dict(self.data.dtypes)
        }
        
        # 2. Statistiques numériques
        if self.numeric_columns:
            stats['numeriques'] = {}
            for col in self.numeric_columns:
                col_stats = {
                    'count': self.data[col].count(),
                    'mean': self.data[col].mean(),
                    'median': self.data[col].median(),
                    'std': self.data[col].std(),
                    'min': self.data[col].min(),
                    'max': self.data[col].max(),
                    'q25': self.data[col].quantile(0.25),
                    'q75': self.data[col].quantile(0.75),
                    'missing': self.data[col].isnull().sum(),
                    'zeros': (self.data[col] == 0).sum()
                }
                stats['numeriques'][col] = col_stats
        
        # 3. Statistiques catégorielles
        if self.categorical_columns:
            stats['categorielles'] = {}
            for col in self.categorical_columns:
                col_stats = {
                    'unique_values': self.data[col].nunique(),
                    'most_common': self.data[col].mode().iloc[0] if len(self.data[col].mode()) > 0 else None,
                    'value_counts': dict(self.data[col].value_counts()),
                    'missing': self.data[col].isnull().sum()
                }
                stats['categorielles'][col] = col_stats
        
        # 4. Statistiques temporelles
        if self.date_column:
            stats['temporelles'] = self._analyze_temporal_patterns()
        
        # 5. Corrélations
        if len(self.numeric_columns) > 1:
            corr_matrix = self.data[self.numeric_columns].corr()
            stats['correlations'] = corr_matrix.to_dict()
        
        if save_path:
            # Sauvegarder en format lisible
            self._save_stats_report(stats, save_path)
        
        return stats
    
    def _analyze_temporal_patterns(self) -> Dict:
        """Analyse les patterns temporels"""
        temporal_stats = {}
        
        if self.date_column and self.date_column in self.data.columns:
            # Conversion en datetime si nécessaire
            if not pd.api.types.is_datetime64_any_dtype(self.data[self.date_column]):
                self.data[self.date_column] = pd.to_datetime(self.data[self.date_column])
            
            # Statistiques par période
            temporal_stats['par_annee'] = self._group_stats('annee')
            temporal_stats['par_mois'] = self._group_stats('mois_num')
            temporal_stats['par_jour_semaine'] = self._group_stats('jour_semaine')
            
            # Marhaba vs Hors-Marhaba
            if 'is_marhaba' in self.data.columns:
                temporal_stats['marhaba_vs_normal'] = self._group_stats('is_marhaba')
        
        return temporal_stats
    
    def _group_stats(self, group_col: str) -> Dict:
        """Calcule les statistiques par groupe"""
        if group_col not in self.data.columns:
            return {}
        
        group_stats = {}
        for col in self.numeric_columns:
            group_stats[col] = {
                'mean': dict(self.data.groupby(group_col)[col].mean()),
                'sum': dict(self.data.groupby(group_col)[col].sum()),
                'count': dict(self.data.groupby(group_col)[col].count())
            }
        
        return group_stats
    
    def plot_distributions(self, save_dir: str = None) -> None:
        """
        Crée les graphiques de distribution pour les variables numériques
        
        Args:
            save_dir (str): Répertoire pour sauvegarder les graphiques
        """
        logger.info("Création des graphiques de distribution...")
        
        if not self.numeric_columns:
            logger.warning("Aucune colonne numérique trouvée")
            return
        
        n_cols = 2
        n_rows = (len(self.numeric_columns) + 1) // 2
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        fig.suptitle('Distributions des Variables Numériques', fontsize=16, y=1.02)
        
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(self.numeric_columns):
            ax = axes[i]
            
            # Histogramme avec KDE
            self.data[col].hist(ax=ax, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            ax2 = ax.twinx()
            self.data[col].plot.kde(ax=ax2, color='red', linewidth=2)
            
            ax.set_title(f'Distribution de {col.replace("_", " ").title()}')
            ax.set_xlabel(col.replace("_", " ").title())
            ax.set_ylabel('Fréquence')
            ax2.set_ylabel('Densité', color='red')
            
            # Statistiques sur le graphique
            stats_text = f'Moyenne: {self.data[col].mean():.1f}\nMédiane: {self.data[col].median():.1f}'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Masquer les axes inutilisés
        for i in range(len(self.numeric_columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/distributions.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_categorical_analysis(self, save_dir: str = None) -> None:
        """
        Analyse des variables catégorielles
        
        Args:
            save_dir (str): Répertoire pour sauvegarder les graphiques
        """
        logger.info("Analyse des variables catégorielles...")
        
        if not self.categorical_columns:
            logger.warning("Aucune colonne catégorielle trouvée")
            return
        
        n_cols = 2
        n_rows = (len(self.categorical_columns) + 1) // 2
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        fig.suptitle('Analyse des Variables Catégorielles', fontsize=16, y=1.02)
        
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(self.categorical_columns):
            ax = axes[i]
            
            # Graphique en barres
            value_counts = self.data[col].value_counts()
            bars = ax.bar(range(len(value_counts)), value_counts.values, 
                         color=plt.cm.Set3(np.linspace(0, 1, len(value_counts))))
            
            ax.set_title(f'Distribution de {col.replace("_", " ").title()}')
            ax.set_xlabel(col.replace("_", " ").title())
            ax.set_ylabel('Nombre d\'observations')
            ax.set_xticks(range(len(value_counts)))
            ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
            
            # Ajouter les valeurs sur les barres
            for bar, value in zip(bars, value_counts.values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value}', ha='center', va='bottom')
        
        # Masquer les axes inutilisés
        for i in range(len(self.categorical_columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/categorical_analysis.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_time_series(self, save_dir: str = None) -> None:
        """
        Crée les graphiques de séries temporelles
        
        Args:
            save_dir (str): Répertoire pour sauvegarder les graphiques
        """
        logger.info("Création des graphiques de séries temporelles...")
        
        if not self.date_column or not self.numeric_columns:
            logger.warning("Colonne date ou colonnes numériques manquantes")
            return
        
        # 1. Évolution mensuelle
        self._plot_monthly_trends(save_dir)
        
        # 2. Évolution hebdomadaire
        self._plot_weekly_patterns(save_dir)
        
        # 3. Comparaison Marhaba vs Normal
        if 'is_marhaba' in self.data.columns:
            self._plot_marhaba_comparison(save_dir)
    
    def _plot_monthly_trends(self, save_dir: str = None) -> None:
        """Graphiques d'évolution mensuelle"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Évolution Mensuelle du Trafic', fontsize=16)
        
        axes = axes.flatten()
        
        # Agrégation mensuelle
        if 'mois_num' in self.data.columns:
            monthly_data = self.data.groupby('mois_num')[self.numeric_columns].sum()
        else:
            monthly_data = self.data.groupby(self.data[self.date_column].dt.month)[self.numeric_columns].sum()
        
        for i, col in enumerate(self.numeric_columns[:4]):  # Limiter à 4 graphiques
            ax = axes[i]
            
            bars = ax.bar(monthly_data.index, monthly_data[col], 
                         color=plt.cm.viridis(i/len(self.numeric_columns)))
            
            ax.set_title(f'Évolution Mensuelle - {col.replace("_", " ").title()}')
            ax.set_xlabel('Mois')
            ax.set_ylabel('Total')
            ax.set_xticks(monthly_data.index)
            ax.set_xticklabels([calendar.month_abbr[m] for m in monthly_data.index])
            
            # Ajouter les valeurs
            for bar, value in zip(bars, monthly_data[col]):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:.0f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/monthly_trends.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_weekly_patterns(self, save_dir: str = None) -> None:
        """Patterns hebdomadaires"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Patterns Hebdomadaires', fontsize=16)
        
        axes = axes.flatten()
        
        # Noms des jours en français
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        if 'jour_semaine' in self.data.columns:
            weekly_data = self.data.groupby('jour_semaine')[self.numeric_columns].mean()
        else:
            weekly_data = self.data.groupby(self.data[self.date_column].dt.dayofweek)[self.numeric_columns].mean()
        
        for i, col in enumerate(self.numeric_columns[:4]):
            ax = axes[i]
            
            bars = ax.bar(range(len(weekly_data)), weekly_data[col], 
                         color=plt.cm.plasma(i/len(self.numeric_columns)))
            
            ax.set_title(f'Pattern Hebdomadaire - {col.replace("_", " ").title()}')
            ax.set_xlabel('Jour de la semaine')
            ax.set_ylabel('Moyenne')
            ax.set_xticks(range(len(weekly_data)))
            ax.set_xticklabels([day_names[i] for i in weekly_data.index], rotation=45)
            
            # Ajouter les valeurs
            for bar, value in zip(bars, weekly_data[col]):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:.0f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/weekly_patterns.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_marhaba_comparison(self, save_dir: str = None) -> None:
        """Comparaison Marhaba vs période normale"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Comparaison Marhaba vs Période Normale', fontsize=16)
        
        axes = axes.flatten()
        
        marhaba_data = self.data.groupby('is_marhaba')[self.numeric_columns].mean()
        
        for i, col in enumerate(self.numeric_columns[:4]):
            ax = axes[i]
            
            categories = ['Hors-Marhaba', 'Marhaba']
            values = [marhaba_data.loc[False, col], marhaba_data.loc[True, col]]
            colors = ['lightcoral', 'lightblue']
            
            bars = ax.bar(categories, values, color=colors)
            
            ax.set_title(f'Comparaison {col.replace("_", " ").title()}')
            ax.set_ylabel('Moyenne')
            
            # Ajouter les valeurs et pourcentage d'augmentation
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
            
            # Calculer et afficher l'augmentation
            if values[0] > 0:
                increase = ((values[1] - values[0]) / values[0]) * 100
                ax.text(0.5, 0.95, f'Augmentation: {increase:.1f}%', 
                       transform=ax.transAxes, ha='center', va='top',
                       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/marhaba_comparison.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_correlation_heatmap(self, save_dir: str = None) -> None:
        """
        Crée une heatmap des corrélations
        
        Args:
            save_dir (str): Répertoire pour sauvegarder le graphique
        """
        logger.info("Création de la heatmap des corrélations...")
        
        if len(self.numeric_columns) < 2:
            logger.warning("Pas assez de colonnes numériques pour les corrélations")
            return
        
        # Calculer la matrice de corrélation
        corr_matrix = self.data[self.numeric_columns].corr()
        
        # Créer la heatmap
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                    square=True, linewidths=0.5, cbar_kws={"shrink": .8},
                    fmt='.2f', annot_kws={'size': 10})
        
        plt.title('Matrice de Corrélation des Variables Numériques', fontsize=14, pad=20)
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_company_analysis(self, save_dir: str = None) -> None:
        """
        Analyse par compagnie maritime
        
        Args:
            save_dir (str): Répertoire pour sauvegarder les graphiques
        """
        logger.info("Analyse par compagnie maritime...")
        
        if 'compagnie_maritime' not in self.data.columns:
            logger.warning("Colonne compagnie_maritime non trouvée")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Analyse par Compagnie Maritime', fontsize=16)
        
        axes = axes.flatten()
        
        # Agrégation par compagnie
        company_data = self.data.groupby('compagnie_maritime')[self.numeric_columns].sum()
        
        for i, col in enumerate(self.numeric_columns[:4]):
            ax = axes[i]
            
            # Trier par valeurs décroissantes
            sorted_data = company_data[col].sort_values(ascending=False)
            
            bars = ax.bar(range(len(sorted_data)), sorted_data.values,
                         color=plt.cm.tab10(np.arange(len(sorted_data))))
            
            ax.set_title(f'{col.replace("_", " ").title()} par Compagnie')
            ax.set_xlabel('Compagnie')
            ax.set_ylabel('Total')
            ax.set_xticks(range(len(sorted_data)))
            ax.set_xticklabels(sorted_data.index, rotation=45, ha='right')
            
            # Ajouter les valeurs et pourcentages
            total = sorted_data.sum()
            for bar, value in zip(bars, sorted_data.values):
                height = bar.get_height()
                percentage = (value / total) * 100 if total > 0 else 0
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:.0f}\n({percentage:.1f}%)', 
                       ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/company_analysis.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_berth_utilization(self, save_dir: str = None) -> None:
        """
        Analyse de l'utilisation des postes (quais)
        
        Args:
            save_dir (str): Répertoire pour sauvegarder les graphiques
        """
        logger.info("Analyse de l'utilisation des postes...")
        
        if 'poste' not in self.data.columns:
            logger.warning("Colonne poste non trouvée")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. Utilisation par poste
        berth_usage = self.data.groupby('poste').size()
        
        ax1 = axes[0]
        bars1 = ax1.bar(berth_usage.index, berth_usage.values, 
                       color=plt.cm.viridis(np.linspace(0, 1, len(berth_usage))))
        
        ax1.set_title('Nombre d\'Opérations par Poste')
        ax1.set_xlabel('Poste')
        ax1.set_ylabel('Nombre d\'opérations')
        
        for bar, value in zip(bars1, berth_usage.values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value}', ha='center', va='bottom')
        
        # 2. Heatmap poste vs jour de la semaine
        if 'jour_semaine' in self.data.columns:
            berth_day_pivot = self.data.pivot_table(
                values='pax', index='poste', columns='jour_semaine', 
                aggfunc='mean', fill_value=0
            )
            
            ax2 = axes[1]
            sns.heatmap(berth_day_pivot, annot=True, cmap='YlOrRd', ax=ax2, fmt='.0f')
            ax2.set_title('Trafic Moyen PAX par Poste et Jour')
            ax2.set_xlabel('Jour de la semaine (0=Lundi)')
            ax2.set_ylabel('Poste')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/berth_utilization.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def generate_comprehensive_report(self, output_dir: str = '/workspace/outputs') -> None:
        """
        Génère un rapport EDA complet avec tous les graphiques et statistiques
        
        Args:
            output_dir (str): Répertoire de sortie
        """
        logger.info("Génération du rapport EDA complet...")
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Statistiques descriptives
        stats = self.generate_descriptive_stats(f'{output_dir}/descriptive_stats.txt')
        
        # 2. Tous les graphiques
        self.plot_distributions(output_dir)
        self.plot_categorical_analysis(output_dir)
        self.plot_time_series(output_dir)
        self.plot_correlation_heatmap(output_dir)
        self.plot_company_analysis(output_dir)
        self.plot_berth_utilization(output_dir)
        
        logger.info(f"Rapport EDA complet généré dans: {output_dir}")
    
    def _save_stats_report(self, stats: Dict, file_path: str) -> None:
        """Sauvegarde le rapport statistique en format texte"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT STATISTIQUES DESCRIPTIVES TANGER MED ===\n\n")
            
            # Informations générales
            f.write("1. INFORMATIONS GÉNÉRALES\n")
            f.write("-" * 30 + "\n")
            for key, value in stats['general'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Statistiques numériques
            if 'numeriques' in stats:
                f.write("2. STATISTIQUES NUMÉRIQUES\n")
                f.write("-" * 30 + "\n")
                for col, col_stats in stats['numeriques'].items():
                    f.write(f"\n{col.upper()}:\n")
                    for stat, value in col_stats.items():
                        f.write(f"  {stat}: {value:.2f if isinstance(value, (int, float)) else value}\n")
                f.write("\n")
            
            # Statistiques catégorielles
            if 'categorielles' in stats:
                f.write("3. STATISTIQUES CATÉGORIELLES\n")
                f.write("-" * 30 + "\n")
                for col, col_stats in stats['categorielles'].items():
                    f.write(f"\n{col.upper()}:\n")
                    f.write(f"  Valeurs uniques: {col_stats['unique_values']}\n")
                    f.write(f"  Plus fréquent: {col_stats['most_common']}\n")
                    f.write(f"  Valeurs manquantes: {col_stats['missing']}\n")
                    f.write("  Distribution:\n")
                    for value, count in col_stats['value_counts'].items():
                        f.write(f"    {value}: {count}\n")
                f.write("\n")
            
            # Statistiques temporelles
            if 'temporelles' in stats:
                f.write("4. STATISTIQUES TEMPORELLES\n")
                f.write("-" * 30 + "\n")
                # Simplifier l'affichage des stats temporelles
                f.write("Patterns temporels calculés et disponibles dans les graphiques.\n\n")


def create_eda_dashboard_data(data: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
    """
    Prépare les données agrégées pour le dashboard Power BI
    
    Args:
        data (pd.DataFrame): Données nettoyées
        output_path (str): Chemin de sauvegarde (optionnel)
        
    Returns:
        pd.DataFrame: Données agrégées pour le dashboard
    """
    logger.info("Préparation des données pour le dashboard...")
    
    # Agrégations multiples pour le dashboard
    dashboard_data = {}
    
    # 1. Données journalières
    if 'date' in data.columns:
        daily_agg = data.groupby('date').agg({
            'pax': ['sum', 'count'],
            'vehicules_legers': 'sum',
            'poids_lourds': 'sum',
            'temps_attente': 'mean',
            'temps_transit': 'mean'
        }).reset_index()
        
        # Aplatir les colonnes multi-niveaux
        daily_agg.columns = ['date'] + [f'{col[0]}_{col[1]}' if col[1] != '' else col[0] 
                                       for col in daily_agg.columns[1:]]
        dashboard_data['daily'] = daily_agg
    
    # 2. Données par compagnie et mois
    if 'compagnie_maritime' in data.columns and 'mois_num' in data.columns:
        company_monthly = data.groupby(['compagnie_maritime', 'mois_num']).agg({
            'pax': 'sum',
            'vehicules_legers': 'sum',
            'poids_lourds': 'sum'
        }).reset_index()
        dashboard_data['company_monthly'] = company_monthly
    
    # 3. Données par poste et période
    if 'poste' in data.columns and 'is_marhaba' in data.columns:
        berth_period = data.groupby(['poste', 'is_marhaba']).agg({
            'pax': 'sum',
            'vehicules_legers': 'sum',
            'poids_lourds': 'sum'
        }).reset_index()
        dashboard_data['berth_period'] = berth_period
    
    # Combiner toutes les données pour le dashboard principal
    main_dashboard = data.copy()
    
    if output_path:
        main_dashboard.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Données dashboard sauvegardées: {output_path}")
    
    return main_dashboard


if __name__ == "__main__":
    # Exemple d'utilisation
    from data_preprocessing import TangerMedDataProcessor
    
    # Charger et nettoyer les données
    processor = TangerMedDataProcessor()
    
    # Utiliser les données d'exemple si elles existent
    try:
        cleaned_data = processor.full_preprocessing('/workspace/data/sample_tanger_med_data.csv')
    except:
        # Créer des données d'exemple si le fichier n'existe pas
        from data_preprocessing import create_sample_data
        sample_data = create_sample_data(5000, '/workspace/data/sample_tanger_med_data.csv')
        cleaned_data = processor.full_preprocessing('/workspace/data/sample_tanger_med_data.csv')
    
    # Créer l'instance EDA
    eda = TangerMedEDA(cleaned_data)
    
    # Générer le rapport complet
    eda.generate_comprehensive_report()
    
    # Préparer les données pour le dashboard
    dashboard_data = create_eda_dashboard_data(cleaned_data, '/workspace/outputs/dashboard_data.csv')
    
    print("Analyse EDA terminée! Consultez le dossier /workspace/outputs pour les résultats.")