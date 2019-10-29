
from rstoys.geo import LatLon
from rstoys.geo import BearingEstimator
from rstoys.geo import diff_bearing
from rstoys.geo import WayPoints


path = WayPoints()

path.append(LatLon(50.608124, -1.946433))
path.append(LatLon(50.609949, -1.947380))
path.append(LatLon(50.611304, -1.950127))
path.append(LatLon(50.610208, -1.952272))
path.append(LatLon(50.609055, -1.954800))
path.append(LatLon(50.608348, -1.954082))


# assume we start near the beginning of the path
location = LatLon(50.6, -1.9)

estimator = BearingEstimator(5)

while not path.completed():

    estimator.add_location(location)

    target = path.target(location)
    if target is None:
        break

    target_bearing = location.bearing(target)
    course_bearing = estimator.get_bearing()

    if course_bearing:

        error_bearing = diff_bearing(course_bearing, target_bearing)

        print(
            "loc = (%s) | target = (%s) | target_b = %5.1f | course_b = %5.1f | error_b = %5.1f | progress = %3.0f%%"
            % (location, target, target_bearing, course_bearing, error_bearing, path.progress())
        )

    # assume we move a fraction towards the target
    fraction = 0.3
    lat = location.lat * (1-fraction) + target.lat * fraction
    lon = location.lon * (1-fraction) + target.lon * fraction
    location = LatLon(lat, lon)


print("loc = (%s) | progress = %3.0f%%" % (location, path.progress()))
