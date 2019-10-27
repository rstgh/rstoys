
from rstoys.geo import *


alaska = LatLon(61.0231802, -167.7506614)
munich = LatLon(48.133333, 11.566667)
london = LatLon(51.5287718, -0.2416795)
zeland = LatLon(-40.4342861, 166.3346344)

p = WebMercatorProjection()  # default zoom level = 0, so that (x,y) values will be in range [0 ... 256)

print("")

print("Alaska        x=%11.6f y=%11.6f" % p.project(alaska))
print("London        x=%11.6f y=%11.6f" % p.project(london))
print("Munich        x=%11.6f y=%11.6f" % p.project(munich))
print("New Zeland    x=%11.6f y=%11.6f" % p.project(zeland))

print("")

print("Bearing from MUC to LCY airports: %.6f deg" % (p.bearing(48.353889, 11.786111, 51.505278, 0.055278)))
print("Bearing from LCY to MUC airports: %.6f deg" % (p.bearing(51.505278, 0.055278, 48.353889, 11.786111)))
print("")

print("Bearing from MUC to WRO airports: %.6f deg" % (p.bearing(48.353889, 11.786111, 51.109444, 16.880278)))
print("Bearing from WRO to MUC airports: %.6f deg" % (p.bearing(51.109444, 16.880278, 48.353889, 11.786111)))
print("")


be = BearingEstimator(2)

be.add_location(munich)
print("Bearing after 1:munich: " + str(be.get_bearing()))

be.add_location(london)
print("Bearing after 2:london: " + str(be.get_bearing()))

be.add_location(alaska)
print("Bearing after 3:alaska: " + str(be.get_bearing()))