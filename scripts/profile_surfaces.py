"""Bounded cubic fuselage construction, without document or GUI operations.

Each longitudinal interval must be a cubic (or lower degree) branch of
``profile_value(index, x)``. Supply the original Hermite key stations and every
additional branch boundary. A cubic is reconstructed exactly from four samples,
so this does not introduce the overshoot of a global interpolating CAD loft.

The eight sided section deliberately keeps planar/faceted crosswise chines;
longitudinal curvature is smooth wherever the supplied profile is C1.
"""

import FreeCAD as App
import Part


def _vertices(x, profile_value, wall):
    w = float(profile_value(1, x)) - wall
    bot = float(profile_value(2, x)) + wall
    top = float(profile_value(3, x)) - wall
    if w <= 0 or top <= bot:
        raise ValueError("Nonpositive section at x=%s, wall=%s" % (x, wall))
    mid, ht = (bot + top) / 2.0, top - bot
    yz = [(-w, mid + .25 * ht), (-.75 * w, top),
          (.75 * w, top), (w, mid + .25 * ht),
          (w, mid - .3 * ht), (.92 * w, bot),
          (-.92 * w, bot), (-w, mid - .3 * ht)]
    return [App.Vector(float(x), y, z) for y, z in yz]


def _bezier_poles(samples):
    """Cubic Bezier poles from f(0), f(1/3), f(2/3), f(1)."""
    p0, q1, q2, p3 = samples
    p1 = q1 * 3.0 - q2 * 1.5 - p0 * (5.0 / 6.0) + p3 / 3.0
    p2 = q2 * 3.0 - q1 * 1.5 + p0 / 3.0 - p3 * (5.0 / 6.0)
    return [p0, p1, p2, p3]


def build_profile_solid(key_stations, profile_value, wall=0.0,
                        cap_inset=0.0, breakpoints=(), validate=True):
    """Return a closed Part solid bounded by exact local cubic section rails.

    ``key_stations``: original profile rows (x, width, bottom, top), not the
    samples of a globally fitted curve. Their x values delimit cubic branches.
    ``profile_value``: callable accepting field index 1, 2 or 3 and x.
    ``wall``: section-coordinate inset. This preserves the previous shell's
    convention; it is not an exact surface-normal offset thickness.
    ``cap_inset``: shorten both ends by this amount before building the solid.
    ``breakpoints``: extra x values at which an overridden profile branch ends.

    R4 example:
        outer = build_profile_solid(key_stations, profile_value,
                                    breakpoints=(35, 58))
        inner = build_profile_solid(key_stations, profile_value, wall=1.0,
                                    cap_inset=1.2, breakpoints=(35, 58))
    """
    keys = sorted({float(row[0]) for row in key_stations})
    if len(keys) < 2 or wall < 0 or cap_inset < 0:
        raise ValueError("Invalid stations, wall, or cap inset")
    x0, x1 = keys[0] + cap_inset, keys[-1] - cap_inset
    if x1 <= x0:
        raise ValueError("End cap inset consumes the complete shape")
    cuts = sorted({x0, x1} | {x for x in keys if x0 < x < x1}
                  | {float(x) for x in breakpoints if x0 < float(x) < x1})
    # Assemble every local Bezier span into one longitudinal B-spline per chine
    # rail. Interior multiplicity three preserves each original cubic exactly;
    # coincident tangent directions still give geometric smoothness where the
    # input profile is C1. This yields only eight lateral faces for downstream
    # booleans instead of eight faces per key interval.
    all_rails = [[] for _ in range(8)]
    for a, b in zip(cuts, cuts[1:]):
        h = b - a
        samples = [_vertices(a + h * t, profile_value, wall)
                   for t in (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0)]
        rails = [_bezier_poles([row[k] for row in samples]) for k in range(8)]
        for k in range(8):
            all_rails[k].extend(rails[k][1:] if all_rails[k] else rails[k])

    faces = []
    u_mults = [4] + [3] * (len(cuts) - 2) + [4]
    for k in range(8):
        nxt = (k + 1) % 8
        poles = [[a, b] for a, b in zip(all_rails[k], all_rails[nxt])]
        surface = Part.BSplineSurface()
        surface.buildFromPolesMultsKnots(
            poles, u_mults, [2, 2], cuts, [0.0, 1.0],
            False, False, 3, 1)
        faces.append(surface.toShape())

    first = _vertices(x0, profile_value, wall)
    last = _vertices(x1, profile_value, wall)
    # This yz ordering has a -X face normal; reverse the positive-X end cap.
    faces.append(Part.Face(Part.makePolygon(first + [first[0]])))
    cap = Part.Face(Part.makePolygon(last + [last[0]]))
    cap.reverse()
    faces.append(cap)
    shell = Part.makeShell(faces)
    shell.sewShape()
    if not shell.isClosed():
        raise RuntimeError("Cubic profile shell did not sew into a closed shell")
    solid = Part.makeSolid(shell)
    if solid.Volume < 0:
        solid.reverse()
    if validate and (solid.isNull() or not solid.isValid()
                     or not solid.isClosed() or len(solid.Solids) != 1
                     or solid.Volume <= 0):
        raise RuntimeError("Cubic profile failed solid validity checks")
    return solid
