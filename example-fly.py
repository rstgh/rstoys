
from rstoys.geo import LatLon
from rstoys.geo import CourseManager
from rstoys.geo import diff_bearing

muc = LatLon(48.353889, 11.786111)
fra = LatLon(50.033333, 8.570556)
lcy = LatLon(51.505278, 0.055278)

print("Absolute bearing from MUC to LCY airport: %.1f deg" % (muc.bearing(lcy)))

# our target is LCY airport
target = lcy

estimator = CourseManager(2)

# we started in muc airport
estimator.add_location(muc)

# we are now in FRA airport
location = fra

estimator.add_location(location)
current_bearing = estimator.get_bearing()
target_bearing = location.bearing(target)

print("current_bearging : %5.1f" % (current_bearing))
print("target_bearging  : %5.1f" % (target_bearing))

error_bearing = diff_bearing(current_bearing, target_bearing)

print("error_bearing    : %5.1f" % (error_bearing))
