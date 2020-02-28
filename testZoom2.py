import matplotlib.pyplot as plt
import numpy as np

x0 = []
x1 = []
y0 = []
y1 = []
y2 = []

nframes = 900
zoomFac = 160

ohare_lon = -87.8369
ohare_lat = 41.9773

def getLatZoom(nframes, zoomFac, zoomi):
	m = -(zoomFac/2.)/nframes
	b = 90
	return m*zoomi + b

for zoomi in range(nframes):

	zoom = float(zoomi)/float(nframes)*zoomFac
	latExtent0 = -90 - (-90 - (-90 + zoomFac/2. + ohare_lat))*zoomi/nframes
	latExtent1 = 90 - (90 - (90 - zoomFac/2. + ohare_lat))*zoomi/nframes
	extent = [-180 + zoom , 180 - zoom, latExtent0, latExtent1]
	x0.append(extent[0])
	x1.append(extent[1])
	y0.append(extent[2])
	y1.append(extent[3])
	y2.append(getLatZoom(nframes, zoomFac, zoomi))

print(np.array(x0) - np.array(x1))
print(np.array(y0) - np.array(y1))

# print(np.diff(x1))
# print(np.diff(y0))
# print(np.diff(y1))
# print(np.diff(y2))

# plt.plot(range(nframes), x0)
# plt.show()

# plt.plot(range(nframes), x1)
# plt.show()

plt.plot(range(nframes), y0)
plt.show()

plt.plot(range(nframes), y1)
plt.show()

plt.plot(range(nframes), y2)
plt.show()