# cube_gen.py
import cadquery as cq
from pathlib import Path

# Fonts folder relative to this file
FONTS_DIR = Path(__file__).parent / "fonts"
DEFAULT_FONT_PATH = FONTS_DIR / "GUNPLAY_.ttf"

def resolve_font(font_path=None):
    """Resolve a usable font path."""
    path = Path(font_path) if font_path else DEFAULT_FONT_PATH
    if not path.exists():
        raise FileNotFoundError(f"Font file not found: {path}")
    return path

def centered_text_solid(plane_name: str, txt: str,
                        size: float, thickness: float,
                        font_path: str = None):
    font_path = resolve_font(font_path)
    wp = cq.Workplane(plane_name)
    t = wp.text(txt, size, thickness,
                halign="center", valign="center",
                fontPath=str(font_path),
                combine=False)

    solid = t.val()
    if solid is None:
        raise RuntimeError(f"Failed to generate solid for '{txt}' using font {font_path}")    
    normal = wp.plane.zDir
    solid = solid.translate((-normal.x * thickness / 2.0,
                             -normal.y * thickness / 2.0,
                             -normal.z * thickness / 2.0))
    return solid

def bbox_extents(*solids):
    mins = [float("inf")] * 3
    maxs = [float("-inf")] * 3
    for s in solids:
        bb = s.BoundingBox()
        mins = [min(mins[i], val) for i, val in enumerate([bb.xmin, bb.ymin, bb.zmin])]
        maxs = [max(maxs[i], val) for i, val in enumerate([bb.xmax, bb.ymax, bb.zmax])]
    return mins, maxs

def build_letter_cube(initials: str,
                      font_path: str = None,
                      font_size: float = 30.0,
                      padding: float = 1.0,
                      bevel_radius: float = 0.5,
                      target_size: float = 30.0):
    """Build a cube with 3 carved initials (XYZ planes)."""
    font_path = resolve_font(font_path)

    # Ensure exactly 3 characters
    letters = (initials + "XXX")[:3]
    A_char, B_char, C_char = letters[0], letters[1], letters[2]

    thin = 1.0
    A_thin = centered_text_solid("XZ", A_char, font_size, thin, font_path)
    B_thin = centered_text_solid("XY", B_char, font_size, thin, font_path)
    C_thin = centered_text_solid("YZ", C_char, font_size, thin, font_path)

    mins, maxs = bbox_extents(A_thin, B_thin, C_thin)
    cube_side = 1.20 * max(maxs[0] - mins[0],
                           maxs[1] - mins[1],
                           maxs[2] - mins[2]) + padding

    cut_len = 1.5 * cube_side
    A_cutter = centered_text_solid("XZ", A_char, font_size, cut_len, font_path)
    B_cutter = centered_text_solid("XY", B_char, font_size, cut_len, font_path)
    C_cutter = centered_text_solid("YZ", C_char, font_size, cut_len, font_path)

    base_cube = cq.Workplane("XY").box(cube_side, cube_side, cube_side, centered=True)
    if bevel_radius and bevel_radius > 0:
        base_cube = base_cube.edges().fillet(bevel_radius)

    cube_ABC = base_cube.cut(A_cutter).cut(B_cutter).cut(C_cutter)
    scale_factor = target_size / cube_side
    return cube_ABC.val().scale(scale_factor)

def export_stl(cube, out_name="cube_ABC.stl"):
    cq.exporters.export(cube, out_name)
    return out_name
