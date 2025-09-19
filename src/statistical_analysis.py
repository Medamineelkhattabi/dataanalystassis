"""
Module d'Analyse Statistique Tanger Med
Tests ANOVA, corrélations, tests post-hoc et analyses statistiques avancées
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import f_oneway, pearsonr, spearmanr, chi2_contingency
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols
import warnings
import logging
from typing import Dict, List, Tuple, Optional, Any

# Configuration
warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class TangerMedStatisticalAnalyzer:
    """
    Classe pour l'analyse statistique des données Tanger Med
    """
    
    def __init__(self, data: pd.DataFrame, significance_level: float = 0.05):
        self.data = data.copy()
        self.alpha = significance_level
        self.results = {}
        self._prepare_data()
    
    def _prepare_data(self):
        """Prépare les données pour l'analyse statistique"""
        # Identifier les colonnes numériques et catégorielles
        self.numeric_columns = []
        self.categorical_columns = []
        
        for col in self.data.columns:
            if self.data[col].dtype in ['int64', 'float64']:
                self.numeric_columns.append(col)
            elif self.data[col].dtype == 'object' or self.data[col].dtype.name == 'category':
                self.categorical_columns.append(col)
        
        logger.info(f"Colonnes numériques: {self.numeric_columns}")
        logger.info(f"Colonnes catégorielles: {self.categorical_columns}")
    
    def test_normality(self, columns: List[str] = None) -> Dict:
        """
        Test de normalité (Shapiro-Wilk pour n<5000, Kolmogorov-Smirnov sinon)
        
        Args:
            columns (List[str]): Colonnes à tester (toutes les numériques par défaut)
            
        Returns:
            Dict: Résultats des tests de normalité
        """
        logger.info("Test de normalité des distributions...")
        
        if columns is None:
            columns = self.numeric_columns
        
        normality_results = {}
        
        for col in columns:
            if col not in self.data.columns:
                continue
                
            data_col = self.data[col].dropna()
            
            if len(data_col) < 3:
                normality_results[col] = {
                    'test': 'Insufficient data',
                    'statistic': None,
                    'p_value': None,
                    'is_normal': None
                }
                continue
            
            # Choisir le test approprié selon la taille de l'échantillon
            if len(data_col) <= 5000:
                # Shapiro-Wilk pour petits échantillons
                statistic, p_value = stats.shapiro(data_col)
                test_name = 'Shapiro-Wilk'
            else:
                # Kolmogorov-Smirnov pour grands échantillons
                statistic, p_value = stats.kstest(data_col, 'norm', args=(data_col.mean(), data_col.std()))
                test_name = 'Kolmogorov-Smirnov'
            
            is_normal = p_value > self.alpha
            
            normality_results[col] = {
                'test': test_name,
                'statistic': statistic,
                'p_value': p_value,
                'is_normal': is_normal,
                'interpretation': 'Normale' if is_normal else 'Non-normale'
            }
        
        self.results['normality'] = normality_results
        return normality_results
    
    def anova_analysis(self, dependent_vars: List[str] = None, 
                      independent_vars: List[str] = None) -> Dict:
        """
        Analyse ANOVA pour tester les différences entre groupes
        
        Args:
            dependent_vars (List[str]): Variables dépendantes (numériques)
            independent_vars (List[str]): Variables indépendantes (catégorielles)
            
        Returns:
            Dict: Résultats des analyses ANOVA
        """
        logger.info("Analyse ANOVA...")
        
        if dependent_vars is None:
            dependent_vars = ['pax', 'vehicules_legers', 'poids_lourds', 'temps_attente', 'temps_transit']
            dependent_vars = [col for col in dependent_vars if col in self.numeric_columns]
        
        if independent_vars is None:
            independent_vars = ['compagnie_maritime', 'poste', 'sens', 'plage_horaire', 'is_marhaba']
            independent_vars = [col for col in independent_vars if col in self.categorical_columns]
        
        anova_results = {}
        
        for dep_var in dependent_vars:
            if dep_var not in self.data.columns:
                continue
                
            anova_results[dep_var] = {}
            
            for indep_var in independent_vars:
                if indep_var not in self.data.columns:
                    continue
                
                # Préparer les données
                analysis_data = self.data[[dep_var, indep_var]].dropna()
                
                if len(analysis_data) < 10:  # Échantillon trop petit
                    continue
                
                # Grouper les données
                groups = [group[dep_var].values for name, group in analysis_data.groupby(indep_var)]
                
                # Filtrer les groupes avec au moins 2 observations
                groups = [group for group in groups if len(group) >= 2]
                
                if len(groups) < 2:  # Pas assez de groupes
                    continue
                
                # Test ANOVA
                try:
                    f_statistic, p_value = f_oneway(*groups)
                    
                    # Calcul de l'effet size (eta squared)
                    ss_between = sum(len(group) * (np.mean(group) - np.mean(analysis_data[dep_var]))**2 for group in groups)
                    ss_total = np.sum((analysis_data[dep_var] - np.mean(analysis_data[dep_var]))**2)
                    eta_squared = ss_between / ss_total if ss_total > 0 else 0
                    
                    # Interprétation de l'effet size
                    if eta_squared < 0.01:
                        effect_size = 'Très petit'
                    elif eta_squared < 0.06:
                        effect_size = 'Petit'
                    elif eta_squared < 0.14:
                        effect_size = 'Moyen'
                    else:
                        effect_size = 'Grand'
                    
                    is_significant = p_value < self.alpha
                    
                    anova_results[dep_var][indep_var] = {
                        'f_statistic': f_statistic,
                        'p_value': p_value,
                        'is_significant': is_significant,
                        'eta_squared': eta_squared,
                        'effect_size': effect_size,
                        'groups_count': len(groups),
                        'total_n': len(analysis_data),
                        'interpretation': 'Différence significative' if is_significant else 'Pas de différence significative'
                    }
                    
                except Exception as e:
                    logger.warning(f"Erreur ANOVA pour {dep_var} ~ {indep_var}: {e}")
                    continue
        
        self.results['anova'] = anova_results
        return anova_results
    
    def post_hoc_analysis(self, dependent_var: str, independent_var: str) -> Dict:
        """
        Analyse post-hoc (Test de Tukey) après ANOVA significative
        
        Args:
            dependent_var (str): Variable dépendante
            independent_var (str): Variable indépendante
            
        Returns:
            Dict: Résultats du test de Tukey
        """
        logger.info(f"Analyse post-hoc Tukey: {dependent_var} ~ {independent_var}")
        
        # Vérifier si l'ANOVA était significative
        if ('anova' in self.results and 
            dependent_var in self.results['anova'] and 
            independent_var in self.results['anova'][dependent_var] and
            self.results['anova'][dependent_var][independent_var]['is_significant']):
            
            # Préparer les données
            analysis_data = self.data[[dependent_var, independent_var]].dropna()
            
            try:
                # Test de Tukey
                tukey_result = pairwise_tukeyhsd(
                    endog=analysis_data[dependent_var],
                    groups=analysis_data[independent_var],
                    alpha=self.alpha
                )
                
                # Organiser les résultats
                tukey_summary = {
                    'summary': str(tukey_result.summary()),
                    'pairwise_comparisons': [],
                    'significant_pairs': []
                }
                
                # Extraire les comparaisons par paires
                for i in range(len(tukey_result.groupsunique)):
                    for j in range(i+1, len(tukey_result.groupsunique)):
                        group1 = tukey_result.groupsunique[i]
                        group2 = tukey_result.groupsunique[j]
                        
                        # Trouver l'index dans les résultats
                        idx = None
                        for k, (g1, g2) in enumerate(zip(tukey_result.data[0], tukey_result.data[1])):
                            if (g1 == group1 and g2 == group2) or (g1 == group2 and g2 == group1):
                                idx = k
                                break
                        
                        if idx is not None:
                            p_adj = tukey_result.pvalues[idx]
                            mean_diff = tukey_result.meandiffs[idx]
                            reject = tukey_result.reject[idx]
                            
                            comparison = {
                                'group1': str(group1),
                                'group2': str(group2),
                                'mean_difference': mean_diff,
                                'p_adj': p_adj,
                                'significant': reject,
                                'interpretation': 'Différence significative' if reject else 'Pas de différence'
                            }
                            
                            tukey_summary['pairwise_comparisons'].append(comparison)
                            
                            if reject:
                                tukey_summary['significant_pairs'].append(f"{group1} vs {group2}")
                
                return tukey_summary
                
            except Exception as e:
                logger.error(f"Erreur dans l'analyse post-hoc: {e}")
                return {'error': str(e)}
        
        else:
            return {'message': 'ANOVA non significative - analyse post-hoc non nécessaire'}
    
    def correlation_analysis(self, variables: List[str] = None, method: str = 'both') -> Dict:
        """
        Analyse de corrélation (Pearson et/ou Spearman)
        
        Args:
            variables (List[str]): Variables à analyser
            method (str): 'pearson', 'spearman', ou 'both'
            
        Returns:
            Dict: Matrices et tests de corrélation
        """
        logger.info("Analyse de corrélation...")
        
        if variables is None:
            variables = self.numeric_columns
        
        # Filtrer les variables existantes
        variables = [var for var in variables if var in self.data.columns]
        
        if len(variables) < 2:
            return {'error': 'Pas assez de variables numériques pour l\'analyse de corrélation'}
        
        correlation_data = self.data[variables].dropna()
        
        if len(correlation_data) < 3:
            return {'error': 'Pas assez d\'observations pour l\'analyse de corrélation'}
        
        results = {}
        
        # Corrélation de Pearson
        if method in ['pearson', 'both']:
            pearson_corr = correlation_data.corr(method='pearson')
            
            # Tests de significativité pour Pearson
            pearson_p_values = pd.DataFrame(index=variables, columns=variables)
            
            for i, var1 in enumerate(variables):
                for j, var2 in enumerate(variables):
                    if i != j:
                        corr_coef, p_value = pearsonr(correlation_data[var1], correlation_data[var2])
                        pearson_p_values.loc[var1, var2] = p_value
                    else:
                        pearson_p_values.loc[var1, var2] = 0.0
            
            results['pearson'] = {
                'correlation_matrix': pearson_corr.to_dict(),
                'p_values': pearson_p_values.to_dict(),
                'significant_correlations': self._extract_significant_correlations(
                    pearson_corr, pearson_p_values, 'Pearson'
                )
            }
        
        # Corrélation de Spearman
        if method in ['spearman', 'both']:
            spearman_corr = correlation_data.corr(method='spearman')
            
            # Tests de significativité pour Spearman
            spearman_p_values = pd.DataFrame(index=variables, columns=variables)
            
            for i, var1 in enumerate(variables):
                for j, var2 in enumerate(variables):
                    if i != j:
                        corr_coef, p_value = spearmanr(correlation_data[var1], correlation_data[var2])
                        spearman_p_values.loc[var1, var2] = p_value
                    else:
                        spearman_p_values.loc[var1, var2] = 0.0
            
            results['spearman'] = {
                'correlation_matrix': spearman_corr.to_dict(),
                'p_values': spearman_p_values.to_dict(),
                'significant_correlations': self._extract_significant_correlations(
                    spearman_corr, spearman_p_values, 'Spearman'
                )
            }
        
        self.results['correlation'] = results
        return results
    
    def _extract_significant_correlations(self, corr_matrix: pd.DataFrame, 
                                        p_matrix: pd.DataFrame, method: str) -> List[Dict]:
        """Extrait les corrélations significatives"""
        significant_corrs = []
        
        for i, var1 in enumerate(corr_matrix.columns):
            for j, var2 in enumerate(corr_matrix.columns):
                if i < j:  # Éviter les doublons et la diagonale
                    corr_value = corr_matrix.loc[var1, var2]
                    p_value = p_matrix.loc[var1, var2]
                    
                    if p_value < self.alpha and not np.isnan(corr_value):
                        # Interprétation de la force de corrélation
                        abs_corr = abs(corr_value)
                        if abs_corr < 0.1:
                            strength = 'Très faible'
                        elif abs_corr < 0.3:
                            strength = 'Faible'
                        elif abs_corr < 0.5:
                            strength = 'Modérée'
                        elif abs_corr < 0.7:
                            strength = 'Forte'
                        else:
                            strength = 'Très forte'
                        
                        direction = 'Positive' if corr_value > 0 else 'Négative'
                        
                        significant_corrs.append({
                            'variable1': var1,
                            'variable2': var2,
                            'correlation': corr_value,
                            'p_value': p_value,
                            'method': method,
                            'strength': strength,
                            'direction': direction,
                            'interpretation': f"Corrélation {direction.lower()} {strength.lower()}"
                        })
        
        return significant_corrs
    
    def chi_square_analysis(self, var1: str, var2: str) -> Dict:
        """
        Test du Chi-carré pour l'indépendance entre deux variables catégorielles
        
        Args:
            var1 (str): Première variable catégorielle
            var2 (str): Seconde variable catégorielle
            
        Returns:
            Dict: Résultats du test du Chi-carré
        """
        logger.info(f"Test du Chi-carré: {var1} vs {var2}")
        
        if var1 not in self.data.columns or var2 not in self.data.columns:
            return {'error': 'Variables non trouvées dans les données'}
        
        # Créer la table de contingence
        contingency_table = pd.crosstab(self.data[var1], self.data[var2])
        
        if contingency_table.size == 0:
            return {'error': 'Table de contingence vide'}
        
        try:
            # Test du Chi-carré
            chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
            
            # Calcul du V de Cramér (mesure d'association)
            n = contingency_table.sum().sum()
            cramer_v = np.sqrt(chi2_stat / (n * (min(contingency_table.shape) - 1)))
            
            # Interprétation du V de Cramér
            if cramer_v < 0.1:
                association_strength = 'Très faible'
            elif cramer_v < 0.3:
                association_strength = 'Faible'
            elif cramer_v < 0.5:
                association_strength = 'Modérée'
            else:
                association_strength = 'Forte'
            
            is_significant = p_value < self.alpha
            
            results = {
                'chi2_statistic': chi2_stat,
                'p_value': p_value,
                'degrees_of_freedom': dof,
                'is_significant': is_significant,
                'cramer_v': cramer_v,
                'association_strength': association_strength,
                'contingency_table': contingency_table.to_dict(),
                'expected_frequencies': pd.DataFrame(expected, 
                                                   index=contingency_table.index,
                                                   columns=contingency_table.columns).to_dict(),
                'interpretation': f"Association {association_strength.lower()}" + 
                               (" et significative" if is_significant else " mais non significative")
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans le test du Chi-carré: {e}")
            return {'error': str(e)}
    
    def regression_analysis(self, dependent_var: str, independent_vars: List[str]) -> Dict:
        """
        Analyse de régression multiple
        
        Args:
            dependent_var (str): Variable dépendante
            independent_vars (List[str]): Variables indépendantes
            
        Returns:
            Dict: Résultats de la régression
        """
        logger.info(f"Analyse de régression: {dependent_var} ~ {' + '.join(independent_vars)}")
        
        # Préparer les données
        all_vars = [dependent_var] + independent_vars
        regression_data = self.data[all_vars].dropna()
        
        if len(regression_data) < len(independent_vars) + 2:
            return {'error': 'Pas assez d\'observations pour la régression'}
        
        try:
            # Créer la formule
            formula = f"{dependent_var} ~ " + " + ".join(independent_vars)
            
            # Ajuster le modèle
            model = ols(formula, data=regression_data).fit()
            
            # Résultats
            results = {
                'formula': formula,
                'r_squared': model.rsquared,
                'r_squared_adj': model.rsquared_adj,
                'f_statistic': model.fvalue,
                'f_pvalue': model.f_pvalue,
                'aic': model.aic,
                'bic': model.bic,
                'n_observations': len(regression_data),
                'coefficients': {},
                'residuals_stats': {
                    'mean': model.resid.mean(),
                    'std': model.resid.std(),
                    'min': model.resid.min(),
                    'max': model.resid.max()
                }
            }
            
            # Coefficients et tests de significativité
            for var in model.params.index:
                results['coefficients'][var] = {
                    'coefficient': model.params[var],
                    'std_error': model.bse[var],
                    't_statistic': model.tvalues[var],
                    'p_value': model.pvalues[var],
                    'is_significant': model.pvalues[var] < self.alpha
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse de régression: {e}")
            return {'error': str(e)}
    
    def comprehensive_statistical_report(self) -> Dict:
        """
        Génère un rapport statistique complet
        
        Returns:
            Dict: Rapport statistique complet
        """
        logger.info("Génération du rapport statistique complet...")
        
        report = {
            'summary': {
                'total_observations': len(self.data),
                'numeric_variables': len(self.numeric_columns),
                'categorical_variables': len(self.categorical_columns),
                'significance_level': self.alpha
            }
        }
        
        # 1. Tests de normalité
        report['normality'] = self.test_normality()
        
        # 2. Analyses ANOVA
        report['anova'] = self.anova_analysis()
        
        # 3. Analyses de corrélation
        report['correlation'] = self.correlation_analysis()
        
        # 4. Tests post-hoc pour les ANOVA significatives
        report['post_hoc'] = {}
        if 'anova' in report:
            for dep_var, indep_results in report['anova'].items():
                for indep_var, anova_result in indep_results.items():
                    if anova_result['is_significant']:
                        post_hoc_key = f"{dep_var}_vs_{indep_var}"
                        report['post_hoc'][post_hoc_key] = self.post_hoc_analysis(dep_var, indep_var)
        
        # 5. Tests du Chi-carré entre variables catégorielles importantes
        report['chi_square'] = {}
        important_cat_vars = ['compagnie_maritime', 'poste', 'sens', 'is_marhaba']
        important_cat_vars = [var for var in important_cat_vars if var in self.categorical_columns]
        
        for i, var1 in enumerate(important_cat_vars):
            for j, var2 in enumerate(important_cat_vars):
                if i < j:
                    chi_key = f"{var1}_vs_{var2}"
                    report['chi_square'][chi_key] = self.chi_square_analysis(var1, var2)
        
        self.results = report
        return report
    
    def plot_statistical_results(self, save_dir: str = None) -> None:
        """
        Crée les graphiques pour les résultats statistiques
        
        Args:
            save_dir (str): Répertoire pour sauvegarder les graphiques
        """
        logger.info("Création des graphiques statistiques...")
        
        if not self.results:
            self.comprehensive_statistical_report()
        
        # 1. Graphiques de normalité
        self._plot_normality_tests(save_dir)
        
        # 2. Résultats ANOVA
        self._plot_anova_results(save_dir)
        
        # 3. Matrice de corrélation
        self._plot_correlation_matrix(save_dir)
        
        # 4. Résidus de régression (si applicable)
        self._plot_regression_diagnostics(save_dir)
    
    def _plot_normality_tests(self, save_dir: str = None) -> None:
        """Graphiques des tests de normalité"""
        if 'normality' not in self.results:
            return
        
        normality_results = self.results['normality']
        
        # Q-Q plots pour les variables numériques
        n_vars = len(normality_results)
        if n_vars == 0:
            return
        
        n_cols = 3
        n_rows = (n_vars + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        fig.suptitle('Tests de Normalité - Q-Q Plots', fontsize=16)
        
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, (var, result) in enumerate(normality_results.items()):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            if var in self.data.columns and result['p_value'] is not None:
                data_var = self.data[var].dropna()
                
                # Q-Q plot
                stats.probplot(data_var, dist="norm", plot=ax)
                ax.set_title(f'{var}\n{result["test"]}: p={result["p_value"]:.4f}\n{result["interpretation"]}')
                ax.grid(True, alpha=0.3)
        
        # Masquer les axes inutilisés
        for i in range(len(normality_results), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/normality_tests.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_anova_results(self, save_dir: str = None) -> None:
        """Graphiques des résultats ANOVA"""
        if 'anova' not in self.results:
            return
        
        # Créer un résumé visuel des ANOVA significatives
        significant_results = []
        
        for dep_var, indep_results in self.results['anova'].items():
            for indep_var, result in indep_results.items():
                if result['is_significant']:
                    significant_results.append({
                        'Dependent': dep_var,
                        'Independent': indep_var,
                        'F-statistic': result['f_statistic'],
                        'p-value': result['p_value'],
                        'Effect Size': result['eta_squared']
                    })
        
        if not significant_results:
            logger.info("Aucun résultat ANOVA significatif à afficher")
            return
        
        # Graphique des F-statistics
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Résultats ANOVA Significatifs', fontsize=16)
        
        df_results = pd.DataFrame(significant_results)
        
        # F-statistics
        ax1 = axes[0]
        y_pos = np.arange(len(significant_results))
        bars = ax1.barh(y_pos, df_results['F-statistic'], color='skyblue')
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels([f"{row['Dependent']} ~ {row['Independent']}" for _, row in df_results.iterrows()])
        ax1.set_xlabel('F-statistic')
        ax1.set_title('F-statistics des ANOVA Significatives')
        
        # Ajouter les valeurs
        for i, (bar, f_stat) in enumerate(zip(bars, df_results['F-statistic'])):
            width = bar.get_width()
            ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'{f_stat:.2f}', ha='left', va='center')
        
        # Effect sizes
        ax2 = axes[1]
        bars2 = ax2.barh(y_pos, df_results['Effect Size'], color='lightcoral')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels([f"{row['Dependent']} ~ {row['Independent']}" for _, row in df_results.iterrows()])
        ax2.set_xlabel('Eta Squared (Effect Size)')
        ax2.set_title('Tailles d\'Effet (Eta Squared)')
        
        # Ajouter les valeurs
        for i, (bar, eta) in enumerate(zip(bars2, df_results['Effect Size'])):
            width = bar.get_width()
            ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'{eta:.3f}', ha='left', va='center')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/anova_results.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_correlation_matrix(self, save_dir: str = None) -> None:
        """Matrice de corrélation avec significativité"""
        if 'correlation' not in self.results:
            return
        
        correlation_results = self.results['correlation']
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Matrices de Corrélation', fontsize=16)
        
        # Pearson
        if 'pearson' in correlation_results:
            ax1 = axes[0]
            pearson_corr = pd.DataFrame(correlation_results['pearson']['correlation_matrix'])
            pearson_p = pd.DataFrame(correlation_results['pearson']['p_values'])
            
            # Masquer les corrélations non significatives
            mask = pearson_p > self.alpha
            
            sns.heatmap(pearson_corr, annot=True, cmap='coolwarm', center=0,
                       mask=mask, square=True, linewidths=0.5, ax=ax1,
                       fmt='.2f', annot_kws={'size': 8})
            ax1.set_title('Corrélations de Pearson\n(Non significatives masquées)')
        
        # Spearman
        if 'spearman' in correlation_results:
            ax2 = axes[1]
            spearman_corr = pd.DataFrame(correlation_results['spearman']['correlation_matrix'])
            spearman_p = pd.DataFrame(correlation_results['spearman']['p_values'])
            
            # Masquer les corrélations non significatives
            mask = spearman_p > self.alpha
            
            sns.heatmap(spearman_corr, annot=True, cmap='coolwarm', center=0,
                       mask=mask, square=True, linewidths=0.5, ax=ax2,
                       fmt='.2f', annot_kws={'size': 8})
            ax2.set_title('Corrélations de Spearman\n(Non significatives masquées)')
        
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(f'{save_dir}/correlation_matrices.png', dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_regression_diagnostics(self, save_dir: str = None) -> None:
        """Graphiques de diagnostic pour les régressions"""
        # Cette fonction peut être étendue si des analyses de régression sont effectuées
        pass
    
    def export_statistical_results(self, file_path: str) -> None:
        """
        Exporte les résultats statistiques vers Excel
        
        Args:
            file_path (str): Chemin du fichier Excel de sortie
        """
        logger.info("Export des résultats statistiques...")
        
        if not self.results:
            self.comprehensive_statistical_report()
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Feuille de résumé
            summary_data = [
                ['Nombre d\'observations', self.results['summary']['total_observations']],
                ['Variables numériques', self.results['summary']['numeric_variables']],
                ['Variables catégorielles', self.results['summary']['categorical_variables']],
                ['Seuil de significativité', self.results['summary']['significance_level']]
            ]
            
            summary_df = pd.DataFrame(summary_data, columns=['Statistique', 'Valeur'])
            summary_df.to_excel(writer, sheet_name='Résumé', index=False)
            
            # Tests de normalité
            if 'normality' in self.results:
                normality_data = []
                for var, result in self.results['normality'].items():
                    normality_data.append({
                        'Variable': var,
                        'Test': result['test'],
                        'Statistique': result['statistic'],
                        'p-value': result['p_value'],
                        'Normale': result['is_normal'],
                        'Interprétation': result['interpretation']
                    })
                
                if normality_data:
                    normality_df = pd.DataFrame(normality_data)
                    normality_df.to_excel(writer, sheet_name='Tests de Normalité', index=False)
            
            # Résultats ANOVA
            if 'anova' in self.results:
                anova_data = []
                for dep_var, indep_results in self.results['anova'].items():
                    for indep_var, result in indep_results.items():
                        anova_data.append({
                            'Variable Dépendante': dep_var,
                            'Variable Indépendante': indep_var,
                            'F-statistique': result['f_statistic'],
                            'p-value': result['p_value'],
                            'Significatif': result['is_significant'],
                            'Eta²': result['eta_squared'],
                            'Taille Effet': result['effect_size'],
                            'Interprétation': result['interpretation']
                        })
                
                if anova_data:
                    anova_df = pd.DataFrame(anova_data)
                    anova_df.to_excel(writer, sheet_name='Résultats ANOVA', index=False)
            
            # Corrélations significatives
            if 'correlation' in self.results:
                corr_data = []
                
                for method in ['pearson', 'spearman']:
                    if method in self.results['correlation']:
                        sig_corrs = self.results['correlation'][method]['significant_correlations']
                        for corr in sig_corrs:
                            corr_data.append({
                                'Variable 1': corr['variable1'],
                                'Variable 2': corr['variable2'],
                                'Méthode': corr['method'],
                                'Corrélation': corr['correlation'],
                                'p-value': corr['p_value'],
                                'Force': corr['strength'],
                                'Direction': corr['direction'],
                                'Interprétation': corr['interpretation']
                            })
                
                if corr_data:
                    corr_df = pd.DataFrame(corr_data)
                    corr_df.to_excel(writer, sheet_name='Corrélations Significatives', index=False)
        
        logger.info(f"Résultats statistiques exportés vers: {file_path}")
    
    def save_complete_analysis(self, output_dir: str = '/workspace/outputs') -> None:
        """
        Sauvegarde l'analyse statistique complète
        
        Args:
            output_dir (str): Répertoire de sortie
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer le rapport complet
        self.comprehensive_statistical_report()
        
        # Créer les graphiques
        self.plot_statistical_results(output_dir)
        
        # Exporter vers Excel
        self.export_statistical_results(f'{output_dir}/statistical_analysis.xlsx')
        
        logger.info(f"Analyse statistique complète sauvegardée dans: {output_dir}")


if __name__ == "__main__":
    # Exemple d'utilisation
    from data_preprocessing import TangerMedDataProcessor, create_sample_data
    
    # Créer des données d'exemple
    sample_data = create_sample_data(5000, '/workspace/data/sample_tanger_med_data.csv')
    
    # Prétraitement
    processor = TangerMedDataProcessor()
    cleaned_data = processor.full_preprocessing('/workspace/data/sample_tanger_med_data.csv')
    
    # Analyse statistique
    stat_analyzer = TangerMedStatisticalAnalyzer(cleaned_data)
    
    # Générer l'analyse complète
    stat_analyzer.save_complete_analysis()
    
    print("Analyse statistique terminée! Consultez /workspace/outputs pour les résultats.")