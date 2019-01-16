from flask import (Flask, render_template, request)
app = Flask(__name__, template_folder='./templates')

import math, sys

API_KEY = ""
COMPANY_SEARCH = ""
types = ""
RADIUS_KM = 0
LIMIT = 60

southwest_lat = 0
southwest_lng = 0
northeast_lat = 0
northeast_lng = 0

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/map')
def create_map():
    # api, company, radius, swlat, swlng, nelat, nelng, types
    API_KEY = request.args.get('api')
    COMPANY_SEARCH = request.args.get('company')
    types = request.args.get('types')
    RADIUS_KM = float(request.args.get('radius'))
    southwest_lat = float(request.args.get('swlat'))
    southwest_lng = float(request.args.get('swlng'))
    northeast_lat = float(request.args.get('nelat'))
    northeast_lng = float(request.args.get('nelng'))

    class coordinates_box(object):
        """
        Initialise a coordinates_box class which will hold the produced coordinates and
        output a html map of the search area
        """
        def __init__(self):
            self.coordset = []
            self.htmltext = ''
    
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
    

        def htmlmaplog(self):
            """
            Outputs a HTML map
            """
            self.htmltext = """
            <!DOCTYPE html >
            <style type="text/css">
                        html, body {
                            height: 100%;
                            width: 100%;
                            padding: 0px;
                            margin: 0px;
                        }
            </style>
            <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
            <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
            <title>Boundary Partitioning</title>
            <xml id="myxml">
            <markers>
            """
            # Content
            for coord in self.coordset:
                rowcord = '<marker name = "' + COMPANY_SEARCH + '" lat = "' + \
                        '%.5f' % coord[0] + '" lng = "' + '%.5f' % coord[1] + '"/>\n'
                self.htmltext += rowcord
            # Bottom
            self.htmltext += """
            </markers>
            </xml>
            <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAf-6tsTGCPib1xkDgVkTcZp_G6uSMHBCg&sensor=false&libraries=geometry"></script>
            <script type="text/javascript">
            var XML = document.getElementById("myxml");
            if(XML.documentElement == null)
            XML.documentElement = XML.firstChild;
            var MARKERS = XML.getElementsByTagName("marker");
            """
            self.htmltext += "var RADIUS_KM = " + str(RADIUS_KM) + ";"
            self.htmltext += """
            var map;
            var geocoder = new google.maps.Geocoder();
            var counter = 0
            function load() {
                // Initialize around City, London
                var my_lat = 51.518175;
                var my_lng = -0.129064;
                var mapOptions = {
                        center: new google.maps.LatLng(my_lat, my_lng),
                        zoom: 11
                };
                map = new google.maps.Map(document.getElementById('map'),
                    mapOptions);
                var bounds = new google.maps.LatLngBounds();
                for (var i = 0; i < MARKERS.length; i++) {
                    var name = MARKERS[i].getAttribute("name");
                    var point_i = new google.maps.LatLng(
                        parseFloat(MARKERS[i].getAttribute("lat")),
                        parseFloat(MARKERS[i].getAttribute("lng")));
                    var icon = {icon: 'http://labs.google.com/ridefinder/images/mm_20_gray.png'};
                    var col = '#0033CC';
                    var draw_circle = new google.maps.Circle({
                        center: point_i,
                        radius: RADIUS_KM*1000,
                        strokeColor: col,
                        strokeOpacity: 0.15,
                        strokeWeight: 2,
                        fillColor: col,
                        fillOpacity: 0.15,
                        map: map
                    });
                    var marker = new google.maps.Marker({
                        position: point_i,
                        map: map,
                        icon: 'https://maps.gstatic.com/intl/en_us/mapfiles/markers2/measle_blue.png'
                    })
                    bounds.extend(point_i);
                };
                map.fitBounds(bounds);
            }
            </script>
            </head>
            <body onload="load()">
            <center>
            <div style="padding-top: 20px; padding-bottom: 20px;">
            <div id="map" style="width:90%; height:1024px;"></div>
            </center>
            </body>
            </html>
            """
            print(type(self.htmltext), file=sys.stderr) 
            # return self.html

    coord = coordinates_box()
    coord.createcoordinates(southwest_lng, southwest_lat, northeast_lng, northeast_lat)
    coord.htmlmaplog()

    print(coord.htmltext, file=sys.stderr)
    return coord.htmltext


if __name__ == '__main__':
    app.run()