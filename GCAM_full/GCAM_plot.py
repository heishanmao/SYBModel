import geopandas as gpd
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


class plot_gcam():
    def __init__(self, prefix, scenario):
        ## mapping base layer
        self.root = os.path.abspath('..')  #
        self.prefix = prefix # '2_emission.csv'
        self.scenario = scenario # 'SSP2'

    def create_sum(self, ax, cmap = 'RdBu_r'):
        if self.prefix != '20220421_GCAM_totalarea.csv':
            if f == '2_water.csv':
                mgt_list = ['IRR']
            else:
                mgt_list = ['IRR', 'RFD']

            count = 0
            for mgt in mgt_list:
                for lev in ['hi','lo']:
                    temp = pd.read_csv(self.root + f'/GCAM_full/ArcGIS/data/{self.prefix}_{self.scenario}_{mgt}_{lev}.csv')
                    temp = temp[['subregion', '2030']].set_index('subregion')
                    if count == 0:
                        data = temp
                    else:
                        data = temp + data
                    count += 1
            df = data.reset_index()
        else:
            df = pd.read_csv(self.root + f'/GCAM_full/ArcGIS/data/{self.prefix}_{self.scenario}.csv')

        df = df.rename({'subregion': 'glu_nm'}, axis = 'columns')

        USA = gpd.read_file(self.root + '/Shapefiles/cb_2018_us_state_20m.shp')
        Outside = ['AK', 'HI', 'PR']
        States = [state for state in USA.STUSPS.tolist() if state not in Outside]
        # USA.plot()
        USA[USA['STUSPS'].isin(States)].boundary.plot(ax=ax, color='#828282', zorder=-2)

        basins = gpd.read_file(self.root + '/GCAM_full/ArcGIS/merged_shapefiles/base.shp')
        basins = basins.merge(df, on = 'glu_nm', how = 'left')
        # if self.prefix == '2_emission.csv':
        #     vmin = -3.16; vmax = 1.1156
        # elif self.prefix == '2_N2.csv':
        #     vmin = 6.57e-5; vmax = 0.0804
        # elif self.prefix == '2_water.csv':
        #     vmin = 0.0281; vmax = 3.6
        # elif self.prefix == '20220421_gcam_leafarea.csv':
        #     vmin = 0.0594595; vmax = 45.2
        # else:
        #     vmin = 0.022452; vmax = 30.5887
        basins.plot(ax=ax, zorder=-1, column = '2030', cmap=cmap, legend=True)  ##, vmin = vmin, vmax = vmax)
        plotname = self.root + f'/GCAM_full/ArcGIS/graphs/sum_{f}_{self.scenario}.png'
        return plotname

    def create_single(self, ax, mgt = None, lev = None, cmap = 'RdBu_r'):
        temp = pd.read_csv(self.root + f'/GCAM_full/ArcGIS/data/{self.prefix}_{self.scenario}_{mgt}_{lev}.csv')
        df = temp[['subregion', '2030']]
        df = df.rename({'subregion': 'glu_nm'}, axis = 'columns')

        USA = gpd.read_file(self.root + '/Shapefiles/cb_2018_us_state_20m.shp')
        Outside = ['AK', 'HI', 'PR']
        States = [state for state in USA.STUSPS.tolist() if state not in Outside]
        # USA.plot()
        USA[USA['STUSPS'].isin(States)].boundary.plot(ax=ax, color='#828282', zorder=-2)

        basins = gpd.read_file(self.root + '/GCAM_full/ArcGIS/merged_shapefiles/base.shp')
        basins = basins.merge(df, on = 'glu_nm', how = 'left')
        if self.prefix == '2_emission.csv':
            vmin = -3.16; vmax = 1.1156
        elif self.prefix == '2_N2.csv':
            vmin = 6.57e-5; vmax = 0.0804
        elif self.prefix == '2_water.csv':
            vmin = 0.0281; vmax = 3.6
        elif self.prefix == '20220421_gcam_leafarea.csv':
            vmin = 0.0594595; vmax = 45.2
        else:
            vmin = 0.022452; vmax = 30.5887
        basins.plot(ax=ax, zorder=-1, column = '2030', cmap=cmap, legend=True, vmin = vmin, vmax = vmax)
        plotname = self.root + f'/GCAM_full/ArcGIS/graphs/single_{f}_{self.scenario}.png'
        return plotname


if __name__ == '__main__':
    file_list = ['2_emission.csv', '2_N2.csv', '2_water.csv',   # '20220421_gcam_leafarea.csv',
                 '20220421_gcam_production.csv', '20220421_GCAM_totalarea.csv']
    scenario = 'SSP2'

    for i, f in enumerate(file_list):
        fig, ax = plt.subplots(figsize=(5,5), facecolor='#faf8ed')
        pgc = plot_gcam(f, scenario)
        plotname = pgc.create_sum(ax)
        plt.savefig(plotname, dpi=300)
        plt.close()


    ###########################
    file_list = ['2_emission.csv', '2_N2.csv', '2_water.csv', '20220421_gcam_leafarea.csv', '20220421_gcam_production.csv']
    scenario = 'SSP2'

    for f in file_list:
        fig = plt.figure(figsize=(20, 20), facecolor='#faf8ed')
        if f == '2_water.csv':
            mgt_list = ['IRR']
            gs = GridSpec(2, 1, figure=fig)
        else:
            mgt_list = ['IRR', 'RFD']
            gs = GridSpec(2, 2, figure=fig)
        for j, mgt in enumerate(mgt_list):
            for k, lev in enumerate(['hi','lo']):
                if f == '2_water.csv':
                    ax = fig.add_subplot(gs[k])
                else:
                    ax = fig.add_subplot(gs[j, k])
                pgc = plot_gcam(f, scenario)
                plotname = pgc.create_single(ax, mgt, lev)
        plt.savefig(plotname, dpi=300)
        plt.close()
