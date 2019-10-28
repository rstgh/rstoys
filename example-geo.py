
from rstoys.geo import LatLon
from rstoys.geo import WebMercatorProjection
from rstoys.geo import BearingEstimator

from rstoys.geo import diff_bearing


alaska = LatLon(61.0231802, -167.7506614)
munich = LatLon(48.133333, 11.566667)
london = LatLon(51.5287718, -0.2416795)
zeland = LatLon(-40.4342861, 166.3346344)

p = WebMercatorProjection(0)  # default zoom level = 0, so that (x,y) values will be in range [0 ... 256)

print("")

print("Alaska        x=%11.6f y=%11.6f" % p.project(alaska))
print("London        x=%11.6f y=%11.6f" % p.project(london))
print("Munich        x=%11.6f y=%11.6f" % p.project(munich))
print("New Zeland    x=%11.6f y=%11.6f" % p.project(zeland))

print("")

muc = LatLon(48.353889, 11.786111)
lcy = LatLon(51.505278, 0.055278)
wro = LatLon(51.109444, 16.880278)

print("Bearing from MUC to LCY airports: %5.1f deg" % (muc.bearing(lcy)))
print("Bearing from LCY to MUC airports: %5.1f deg" % (lcy.bearing(muc)))
print("Bearing from MUC to WRO airports: %5.1f deg" % (muc.bearing(wro)))
print("Bearing from WRO to MUC airports: %5.1f deg" % (wro.bearing(muc)))

print("")

print("Distance MUC-LCY is %.1f meters" % (muc.distance(lcy)))
print("Distance MUC-WRO is %.1f meters" % (muc.distance(wro)))

print("")

be = BearingEstimator(3)

be.add_location(munich)
print("Bearing after 1:munich: " + str(be.get_bearing()))

be.add_location(london)
print("Bearing after 2:london: " + str(be.get_bearing()))

be.add_location(alaska)
print("Bearing after 3:alaska: " + str(be.get_bearing()))

print("")

def test_diff_bearing(b1, b2):
    print("diff_bearing(%8.3f, %8.3f) => %8.3f" % (b1, b2, diff_bearing(b1, b2)))

test_diff_bearing(0, 0)
test_diff_bearing(0, -1)
test_diff_bearing(45, 90)
test_diff_bearing(0, 180)
test_diff_bearing(0, 181)
test_diff_bearing(350, 10)
test_diff_bearing(0, 721)

print("")
