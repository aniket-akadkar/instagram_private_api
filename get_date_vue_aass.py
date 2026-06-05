from datetime import datetime, timedelta

def get_date_vue_aass(aass_force=None, aass_local='aass', date_vue_local='date_vue', date_vue_L_local='date_vue_L'):
    """
    Get the view date and aass (week) for the dashboard.
    Matches SAS logic exactly.
    
    Parameters:
    -----------
    aass_force : str, optional
        Force a specific week (format: SSYY where SS=week number, YY=year)
    
    Returns:
    --------
    dict : Dictionary containing aass, date_vue, and date_vue_L
    """
    
    if aass_force is None:
        today = datetime.now().date()
        iso_cal = today.isocalendar()
        week_num = iso_cal.week
        year = iso_cal.year
        aass = f"{week_num:02d}{year % 100:02d}"
    else:
        aass = aass_force
    
    # Extract week and year from aass
    ss = int(aass[:2])  # Week number
    aa = int(aass[2:])  # Year (2 digits)
    aa2 = aa + 2000    # Convert to 4-digit year
    
    # First day of the year
    premier_jour_annee = datetime(aa2, 1, 1).date()
    
    # Calculate first Saturday of the year
    # weekday(): 0=Monday, 5=Saturday, 6=Sunday
    weekday = premier_jour_annee.weekday()
    
    # SAS logic: premier_samedi_annee = premier_jour_annee + 7 + 7*(weekday(premier_jour_annee) in (6,7)) - weekday(premier_jour_annee)
    if weekday in (5, 6):  # Saturday or Sunday
        premier_samedi_annee = premier_jour_annee + timedelta(days=7 - weekday)
    else:
        premier_samedi_annee = premier_jour_annee + timedelta(days=5 - weekday)
    
    # Calculate the date for the given week
    date_vue = premier_samedi_annee + timedelta(weeks=ss - 1)
    date_vue_L = date_vue.strftime('%d/%m/%Y')
    
    return {
        aass_local: aass,
        date_vue_local: date_vue,
        date_vue_L_local: date_vue_L
    }


if __name__ == "__main__":
    result = get_date_vue_aass()
    print(f"AASS: {result.get('aass')}")
    print(f"Date Vue: {result.get('date_vue')}")
    print(f"Date Vue Formatted: {result.get('date_vue_L')}")
