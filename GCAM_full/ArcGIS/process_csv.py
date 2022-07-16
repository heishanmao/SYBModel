import pandas as pd
import os

def get_boundary(df, scenarios):
    df.query('scenario in @scenarios', inplace = True)

    max = df.iloc[:, -1].max()
    min = df.iloc[:, -1].min()

    return max, min


path_in = "D:/OneDrive - University of Tennessee/Scripts/SYBModel/GCAM_full/"

subregion_fullname = {
    'ArkWhtRedR': 'Arkansas_White_Red_Basin',
    'MissppRN': 'Upper_Mississippi_Basin',
    'OhioR': 'Ohio_River_Basin',
    'MissouriR': 'Missouri_River_Basin',
    'NelsonR': 'Saskatchewan_Nelson',
    'GreatLakes': 'Great_Lakes_Basin'
}

file_list = ['2_emission.csv', '2_N2.csv', '2_water.csv', '20220421_gcam_leafarea.csv', '20220421_gcam_production.csv', '20220421_GCAM_totalarea.csv']
scenarios = ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']

for year in ['2020', '2025', '2030', '2035', '2040', '2045', '2050']:
    for scenario in scenarios:
        for f in file_list:

            data = pd.read_csv(os.path.join(path_in, f))
            data['subregion'] = data['subregion'].map(subregion_fullname)
            data = data.dropna(axis = 0, how = 'any')

            if f == '20220421_GCAM_totalarea.csv':
                data = data[['scenario', 'subregion', year]]
                ssp_max, ssp_min = get_boundary(data, scenarios)
                data = data.query('scenario == @scenario')
                data.loc[:, 'ssps_max'] = ssp_max
                data.loc[:, 'ssps_min'] = ssp_min
                data.to_csv(os.path.join(path_in, 'ArcGIS', 'data', f'{f[:-4]}_{scenario}_{year}.csv'), index = False)
            else:
                data = data[['scenario', 'subregion', 'management', 'level', year]]
                ssp_max, ssp_min = get_boundary(data, scenarios)
                for mgt in ['IRR','RFD']:
                    for lev in ['hi','lo']:
                        data2 = data.query('scenario == @scenario and management == @mgt and level == @lev')
                        data.loc[:, 'ssps_max'] = ssp_max
                        data.loc[:, 'ssps_min'] = ssp_min
                        data2.to_csv(os.path.join(path_in, 'ArcGIS', 'data', f'{f[:-4]}_{scenario}_{mgt}_{lev}_{year}.csv'), index = False)

        # find range of values
        print(f, data.query('scenario == @scenario')[year].min(), data.query('scenario == @scenario')[year].max())