import pandas as pd
import numpy as np


class RCVIndicators:
    """Process RCV indicators - Telephone and BO data"""
    
    def __init__(self, rep_out, nom_fic, rep_fic_rcv=None, nom_fic_rcv=None):
        self.rep_out = rep_out
        self.nom_fic = nom_fic
        self.rep_fic_rcv = rep_fic_rcv or r"\\assushare.sogecap.socgen\ASSU\_Applications\SAS-RCF-TRF-PIL-DOM\AUTRE\DEMANDES AD-HOC\202510 - POC Migration SAS"
        self.nom_fic_rcv = nom_fic_rcv or "template_RCV.xlsx"
        self.JACTCCAMIN = 451
    
    def process_telephone_data(self, ctels_df, S, Sm1, Sm2, Sm3, Sm4, Sm5, Sp1):
        """
        Process telephone indicators for RCV.
        
        Filters and processes RCV-specific columns:
        - NBAPRCV: Appels présentés RCV
        - NBARRCV: Appels réceptionnés RCV  
        - NBAPTOTRCV: Total appels RCV
        - NBAARCV: Appels abandonnés RCV
        - NBADRCV: Appels déclinés RCV
        - NBARI180RCV: Appels répondus <180s RCV
        - TPSREPRCV: Temps de réponse RCV
        - And C (compressed) variants for sub-channels
        """
        
        # Select RCV-related columns (containing 'SEMAINE' or 'RCV')
        rcv_cols = [col for col in ctels_df.columns 
                   if 'SEMAINE' in col or 'RCV' in col]
        
        # Filter data - exclude next week
        ctels_rcv = ctels_df[rcv_cols][ctels_df['SEMAINE'] != Sp1].copy()
        
        # Sort by week descending
        ctels_rcv = ctels_rcv.sort_values('SEMAINE', ascending=False)
        
        # Keep only last 52 weeks
        ctels_rcv = ctels_rcv.head(52)
        
        # Create datasets for different periods
        ctels_rcvs = ctels_rcv[ctels_rcv['SEMAINE'].isin([S, Sm1])].copy()
        ctels_rcvs['PERIODE'] = ctels_rcvs['SEMAINE']
        
        ctels_rcvm = ctels_rcv[ctels_rcv['SEMAINE'].isin([S, Sm1, Sm2, Sm3, Sm4, Sm5])].copy()
        ctels_rcvm['PERIODE'] = 'MOIS'
        
        ctels_rcva = ctels_rcv.copy()
        ctels_rcva['PERIODE'] = 'ANNEE'
        
        # Combine all datasets
        ctels_rcv2 = pd.concat([ctels_rcvs, ctels_rcvm, ctels_rcva], ignore_index=True)
        
        # Calculate means by period for numeric columns
        numeric_cols = ctels_rcv2.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col not in ['PERIODE']]
        
        tabfinrcvtel = ctels_rcv2.groupby('PERIODE')[numeric_cols].mean()
        
        # Calculate average waiting times for EPA variants
        waiting_time_calcs_epa = {
            'TPSATTMRCVEPA': ('TPSREPRCVEPA', 'NBARRCVEPA'),
            'TPSATTMRCVEPAASS': ('TPSREPRCVEPAASS', 'NBARRCVEPAASS'),
            'TPSATTMRCVEPARES': ('TPSREPRCVEPARES', 'NBARRCVEPARES'),
            'CTPSATTMRCVEPAASSBDDF': ('CTPSREPRCVEPAASSBDDF', 'CNBARRCVEPAASSBDDF'),
            'CTPSATTMRCVEPAASSCDN': ('CTPSREPRCVEPAASSCDN', 'CNBARRCVEPAASSCDN'),
            'CTPSATTMRCVEPAASSORA': ('CTPSREPRCVEPAASSORA', 'CNBARRCVEPAASSORA'),
            'CTPSATTMRCVEPARESBDDF': ('CTPSREPRCVEPARESBDDF', 'CNBARRCVEPARESBDDF'),
            'CTPSATTMRCVEPARESCDN': ('CTPSREPRCVEPARESCDN', 'CNBARRCVEPARESCDN'),
        }
        
        for calc_col, (time_col, count_col) in waiting_time_calcs_epa.items():
            if time_col in tabfinrcvtel.columns and count_col in tabfinrcvtel.columns:
                tabfinrcvtel[calc_col] = np.where(
                    tabfinrcvtel[count_col] > 0,
                    tabfinrcvtel[time_col] / tabfinrcvtel[count_col],
                    np.nan
                )
        
        # Calculate average waiting times for PRE (Prevention) variants
        waiting_time_calcs_pre = {
            'TPSATTMRCVPRE': ('TPSREPRCVPRE', 'NBARRCVPRE'),
            'TPSATTMRCVPREASS': ('TPSREPRCVPREASS', 'NBARRCVPREASS'),
            'TPSATTMRCVPRERES': ('TPSREPRCVPRERES', 'NBARRCVPRERES'),
            'CTPSATTMRCVPREASSBDDF': ('CTPSREPRCVPREASSBDDF', 'CNBARRCVPREASSBDDF'),
            'CTPSATTMRCVPREINDASSBDDF': ('CTPSREPRCVPREINDASSBDDF', 'CNBARRCVPREINDASSBDDF'),
            'CTPSATTMRCVPREADEASSBDDF': ('CTPSREPRCVPREADEASSBDDF', 'CNBARRCVPREADEASSBDDF'),
            'CTPSATTMRCVPREASSCDN': ('CTPSREPRCVPREASSCDN', 'CNBARRCVPREASSCDN'),
            'CTPSATTMRCVPREASSBRS': ('CTPSREPRCVPREASSBRS', 'CNBARRCVPREASSBRS'),
            'CTPSATTMRCVPRERESBDDF': ('CTPSREPRCVPRERESBDDF', 'CNBARRCVPRERESBDDF'),
            'CTPSATTMRCVPREINDRESBDDF': ('CTPSREPRCVPREINDRESBDDF', 'CNBARRCVPREINDRESBDDF'),
            'CTPSATTMRCVPREADERESBDDF': ('CTPSREPRCVPREADERESBDDF', 'CNBARRCVPREADERESBDDF'),
            'CTPSATTMRCVPRERESCDN': ('CTPSREPRCVPRERESCDN', 'CNBARRCVPRERESCDN'),
        }
        
        for calc_col, (time_col, count_col) in waiting_time_calcs_pre.items():
            if time_col in tabfinrcvtel.columns and count_col in tabfinrcvtel.columns:
                tabfinrcvtel[calc_col] = np.where(
                    tabfinrcvtel[count_col] > 0,
                    tabfinrcvtel[time_col] / tabfinrcvtel[count_col],
                    np.nan
                )
        
        # Transpose for export (periods as columns)
        tabfinrcvtel = tabfinrcvtel.T
        
        return tabfinrcvtel
    
    def process_bo_data(self, bogedrcc_df, S, Sm1, Sm2, Sm3, Sm4, Sm5, SAM1, Sp1):
        """
        Process BO (Back Office) indicators for RCV.
        Imports template file and processes EPA and PREV metrics.
        
        Parameters:
        -----------
        bogedrcc_df : pd.DataFrame
            BO data (can be from Excel template)
        S, Sm1, Sm2, Sm3, Sm4, Sm5 : str
            Week identifiers
        SAM1 : str
            Week from 52 weeks ago
        Sp1 : str
            Next week identifier
        """
        
        # In real usage, this would import from Excel:
        # try:
        #     import_df = pd.read_excel(f"{self.rep_fic_rcv}/{self.nom_fic_rcv}", sheet_name='Feuil1')
        # except Exception as e:
        #     print(f"Error reading template file: {e}")
        #     return None
        
        # For testing, use provided DataFrame
        import_df = bogedrcc_df.copy()
        
        # Transform week format: "SXXJJ" -> "SXXYY"
        if 'semaine' in import_df.columns:
            import_df['semaine'] = import_df['semaine'].apply(
                lambda x: f"S{str(x)[2:4]}{str(x)[6:8]}" if isinstance(x, str) and len(str(x)) >= 8 else x
            )
        
        # Filter data
        import2 = import_df.copy()
        if 'semaine' in import2.columns:
            import2 = import2[import2['semaine'] != SAM1].copy()
            import2 = import2[import2['semaine'] != Sp1].copy()
        
        # Sort by week descending
        if 'semaine' in import2.columns:
            import2 = import2.sort_values('semaine', ascending=False)
        
        # Keep only last 52 records
        import2 = import2.head(52)
        
        # Create datasets for different periods
        week_col = 'semaine' if 'semaine' in import2.columns else 'SEMAINE'
        
        borcfs = import2[import2[week_col].isin([S, Sm1])].copy()
        borcfs['PERIODE'] = borcfs[week_col]
        
        borcfm = import2[import2[week_col].isin([S, Sm1, Sm2, Sm3, Sm4, Sm5])].copy()
        borcfm['PERIODE'] = 'MOIS'
        
        borcfa = import2.copy()
        borcfa['PERIODE'] = 'ANNEE'
        
        # Combine all datasets
        borcf2 = pd.concat([borcfs, borcfm, borcfa], ignore_index=True)
        
        # Select EPA and PREV columns (wildcard matching)
        epa_prev_cols = [col for col in borcf2.columns 
                        if col.upper().startswith('EPA') or col.upper().startswith('PREV')]
        
        if not epa_prev_cols:
            # If no EPA/PREV columns, return empty with PERIODE
            borcf3 = borcf2.groupby('PERIODE').size().to_frame(name='count').drop('count', axis=1)
            return borcf3
        
        # Calculate means by period
        borcf3 = borcf2.groupby('PERIODE')[epa_prev_cols].mean()
        
        # Transpose for export (periods as columns)
        borcf3 = borcf3.T
        
        return borcf3
    
    def export_to_excel(self, tabfinrcvtel, borcf3, output_path):
        """
        Export results to Excel.
        
        Parameters:
        -----------
        tabfinrcvtel : pd.DataFrame
            Telephone indicators
        borcf3 : pd.DataFrame
            BO indicators
        output_path : str
            Path to Excel file
        """
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
                tabfinrcvtel.to_excel(writer, sheet_name='DONRCV')
                borcf3.to_excel(writer, sheet_name='DONBORCV')
            print(f"✓ RCV indicators exported to: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error exporting RCV indicators: {e}")
            return False
