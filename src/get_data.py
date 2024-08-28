import pandas as pd
import requests

class GetData(object):
    def __init__(self, url) -> None:
        self.url = url
        response = requests.get(self.url)
        self.data = response.json()

    def processing_one_point(self, data_dict: dict):
        # Affichez la structure de geo_point_2d pour débogage
        geo_point = data_dict.get('geo_point_2d', {})
        print("Contenu de geo_point_2d:", geo_point)

        # Mettez à jour les clés si nécessaire
        temp = pd.DataFrame({key: [data_dict.get(key, None)] for key in ['datetime', 'trafficstatus', 'geo_point_2d', 'averagevehiclespeed', 'traveltime']})
        temp = temp.rename(columns={'trafficstatus': 'traffic'})

        if 'geo_point_2d' in temp.columns:
            # Adaptez ici en fonction des clés trouvées dans geo_point_2d
            temp['lat'] = temp.geo_point_2d.map(lambda x: x.get('lat', None) if isinstance(x, dict) else None)
            temp['lon'] = temp.geo_point_2d.map(lambda x: x.get('lon', None) if isinstance(x, dict) else None)
            del temp['geo_point_2d']

        return temp

    def __call__(self):
        res_df = pd.DataFrame({})
        for data_dict in self.data:
            temp_df = self.processing_one_point(data_dict)
            res_df = pd.concat([res_df, temp_df], ignore_index=True)

        res_df = res_df[res_df.traffic != 'unknown']

        return res_df
