import cartopy 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

#trying to make the lines smoother
#https://stackoverflow.com/questions/40270990/cartopy-higher-resolution-for-great-circle-distance-line
class LowerThresholdPlateCarree(ccrs.PlateCarree):
	@property
	def threshold(self):
		return 0.15




ohare_lon = -87.8369
ohare_lat = 41.9773

xpix = 1920
ypix = 1080
dpi = 72

zoomi = 900
nframes=900
zoomFac=90


#create the map projection
proj = LowerThresholdPlateCarree(central_longitude=ohare_lon)
#proj = ccrs.Mercator(central_longitude=ohare_lon)
#proj = ccrs.Mollweide(central_longitude=ohare_lon)
#proj = ccrs.Robinson(central_longitude=ohare_lon)
data_crs = LowerThresholdPlateCarree()
f = plt.figure(figsize=(xpix/dpi, ypix/dpi), dpi=dpi, frameon=False) 
ax = f.add_axes([0, 0, 1, 1], projection = proj)
ax.axis('off')
ax.outline_patch.set_visible(False)
#ax.set_global()

zoom = float(zoomi)/float(nframes)*zoomFac
latExtent = -90 - (-90 - (-90 + zoom/2. + ohare_lat))*zoomi/nframes
lonExtent = 90 - (90 - (90 - zoom/2. + ohare_lat))*zoomi/nframes
print(-90 - (-90 - (-90 + zoom/2. + ohare_lat))*zoomi/nframes)
extent = [-180 + zoom , 180 - zoom, latExtent, lonExtent]
#extent = [-180, 180, -90, 90]
print(zoom, extent)
ax.set_extent(extent, crs=proj)


# #include the map in the background?
ax.add_feature(cartopy.feature.LAND, color='brown')
ax.add_feature(cartopy.feature.OCEAN, facecolor='blue')
ax.add_feature(cartopy.feature.LAKES, color='blue')
ax.add_feature(cartopy.feature.RIVERS, edgecolor='blue')
ax.add_feature(cartopy.feature.COASTLINE, linewidth=1, edgecolor='black')
ax.add_feature(cartopy.feature.BORDERS, linewidth=1, edgecolor='black')

f.savefig('test.png',format='png', bbox_inches='tight', dpi=dpi)