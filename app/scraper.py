import urllib
import csv
import time
import math
import requests
import itertools


API_KEY = ['AIzaSyDpa9FUmUBcVQwg37VRDoOs3W3JVUjaD00']
shops_list = []
debug_list = []
SAVE_PATH = r"D:\Downloads"
COMPANY_SEARCH = "bar"
types = ''
RADIUS_KM = 1
LIMIT = 60
southwest_lat = -75.1498901844
southwest_lng = 40.1613129009
northeast_lat = -75.1134979725
northeast_lng = 40.1791522689


def setvariables():
    pass


class coordinates_box(object):
    """
    Initialise a coordinates_box class which will hold the produced coordinates and
    output a html map of the search area
    """
    def __init__(self):
        self.coordset = []
 
    def createcoordinates(self,
                          southwest_lat,
                          southwest_lng,
                          northeast_lat,
                          northeast_lng):
        """
        Based on the input radius this tesselates a 2D space with circles in
        a hexagonal structure
        """
        earth_radius_km = 6371
        lat_start = math.radians(southwest_lat)
        lon_start = math.radians(southwest_lng)
        lat = lat_start
        lon = lon_start
        lat_level = 1
        while True:
            if (math.degrees(lat) <= northeast_lat) & (math.degrees(lon) <= northeast_lng):
                self.coordset.append([math.degrees(lat), math.degrees(lon)])
            parallel_radius = earth_radius_km * math.cos(lat)
            if math.degrees(lat) > northeast_lat:
                break
            elif math.degrees(lon) > northeast_lng:
                lat_level += 1
                lat += (RADIUS_KM / earth_radius_km) + (RADIUS_KM / earth_radius_km) * math.sin(math.radians(30))
                if lat_level % 2 != 0:
                    lon = lon_start
                else:
                    lon = lon_start + (RADIUS_KM / parallel_radius) * math.cos(math.radians(30))
            else:
                lon += 2 * (RADIUS_KM / parallel_radius) * math.cos(math.radians(30))
 
        
        # Save coordinates:
        f = open(SAVE_PATH + 'circles_' + COMPANY_SEARCH + '_python_mined.csv', 'w', newline='')
        w = csv.writer(f)
        for coord in self.coordset:
            w.writerow(coord)
        f.close()
        # LOG MAP
        # self.htmlmaplog(SAVE_PATH + 'htmlmaplog_' + COMPANY_SEARCH + '.html')
 
class counter(object):
    """
    Counter class to keep track of the requests usage
    """
    def __init__(self):
        self.keynum = 0
        self.partition_num = 0
        self.detailnum = 0
 
    def increment_key(self):
        self.keynum += 1
 
    def increment_partition(self):
        self.partition_num += 1
 
    def increment_detail(self):
        self.detailnum += 1
 
 
def googleplaces(lat,
                 lng,
                 radius_metres,
                 search_term,
                 key,
                 pagetoken=None,
                 nmbr_returned=0):
    """
    Function uses the 'nearbysearch', however it is possible to use the radar-search and others
    located here: https://developers.google.com/places/web-service/search
    The API call returns a page_token for the next page up to a total of 60 results
    """
    location = urllib.parse.quote("%.5f,%.5f" % (lat,lng))
    radius = float(radius_metres)
    name = urllib.parse.quote(str(search_term))
    
    if types:
         search_url = ('https://maps.googleapis.com/maps/api/place/' + 'nearbysearch' +
                      '/json?location=%s&radius=%d&keyword=%s&type=%s&key=%s') % (location, radius, name, types, key)        
    else:
        search_url = ('https://maps.googleapis.com/maps/api/place/' + 'nearbysearch' +
                      '/json?location=%s&radius=%d&keyword=%s&key=%s') % (location, radius, name, key)
    if pagetoken is not None:
        search_url += '&pagetoken=%s' % pagetoken
        # SLEEP so that request is generated
        time.sleep(2)
 
    time.sleep(0.1)
    req_count.increment_key()
    
    google_search_request = requests.get(search_url)
    search_json_data = google_search_request.json()
 
    
    if search_json_data['status'] == 'OK':
        nmbr_returned += len(search_json_data['results'])
        for place in search_json_data['results']:
            try:
                shop = [place['name'].encode('ascii', 'ignore').decode('ascii'),
                        place['vicinity'].encode('ascii', 'ignore').decode('ascii'),
                        place['geometry']['location']['lat'],
                        place['geometry']['location']['lng'],
                        place['types'],
                        place['place_id']]
            except:
                shop = [place['name'].encode('ascii', 'ignore').decode('ascii'),
                        place['vicinity'].encode('ascii', 'ignore').decode('ascii'),
                        place['geometry']['location']['lat'],
                        place['geometry']['location']['lng'],
                        place['types'],
                        place['place_id']]
            if shop not in shops_list:
                shops_list.append(shop)
        # Possible to get up to 60 results
        # from one search by passing next_page_token
        try:
            next_token = search_json_data['next_page_token']
            googleplaces(lat=lat,
                         lng=lng,
                         radius_metres=radius_metres,
                         search_term=search_term,
                         key=key,
                         pagetoken=next_token,
                         nmbr_returned=nmbr_returned)
            return
        except KeyError:
            pass
    elif search_json_data['status'] == 'ZERO_RESULTS':
        pass
    else:
        try:
            print('Error: %s' % search_json_data['error_message'])
        except KeyError:
            print('Unknown error message - check URL')
 
    debug_list.append([lat, lng, nmbr_returned])

 
 
