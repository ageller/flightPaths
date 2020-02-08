#why am I getting so many seg faults??

import numpy as np
import pandas as pd
import cartopy 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib

#also see this for plotting specific city:  
# https://stackoverflow.com/questions/41527234/trying-to-draw-map-of-a-particular-city-with-cartopy

cmap = matplotlib.cm.get_cmap('viridis')


mfc = 'yellow' #could make this Adler yellow
mec = '#333333' #could make this the other Adler color
ohare_lon = -87.8369
ohare_lat = 41.9773




#trying to make the lines smoother
#https://stackoverflow.com/questions/40270990/cartopy-higher-resolution-for-great-circle-distance-line
class LowerThresholdPlateCarree(ccrs.PlateCarree):
	@property
	def threshold(self):
		return 0.15
	
def drawLineSegment(ax, lon, lat, dt, llen=20, alpha=0.8, linewidth=5, color=cmap(0.9), ms=20):
	if (dt < llen):
		llen = dt
		dt = 0

		
	#print(dt, llen, ms, lon, lat, ohare_lon, ohare_lat)
	
	x = ax.plot([lon, ohare_lon], [lat, ohare_lat],
		color=color, alpha=alpha, transform=ccrs.Geodetic(),
		linewidth=linewidth, dashes=[0, dt, llen, 2000], dash_capstyle='round')
	#print(len(x), x[0].get_path().__dict__)

		
def drawMap(df, t, i, nframes, tfac = 100., llen=20, alpha=0.8, linewidth=5, color=cmap(0.9), ms=20, mstlen=5):

	#create the map projection
	proj = LowerThresholdPlateCarree(central_longitude=ohare_lon)
	#proj = ccrs.Mercator(central_longitude=ohare_lon)
	#proj = ccrs.Mollweide(central_longitude=ohare_lon)
	#proj = ccrs.Robinson(central_longitude=ohare_lon)
	data_crs = LowerThresholdPlateCarree()
	f = plt.figure(figsize=(20,10), frameon=False) #72 dpi
	ax = f.add_axes([0, 0, 1, 1], projection = proj)
	ax.axis('off')
	ax.outline_patch.set_visible(False)
	#ax.set_global()
	shrink = float(i)/float(nframes)*40.
	extent = [-180 + shrink , 180 - shrink, -90 + shrink/2., 90 - shrink/2.]
	#extent = [-180, 180, -90, 90]
	print(shrink, extent)
	ax.set_extent(extent, crs=proj)

	ax.add_feature(cartopy.feature.LAND, color=cmap(0.4))
	ax.add_feature(cartopy.feature.OCEAN, facecolor=cmap(0))
	ax.add_feature(cartopy.feature.LAKES, color=cmap(0))
	ax.add_feature(cartopy.feature.RIVERS, edgecolor=cmap(0))
	ax.add_feature(cartopy.feature.COASTLINE, linewidth=1, edgecolor=cmap(0.3))
	ax.add_feature(cartopy.feature.BORDERS, linewidth=1, edgecolor=cmap(0.3))


	for index, row in df.iterrows():
		dt = (t - float(row['departure']))*tfac
		drawLineSegment(ax, row['longitude'], row['latitude'], dt,  
						llen=llen, alpha=alpha, linewidth=linewidth, color=color, ms=ms)

	departing = df.loc[(t - df['departure'].astype(float))*tfac < mstlen]
	#marker at departure
	if (len(departing) > 0):
		ax.plot(departing['longitude'].values, departing['latitude'].values, 
				color=color, alpha=alpha, transform=ccrs.Geodetic(),
				marker='o', ms=ms, mfc=color, mew=0, linewidth=0)
		
	#https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.get_path
	#want marker at arrival?
#     if (dt < llen):
#         ax.plot([ohare_lon], [ohare_lat], marker='o', ms=ms, mfc=color, mew=0)
#         if (index > 1000):
#             break

	f.savefig('plots/test_flights_'+str(i).zfill(3)+'.png', format='png', bbox_inches='tight')
	plt.close()


if __name__ == "__main__":
	#read in the file
	flights_df = pd.read_csv('flights.csv')

	#remove any that didn't get converted correctly
	def isFloat(x):
		try:
			float(x)
			return True
		except:
			return False
	mask = np.array([isFloat(x) for x in flights_df["departure"].values])
	flights_df = flights_df[mask]
	mask = np.array([isFloat(x) for x in flights_df["arrival"].values])
	flights_df = flights_df[mask]

	#flights_df = flights_df[0:1000]

	tmin = float(min(flights_df['departure'].astype(float).values))
	tmax = float(max(flights_df['arrival'].astype(float).values))
	print(tmin, tmax)

	iStart = 162
	nframes = 500
	for i, t in enumerate(np.linspace(tmin, tmax, nframes)):
		if (i >= iStart):
			inTime = flights_df.loc[flights_df["departure"].astype(float) <= t]
			print(i, t, len(inTime["departure"]))
			drawMap(inTime, t, i, nframes, llen=2000, alpha=0.1, linewidth=1, ms=15, mstlen=20)


	print('done.')

#ffmpeg -r 30  -i plots/test_flights_%03d.png -c:v mpeg4 -q:v 1  flightPaths.mp4