"""Read-only, approximate wire/printed-solid clearance screen for FreeCADCmd.

No BRep boolean intersection or point-in-BRep classification is used. Circular
wire sections are sampled against tessellated solids by triangle ray parity.
Absence of sampled overlap is not proof of continuous clearance or flex motion.
"""
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import time
import traceback

import FreeCAD as App
import Part
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'engineering/wire_sampling_check.json'
STEP = .5
DEFLECTION = .05
ANGLES = 16
CELL = 2.0
START = time.time()
REPORT = {'complete': False, 'method': 'Dense circular-section point samples versus triangle-mesh ray parity',
          'continuous_exact_proof': False, 'flight_release': False,
          'nominal_centerline_step_mm': STEP, 'mesh_linear_deflection_mm': DEFLECTION,
          'angles_per_ring': ANGLES, 'radial_fractions': [0, .5, 1],
          'ray_directions': ['+X', '+Y'],
          'limitations': [
              'Finite spatial samples may miss shallow or small intersections between samples.',
              'Mesh deflection is a meshing request, not a proved global error bound.',
              'Circular sections are perpendicular to reconstructed centerline tangents.',
              'Neutral wire routing only; bend stiffness and moving service-loop sweep are not verified.',
              'Concentric routed passages are constructive exclusions, not independently tested here.',
              'All-wire electronics terminal overlaps are not screened; main-power leads versus nonterminal electronics and power-splice versus shell are screened separately.'],
          'constructive_exclusions': [], 'parts': [], 'routes': [], 'hits': [], 'ambiguous_hits': []}


def save():
    REPORT['elapsed_s'] = round(time.time() - START, 2)
    OUT.write_text(json.dumps(REPORT, indent=2))


def route_definitions():
    """Execute only route expressions and their control loops from canonical CAD."""
    source = (ROOT / 'scripts/build_freecad.py').read_text()
    original = ast.parse(source)
    def prune(nodes):
        result = []
        for n in nodes:
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'route':
                result.append(n)
            elif isinstance(n, ast.For):
                body = prune(n.body)
                if body:
                    assignments = [a for a in n.body if isinstance(a, ast.Assign)
                                   and any(isinstance(t, ast.Name) and t.id == 'tag' for t in a.targets)]
                    result.append(ast.For(target=n.target, iter=n.iter,
                                          body=assignments + body, orelse=[], type_comment=None))
        return result
    routes = {}
    def route(name, points, diam, color, net, awg, src, dst, slack=0):
        routes[name] = {'points': points, 'diameter_mm': diam, 'net': net, 'from': src, 'to': dst}
    reduced = ast.fix_missing_locations(ast.Module(body=prune(original.body), type_ignores=[]))
    exec(compile(reduced, '<route-only AST>', 'exec'), {'route': route})
    expected = {w['name'] for w in json.loads((ROOT / 'engineering/wiring_routes.json').read_text())}
    if set(routes) != expected:
        raise RuntimeError('Reconstructed route set differs: ' + str(set(routes) ^ expected))
    return routes


def wire_samples(definition):
    curve = Part.BSplineCurve()
    curve.interpolate([App.Vector(*p) for p in definition['points']])
    edge = curve.toShape()
    # FreeCAD's Number discretization uses approximately equal arc-length steps.
    centers_v = edge.discretize(Number=max(2, math.ceil(edge.Length / STEP) + 1))
    centers = np.array([[p.x, p.y, p.z] for p in centers_v])
    tangents = []
    for p in centers_v:
        tangent = curve.tangent(curve.parameter(p))[0]
        tangents.append([tangent.x, tangent.y, tangent.z])
    tangents = np.array(tangents)
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]
    refs = np.tile([0., 0., 1.], (len(centers), 1))
    refs[np.abs(tangents[:, 2]) > .9] = [0., 1., 0.]
    n1 = np.cross(tangents, refs)
    n1 /= np.linalg.norm(n1, axis=1)[:, None]
    n2 = np.cross(tangents, n1)
    clouds = [centers]
    radius = definition['diameter_mm'] / 2
    for fraction in (.5, 1):
        for k in range(ANGLES):
            theta = 2 * math.pi * k / ANGLES
            clouds.append(centers + radius * fraction * (math.cos(theta) * n1 + math.sin(theta) * n2))
    return np.concatenate(clouds), {'center_samples': len(centers),
        'total_samples': len(centers) * (2 * ANGLES + 1),
        'reconstructed_length_mm': edge.Length,
        'maximum_adjacent_center_chord_mm': float(np.linalg.norm(np.diff(centers, axis=0), axis=1).max())}