def googledetails(place_id,
                  key):
    """
    Function uses the mined place_ids to get further data from the details API
    """
    detail_url = ('https://maps.googleapis.com/maps/api/place/' + 'details' +
                  '/json?placeid=%s&key=%s') % (place_id, key)
    
    google_detail_request = requests.get(detail_url)
    detail_json_data = google_detail_request.json()
    time.sleep(0.1)
 
    if detail_json_data['status'] == 'OK':
        try:
            address_components = detail_json_data['result']['address_components']
            phone_components = detail_json_data['result']
            
            # At the moment care only about extracting postcode, however possible to get:
            # Street number, Town, etc.
            postcode = phone_components['formatted_phone_number'].encode('ascii', 'ignore').decode('ascii')
        except KeyError:
            postcode = 'NaN'
        try:
            formatted_address = detail_json_data['result']['formatted_address'].encode('ascii', 'ignore').decode('ascii')
        except KeyError:
            formatted_address = 'NaN'
        try:
            website = detail_json_data['result']['website'].encode('ascii', 'ignore').decode('ascii')
        except KeyError:
            website = 'NaN'
        try:
            p_closed = detail_json_data['result']['permanently_closed']
            if p_closed:
                closed = 'Permanently Closed'
        except KeyError:
            closed = 'Open'
        detail = [postcode, formatted_address, website, closed]
    else:
        detail = detail_json_data['status'].encode('ascii', 'ignore').decode('ascii')
 
    
    return detail
 
 
def fillindetails(f=SAVE_PATH + COMPANY_SEARCH + '_python_mined.csv'):
    """
    Opens the produced CSV and extracts the place ID for querying 
    """
    detailed_stores_out = []
    simple_stores_out = []
    with open(f, 'r') as csvin:
        reader = csv.reader(csvin)
 
        for store in reader:
            req_count.increment_detail()
            key_number = (req_count.keynum // 950)
 
            detailed_store = googledetails(store[5],  API_KEY[key_number])
            
            detailed_stores_out.append(detailed_store)
            simple_stores_out.append(store)
 
    # OUTPUT to CSV
    f = open(SAVE_PATH + 'detailed_' + COMPANY_SEARCH + '_python_mined.csv', 'w', newline='')
    w = csv.writer(f)
 
    # Combine both lists into one
    combined_list = [list(itertools.chain(*a)) for a in zip(simple_stores_out, detailed_stores_out)]
 
    for one_store in combined_list:
        try:
            w.writerow(one_store)
        except Exception as err:
            print("Something went wrong: %s" % err)
            w.writerow("Error")
    f.close()
     
     
def runsearch():
    """
    Initialises the searches for each partition produced
    """
    print("%d Keys Remaining" % (len(API_KEY)-1))
    for partition in coord.coordset:
        # Keys have a life-span of 1000 requests
        key_number = (req_count.keynum // 1000)
        req_count.increment_partition()
 
        googleplaces(lat=partition[0],
                     lng=partition[1],
                     radius_metres=RADIUS_KM*1000,
                     search_term=COMPANY_SEARCH,
                     key=API_KEY[key_number])
 
    # OUTPUT to CSV
    f = open(SAVE_PATH + COMPANY_SEARCH + '_python_mined.csv', 'w', newline='')
    w = csv.writer(f)
    #w.writerow(['Name', 'Partial Address', 'Latitude', 'Longitude', 'Google Place Tags', 'Google Place ID', 'Phone', 'Full Address', 'Website', 'Open Status'])
    for one_store in shops_list:
        w.writerow(one_store)
    f.close()
 
    # OUTPUT LOG to CSV
    f = open(SAVE_PATH + 'log_' + COMPANY_SEARCH + '_python_mined.csv', 'w', newline='')
    w = csv.writer(f)
    for debug_result in debug_list:
        w.writerow(debug_result)
    f.close()
 
    # DETAIL SEARCH
    fillindetails()


setvariables()
coord = coordinates_box()
coord.createcoordinates(southwest_lng, southwest_lat, northeast_lng, northeast_lat)

req_count = counter()
runsearch()
 
 
if __name__ == "__main__":
    print('scraping')
    # 1. CREATE PARTITIONS
    # Setup coordinates
    # coord = coordinates_box()
    # #coord.createcoordinates(southwest_lng, southwest_lat, northeast_lng, northeast_lat)
    # coord.createcoordinates(40.1613129009,-75.1498901844,40.1791522689,-75.1134979725)
    
    
    # 2. SEARCH PARTITIONS
    # Setup counter
    # req_count = counter()
    # runsearch()
    print(shops_list)
