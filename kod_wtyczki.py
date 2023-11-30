# Necessary imports
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtCore import Qt
from math import radians, degrees, sin, cos, sqrt, atan2
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Define project and crs variables
project = QgsProject.instance()
source_crs = project.crs()
destination_crs = QgsCoordinateReferenceSystem(4326)

# Get the current project CRS
project_crs = QgsProject.instance().crs()
git_url = 'https://raw.githubusercontent.com/drFilimer/the_rep/main/turbines_csv.csv'
dist_tool = QgsDistanceArea()
df = pd.read_csv(git_url)
gdf = gpd.GeoDataFrame(data = df, geometry = gpd.points_from_xy(df['X'], df['Y']))

class ClickTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.gdf = gdf
        
    def find_nearest_point(self, clicked_point):
        distances = self.gdf['geometry'].apply(lambda x: dist_tool.measureLine(QgsPointXY(x.x, x.y), clicked_point))
        nearest_index = distances.idxmin()
        return (self.gdf.loc[nearest_index, 'Address'], self.gdf.loc[nearest_index, 'geometry'])

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Calculate the differences in latitude and longitude
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula to calculate the great-circle distance between two points
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Radius of the Earth in kilometers
        radius_earth_km = 6371.0

        # Calculate the distance using the Haversine formula
        distance_km = radius_earth_km * c

        return distance_km
        
    def calculate_azimuth(self, lat_1, lon_1, lat_2, lon_2):
        # Calculate the differences in x and y coordinates
        delta_x = lat_2 - lat_1
        delta_y = lon_2 - lon_1

        # Calculate the azimuth in radians
        azimuth_rad = math.atan2(delta_y, delta_x)

        # Convert radians to degrees; get rid off negative values
        azimuth_deg = (degrees(azimuth_rad) + 360) % 360

        return azimuth_deg
        
    def identify_direction(self, azimuth_deg):
        directions = ["North", "North-Northeast", "Northeast", "East-Northeast", 
                      "East", "East-Southeast", "Southeast", "South-Southeast", 
                      "South", "South-Southwest", "Southwest", "West-Southwest", 
                      "West", "West-Northwest", "Northwest", "North-Northwest"]
        
        sector_size = 360 / len(directions)
        direction_idx = int((azimuth_deg + sector_size / 2) / sector_size) % len(directions)
        direction = directions[direction_idx]
        
        return direction

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = self.toMapCoordinates(event.pos())
            
            if source_crs.authid() == 'EPSG:2180':
                transform = QgsCoordinateTransform(project_crs, destination_crs, QgsProject.instance())
                pt_4326 = transform.transform(point)
                nearest_turbine, turbine_location = self.find_nearest_point(pt_4326)
                distance = self.haversine_distance(pt_4326.x(), pt_4326.y(), turbine_location.x, turbine_location.y)
                azimuth = self.calculate_azimuth(pt_4326.y(), pt_4326.x(), turbine_location.y, turbine_location.x)
                direction = self.identify_direction(azimuth)
                
                print(nearest_turbine)
                print(turbine_location)
                print(f'{round(distance,2)} km {direction}')
          
# Create an instance of the ClickTool class
click_tool = ClickTool(iface.mapCanvas())

# Set the map tool to the created instance
iface.mapCanvas().setMapTool(click_tool)