class TriangleSolid:
    def __init__(self, shape):
        vertices, indices = shape.tessellate(DEFLECTION)
        vertices = np.array([[p.x, p.y, p.z] for p in vertices])
        self.tri = vertices[np.array(indices, dtype=int)]
        self.lo, self.hi = vertices.min(axis=0), vertices.max(axis=0)
        self.cache = {}
        self.axes = {}
        for axis in (0, 1):
            plane = [k for k in range(3) if k != axis]
            tri = self.tri[:, :, plane]
            q0, q1, q2 = tri[:, 0], tri[:, 1], tri[:, 2]
            den = (q1[:, 1] - q2[:, 1]) * (q0[:, 0] - q2[:, 0]) + (q2[:, 0] - q1[:, 0]) * (q0[:, 1] - q2[:, 1])
            mask = np.abs(den) > 1e-12
            self.axes[axis] = (plane, tri[mask], self.tri[mask, :, axis], den[mask],
                               tri[mask].min(axis=1), tri[mask].max(axis=1))

    def inside(self, points, axis):
        """Ray parity; projection jitter avoids counting shared triangle edges twice."""
        plane, tri, depths, den, lows, highs = self.axes[axis]
        answer = np.zeros(len(points), dtype=bool)
        projected = points[:, plane] + np.array([1.137e-7, 2.193e-7])
        cells = np.floor(projected / CELL).astype(int)
        unique, inverse = np.unique(cells, axis=0, return_inverse=True)
        for i, cell in enumerate(unique):
            ids = np.flatnonzero(inverse == i)
            key = (axis, int(cell[0]), int(cell[1]))
            candidates = self.cache.get(key)
            if candidates is None:
                low, high = cell * CELL, (cell + 1) * CELL
                candidates = np.flatnonzero(np.all(highs >= low, axis=1) & np.all(lows <= high, axis=1))
                self.cache[key] = candidates
            if not len(candidates):
                continue
            q = tri[candidates]
            d = den[candidates]
            dep = depths[candidates]
            for j in range(0, len(ids), 256):
                row = ids[j:j + 256]
                p = projected[row]
                u = ((q[None, :, 1, 1] - q[None, :, 2, 1]) * (p[:, None, 0] - q[None, :, 2, 0]) +
                     (q[None, :, 2, 0] - q[None, :, 1, 0]) * (p[:, None, 1] - q[None, :, 2, 1])) / d
                v = ((q[None, :, 2, 1] - q[None, :, 0, 1]) * (p[:, None, 0] - q[None, :, 2, 0]) +
                     (q[None, :, 0, 0] - q[None, :, 2, 0]) * (p[:, None, 1] - q[None, :, 2, 1])) / d
                w = 1 - u - v
                ray_depth = u * dep[None, :, 0] + v * dep[None, :, 1] + w * dep[None, :, 2]
                hit = (u >= 0) & (v >= 0) & (w >= 0) & (ray_depth > points[row, axis, None] + 1e-8)
                answer[row] = np.count_nonzero(hit, axis=1) % 2 == 1
        return answer


