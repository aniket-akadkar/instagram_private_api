import os
import shutil
from datetime import datetime, timedelta
import pandas as pd
import time

# ============================================================================
# LAUNCHER FOR COMEX DASHBOARD
# Subject: COMEX Dashboard
# Purpose: Recovery of common statistics (RCC, SIN, RCV)
# Description: Phone Stats + BO Stats
# ============================================================================

class LauncherHebdo:
    """Main launcher for weekly COMEX dashboard"""
    
    def __init__(self, rep_pg=None, rep_maq=None, rep_out=None):
        self.rep_pg = rep_pg or r"\\assushare.sogecap.socgen\ASSU\_Applications\SAS-RCF-TRF-PIL-DOM\AUTRE\DEMANDES AD-HOC\202510 - POC Migration SAS"
        self.rep_maq = rep_maq or self.rep_pg
        self.rep_out = rep_out or self.rep_pg
        self.nom_maq = "TBB RCF_COMEX - Maquette - en cours.xlsx"
        self.nom_fic = "TBB RCF_COMEX - H&aass..xlsx"
        
        self.tdeb = time.time()
    
    def get_date_parameters(self):
        """Calculate all date parameters - matches SAS logic"""
        today = datetime.now().date()
        iso_cal = today.isocalendar()
        
        # Current week
        S = f"S{iso_cal.week:02d}{iso_cal.year % 100:02d}"
        
        # Previous weeks
        Sm1 = f"S{iso_cal.week-1:02d}{iso_cal.year % 100:02d}"
        Sm2 = f"S{iso_cal.week-2:02d}{iso_cal.year % 100:02d}"
        Sm3 = f"S{iso_cal.week-3:02d}{iso_cal.year % 100:02d}"
        Sm4 = f"S{iso_cal.week-4:02d}{iso_cal.year % 100:02d}"
        Sm5 = f"S{iso_cal.week-5:02d}{iso_cal.year % 100:02d}"
        
        # Next week
        Sp1 = f"S{iso_cal.week+1:02d}{iso_cal.year % 100:02d}"
        
        # 52 weeks ago + beginning calculation
        SM52 = today - timedelta(weeks=51)
        # Get Monday of 52 weeks ago
        SM52_monday = SM52 - timedelta(days=SM52.weekday())
        
        SAM1 = f"S{(SM52_monday - timedelta(weeks=1)).isocalendar()[1]:02d}{(SM52_monday - timedelta(weeks=1)).isocalendar()[0] % 100:02d}"
        
        return {
            'S': S,
            'Sm1': Sm1,
            'Sm2': Sm2,
            'Sm3': Sm3,
            'Sm4': Sm4,
            'Sm5': Sm5,
            'Sp1': Sp1,
            'SAM1': SAM1,
            'today': today,
            'SM52': SM52_monday,
        }
    
    def export_parameters(self, date_params):
        """Export date parameters to DataFrame (instead of Excel for testing)"""
        datedeb1 = date_params['SM52']
        dateS = date_params['SM52']
        dateSM1 = date_params['SM52'] - timedelta(weeks=1)
        
        df = pd.DataFrame({
            'SM1': [date_params['Sm1']],
            'S': [date_params['S']],
            'datedeb1': [datedeb1.strftime('%d/%m/%Y')],
            'datedeb2': [date_params['today'].strftime('%d/%m/%Y')],
            'datedon': [date_params['today'].strftime('%d/%m/%Y')],
            'dateS': [dateS.strftime('%d/%m/%Y')],
            'dateSM1': [dateSM1.strftime('%d/%m/%Y')]
        })
        
        return df
    
    def run(self):
        """Execute launcher"""
        print("\n" + "=" * 90)
        print(" " * 25 + "LANCEUR HEBDO - COMEX DASHBOARD")
        print("=" * 90)
        
        # Get date parameters
        date_params = self.get_date_parameters()
        print(f"\n[DATE PARAMETERS]")
        print(f"  Current Week (S):      {date_params['S']}")
        print(f"  Previous Week (Sm1):   {date_params['Sm1']}")
        print(f"  5 Weeks Back (Sm5):    {date_params['Sm5']}")
        print(f"  Next Week (Sp1):       {date_params['Sp1']}")
        print(f"  52 Weeks Ago (SAM1):   {date_params['SAM1']}")
        print(f"  Start Date (dtdeb):    {date_params['SM52']}")
        
        # Export parameters
        params_df = self.export_parameters(date_params)
        print(f"\n[PARAMETERS EXPORT]")
        print(params_df.to_string())
        
        return date_params, params_df


if __name__ == "__main__":
    launcher = LauncherHebdo()
    launcher.run()
