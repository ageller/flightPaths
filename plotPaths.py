#! /Users/ageller/anaconda3/bin/python

#why am I getting so many seg faults??

import numpy as np
import pandas as pd
import cartopy 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib
import os
import sys

import argparse

#also see this for plotting specific city:  
# https://stackoverflow.com/questions/41527234/trying-to-draw-map-of-a-particular-city-with-cartopy



#to center the plot

ohare_lon = -87.8369
ohare_lat = 41.9773

def define_args():
	parser = argparse.ArgumentParser()

	parser.add_argument("-f", "--fps",        type=int, help="frames per second [30]")
	parser.add_argument("-d", "--duration",   type=int, help="number of seconds [30]")
	parser.add_argument("-r", "--dpi",        type=int, help="dpi resolution [72]")
	parser.add_argument("-x", "--xpix",       type=int, help="number of x pixels [6000]")
	parser.add_argument("-y", "--ypix",       type=int, help="number of y pixels [3375]")
	parser.add_argument("-p", "--file",       type=str, help="input file [flightData.csv]")   
	parser.add_argument("-i", "--istart",     type=int, help="starting frame [0]")   
	parser.add_argument("-a", "--alpha",      type=float, help="alpha [0.1]")  
	parser.add_argument("-t", "--tfac",       type=float, help="time factor for length of line [500]") 
	parser.add_argument("-s", "--zoom",       type=float, help="factor to zoom in during each scene [160]") 
	parser.add_argument("-l", "--linelen",    type=int, help="default line length [2000]")
	parser.add_argument("-w", "--linewidth",  type=int, help="default line width [7]")	
	parser.add_argument("-g", "--colorORD",   type=str, help="hex color for ORD [#F8D136]")	
	parser.add_argument("-j", "--colorOTHER", type=str, help="hex color for other airports [#00FA9A]")	
	parser.add_argument("-b", "--colorBACK",  type=str, help="hex color for background [#000016]")	
	parser.add_argument("-m", "--ms",         type=int, help="marker size [20]")


	#https://docs.python.org/2/howto/argparse.html
	args = parser.parse_args()
	
	#apply the defaults
	if (args.fps is None):
		args.fps = 30
	if (args.duration is None):
		args.duration = 30
	if (args.dpi is None):
		args.dpi = 72
	if (args.xpix is None):
		args.xpix = 6000
	if (args.ypix is None):
		args.ypix = 3375
	if (args.file is None):
		args.file = 'flightData.csv'
	if (args.istart is None):
		args.istart = 0
	if (args.alpha is None):
		args.alpha = 0.1
	if (args.tfac is None):
		args.tfac = 500.
	if (args.zoom is None):
		args.zoom = 160.
	if (args.linelen is None):
		args.linelen = 1000
	if (args.linewidth is None):
		args.linewidth = 7
	if (args.colorORD is None):
		args.colorORD = '#D8D136'
	if (args.colorOTHER is None):
		args.colorOTHER = '#00FA9A'
	if (args.colorBACK is None):
		args.colorBACK = '#000016'
	if (args.ms is None):
		args.ms = 20

	#to print out the options that were selected (probably some way to use this to quickly assign args)
	opts = vars(args)
	options = { k : opts[k] for k in opts if opts[k] is not None }
	print(options)

	return args


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
	
def drawLineSegment(ax, lon1, lat1, lon2, lat2, linelen, offsetlen, alpha, linewidth, color, zorder=1):
		
	#print(lon1, lat1, lon2, lat2, color, alpha)
	
	x = ax.plot([lon1, lon2], [lat1, lat2],
		color=color, alpha=alpha, transform=ccrs.Geodetic(),
		linewidth=linewidth, dashes=[0, offsetlen, linelen, 2000], dash_capstyle='round', zorder=zorder)
	#print(len(x), x[0].get_path().__dict__)

		
