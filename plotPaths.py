#why am I getting so many seg faults??

import numpy as np
import pandas as pd
import cartopy 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib
import os

#also see this for plotting specific city:  
# https://stackoverflow.com/questions/41527234/trying-to-draw-map-of-a-particular-city-with-cartopy

cmap = matplotlib.cm.get_cmap('viridis')

my_dpi = 72
xpix = 1920/4.
ypix = 1080/4.

ohare_lon = -87.8369
ohare_lat = 41.9773

def isFloat(x):
	try:
		float(x)
		return True
	except:
		return False

#trying to make the lines smoother
#https://stackoverflow.com/questions/40270990/cartopy-higher-resolution-for-great-circle-distance-line
class LowerThresholdPlateCarree(ccrs.PlateCarree):
	@property
	def threshold(self):
		return 0.15
	
def drawLineSegment(ax, lon1, lat1, lon2, lat2, dt, llen=20, alpha=0.8, linewidth=5, color=cmap(0.9), ms=20):
	if (dt < llen):
		llen = dt
		dt = 0

		
	#print(dt, llen, ms, lon, lat, ohare_lon, ohare_lat)
	
	x = ax.plot([lon1, lon2], [lat1, lat2],
		color=color, alpha=alpha, transform=ccrs.Geodetic(),
		linewidth=linewidth, dashes=[0, dt, llen, 2000], dash_capstyle='round')
	#print(len(x), x[0].get_path().__dict__)

		
def drawMap(df, t, i, nframes, tfac = 100., llen=20, alpha=0.8, linewidth=5, color1=cmap(0.9), color2=cmap(0.5), ms=20, mstlen=5):

	#create the map projection
	proj = LowerThresholdPlateCarree(central_longitude=ohare_lon)
	#proj = ccrs.Mercator(central_longitude=ohare_lon)
	#proj = ccrs.Mollweide(central_longitude=ohare_lon)
	#proj = ccrs.Robinson(central_longitude=ohare_lon)
	data_crs = LowerThresholdPlateCarree()
	f = plt.figure(figsize=(xpix/my_dpi, ypix/my_dpi), dpi=my_dpi, frameon=False) 
	ax = f.add_axes([0, 0, 1, 1], projection = proj)
	ax.axis('off')
	ax.outline_patch.set_visible(False)
	#ax.set_global()
	shrink = float(i)/float(nframes)*40.
	extent = [-180 + shrink , 180 - shrink, -90 + shrink/2., 90 - shrink/2.]
	#extent = [-180, 180, -90, 90]
	print(shrink, extent)
	ax.set_extent(extent, crs=proj)

	ax.background_patch.set_facecolor('k')

	# #include the map in the background?
	# ax.add_feature(cartopy.feature.LAND, color=cmap(0.4))
	# ax.add_feature(cartopy.feature.OCEAN, facecolor=cmap(0))
	# ax.add_feature(cartopy.feature.LAKES, color=cmap(0))
	# ax.add_feature(cartopy.feature.RIVERS, edgecolor=cmap(0))
	# ax.add_feature(cartopy.feature.COASTLINE, linewidth=1, edgecolor=cmap(0.3))
	# ax.add_feature(cartopy.feature.BORDERS, linewidth=1, edgecolor=cmap(0.3))


	for index, row in df.iterrows():
		c = color2
		if (row['arrival_airport'] == 'KORD'):
			c = color1
		dt = (t - float(row['departure_time']))*tfac
		drawLineSegment(ax, row['departure_longitude'], row['departure_latitude'], 
						row['arrival_longitude'], row['arrival_latitude'], dt,  
						llen=llen, alpha=alpha, linewidth=linewidth, color=c, ms=ms)

	departing = df.loc[((t - df['departure_time'].astype(float))*tfac < mstlen) & (df['arrival_airport'] != 'KORD')]
	departingORD = df.loc[((t - df['departure_time'].astype(float))*tfac < mstlen) & (df['arrival_airport'] == 'KORD')]
	#marker at departure
	if (len(departing) > 0):
		ax.plot(departing['departure_longitude'].values, departing['departure_latitude'].values, 
				color=color2, alpha=alpha, transform=ccrs.Geodetic(),
				marker='o', ms=ms, mfc=color2, mew=0, linewidth=0)
	if (len(departingORD) > 0):
		ax.plot(departingORD['departure_longitude'].values, departingORD['departure_latitude'].values, 
				color=color1, alpha=alpha, transform=ccrs.Geodetic(),
				marker='o', ms=ms, mfc=color1, mew=0, linewidth=0)	

	#https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.get_path
	#want marker at arrival?
#     if (dt < llen):
#         ax.plot([ohare_lon], [ohare_lat], marker='o', ms=ms, mfc=color, mew=0)
#         if (index > 1000):
#             break

	f.savefig('plots/flights_'+str(i).zfill(3)+'.png', format='png', bbox_inches='tight', dpi=my_dpi)
	plt.close()


if __name__ == "__main__":
	#read in all the files
	flights_df = None
	for f in os.listdir('flightData'):
		df = pd.read_csv(os.path.join('flightData',f))
		if (flights_df is None):
			flights_df = df
		else:
			flights_df = pd.concat([flights_df, df])

	#print(flights_df)

	#remove any that didn't get converted correctly
	mask = np.array([isFloat(x) for x in flights_df["departure_time"].values])
	flights_df = flights_df[mask]
	mask = np.array([isFloat(x) for x in flights_df["arrival_time"].values])
	flights_df = flights_df[mask]

	#flights_df = flights_df[0:1000]

	tmin = float(min(flights_df['departure_time'].astype(float).values))
	tmax = float(max(flights_df['arrival_time'].astype(float).values))
	print(tmin, tmax)

	iStart = 0
	nframes = 500
	for i, t in enumerate(np.linspace(tmin, tmax, nframes)):
		if (i >= iStart):
			inTime = flights_df.loc[flights_df["departure_time"].astype(float) <= t]
			print(i, t, len(inTime["departure_time"]))
			drawMap(inTime, t, i, nframes, llen=2000, alpha=0.5, linewidth=1, ms=5, mstlen=20)


	print('done.')

#ffmpeg -r 30  -i plots/test_flights_%03d.png -c:v mpeg4 -q:v 1  flightPaths.mp4

# git filter-branch --force --index-filter \
#   "git rm --cached --ignore-unmatch flightPaths.mp4" \
#   --prune-empty --tag-name-filter cat -- --all