import csv
import os
from exif import Image
from gpx_converter import Converter
import folium

csvfilename = "image_data.csv"
gpxfilename = "map_coordinates.gpx"
coords = []
image_loc = []
gps_dict = []

# Main image attr, holds lat,long,img_path
image_attr = []

def write_to_csv(image_attr):
    fields = ['latitude', 'longitude', 'image_path']

    for gps, pth in image_attr:
        gps_dict.append({'latitude': gps[0], 'longitude': gps[1], 'image_path': pth})

    with open(csvfilename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=fields)
        writer.writeheader()
        writer.writerows(gps_dict)

def read_from_csv(csv_file):
    with open(csv_file, mode = 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        # Append each row to the coordinate_data array
        for row in csvreader:
            latitude, longitude, pt = float(row[0]), float(row[1]), str(row[2])
            image_attr.append(((latitude, longitude),pt))

def create_gpx():
    Converter(input_file=csvfilename).csv_to_gpx(lats_colname='latitude', longs_colname='longitude', output_file=gpxfilename)

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref =='W' :
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def get_image_coordinates(image_path):  
    with open(image_path, 'rb') as src:
        img = Image(src)
    if img.has_exif:
        try:
            coords = (decimal_coords(img.gps_latitude,img.gps_latitude_ref),decimal_coords(img.gps_longitude,img.gps_longitude_ref))
            image_attr.append((coords, image_path))        
            #pprint ({"YES Coordinates : IMAGE PATH:": image_path})
        except AttributeError:
            #pprint ({"NO Coordinates : IMAGE PATH:": image_path})
            return
    else:
        print ('The Image has no EXIF information')  

# Check if CSV exists in base dir
def check_csv_exists(filename):
    return os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


# MAIN #

for im in os.listdir("./photos/"):
    if (im.endswith(".png") | im.endswith(".jpg") | im.endswith(".jpeg")):
        t = "photos/" + im
        image_loc.append(t)

if not check_csv_exists(csvfilename):
    print("CSV File not found. Parsing.")
    for loc in image_loc:
        get_image_coordinates(loc) 
    write_to_csv(image_attr)  
else:
    print("CSV File found. Skipping writing process.")
    read_from_csv(csvfilename)

create_gpx()

if image_attr:
    avg_lat = sum(p[0] for p,_ in image_attr) / len(image_attr)
    avg_lon = sum(p[1] for p,_ in image_attr) / len(image_attr)
    my_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=14)

    # Add the points to the map with markers
    for point, image_path in image_attr:
        popup = folium.Popup(f'<img src="{image_path}" width="1280" height="720">')
        folium.Marker(location=point, popup=popup).add_to(my_map)

    folium.PolyLine(list(zip(*image_attr))[0], color="green", weight=2.5, opacity=1).add_to(my_map)
    my_map.save("gpx_map.html")

    print("Map created successfully!")