import pandas as pd
import os

path_in = "D:/OneDrive - University of Tennessee/Scripts/SYBModel/GCAM_full/"
scenario = 'SSP2'
subregion_fullname = {
    'ArkWhtRedR': 'Arkansas_White_Red_Basin',
    'MissppRN': 'Upper_Mississippi_Basin',
    'OhioR': 'Ohio_River_Basin',
    'MissouriR': 'Missouri_River_Basin',
    'NelsonR': 'Saskatchewan_Nelson',
    'GreatLakes': 'Great_Lakes_Basin'
}


file_list = ['2_emission.csv', '2_N2.csv', '2_water.csv', '20220421_gcam_leafarea.csv', '20220421_gcam_production.csv', '20220421_GCAM_totalarea.csv']
for f in file_list:

    data = pd.read_csv(os.path.join(path_in, f))
    data['subregion'] = data['subregion'].map(subregion_fullname)
    data = data.dropna(axis = 0, how = 'any')

    if f == '20220421_GCAM_totalarea.csv':
        data = data[['scenario', 'subregion', '2030']]
        data = data.query('scenario == @scenario')
        data.to_csv(os.path.join(path_in, 'ArcGIS', 'data', f'{f}_{scenario}.csv'), index = False)
    else:
        data = data[['scenario', 'subregion', 'management', 'level', '2030']]
        for mgt in ['IRR','RFD']:
            for lev in ['hi','lo']:
                data2 = data.query('scenario == @scenario and management == @mgt and level == @lev')
                data2.to_csv(os.path.join(path_in, 'ArcGIS', 'data', f'{f}_{scenario}_{mgt}_{lev}.csv'), index = False)

        # find range of values
        print(f, data.query('scenario == @scenario')['2030'].min(), data.query('scenario == @scenario')['2030'].max())