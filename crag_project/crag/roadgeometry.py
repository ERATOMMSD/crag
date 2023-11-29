import math
import random as ra
from shapely import geometry
from . import utils


def frenet_to_cartesian_road_points_with_reframability_check(x0, y0, theta0, ds, kappas, lane_width, map_size):
    """Convert a set of curvatures into a set of points in Cartesian
    coordinates representing the center line of a road.
    Together with the road points extra information about its
    reframability is returned. A road is called reframable if its coordinates
    can be translated to fit it inside a given map size."""
    road_points = [(x0, y0)]
    x = x0
    y = y0
    theta = theta0
    n = len(kappas) + 1
    min_x = x
    min_y = y
    max_x = x
    max_y = y
    for i in range(n):
        x = x + (ds * math.cos(theta))
        y = y + (ds * math.sin(theta))
        road_points.append((x, y))
        if i < n - 1:
            theta = theta + (kappas[i] * ds)

        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y

        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y

    is_reframable = (max_x - min_x <= map_size - 2 * lane_width) and (max_y - min_y <= map_size - 2 * lane_width)
    is_in_map = (max_x < map_size - lane_width) and (min_x > lane_width) and (max_y < map_size - lane_width) and (min_y > lane_width)
    if is_reframable:
        road_points = reframe_road(road_points, min_x, min_y, lane_width)
        is_in_map = True
    return (road_points, is_in_map, is_reframable)


def is_likely_self_intersecting(road_points, lane_width):
    """Verifies two of the self-intersection checks discussed in
    Castellano, Klikovits, Cetinkaya, Arcaini,
    'FreneticV at the SBST 2022 tool competition',
    SBST '22: Proceedings of the 15th Workshop on Search-Based
    Software Testing, pp. 47-48, 2022"""
    center_line = geometry.LineString(road_points)

    left_line = center_line.parallel_offset(lane_width, "left")
    right_line = center_line.parallel_offset(lane_width, "right")

    drop_road_checks = {'center_complex': not center_line.is_simple,
                        'left_int_right': left_line.intersects(right_line)}

    return any(drop_road_checks.values())


def reframe_road(road_points, min_x, min_y, lane_width):
    """Road reframing based on the idea from
    Castellano, Cetinkaya, Ho Thanh, Klikovits, Zhang, Arcaini,
    'Frenetic at the SBST 2021 Tool Competition',
    SBST '21: Proceedings of the 14th Workshop on Search-Based
    Software Testing, pp. 36-37, 2021"""
    return [(x - min_x + lane_width, y - min_y + lane_width) for (x, y) in road_points]


def generate_road_with_reframability_check(lengths_indices, kappas_indices, param_value_count,
                                           min_segment_count, max_segment_count,
                                           global_curvature_bound, ds, lane_width, map_size):
    """Generate a random road using indices identifying parameter values."""
    x0 = 0
    y0 = 0
    theta0 = ra.uniform(0, 2 * math.pi)
    segment_counts = [int(utils.divide_and_sample(min_segment_count, max_segment_count + 1, param_value_count, i)) for i in lengths_indices]
    kappas = []
    for i in range(len(segment_counts)):
        segment_count = segment_counts[i]
        kappa = utils.divide_and_sample(-global_curvature_bound, global_curvature_bound,
                                        param_value_count, kappas_indices[i])
        kappas += [kappa for j in range(segment_count)]
    return frenet_to_cartesian_road_points_with_reframability_check(x0, y0, theta0, ds, kappas, lane_width, map_size)