def exclusions():
    source = (ROOT / 'scripts/build_freecad.py').read_text()
    # Only the canonical declaration/list-building block; stop before any CAD
    # object access or mutation. This follows new constructive passages added by
    # the design owner rather than silently keeping a stale exclusion list.
    block = source[source.index('channel_pairs=[]'):source.index('for wire_name,part_name in channel_pairs:')]
    ns = {}
    exec(block, ns)
    return set(tuple(pair) for pair in ns['channel_pairs'])


def main():
    complete = json.loads((ROOT / 'engineering/headless_completion.json').read_text())
    if not complete.get('complete'):
        raise RuntimeError('Final headless geometry is not complete')
    cad = ROOT / 'cad/Kestrel_Mini_R4.FCStd'
    REPORT['cad_sha256'] = hashlib.sha256(cad.read_bytes()).hexdigest()
    REPORT['canonical_build_sha256'] = hashlib.sha256((ROOT / 'scripts/build_freecad.py').read_bytes()).hexdigest()
    D = App.openDocument(str(cad))
    routes = route_definitions()
    # Sanity check the triangle classifier on a known closed cube.
    cube = TriangleSolid(Part.makeBox(10, 10, 10))
    test = np.array([[5., 5., 5.], [11., 5., 5.], [-1., 5., 5.], [5., 11., 5.]])
    for axis in (0, 1):
        if not np.array_equal(cube.inside(test, axis), [True, False, False, False]):
            raise RuntimeError('Triangle parity classifier sanity check failed')
    # A nested closed shell represents a cavity under the same parity rule.
    cavity = Part.makeBox(8, 8, 8, App.Vector(1, 1, 1))
    hollow = TriangleSolid(Part.makeCompound([Part.makeBox(10, 10, 10).Shells[0], cavity.Shells[0]]))
    for axis in (0, 1):
        if not np.array_equal(hollow.inside(np.array([[5., 5., 5.], [.5, .5, 5.], [11., 5., 5.]]), axis), [False, True, False]):
            raise RuntimeError('Triangle parity cavity sanity check failed')
    REPORT['classifier_sanity_checks'] = 'Solid box and nested-shell cavity pass both ray directions'
    printed = [o for o in D.Objects if hasattr(o, 'Printable') and o.Printable
               and getattr(o, 'Installed', True) and hasattr(o, 'Shape')]
    REPORT['route_count'] = len(routes)
    REPORT['installed_printed_parts'] = len(printed)
    skip = exclusions()
    REPORT['constructive_exclusions'] = [{'wire': w, 'part': p, 'radial_channel_allowance_mm': .6}
                                        for w, p in sorted(skip)]
    save()
    meshes = {}
    for o in printed:
        REPORT['current_step'] = 'Tessellating ' + o.Name
        save()
        meshes[o.Name] = TriangleSolid(o.Shape)
        REPORT['parts'].append({'name': o.Name, 'triangles': len(meshes[o.Name].tri)})
    pair_count = 0
    for name, definition in routes.items():
        REPORT['current_step'] = 'Sampling ' + name
        save()
        points, info = wire_samples(definition)
        existing = D.getObject(name)
        info.update({'wire': name, 'diameter_mm': definition['diameter_mm'],
                     'saved_route_length_mm': float(existing.RouteLength),
                     'length_match': abs(info['reconstructed_length_mm'] - float(existing.RouteLength)) < .001,
                     'sampled_part_pairs': []})
        if not info['length_match']:
            raise RuntimeError('Saved wire differs from canonical route length: ' + name)
        for part_name, mesh in meshes.items():
            if (name, part_name) in skip:
                continue
            mask = np.all(points >= mesh.lo, axis=1) & np.all(points <= mesh.hi, axis=1)
            p = points[mask]
            if not len(p):
                continue
            pair_count += 1
            inside_x = mesh.inside(p, 0)
            inside_y = mesh.inside(p, 1)
            both = inside_x & inside_y
            either_only = inside_x ^ inside_y
            info['sampled_part_pairs'].append({'part': part_name, 'bbox_samples': len(p),
                                               'confirmed_inside_samples': int(both.sum()),
                                               'ray_disagreement_samples': int(either_only.sum())})
            if both.any():
                REPORT['hits'].append({'wire': name, 'part': part_name, 'sample_count': int(both.sum()),
                                       'example_points_mm': p[both][:12].tolist()})
            if either_only.any():
                REPORT['ambiguous_hits'].append({'wire': name, 'part': part_name,
                    'sample_count': int(either_only.sum()), 'example_points_mm': p[either_only][:6].tolist()})
        REPORT['routes'].append(info)
        save()
    # Dense 0.5 mm Cartesian envelope sample for the relocated insulated splice.
    splice = D.Power_splice_insulated.Shape.BoundBox
    axes = [np.linspace(a, b, math.ceil((b-a) / STEP) + 1)
            for a, b in [(splice.XMin, splice.XMax), (splice.YMin, splice.YMax), (splice.ZMin, splice.ZMax)]]
    grid = np.array(np.meshgrid(*axes, indexing='ij')).reshape(3, -1).T
    REPORT['power_splice_shell_check'] = {'sample_count': len(grid), 'hits': [], 'ray_disagreements': []}
    for o in D.Shell.Group:
        if o.Name not in meshes:
            continue
        mesh = meshes[o.Name]
        p = grid[np.all(grid >= mesh.lo, axis=1) & np.all(grid <= mesh.hi, axis=1)]
        if not len(p):
            continue
        a, b = mesh.inside(p, 0), mesh.inside(p, 1)
        if (a & b).any():
            REPORT['power_splice_shell_check']['hits'].append({'part': o.Name, 'sample_count': int((a & b).sum()), 'examples_mm': p[a & b][:12].tolist()})
        if (a ^ b).any():
            REPORT['power_splice_shell_check']['ray_disagreements'].append({'part': o.Name, 'sample_count': int((a ^ b).sum())})
    REPORT['sampled_pair_count'] = pair_count
    REPORT['total_wire_samples'] = sum(w['total_samples'] for w in REPORT['routes'])
    REPORT['main_power_electronics_check'] = {'terminal_exclusions': ['J1_XT60', 'Power_splice_insulated'], 'hits': [], 'ray_disagreements': []}
    for obj in D.Electronics.Group:
        if obj.Name in REPORT['main_power_electronics_check']['terminal_exclusions']:
            continue
        mesh = TriangleSolid(obj.Shape)
        for wire in ['B1_positive', 'B1_negative']:
            points, _ = wire_samples(routes[wire])
            p = points[np.all(points >= mesh.lo, axis=1) & np.all(points <= mesh.hi, axis=1)]
            if not len(p):
                continue
            a, b = mesh.inside(p, 0), mesh.inside(p, 1)
            if (a & b).any():
                REPORT['main_power_electronics_check']['hits'].append({'wire': wire, 'part': obj.Name, 'sample_count': int((a & b).sum()), 'examples_mm': p[a & b][:12].tolist()})
            if (a ^ b).any():
                REPORT['main_power_electronics_check']['ray_disagreements'].append({'wire': wire, 'part': obj.Name, 'sample_count': int((a ^ b).sum())})
    REPORT['complete'] = True
    REPORT['current_step'] = 'Complete'
    REPORT['result'] = 'Sampled overlaps detected' if REPORT['hits'] or REPORT['power_splice_shell_check']['hits'] or REPORT['main_power_electronics_check']['hits'] else 'No sampled overlap detected; approximate screen only'
    save()
    App.closeDocument(D.Name)


try:
    main()
except BaseException:
    REPORT['error'] = traceback.format_exc()
    save()
    print(REPORT['error'])
print(json.dumps({'complete': REPORT['complete'], 'hits': len(REPORT['hits']), 'elapsed_s': REPORT.get('elapsed_s')}))
# This script is deliberately an isolated command-line audit, never a GUI macro.
if not App.GuiUp:
    os._exit(0 if REPORT['complete'] else 1)
