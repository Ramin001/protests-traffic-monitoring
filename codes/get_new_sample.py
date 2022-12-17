import warnings
import requests
import time
import pandas as pd
import numpy as np
import pytz
import geopandas as gpd

#Initialize functions==================================================================================================================

#finding all neighbors in shp file------------------------------------------------------------------------------------

def create_cross_neighbors(shp_file, location_key, geometry_col, neighbors_key):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        shp_file[neighbors_key]=np.empty((len(shp_file), 0)).tolist()
        for index, row in shp_file.iterrows():  
            neighbors = shp_file[shp_file.geometry.touches(row[geometry_col])][location_key].tolist() 
            shp_file[neighbors_key].iloc[index] = neighbors
        return shp_file.explode(neighbors_key).reset_index()[[location_key,neighbors_key]]


# function to run Google's distance matrix API and add all cross location traffics
#  to an excel file, together witht the time the sample is taken-------------------------------------------------------

def update_regions_online_traffic(shp_address, API_url, API_key, output_file_address):

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")

        orig_dest_matrix_all = pd.DataFrame()
        places = gpd.read_file(shp_address)
        places ['address'] = [places.loc[i, 'NAME_MAHAL'] + " منطقه " + str(int(places.loc[i, 'REGION'])) + ", Tehran, Tehran Province, Iran" 
                                              for i in range(len(places))]        
        neighbors = create_cross_neighbors(places, 'address', 'geometry', 'address_dest')

        for place in places['address'].tolist()[2:6]:
            time.sleep(1)
            orig_dest_matrix = pd.DataFrame()

            # define origin and destinations (its neighbors) for the API request
            orig_str = place 

            destinations = [i for i in neighbors[neighbors['address']==place]['address_dest'].tolist() ]
            dest_str = destinations[0]
            for s in range(1,len(destinations)):
                dest_str = dest_str + ' | ' + destinations[s] 

            # API request
            info = requests.get(  API_url+'&destinations='+dest_str+'&origins='+orig_str+'&key='+API_key  ).json()
            if len(info['rows'])>0:

                orig_dest_matrix['distance'] = 0
                orig_dest_matrix['duration'] = 0
                orig_dest_matrix['duration_in_traffic'] = 0

                for i in range(len(info['rows'][0]['elements'])):
                    #replace not found elements with nan
                    if info['rows'][0]['elements'][i] ==  'NOT_FOUND':
                        info['rows'][0]['elements'][i] = {'distance': {'text': '', 'value': pd.NA},
                                                            'duration': {'text': '', 'value': pd.NA},
                                                            'duration_in_traffic': {'text': '', 'value': pd.NA},
                                                            'status': 'CHANGED_MANUALY'}

                #get request data in a df 
                for var in ['distance','duration','duration_in_traffic']:
                    orig_dest_matrix[var] = [info['rows'][0]['elements'][i][var]['value'] for i in 
                                             range(len(info['rows'][0]['elements']))
                                            ]

                orig_dest_matrix['time_observed'] = pd.Timestamp.now(tz=pytz.timezone('Asia/Tehran'))
                orig_dest_matrix['time_observed'] = orig_dest_matrix['time_observed'].dt.tz_localize(None)

                orig_dest_matrix_all = orig_dest_matrix_all.append(orig_dest_matrix)

        orig_dest_matrix_all.to_excel(output_file_address, index=False)  

#Initialize values==================================================================================================================
         

API_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?departure_time=now&traffic_model=best_guess'
output_file_address = "../traffic_data.xlsx"
shp_address = '../regions_shapefiles/mahale.shp'


######### main code
update_regions_online_traffic(shp_address, API_url, API_key, output_file_address)