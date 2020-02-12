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
	parser.add_argument("-x", "--xpix",       type=int, help="number of x pixels [1920]")
	parser.add_argument("-y", "--ypix",       type=int, help="number of y pixels [1080]")
	parser.add_argument("-c", "--cmap",       type=str, help="color map [viridis]")
	parser.add_argument("-p", "--file",       type=str, help="input file [flightData.csv]")   
	parser.add_argument("-i", "--istart",     type=int, help="starting frame [0]")   
	parser.add_argument("-a", "--alpha",      type=float, help="alpha [0.1]")  
	parser.add_argument("-b", "--tfac",       type=float, help="time factor for length of line [500]") 
	parser.add_argument("-l", "--linelen",    type=int, help="default line length [2000]")
	parser.add_argument("-w", "--linewidth",  type=int, help="default line width [2]")	
	parser.add_argument("-g", "--color1",     type=float, help="colormap location of ORD [0.9]")	
	parser.add_argument("-j", "--color2",     type=float, help="colormap location of other airports [0.5]")	
	parser.add_argument("-m", "--ms",        type=int, help="marker size [5]")


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
		args.xpix = 1920
	if (args.ypix is None):
		args.ypix = 1080
	if (args.cmap is None):
		args.cmap = 'viridis'
	if (args.file is None):
		args.file = 'flightData.csv'
	if (args.istart is None):
		args.istart = 0
	if (args.alpha is None):
		args.alpha = 0.1
	if (args.tfac is None):
		args.tfac = 500.
	if (args.linelen is None):
		args.linelen = 1000
	if (args.linewidth is None):
		args.linewidth = 2
	if (args.color1 is None):
		args.color1 = 0.9
	if (args.color2 is None):
		args.color2 = 0.5
	if (args.ms is None):
		args.ms = 5

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

		
def drawMap(df, t, shrinki, nframes, color1, color2, xpix, ypix, dpi, tfac, linelen, alpha, linewidth, ms, fname=None):

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
	shrink = float(shrinki)/float(nframes)*40.
	extent = [-180 + shrink , 180 - shrink, -90 + shrink/2., 90 - shrink/2.]
	#extent = [-180, 180, -90, 90]
	#print(shrink, extent)
	ax.set_extent(extent, crs=proj)

	ax.background_patch.set_facecolor('k')

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
		for index, row in destinationOther.iterrows():
			c = color2
			lw = linewidth
			a = alpha
			llen = (t - float(row['source_departure_time']))*tfac
			drawLineSegment(ax, row['source_longitude'], row['source_latitude'], 
							row['destination_longitude'], row['destination_latitude'], offsetlen=0,  
							linelen=llen, alpha=a, linewidth=lw, color=c, zorder=1)

		ax.plot(destinationOther['source_longitude'].values, destinationOther['source_latitude'].values, 
				color=color2, alpha=alpha, transform=ccrs.Geodetic(),
				marker='o', ms=ms, mfc=color2, mew=0, linewidth=0, zorder=1)

	destinationORD = df.loc[(df['source_departure_time'].astype(float)<= t) & (df['destination_airport'] == 'ORD')]
	if (len(destinationORD) > 0):
		for index, row in destinationORD.iterrows():
			c = color1
			lw = linewidth*ORDlfac
			a = alpha*ORDafac
			llen = (t - float(row['source_departure_time']))*tfac
			drawLineSegment(ax, row['source_longitude'], row['source_latitude'], 
							row['destination_longitude'], row['destination_latitude'], offsetlen=0,  
							linelen=llen, alpha=a, linewidth=lw, color=c, zorder=2)

		ax.plot(destinationORD['source_longitude'].values, destinationORD['source_latitude'].values, 
				color=color1, alpha=ORDafac*alpha, transform=ccrs.Geodetic(),
				marker='o', ms=ORDmfac*ms, mfc=color1, mew=0, linewidth=0, zorder=2)	

	#https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.get_path
	#want marker at destination?


	if (fname is None):
		fname = 'plots/flights_'+str(i).zfill(3)+'.png'
	f.savefig(fname, format='png', bbox_inches='tight', dpi=dpi)
	plt.close()


if __name__ == "__main__":

	args = define_args()

	cmap = matplotlib.cm.get_cmap(args.cmap)
	nframes = args.duration*args.fps

	flights_df = pd.read_csv(args.file)

	#flights_df = flights_df[0:5000]

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
			drawMap(inTime, t, i, nframes, cmap(args.color1), cmap(args.color2), args.xpix, args.ypix, args.dpi, args.tfac, args.linelen, args.alpha, args.linewidth, args.ms)



	print('done.')

#ffmpeg -r 30  -i plots/flights_%03d.png -c:v mpeg4 -q:v 1  flightPaths.mp4

# git filter-branch --force --index-filter \
#   "git rm --cached --ignore-unmatch flightPaths.mp4" \
#   --prune-empty --tag-name-filter cat -- --all