def drawMap(df, t, zoomi, nframes, zoomFac, colorORD, colorOTHER, colorBACK, xpix, ypix, dpi, tfac, linelen, alpha, linewidth, ms, fname=None):

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
	extent = [-180 + zoom , 180 - zoom, latExtent, lonExtent]
	#extent = [-180, 180, -90, 90]
	#print(zoom, extent)
	ax.set_extent(extent, crs=proj)

	ax.background_patch.set_facecolor(colorBACK)

	# #include the map in the background?
	# ax.add_feature(cartopy.feature.LAND, color=cmap(0.4))
	# ax.add_feature(cartopy.feature.OCEAN, facecolor=cmap(0))
	# ax.add_feature(cartopy.feature.LAKES, color=cmap(0))
	# ax.add_feature(cartopy.feature.RIVERS, edgecolor=cmap(0))
	# ax.add_feature(cartopy.feature.COASTLINE, linewidth=1, edgecolor=cmap(0.3))
	# ax.add_feature(cartopy.feature.BORDERS, linewidth=1, edgecolor=cmap(0.3))

	ORDafac = 4.
	ORDlfac = 2.
	ORDmfac = 2.

	destinationOther = df.loc[(df['source_departure_time'].astype(float)<= t) & (df['destination_airport'] != 'ORD')]
	if (len(destinationOther) > 0):
		c = colorOTHER
		lw = linewidth
		a = alpha
		m = ms
		for index, row in destinationOther.iterrows():

			llen = (t - float(row['source_departure_time']))*tfac
			drawLineSegment(ax, row['source_longitude'], row['source_latitude'], 
							row['destination_longitude'], row['destination_latitude'], offsetlen=0,  
							linelen=llen, alpha=a, linewidth=lw, color=c, zorder=1)

		ax.plot(destinationOther['source_longitude'].values, destinationOther['source_latitude'].values, 
				color=c, alpha=a, transform=data_crs,#ccrs.Geodetic(),
				marker='o', ms=m, mfc=c, mew=0, linewidth=0, zorder=1)

	destinationORD = df.loc[(df['source_departure_time'].astype(float)<= t) & (df['destination_airport'] == 'ORD')]
	if (len(destinationORD) > 0):
		c = colorORD
		lw = linewidth*ORDlfac
		a = alpha*ORDafac
		m = ms*ORDmfac
		for index, row in destinationORD.iterrows():

			llen = (t - float(row['source_departure_time']))*tfac
			drawLineSegment(ax, row['source_longitude'], row['source_latitude'], 
							row['destination_longitude'], row['destination_latitude'], offsetlen=0,  
							linelen=llen, alpha=a, linewidth=lw, color=c, zorder=2)

		ax.plot(destinationORD['source_longitude'].values, destinationORD['source_latitude'].values, 
				color=c, alpha=a, transform=data_crs,#ccrs.Geodetic(),
				marker='o', ms=m, mfc=c, mew=0, linewidth=0, zorder=2)	

	#https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.get_path
	#want marker at destination?


	if (fname is None):
		fname = 'plots/flights_'+str(i).zfill(3)+'.png'
	f.savefig(fname, format='png', bbox_inches='tight', dpi=dpi)
	plt.close()


if __name__ == "__main__":

	args = define_args()

	nframes = args.duration*args.fps

	flights_df = pd.read_csv(args.file)

	#flights_df = flights_df[0:1000]

	tmin = float(min(flights_df['source_departure_time'].astype(float).values))
	tmax = float(max(flights_df['source_departure_time'].astype(float).values))
	print(tmin, tmax)

	# drawMap(flights_df, tmax, 0, 1, cmap(args.color1), cmap(args.color2), args.xpix, args.ypix, args.dpi, args.tfac, args.linelen, args.alpha, args.linewidth, args.ms, fname='testPlot.png')

	for i, t in enumerate(np.linspace(tmin, tmax, nframes)):
		if (i >= args.istart):
			inTime = flights_df.loc[flights_df["source_departure_time"].astype(float) <= t]
			print("plotting", i, t, len(inTime["source_departure_time"]))
			try:
				sys.stdout.flush()
			except:
				print("can't flush stdout")
			drawMap(inTime, t, i, nframes, args.zoom, args.colorORD, args.colorOTHER, args.colorBACK, args.xpix, args.ypix, args.dpi, args.tfac, args.linelen, args.alpha, args.linewidth, args.ms)



	print('done.')

#ffmpeg -r 30  -i plots/flights_%03d.png -c:v mpeg4 -q:v 1  flightPaths.mp4

# git filter-branch --force --index-filter \
#   "git rm --cached --ignore-unmatch flightPaths.mp4" \
#   --prune-empty --tag-name-filter cat -- --all

