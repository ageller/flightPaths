#https://www.gicentre.net/geomap/using
add_library('GeoMap')

#shape files from https://www.naturalearthdata.com/downloads/
geoMap_land = None
geoMap_lakes = None


def setup():
    global geoMap_land, geoMap_lakes
    
    size(1600, 800)  

def readData
    geoMap_land = GeoMap(this) 
    geoMap_land.readFile("../world")  
    #geoMap_land.readFile("../10m_physical/ne_10m_land")  
     
    geoMap_lakes = GeoMap(this) 
    geoMap_lakes.readFile("../10m_physical/ne_10m_lakes")   

    noLoop()                   # Static map so no need to redraw.

def draw():
    global geoMap_land, geoMap_lakes
    
    background(202, 226, 245)  # Ocean color
    fill(206,173,146)          # Land color
    stroke(0,40)               # boundary color
    geoMap_land.draw()              

    fill(202, 226, 245)        # lake color
    stroke(0,40)               # boundary color
    geoMap_lakes.draw()   
    
    
