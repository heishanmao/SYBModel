import geopandas as gpd
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
from matplotlib.colors import ListedColormap

class plot_map():
    def __init__(self, prefix, scenario, year):
        ## mapping base layer
        self.root = 'D:\\OneDrive - University of Tennessee\\Scripts\\SYBModel\\'  #os.path.abspath('.')
        self.prefix = prefix[:-4] # '2_emission'
        self.scenario = scenario # 'SSP2'
        self.year = year

    def create_sum(self, ax, leg, cmap='RdBu_r'):
        if self.prefix != '20220421_GCAM_totalarea':
            if self.prefix == '2_water':
                mgt_list = ['IRR']
            else:
                mgt_list = ['IRR', 'RFD']

            count = 0
            for mgt in mgt_list:
                for lev in ['hi','lo']:
                    temp = pd.read_csv(self.root + f'/GCAM_full/ArcGIS/data/{self.prefix}_{self.scenario}_{mgt}_{lev}_{self.year}.csv')
                    temp = temp[['subregion', self.year]].set_index('subregion')
                    if count == 0:
                        data = temp
                    else:
                        data = temp + data
                    count += 1
            df = data.reset_index()
        else:
            df = pd.read_csv(self.root + f'/GCAM_full/ArcGIS/data/{self.prefix}_{self.scenario}_{self.year}.csv')

        df = df.rename({'subregion': 'glu_nm'}, axis = 'columns')

        USA = gpd.read_file(self.root + '/Shapefiles/cb_2018_us_state_20m.shp')
        Outside = ['AK', 'HI', 'PR']
        States = [state for state in USA.STUSPS.tolist() if state not in Outside]
        # USA.plot()
        USA[USA['STUSPS'].isin(States)].boundary.plot(ax=ax, color='#828282', zorder=-2, linewidths=0.2)

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
        basins.plot(ax=ax, zorder=2, column=self.year, cmap=cmap,
                    legend=True,
                    legend_kwds={'orientation': "horizontal",
                            'location': 'bottom',
                            'pad':0.01,
                        })

        ax.set_title(leg, fontweight='bold')

        ax.set_facecolor('#faf8ed')
        ax.set_axis_off()  # hide the axis
        ax.grid(False)

        plotname = self.root + f'/GCAM_full/ArcGIS/graphs/sum_{self.prefix}_{self.scenario}_{self.year}.png'
        return plotname, df

    def create_single(self, ax, mgt = None, lev = None, cmap = 'RdBu_r'):
        temp = pd.read_csv(self.root + f'/GCAM_full/ArcGIS/data/{self.prefix}_{self.scenario}_{mgt}_{lev}_{self.year}.csv')
        df = temp[['subregion', self.year]]
        df = df.rename({'subregion': 'glu_nm'}, axis = 'columns')

        USA = gpd.read_file(self.root + '/Shapefiles/cb_2018_us_state_20m.shp')
        Outside = ['AK', 'HI', 'PR']
        States = [state for state in USA.STUSPS.tolist() if state not in Outside]
        # USA.plot()
        USA[USA['STUSPS'].isin(States)].boundary.plot(ax=ax, color='#828282', zorder=-2)

        basins = gpd.read_file(self.root + '/GCAM_full/ArcGIS/merged_shapefiles/base.shp')
        basins = basins.merge(df, on = 'glu_nm', how = 'left')

        if self.prefix == '2_emission':
            vmin = -3.16; vmax = 1.1156
        elif self.prefix == '2_N2':
            vmin = 6.57e-5; vmax = 0.0804
        elif self.prefix == '2_water':
            vmin = 0.0281; vmax = 3.6
        elif self.prefix == '20220421_gcam_leafarea':
            vmin = 0.0594595; vmax = 45.2
        else:
            vmin = 0.022452; vmax = 30.5887

        basins.plot(ax=ax, zorder=2, column=self.year, cmap=cmap, legend=True, vmin = vmin, vmax = vmax)

        ax.set_facecolor('#faf8ed')
        ax.set_axis_off()  # hide the axis
        ax.grid(False)

        plotname = self.root + f'/GCAM_full/ArcGIS/graphs/single_{self.prefix}_{self.scenario}_{self.year}.png'
        return plotname


if __name__ == '__main__':
    file_list = ['2_emission.csv', '2_N2.csv', '2_water.csv',   # '20220421_gcam_leafarea.csv',
                 '20220421_gcam_production.csv', '20220421_GCAM_totalarea.csv']
    scenario = 'SSP2'
    year = '2050'

    colors =[
        ['#f6e8c3', '#dfc27d', '#d8b365', '#bf812d', '#a6611a', '#8c510a'],
        ['#feebe2', '#fcc5c0', '#fa9fb5', '#f768a1', '#c51b8a', '#7a0177'],
        ['#f0f9e8', '#ccebc5', '#a8ddb5', '#7bccc4', '#43a2ca', '#0868ac'],
        ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026'],
        ['#ffffcc', '#d9f0a3', '#addd8e', '#78c679', '#31a354', '#006837'],
        ['#f0f9e8', '#ccebc5', '#a8ddb5', '#7bccc4', '#43a2ca', '#0868ac'],
    ]
    #cmap = ListedColormap(sns.color_palette(colors[i]))

    legs = ['Emissions', 'Fertilizer', 'Water', 'Production', 'Land']
    pallets = ['summer_r','YlOrRd', 'Blues','YlOrRd','Greens' ]

    for i, f in enumerate(file_list):
        fig, ax = plt.subplots(figsize=(6, 5), facecolor='#faf8ed')
        pgc = plot_map(f, scenario, year)
        plotname = pgc.create_sum(ax, legs[i], cmap = ListedColormap(sns.color_palette(colors[i])))
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
                pgc = plot_map(f, scenario, year)
                plotname = pgc.create_single(ax, mgt, lev)
        plt.savefig(plotname, dpi=300)
        plt.close()
