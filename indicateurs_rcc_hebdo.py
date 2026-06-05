import pandas as pd
import numpy as np

class RCCIndicators:
    """Process RCC indicators - Telephone and BO data"""
    
    def __init__(self, rep_out, nom_fic):
        self.rep_out = rep_out
        self.nom_fic = nom_fic
        self.JACTCCAMIN = 451
    
    def process_telephone_data(self, ctels_df, S, Sm1, Sm2, Sm3, Sm4, Sm5, Sp1):
        """Process telephone indicators for RCC"""
        
        # Filter: exclude next week
        ctels_rcc = ctels_df[ctels_df['SEMAINE'] != Sp1].copy()
        
        # Sort by week descending
        ctels_rcc = ctels_rcc.sort_values('SEMAINE', ascending=False)
        
        # Keep only last 52 weeks
        ctels_rcc = ctels_rcc.head(52)
        
        # Create datasets for different periods
        ctels_rccs = ctels_rcc[ctels_rcc['SEMAINE'].isin([S, Sm1])].copy()
        ctels_rccs['PERIODE'] = ctels_rccs['SEMAINE']
        
        ctels_rccm = ctels_rcc[ctels_rcc['SEMAINE'].isin([S, Sm1, Sm2, Sm3, Sm4, Sm5])].copy()
        ctels_rccm['PERIODE'] = 'MOIS'
        
        ctels_rcca = ctels_rcc.copy()
        ctels_rcca['PERIODE'] = 'ANNEE'
        
        # Combine all datasets
        ctels_rcc2 = pd.concat([ctels_rccs, ctels_rccm, ctels_rcca], ignore_index=True)
        
        # Calculate means by period
        numeric_cols = ctels_rcc2.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col not in ['PERIODE']]
        
        tabfinrcctel = ctels_rcc2.groupby('PERIODE')[numeric_cols].mean()
        
        # Calculate average waiting times
        if 'NBARRCC' in tabfinrcctel.columns and 'TPSREPRCC' in tabfinrcctel.columns:
            tabfinrcctel['TPSATTMRCC'] = np.where(
                tabfinrcctel['NBARRCC'] > 0,
                tabfinrcctel['TPSREPRCC'] / tabfinrcctel['NBARRCC'],
                np.nan
            )
        
        # Transpose for export
        tabfinrcctel = tabfinrcctel.T
        
        return tabfinrcctel
    
    def process_bo_data(self, bogedrcc_df, S, Sm1, Sm2, Sm3, Sm4, Sm5, date_vue, dtdeb):
        """Process BO (Back Office) indicators for RCC"""
        
        # Filter data by date
        bogedrcc = bogedrcc_df[bogedrcc_df['JOUR'] <= date_vue].copy()
        bogedrcc = bogedrcc[bogedrcc['JOUR'] >= dtdeb]
        
        # Create activity type column
        bogedrcc['TYPEACT2'] = bogedrcc['TYPEACT'].apply(
            lambda x: 'MDP' if x == 'MDP' else 'IARD'
        )
        
        # Process incoming flux
        bogedrcc_fe = self._process_flux_entrant(bogedrcc, S, Sm1, Sm2, Sm3, Sm4, Sm5)
        
        # Process stock
        bogedrcc_sfp = self._process_stock(bogedrcc, S, Sm1, Sm2, Sm3, Sm4, Sm5)
        
        # Process processed flux
        bogedrcc_ft = self._process_flux_traite(bogedrcc, S, Sm1, Sm2, Sm3, Sm4, Sm5)
        
        # Consolidate BO data
        tabfinborcc = bogedrcc_fe.merge(bogedrcc_sfp, on=['PERIODE', 'GROUPE'], how='outer')
        tabfinborcc = tabfinborcc.merge(bogedrcc_ft, on=['PERIODE', 'GROUPE'], how='outer')
        
        return tabfinborcc
    
    def _process_flux_entrant(self, bogedrcc, S, Sm1, Sm2, Sm3, Sm4, Sm5):
        """Process incoming flux"""
        
        bogedrccs = bogedrcc[bogedrcc['SEMAINE'].isin([S, Sm1])].copy()
        bogedrccs['PERIODE'] = bogedrccs['SEMAINE']
        
        bogedrccm = bogedrcc[bogedrcc['SEMAINE'].isin([S, Sm1, Sm2, Sm3, Sm4, Sm5])].copy()
        bogedrccm['PERIODE'] = 'MOIS'
        
        bogedrcca = bogedrcc.copy()
        bogedrcca['PERIODE'] = 'ANNEE'
        
        bogedrcc2 = pd.concat([bogedrccs, bogedrccm, bogedrcca])
        
        # Group by period, week, and activity type
        bogedrcc3 = bogedrcc2.groupby(['PERIODE', 'SEMAINE', 'TYPEACT2'])['FLUX_ENTRANT_GED'].sum().reset_index()
        
        # Calculate mean by period and activity type
        bogedrcc_fe = bogedrcc3.groupby(['PERIODE', 'TYPEACT2'])['FLUX_ENTRANT_GED'].mean().reset_index()
        bogedrcc_fe.columns = ['PERIODE', 'GROUPE', 'NBFE']
        
        return bogedrcc_fe
    
    def _process_stock(self, bogedrcc, S, Sm1, Sm2, Sm3, Sm4, Sm5):
        """Process stock"""
        
        bogedrccs = bogedrcc[bogedrcc['SEMAINE'].isin([S, Sm1])].copy()
        bogedrccs['PERIODE'] = bogedrccs['SEMAINE']
        
        bogedrccm = bogedrcc[bogedrcc['SEMAINE'].isin([S, Sm1, Sm2, Sm3, Sm4, Sm5])].copy()
        bogedrccm['PERIODE'] = 'MOIS'
        
        bogedrcca = bogedrcc.copy()
        bogedrcca['PERIODE'] = 'ANNEE'
        
        bogedrcc2 = pd.concat([bogedrccs, bogedrccm, bogedrcca])
        
        # Group and sum
        bogedrcc3 = bogedrcc2.groupby(['PERIODE', 'SEMAINE', 'TYPEACT2'])['STK_RESTANT_JOUR'].sum().reset_index()
        
        # Calculate mean by period and activity type
        bogedrcc_sfp = bogedrcc3.groupby(['PERIODE', 'TYPEACT2'])['STK_RESTANT_JOUR'].mean().reset_index()
        bogedrcc_sfp.columns = ['PERIODE', 'GROUPE', 'NBSFP']
        
        return bogedrcc_sfp
    
    def _process_flux_traite(self, bogedrcc, S, Sm1, Sm2, Sm3, Sm4, Sm5):
        """Process processed flux"""
        
        bogedrccs = bogedrcc[bogedrcc['SEMAINE'].isin([S, Sm1])].copy()
        bogedrccs['PERIODE'] = bogedrccs['SEMAINE']
        
        bogedrccm = bogedrcc[bogedrcc['SEMAINE'].isin([S, Sm1, Sm2, Sm3, Sm4, Sm5])].copy()
        bogedrccm['PERIODE'] = 'MOIS'
        
        bogedrcca = bogedrcc.copy()
        bogedrcca['PERIODE'] = 'ANNEE'
        
        bogedrcc2 = pd.concat([bogedrccs, bogedrccm, bogedrcca])
        
        # Group and sum
        bogedrcc3 = bogedrcc2.groupby(['PERIODE', 'SEMAINE', 'TYPEACT2'])['FLUX_TRAITE_JOUR_MANU'].sum().reset_index()
        
        # Calculate mean by period and activity type
        bogedrcc_ft = bogedrcc3.groupby(['PERIODE', 'TYPEACT2'])['FLUX_TRAITE_JOUR_MANU'].mean().reset_index()
        bogedrcc_ft.columns = ['PERIODE', 'GROUPE', 'NBFT']
        
        return bogedrcc_ft
