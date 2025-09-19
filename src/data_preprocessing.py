"""
Module de prétraitement des données Tanger Med
Nettoyage, transformation et préparation des données pour l'analyse
"""

import pandas as pd
import numpy as np
import warnings
from typing import Tuple, List, Optional
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TangerMedDataProcessor:
    """
    Classe pour le prétraitement des données de trafic Tanger Med
    """
    
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        self.data_info = {}
        
    def load_data(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Charge les données depuis un fichier CSV ou Excel
        
        Args:
            file_path (str): Chemin vers le fichier
            **kwargs: Arguments supplémentaires pour pandas.read_csv/read_excel
            
        Returns:
            pd.DataFrame: Données chargées
        """
        try:
            if file_path.endswith('.csv'):
                self.raw_data = pd.read_csv(file_path, **kwargs)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.raw_data = pd.read_excel(file_path, **kwargs)
            else:
                raise ValueError("Format de fichier non supporté. Utilisez CSV ou Excel.")
                
            logger.info(f"Données chargées: {self.raw_data.shape[0]} lignes, {self.raw_data.shape[1]} colonnes")
            self._generate_data_info()
            return self.raw_data
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            raise
    
    def _generate_data_info(self):
        """Génère des informations sur le dataset"""
        if self.raw_data is not None:
            self.data_info = {
                'shape': self.raw_data.shape,
                'columns': list(self.raw_data.columns),
                'dtypes': dict(self.raw_data.dtypes),
                'missing_values': dict(self.raw_data.isnull().sum()),
                'duplicates': self.raw_data.duplicated().sum()
            }
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les noms de colonnes (supprime espaces, caractères spéciaux)
        
        Args:
            df (pd.DataFrame): DataFrame à nettoyer
            
        Returns:
            pd.DataFrame: DataFrame avec colonnes nettoyées
        """
        df_clean = df.copy()
        
        # Dictionnaire de mapping pour standardiser les noms de colonnes
        column_mapping = {
            'Date': 'date',
            'Jour': 'jour',
            'Mois': 'mois',
            'Compagnie maritime': 'compagnie_maritime',
            'Compagnie': 'compagnie_maritime',
            'Poste': 'poste',
            'Sens': 'sens',
            'PAX': 'pax',
            'Passagers': 'pax',
            'Véhicules légers': 'vehicules_legers',
            'Vehicules legers': 'vehicules_legers',
            'Poids lourds': 'poids_lourds',
            'PlageHoraire': 'plage_horaire',
            'Plage Horaire': 'plage_horaire',
            'Temps d\'attente': 'temps_attente',
            'Temps de transit': 'temps_transit',
            'Temps attente': 'temps_attente',
            'Temps transit': 'temps_transit'
        }
        
        # Nettoyer les noms de colonnes
        new_columns = []
        for col in df_clean.columns:
            if col in column_mapping:
                new_columns.append(column_mapping[col])
            else:
                # Nettoyage général
                clean_name = col.strip().lower().replace(' ', '_').replace('\'', '_')
                clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
                new_columns.append(clean_name)
        
        df_clean.columns = new_columns
        logger.info(f"Colonnes nettoyées: {list(df_clean.columns)}")
        return df_clean
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: dict = None) -> pd.DataFrame:
        """
        Gère les valeurs manquantes selon différentes stratégies
        
        Args:
            df (pd.DataFrame): DataFrame à traiter
            strategy (dict): Stratégies par colonne {'colonne': 'strategie'}
                           Stratégies: 'drop', 'mean', 'median', 'mode', 'forward_fill', 'zero'
        
        Returns:
            pd.DataFrame: DataFrame avec valeurs manquantes traitées
        """
        df_clean = df.copy()
        
        if strategy is None:
            # Stratégies par défaut
            strategy = {
                'pax': 'zero',
                'vehicules_legers': 'zero',
                'poids_lourds': 'zero',
                'temps_attente': 'median',
                'temps_transit': 'median',
                'compagnie_maritime': 'mode',
                'poste': 'mode',
                'sens': 'mode'
            }
        
        missing_before = df_clean.isnull().sum().sum()
        
        for column, method in strategy.items():
            if column in df_clean.columns and df_clean[column].isnull().any():
                if method == 'drop':
                    df_clean = df_clean.dropna(subset=[column])
                elif method == 'mean':
                    df_clean[column].fillna(df_clean[column].mean(), inplace=True)
                elif method == 'median':
                    df_clean[column].fillna(df_clean[column].median(), inplace=True)
                elif method == 'mode':
                    mode_value = df_clean[column].mode()
                    if len(mode_value) > 0:
                        df_clean[column].fillna(mode_value[0], inplace=True)
                elif method == 'forward_fill':
                    df_clean[column].fillna(method='ffill', inplace=True)
                elif method == 'zero':
                    df_clean[column].fillna(0, inplace=True)
        
        missing_after = df_clean.isnull().sum().sum()
        logger.info(f"Valeurs manquantes: {missing_before} → {missing_after}")
        
        return df_clean
    
    def handle_duplicates(self, df: pd.DataFrame, subset: List[str] = None, keep: str = 'first') -> pd.DataFrame:
        """
        Supprime les doublons
        
        Args:
            df (pd.DataFrame): DataFrame à traiter
            subset (List[str]): Colonnes à considérer pour les doublons
            keep (str): 'first', 'last', False
            
        Returns:
            pd.DataFrame: DataFrame sans doublons
        """
        df_clean = df.copy()
        duplicates_before = df_clean.duplicated(subset=subset).sum()
        
        df_clean = df_clean.drop_duplicates(subset=subset, keep=keep)
        
        duplicates_after = df_clean.duplicated(subset=subset).sum()
        logger.info(f"Doublons supprimés: {duplicates_before} → {duplicates_after}")
        
        return df_clean
    
    def convert_datetime(self, df: pd.DataFrame, date_column: str = 'date', 
                        format: str = None) -> pd.DataFrame:
        """
        Convertit la colonne date en format datetime
        
        Args:
            df (pd.DataFrame): DataFrame à traiter
            date_column (str): Nom de la colonne date
            format (str): Format de date (optionnel)
            
        Returns:
            pd.DataFrame: DataFrame avec date convertie
        """
        df_clean = df.copy()
        
        if date_column in df_clean.columns:
            try:
                if format:
                    df_clean[date_column] = pd.to_datetime(df_clean[date_column], format=format)
                else:
                    df_clean[date_column] = pd.to_datetime(df_clean[date_column], infer_datetime_format=True)
                
                # Ajouter des colonnes dérivées
                df_clean['annee'] = df_clean[date_column].dt.year
                df_clean['mois_num'] = df_clean[date_column].dt.month
                df_clean['jour_semaine'] = df_clean[date_column].dt.dayofweek
                df_clean['nom_jour'] = df_clean[date_column].dt.day_name()
                df_clean['nom_mois'] = df_clean[date_column].dt.month_name()
                df_clean['trimestre'] = df_clean[date_column].dt.quarter
                df_clean['semaine'] = df_clean[date_column].dt.isocalendar().week
                
                logger.info(f"Colonne {date_column} convertie en datetime")
                
            except Exception as e:
                logger.warning(f"Erreur conversion datetime: {e}")
                
        return df_clean
    
    def normalize_categorical(self, df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """
        Normalise les variables catégorielles
        
        Args:
            df (pd.DataFrame): DataFrame à traiter
            columns (List[str]): Colonnes à normaliser
            
        Returns:
            pd.DataFrame: DataFrame avec variables normalisées
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = ['compagnie_maritime', 'sens', 'poste', 'plage_horaire']
        
        for col in columns:
            if col in df_clean.columns:
                # Convertir en string et nettoyer
                df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()
                
                # Normalisation spécifique par colonne
                if col == 'sens':
                    df_clean[col] = df_clean[col].replace({
                        'ENTREE': 'ENTRÉE',
                        'ENTRE': 'ENTRÉE',
                        'ENTRY': 'ENTRÉE',
                        'IN': 'ENTRÉE',
                        'SORTIE': 'SORTIE',
                        'EXIT': 'SORTIE',
                        'OUT': 'SORTIE'
                    })
                
                logger.info(f"Colonne {col} normalisée: {df_clean[col].unique()}")
        
        return df_clean
    
    def detect_outliers(self, df: pd.DataFrame, columns: List[str] = None, 
                       method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """
        Détecte les valeurs aberrantes
        
        Args:
            df (pd.DataFrame): DataFrame à analyser
            columns (List[str]): Colonnes numériques à analyser
            method (str): Méthode de détection ('iqr', 'zscore')
            threshold (float): Seuil de détection
            
        Returns:
            pd.DataFrame: DataFrame avec colonne 'is_outlier'
        """
        df_analysis = df.copy()
        
        if columns is None:
            columns = ['pax', 'vehicules_legers', 'poids_lourds', 'temps_attente', 'temps_transit']
        
        outlier_mask = pd.Series([False] * len(df_analysis), index=df_analysis.index)
        
        for col in columns:
            if col in df_analysis.columns and df_analysis[col].dtype in ['int64', 'float64']:
                if method == 'iqr':
                    Q1 = df_analysis[col].quantile(0.25)
                    Q3 = df_analysis[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    col_outliers = (df_analysis[col] < lower_bound) | (df_analysis[col] > upper_bound)
                    
                elif method == 'zscore':
                    z_scores = np.abs((df_analysis[col] - df_analysis[col].mean()) / df_analysis[col].std())
                    col_outliers = z_scores > threshold
                
                outlier_mask |= col_outliers
                logger.info(f"Outliers détectés pour {col}: {col_outliers.sum()}")
        
        df_analysis['is_outlier'] = outlier_mask
        return df_analysis
    
    def create_marhaba_flag(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """
        Crée un indicateur pour la période Marhaba (juin-septembre)
        
        Args:
            df (pd.DataFrame): DataFrame avec colonne date
            date_column (str): Nom de la colonne date
            
        Returns:
            pd.DataFrame: DataFrame avec colonne 'is_marhaba'
        """
        df_clean = df.copy()
        
        if date_column in df_clean.columns:
            # Période Marhaba: juin à septembre (mois 6-9)
            df_clean['is_marhaba'] = df_clean[date_column].dt.month.isin([6, 7, 8, 9])
            
            # Période détaillée
            df_clean['periode'] = df_clean['is_marhaba'].map({
                True: 'Marhaba',
                False: 'Hors-Marhaba'
            })
            
            logger.info(f"Indicateur Marhaba créé: {df_clean['is_marhaba'].sum()} observations Marhaba")
        
        return df_clean
    
    def full_preprocessing(self, file_path: str, **load_kwargs) -> pd.DataFrame:
        """
        Pipeline complet de prétraitement
        
        Args:
            file_path (str): Chemin vers le fichier de données
            **load_kwargs: Arguments pour le chargement
            
        Returns:
            pd.DataFrame: Données nettoyées et préparées
        """
        logger.info("=== DÉBUT DU PRÉTRAITEMENT ===")
        
        # 1. Chargement
        self.load_data(file_path, **load_kwargs)
        df = self.raw_data.copy()
        
        # 2. Nettoyage des noms de colonnes
        df = self.clean_column_names(df)
        
        # 3. Conversion datetime
        if 'date' in df.columns:
            df = self.convert_datetime(df)
        
        # 4. Normalisation des catégories
        df = self.normalize_categorical(df)
        
        # 5. Gestion des valeurs manquantes
        df = self.handle_missing_values(df)
        
        # 6. Suppression des doublons
        df = self.handle_duplicates(df)
        
        # 7. Détection des outliers
        df = self.detect_outliers(df)
        
        # 8. Création de l'indicateur Marhaba
        if 'date' in df.columns:
            df = self.create_marhaba_flag(df)
        
        self.cleaned_data = df
        logger.info(f"=== PRÉTRAITEMENT TERMINÉ === Shape finale: {df.shape}")
        
        return df
    
    def get_data_summary(self) -> dict:
        """
        Retourne un résumé des données traitées
        
        Returns:
            dict: Résumé des données
        """
        if self.cleaned_data is None:
            return {"error": "Aucune donnée traitée disponible"}
        
        df = self.cleaned_data
        
        summary = {
            'shape': df.shape,
            'periode': f"{df['date'].min()} à {df['date'].max()}" if 'date' in df.columns else "Non disponible",
            'compagnies': df['compagnie_maritime'].nunique() if 'compagnie_maritime' in df.columns else 0,
            'postes': df['poste'].nunique() if 'poste' in df.columns else 0,
            'total_pax': df['pax'].sum() if 'pax' in df.columns else 0,
            'total_vehicules_legers': df['vehicules_legers'].sum() if 'vehicules_legers' in df.columns else 0,
            'total_poids_lourds': df['poids_lourds'].sum() if 'poids_lourds' in df.columns else 0,
            'outliers_detected': df['is_outlier'].sum() if 'is_outlier' in df.columns else 0,
            'marhaba_observations': df['is_marhaba'].sum() if 'is_marhaba' in df.columns else 0
        }
        
        return summary
    
    def save_cleaned_data(self, output_path: str, format: str = 'csv'):
        """
        Sauvegarde les données nettoyées
        
        Args:
            output_path (str): Chemin de sortie
            format (str): Format ('csv', 'excel')
        """
        if self.cleaned_data is None:
            logger.error("Aucune donnée nettoyée à sauvegarder")
            return
        
        try:
            if format == 'csv':
                self.cleaned_data.to_csv(output_path, index=False, encoding='utf-8')
            elif format == 'excel':
                self.cleaned_data.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Données sauvegardées: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")


def create_sample_data(n_rows: int = 1000, save_path: str = None) -> pd.DataFrame:
    """
    Crée un dataset d'exemple pour tester les fonctions
    
    Args:
        n_rows (int): Nombre de lignes à générer
        save_path (str): Chemin pour sauvegarder (optionnel)
        
    Returns:
        pd.DataFrame: Dataset d'exemple
    """
    np.random.seed(42)
    
    # Dates entre juin 2022 et septembre 2023
    start_date = pd.Timestamp('2022-06-01')
    end_date = pd.Timestamp('2023-09-30')
    dates = pd.date_range(start_date, end_date, freq='H')
    
    # Génération des données
    sample_data = []
    compagnies = ['COMARIT', 'FRS', 'BALEARIA', 'GRIMALDI', 'TRASMEDITERRANEA']
    postes = ['P1', 'P2', 'P3', 'P4', 'P5']
    sens_values = ['ENTRÉE', 'SORTIE']
    plages_horaires = ['00-06', '06-12', '12-18', '18-24']
    
    for i in range(n_rows):
        date = np.random.choice(dates)
        is_marhaba = date.month in [6, 7, 8, 9]
        
        # Ajustement saisonnier
        seasonal_factor = 1.5 if is_marhaba else 1.0
        
        row = {
            'Date': date.strftime('%Y-%m-%d'),
            'Jour': date.day_name(),
            'Mois': date.month_name(),
            'Compagnie maritime': np.random.choice(compagnies),
            'Poste': np.random.choice(postes),
            'Sens': np.random.choice(sens_values),
            'PAX': int(np.random.exponential(100) * seasonal_factor),
            'Véhicules légers': int(np.random.exponential(20) * seasonal_factor),
            'Poids lourds': int(np.random.exponential(5) * seasonal_factor),
            'PlageHoraire': np.random.choice(plages_horaires),
            'Temps d\'attente': np.random.exponential(30),
            'Temps de transit': np.random.exponential(45)
        }
        
        sample_data.append(row)
    
    df = pd.DataFrame(sample_data)
    
    # Ajouter quelques valeurs manquantes et doublons
    missing_indices = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
    df.loc[missing_indices[:len(missing_indices)//2], 'Temps d\'attente'] = np.nan
    df.loc[missing_indices[len(missing_indices)//2:], 'PAX'] = np.nan
    
    # Ajouter quelques doublons
    duplicate_indices = np.random.choice(df.index, size=20, replace=False)
    df = pd.concat([df, df.loc[duplicate_indices]], ignore_index=True)
    
    if save_path:
        df.to_csv(save_path, index=False, encoding='utf-8')
        print(f"Dataset d'exemple sauvegardé: {save_path}")
    
    return df


if __name__ == "__main__":
    # Exemple d'utilisation
    processor = TangerMedDataProcessor()
    
    # Créer des données d'exemple
    sample_df = create_sample_data(5000, '/workspace/data/sample_tanger_med_data.csv')
    print("Dataset d'exemple créé avec", len(sample_df), "lignes")
    
    # Test du prétraitement
    cleaned_df = processor.full_preprocessing('/workspace/data/sample_tanger_med_data.csv')
    
    # Afficher le résumé
    summary = processor.get_data_summary()
    print("\n=== RÉSUMÉ DES DONNÉES ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Sauvegarder les données nettoyées
    processor.save_cleaned_data('/workspace/data/cleaned_tanger_med_data.csv')