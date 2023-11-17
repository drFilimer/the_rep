from geopy.geocoders import Nominatim

project = QgsProject.instance()
wind_lyr = project.mapLayersByName('wiatrowe')[0]
new_field = QgsField('Address', QVariant.String)
geolocator = Nominatim(user_agent="Nearest Turbine")

with edit(wind_lyr):
    field_names = [f.name() for f in wind_lyr.fields()]
    if "Address" not in field_names:
        pr = wind_lyr.dataProvider()
        pr.addAttributes([new_field])
        wind_lyr.updateFields()

with edit(wind_lyr):
    for idx, f in enumerate(wind_lyr.getFeatures()):
        geom = f.geometry()
        x,y = f.geometry().asPoint().x(), f.geometry().asPoint().y()
        location = geolocator.reverse((y, x), language= 'en')
        an_address = location.address.split(',')[-1:-7:-1]
        mod_address = an_address[::-1]
        a_string = ','.join(mod_address)
        output = a_string.strip()
        f["Address"] = output
        wind_lyr.updateFeature(f)
        wind_lyr.updateExtents()
        print(f'Dodano dane adresowe do rekordu nr {idx}')
        
print('Zakończono dodawanie danych.')