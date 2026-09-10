# Reproduce the prototype checks

The native FreeCAD file is a grouped installation model with named parts and wires. The generator creates Part/PartDesign features from dimensions; the DesignBasis spreadsheet documents parameters and does not drive a live constrained feature history. Purchased parts are installation envelopes; detailed received-hardware interfaces remain provisional.

From this folder, run `python3 scripts/analyze.py`, then `python3 scripts/independent_audit.py` for the mass, thrust, control and structural screens. These use the saved inventory and source tables. Run `python3 scripts/write_report.py` and `python3 scripts/wiring_diagram.py` to regenerate the reports and wiring overview.

Run `scripts/build_freecad.py` inside FreeCAD to rebuild geometry. It closes and recreates the document named Kestrel_Mini_R4, so preserve any manual edits under a different name first. Keep `scripts/profile_surfaces.py` beside it. The original Samson and previous Kestrel revisions are separate files. Shell skin uses a section-coordinate inset, not a guaranteed exact surface-normal thickness.

For isolated read-only geometry checks, use FreeCADCmd with `scripts/check_fixed_clearances.py` and `scripts/check_wire_samples.py`. The latter uses NumPy and records its finite sampling resolution, constructive passage exclusions, canonical source hash and native-file hash. It does not prove continuous motion clearance or flexible wire behavior. The fixed check examines selected component pairs and 22 rotor poses; its method is separate from the wire sampling check.

With the native document open in FreeCAD, `scripts/refresh_exports.py` refreshes inventory, closed-mesh/size checks, STL files, STEP and the saved document. Run the analytical and geometry checks again after any geometry or hardware change. Run the wire check after the final native-file save so its recorded hash matches the delivered file. `scripts/package_release.py` validates the evidence and packages selected artifacts; its name refers to an archive release, not flight qualification.

`OPEN_KESTREL.FCMacro` provides shell visibility and independent ±25° inspection sliders. It hides neutral phase-wire paths while tilted, and returns the pods to neutral when closed. The ±25° geometric display is not a validated flight limit.

## Repository documentation and PDF

After analytical changes, run `python3 scripts/tail_audit.py` and `python3 scripts/build_parts_list.py`. The first performs a limited tail mass/inertia and crosswind sensitivity screen; it does not validate an aerodynamic coefficient or wind envelope.

Install `requirements-docs.txt` into a Python environment and run `python3 scripts/build_pdf.py` to recreate `output/pdf/Kestrel_Mini_R4_Build_Guide.pdf`. The PDF builder needs ReportLab/Pillow; the independent flight audit also requires NumPy. FreeCAD and its OCCT modules are required separately for CAD operations. Render the PDF with Poppler and inspect all pages after any content change; PDF byte hashes vary with build timestamps.

Run `python3 scripts/package_release.py` after the saved CAD and reports agree. It checks existing geometry evidence, refreshes `MANIFEST_SHA256.json` and creates `outputs/Kestrel_Mini_R4_Repository.zip`, including the PDF, parts list and tail assessment. It does not repeat all underlying CAD computations. Historical `outputs/` and temporary PDF renderings are ignored by Git.

Run `python3 scripts/verify_repository.py` for a read-only manifest, native-file, parts/mass and local-link consistency check. Refresh the manifest after intentional modifications. Repository validation does not change `flight_release=false`.
