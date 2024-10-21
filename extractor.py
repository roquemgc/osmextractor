import os
import xml.etree.ElementTree as ET
import string

current_directory = os.path.dirname(os.path.abspath(__file__));
osm_file_path = os.path.join(current_directory, 'limeira.osm')
base_model_file_path = os.path.join(current_directory, 'base_model.txt')
created_model_file_path = os.path.join(current_directory, '..', 'LimeiraPilot', 'config', 'model.txt')
latitudes, longitudes = [], []

def extract_street_coordinates(osm_file_path):
    tree = ET.parse(osm_file_path)
    root = tree.getroot()

    streets = {}
    street_count = {}
    allowed_paths = [
                        'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'tertiary_walk' 
                        'unclassified', 'residential', 'service', 'living_street', 'path',
                        'pedestrian', 'road', 'footway', 'cycleway', 'crossing'
                    ]

    for way in root.findall('way'):
        street_name = None
        coordinates = []
        is_path_alllowed = False

        tags = []

        for tag in way.findall('tag'):
            if tag.attrib['k'] == 'highway':
                if (tag.attrib['v'] not in tags):
                    print(tag.attrib['v'])
            if tag.attrib['k'] == 'highway' or tag.attrib['k'] ==     'junction' and tag.attrib['v'] in allowed_paths:
                is_path_alllowed = True
            if tag.attrib['k'] == 'name':
                street_name = tag.attrib['v']

        tags = [tag for tag in tags if tag]

        if is_path_alllowed and street_name:
            for nd in way.findall('nd'):
                ref = nd.attrib['ref']
                node = root.find(f'./node[@id="{ref}"]')
                if node is not None:
                    lat = float(node.attrib['lat'])
                    lon = float(node.attrib['lon'])
                    latitudes.append(lat)
                    longitudes.append(lon)
                    coordinates.append((lat, lon))
            
            if street_name in street_count:
                street_suffix = string.ascii_uppercase[street_count[street_name]]
                street_name_with_letter = f'{street_name} {street_suffix}'
                street_count[street_name] += 1
            else:
                street_name_with_letter = f'{street_name} A'
                street_count[street_name] = 1

            if street_name_with_letter not in streets:
                streets[street_name_with_letter] = []
            streets[street_name_with_letter].extend(coordinates)

    return streets

def normalize_street_coordinates(street_coordinates):
    lat_min, lat_max = min(latitudes), max(latitudes)
    lon_min, lon_max = min(longitudes), max(longitudes)
    
    normalized_streets = {}
    for street, coords in street_coordinates.items():
        normalized_coords = [
            (
                (lon - lon_min) * 100000,
                (lat_max - lat) * 100000
            )
            for lat, lon in coords
        ]
        normalized_streets[street] = normalized_coords

    return normalized_streets

def print_streets_with_coordinates(street_coordinates):

    for street, coords in street_coordinates.items():
        print(f'Rua: {street}')
        for coord in coords:
            print(f' - Coordenada: {coord}')

def convert_street_coordinantes_to_string(street_coordinates):
    string_street_coordinates = []

    lat_max, lon_max = 0, 0
    

    for street, coords in street_coordinates.items():
        string_line_coords = ''

        for coord in coords:
            string_line_coords += f'[{round(coord[1])},{round(coord[0])}]-'
            
            if (coord[1] > lon_max):
                lon_max = coord[0]
            if (coord[0] > lat_max):
                lat_max = coord[0]

        string_line_coords = string_line_coords[:-1]
        string_street_coordinates.append(f'{street} [STREET]{string_line_coords}\n')

    print(lat_max)
    print(lon_max)

    return ''.join(string_street_coordinates)

def create_model_txt(street_coordinates):

    with open(base_model_file_path, 'r') as base_file:
        file_lines = base_file.readlines()

    for i, line in enumerate(file_lines):
        if '#ROADMAP' in line:
            file_lines.insert(i + 1, street_coordinates)
            break

    with open(created_model_file_path, 'w', encoding='utf-8') as new_file:
        new_file.writelines(file_lines)


street_coordinates = extract_street_coordinates(osm_file_path);
normalized_street_coordinates = normalize_street_coordinates(street_coordinates)
string_street_coordinates = convert_street_coordinantes_to_string(normalized_street_coordinates)
# print_streets_with_coordinates(street_coordinates)
# print(string_street_coordinates)
create_model_txt(string_street_coordinates)

# ways = access, addr:street, addr:suburb, alt_name, amenity, area, barrier, bicycle, bridge, building, building:levels, bus, cuisine, destination:ref, dispensing, email, fee, foot, footway, healthcare, height, highway, internet_access, junction, landuse, lanes, layer, leisure, lit, maxspeed, motor_vehicle, name, note, office, old_name, oneway, oneway_type, opening_hours, operator, operator:type, parking, phone, postal_code, ref, religion, service, shop, short_name, sidewalk, source, sport, supervised, surface, tunnel, website, wheelchair, width



