"""Shared KiCad 10.0+ Electronics Automation Toolkit for ENGINEERING-PORTFOLIO.

Generates UTF-8 (no-BOM) KiCad 10 projects, lockstep symbol/footprint libraries,
on-grid schematics (1.27 mm / 50 mil grid), 2-layer PCBs with filled copper zones,
and drives kicad-cli.exe for ERC, DRC (with --refill-zones & --schematic-parity),
netlist export, Gerber + Excellon drill output, BOM export, 3D STEP/GLB/PNG render,
and engineering validation reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import csv
import json
import math
from pathlib import Path
import re
import subprocess
import uuid
from typing import Dict, List, Optional, Sequence, Set, Tuple


def load_kicad_config(config_path: Optional[Path] = None) -> dict:
    """Load kicad-config.json from the toolkit directory."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent / "kicad-config.json"
    return json.loads(config_path.read_text(encoding="utf-8"))


def write_utf8(path: Path, content: str) -> None:
    """Write text strictly as UTF-8 without BOM and LF line endings for kicad-cli."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def det_uuid(namespace: str, key: str) -> str:
    """Return deterministic UUIDv5 string so repeated builds keep stable IDs."""
    ns = uuid.uuid5(uuid.NAMESPACE_DNS, f"jagjyot2.engineering.{namespace}")
    return str(uuid.uuid5(ns, key))


def grid_mm(steps_127: int) -> float:
    """Convert integer steps of 1.27 mm (50 mil) into rounded millimeter coordinates."""
    return round(steps_127 * 1.27, 2)


def snap_254(val: float) -> float:
    """Snap millimeter coordinate to 2.54 mm grid."""
    return round(round(val / 2.54) * 2.54, 2)


def run_cli(args: Sequence[str], config: Optional[dict] = None, check: bool = False) -> subprocess.CompletedProcess:
    """Invoke kicad-cli.exe with given arguments."""
    cfg = config or load_kicad_config()
    cli_exe = cfg["kicad"]["executables"]["kicad_cli"]
    proc = subprocess.run(
        [cli_exe, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"kicad-cli failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return proc


# ---------------------------------------------------------------------------
# Project Files (.kicad_pro, sym-lib-table, fp-lib-table)
# ---------------------------------------------------------------------------


def build_kicad_pro(project_name: str, design_rules: Optional[dict] = None) -> str:
    """Build KiCad 10 .kicad_pro JSON with aerospace/drone net classes and rules."""
    rules = design_rules or load_kicad_config()["design_rules"]
    pro = {
        "board": {
            "design_settings": {
                "defaults": {
                    "board_outline_line_width": 0.15,
                    "copper_line_width": rules.get("signal_width_mm", 0.25),
                    "copper_text_size_h": 1.2,
                    "copper_text_size_v": 1.2,
                    "copper_text_thickness": 0.2,
                    "silk_line_width": 0.12,
                    "silk_text_size_h": 0.9,
                    "silk_text_size_v": 0.9,
                    "silk_text_thickness": 0.15,
                },
                "diff_pair_dimensions": [],
                "drc_exclusions": [],
                "rules": {
                    "min_clearance": rules.get("min_clearance_mm", 0.2),
                    "min_copper_edge_clearance": rules.get("board_edge_clearance_mm", 0.5),
                    "min_hole_clearance": 0.25,
                    "min_silk_clearance": 0.1,
                    "min_track_width": rules.get("min_track_width_mm", 0.2),
                    "min_via_annular_width": 0.125,
                    "min_via_diameter": rules.get("min_via_diameter_mm", 0.6),
                    "min_through_hole_diameter": 0.3,
                },
                "track_widths": [0.0, 0.25, 0.5, 1.0, 2.0, 3.0],
                "via_dimensions": [
                    {"diameter": 0.0, "drill": 0.0},
                    {"diameter": 0.7, "drill": 0.35},
                    {"diameter": 0.8, "drill": 0.4},
                ],
            }
        },
        "boards": [],
        "libraries": {
            "pinned_footprint_libs": [],
            "pinned_symbol_libs": [],
        },
        "meta": {"filename": f"{project_name}.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12,
                    "clearance": 0.2,
                    "diff_pair_gap": 0.25,
                    "diff_pair_track_width": 0.2,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Default",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.25,
                    "via_diameter": 0.7,
                    "via_drill": 0.35,
                    "wire_width": 6,
                },
                {
                    "bus_width": 12,
                    "clearance": 0.25,
                    "diff_pair_gap": 0.25,
                    "diff_pair_track_width": 0.25,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Power_Logic",
                    "pcb_color": "rgba(255, 165, 0, 0.500)",
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.5,
                    "via_diameter": 0.8,
                    "via_drill": 0.4,
                    "wire_width": 6,
                },
                {
                    "bus_width": 12,
                    "clearance": 0.3,
                    "diff_pair_gap": 0.25,
                    "diff_pair_track_width": 0.25,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Power_HighCurrent",
                    "pcb_color": "rgba(220, 40, 40, 0.600)",
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 2.0,
                    "via_diameter": 1.0,
                    "via_drill": 0.5,
                    "wire_width": 6,
                },
                {
                    "bus_width": 12,
                    "clearance": 0.2,
                    "diff_pair_gap": 0.2,
                    "diff_pair_track_width": 0.25,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "HighSpeed_Bus",
                    "pcb_color": "rgba(60, 180, 255, 0.500)",
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.25,
                    "via_diameter": 0.7,
                    "via_drill": 0.35,
                    "wire_width": 6,
                },
            ],
            "meta": {"version": 2},
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "sheets": [],
        "text_variables": {},
    }
    return json.dumps(pro, indent=2) + "\n"


def write_project_lib_tables(project_dir: Path, lib_name: str) -> None:
    """Write project-local sym-lib-table and fp-lib-table referencing ${KIPRJMOD}."""
    sym_table = (
        "(sym_lib_table\n"
        "  (version 7)\n"
        f'  (lib (name "{lib_name}")(type "KiCad")(uri "${{KIPRJMOD}}/symbols/{lib_name}.kicad_sym")(options "")(descr "{lib_name} project symbols"))\n'
        ")\n"
    )
    fp_table = (
        "(fp_lib_table\n"
        "  (version 7)\n"
        f'  (lib (name "{lib_name}")(type "KiCad")(uri "${{KIPRJMOD}}/footprints/{lib_name}.pretty")(options "")(descr "{lib_name} project footprints"))\n'
        ")\n"
    )
    write_utf8(project_dir / "sym-lib-table", sym_table)
    write_utf8(project_dir / "fp-lib-table", fp_table)


# ---------------------------------------------------------------------------
# Schematic Builder (1.27 mm / 50 mil Exact Grid + Lockstep .kicad_sym)
# ---------------------------------------------------------------------------


@dataclass
class SchPin:
    number: str
    name: str
    net: str
    side: str = "left"  # "left" or "right"
    etype: str = "bidirectional"  # passive, bidirectional, power_in, power_out, input, output, no_connect


@dataclass
class SchComponent:
    ref: str
    value: str
    footprint: str  # e.g., "ProjectLib:FP_Name"
    pins: List[SchPin]
    mpn: str = ""
    manufacturer: str = ""
    description: str = ""
    rating: str = ""
    origin: str = ""
    sym_name: Optional[str] = None
    in_bom: bool = True
    on_board: bool = True
    sx: float = 0.0
    sy: float = 0.0
    uuid_str: str = ""


class SchematicBuilder:
    """Generates on-grid KiCad 10 .kicad_sch and matching project .kicad_sym."""

    def __init__(
        self,
        project_name: str,
        lib_name: str,
        title: str,
        company: str = "Jagjyot Engineering Portfolio",
        rev: str = "1.0",
        date: str = "2026-11-18",
        paper: str = "A2",
    ) -> None:
        self.project_name = project_name
        self.lib_name = lib_name
        self.title = title
        self.company = company
        self.rev = rev
        self.date = date
        self.paper = paper
        self.components: List[SchComponent] = []
        self.notes: List[Tuple[float, float, str]] = []
        self.root_uuid = det_uuid(project_name, "root_schematic")

    def add_component(self, comp: SchComponent) -> None:
        if not comp.sym_name:
            # Distinct symbol definition per pin signature so multi-variant components match cleanly
            safe_val = re.sub(r"[^A-Za-z0-9_]+", "_", comp.value).strip("_")
            comp.sym_name = f"SYM_{comp.ref}_{safe_val}"
        comp.uuid_str = det_uuid(self.project_name, f"sch_sym_{comp.ref}")
        self.components.append(comp)

    def add_note(self, x: float, y: float, text: str) -> None:
        self.notes.append((snap_254(x), snap_254(y), text))

    def _compute_symbol_geometry(self, comp: SchComponent) -> Tuple[float, float, List[Tuple[SchPin, float, float, int]]]:
        """Compute box half-width, half-height (multiples of 2.54 mm) and pin positions (Y-up)."""
        left_pins = [p for p in comp.pins if p.side == "left"]
        right_pins = [p for p in comp.pins if p.side != "left"]
        rows = max(len(left_pins), len(right_pins), 1)
        pin_pitch = 2.54
        box_hw = 10.16  # 4 * 2.54 mm
        pin_len = 2.54
        pin_x_left = -(box_hw + pin_len)   # -12.70 mm
        pin_x_right = +(box_hw + pin_len)  # +12.70 mm
        box_hh = round(((rows - 1) * pin_pitch) / 2.0 + 2.54, 2)
        # Ensure box_hh is multiple of 1.27 mm so top/bottom text aligns nicely
        top_y = round(((rows - 1) * pin_pitch) / 2.0, 2)
        # Snap top_y to multiple of 1.27 mm
        top_y = round(round(top_y / 1.27) * 1.27, 2)

        mapped: List[Tuple[SchPin, float, float, int]] = []
        for idx, p in enumerate(left_pins):
            py = round(top_y - idx * pin_pitch, 2)
            mapped.append((p, pin_x_left, py, 0))
        for idx, p in enumerate(right_pins):
            py = round(top_y - idx * pin_pitch, 2)
            mapped.append((p, pin_x_right, py, 180))
        return box_hw, box_hh, mapped

    def _format_symbol_def(self, comp: SchComponent, qualified: bool) -> str:
        """Render KiCad 10 symbol S-expression (for .kicad_sym or embedded lib_symbols)."""
        assert comp.sym_name is not None
        sym_id = f"{self.lib_name}:{comp.sym_name}" if qualified else comp.sym_name
        box_hw, box_hh, mapped = self._compute_symbol_geometry(comp)
        ref_prefix = re.match(r"^[A-Za-z_]+", comp.ref).group(0) if comp.ref else "U"
        in_bom = "yes" if comp.in_bom else "no"
        on_board = "yes" if comp.on_board else "no"

        lines = [
            f'    (symbol "{sym_id}"',
            f"      (pin_names (offset 1.016))",
            f"      (exclude_from_sim no)",
            f"      (in_bom {in_bom})",
            f"      (on_board {on_board})",
            f"      (in_pos_files {on_board})",
            f"      (duplicate_pin_numbers_are_jumpers no)",
            f'      (property "Reference" "{ref_prefix}" (at 0 {round(box_hh + 1.27, 2)} 0) (effects (font (size 1.27 1.27))))',
            f'      (property "Value" "{comp.value}" (at 0 {round(-(box_hh + 1.27), 2)} 0) (effects (font (size 1.27 1.27))))',
            f'      (property "Footprint" "{comp.footprint}" (at 0 0 0) (effects (font (size 1.0 1.0)) hide))',
            f'      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.0 1.0)) hide))',
            f'      (property "Description" "{comp.description.replace(chr(34), "")}" (at 0 0 0) (effects (font (size 1.0 1.0)) hide))',
            f'      (symbol "{comp.sym_name}_0_1"',
            f'        (rectangle (start -{box_hw} -{box_hh}) (end {box_hw} {box_hh}) (stroke (width 0.254) (type default)) (fill (type background)))',
            f"      )",
            f'      (symbol "{comp.sym_name}_1_1"',
        ]
        for pin, px, py, angle in mapped:
            pname = pin.name.replace('"', "")
            pnum = pin.number.replace('"', "")
            lines.append(
                f'        (pin {pin.etype} line (at {px} {py} {angle}) (length 2.54) '
                f'(name "{pname}" (effects (font (size 0.9 0.9)))) '
                f'(number "{pnum}" (effects (font (size 0.9 0.9)))))'
            )
        lines.append("      )")
        lines.append("    )")
        return "\n".join(lines)

    def _layout_components(self) -> None:
        """Assign non-overlapping 2.54 mm grid positions across an A2/A1 sheet."""
        cols = 4
        col_spacing = 81.28  # 64 * 1.27 mm (ample room for labels & wires)
        start_x = 55.88      # 44 * 1.27 mm
        cur_y = 45.72        # 36 * 1.27 mm

        row_comps: List[SchComponent] = []
        for comp in self.components:
            row_comps.append(comp)
            if len(row_comps) == cols:
                self._place_row(row_comps, start_x, col_spacing, cur_y)
                max_hh = max(self._compute_symbol_geometry(c)[1] for c in row_comps)
                cur_y = snap_254(cur_y + 2 * max_hh + 17.78)
                row_comps = []
        if row_comps:
            self._place_row(row_comps, start_x, col_spacing, cur_y)

    def _place_row(self, row_comps: List[SchComponent], start_x: float, col_spacing: float, cy: float) -> None:
        max_hh = max(self._compute_symbol_geometry(c)[1] for c in row_comps)
        center_y = snap_254(cy + max_hh)
        for idx, c in enumerate(row_comps):
            c.sx = round(start_x + idx * col_spacing, 2)
            c.sy = center_y

    def write(self, project_dir: Path) -> Tuple[Path, Path]:
        """Write .kicad_sch and symbols/<lib_name>.kicad_sym in exact lockstep."""
        self._layout_components()

        # 1. Write project symbol library
        sym_lib_lines = [
            "(kicad_symbol_lib",
            "  (version 20251024)",
            '  (generator "kicad_symbol_editor")',
            '  (generator_version "10.0")',
        ]
        for comp in self.components:
            sym_lib_lines.append(self._format_symbol_def(comp, qualified=False))
        sym_lib_lines.append(")")
        sym_lib_path = project_dir / "symbols" / f"{self.lib_name}.kicad_sym"
        write_utf8(sym_lib_path, "\n".join(sym_lib_lines) + "\n")

        # 2. Build schematic file
        sch_lines = [
            "(kicad_sch",
            "  (version 20250114)",
            '  (generator "eeschema")',
            '  (generator_version "10.0")',
            f'  (uuid "{self.root_uuid}")',
            f'  (paper "{self.paper}")',
            "  (title_block",
            f'    (title "{self.title}")',
            f'    (date "{self.date}")',
            f'    (rev "{self.rev}")',
            f'    (company "{self.company}")',
            "  )",
            "  (lib_symbols",
        ]
        for comp in self.components:
            sch_lines.append(self._format_symbol_def(comp, qualified=True))
        sch_lines.append("  )")

        # Notes
        for idx, (nx, ny, text) in enumerate(self.notes):
            safe_txt = text.replace('"', '\\"').replace("\n", "\\n")
            sch_lines.append(
                f'  (text "{safe_txt}" (exclude_from_sim no) (at {nx} {ny} 0) '
                f'(effects (font (size 1.5 1.5)) (justify left)) '
                f'(uuid "{det_uuid(self.project_name, f"note_{idx}")}"))'
            )

        # Component instances + wires + global_labels / no_connects
        for comp in self.components:
            _, box_hh, mapped = self._compute_symbol_geometry(comp)
            in_bom = "yes" if comp.in_bom else "no"
            on_board = "yes" if comp.on_board else "no"
            sch_lines.append(
                f'  (symbol (lib_id "{self.lib_name}:{comp.sym_name}") (at {comp.sx} {comp.sy} 0) (unit 1)'
            )
            sch_lines.append(f"    (exclude_from_sim no) (in_bom {in_bom}) (on_board {on_board}) (dnp no)")
            sch_lines.append(f'    (uuid "{comp.uuid_str}")')
            sch_lines.append(
                f'    (property "Reference" "{comp.ref}" (at {comp.sx} {round(comp.sy - box_hh - 2.54, 2)} 0) '
                f'(effects (font (size 1.27 1.27))))'
            )
            sch_lines.append(
                f'    (property "Value" "{comp.value}" (at {comp.sx} {round(comp.sy + box_hh + 2.54, 2)} 0) '
                f'(effects (font (size 1.27 1.27))))'
            )
            sch_lines.append(
                f'    (property "Footprint" "{comp.footprint}" (at {comp.sx} {comp.sy} 0) '
                f'(effects (font (size 1.0 1.0)) hide))'
            )
            if comp.mpn:
                sch_lines.append(
                    f'    (property "MPN" "{comp.mpn}" (at {comp.sx} {comp.sy} 0) '
                    f'(effects (font (size 1.0 1.0)) hide))'
                )
            if comp.manufacturer:
                sch_lines.append(
                    f'    (property "Manufacturer" "{comp.manufacturer}" (at {comp.sx} {comp.sy} 0) '
                    f'(effects (font (size 1.0 1.0)) hide))'
                )
            if comp.rating:
                sch_lines.append(
                    f'    (property "Rating" "{comp.rating}" (at {comp.sx} {comp.sy} 0) '
                    f'(effects (font (size 1.0 1.0)) hide))'
                )
            if comp.origin:
                sch_lines.append(
                    f'    (property "Origin" "{comp.origin}" (at {comp.sx} {comp.sy} 0) '
                    f'(effects (font (size 1.0 1.0)) hide))'
                )
            for pin, _, _, _ in mapped:
                sch_lines.append(
                    f'    (pin "{pin.number}" (uuid "{det_uuid(self.project_name, f"pin_{comp.ref}_{pin.number}")}"))'
                )
            sch_lines.append("    (instances")
            sch_lines.append(f'      (project "{self.project_name}"')
            sch_lines.append(f'        (path "/{self.root_uuid}" (reference "{comp.ref}") (unit 1))')
            sch_lines.append("      )")
            sch_lines.append("    )")
            sch_lines.append("  )")

            # Connect each pin on exact 1.27 mm grid (schematic Y-down -> sheet_y = sy - py)
            for pin, px, py, _ in mapped:
                sx_pin = round(comp.sx + px, 2)
                sy_pin = round(comp.sy - py, 2)
                if not pin.net or pin.net.upper().startswith("NC") or pin.etype == "no_connect":
                    sch_lines.append(
                        f'  (no_connect (at {sx_pin} {sy_pin}) (uuid "{det_uuid(self.project_name, f"nc_{comp.ref}_{pin.number}")}"))'
                    )
                    continue
                stub = -5.08 if pin.side == "left" else 5.08
                lbl_angle = 180 if pin.side == "left" else 0
                end_x = round(sx_pin + stub, 2)
                sch_lines.append(
                    f'  (wire (pts (xy {sx_pin} {sy_pin}) (xy {end_x} {sy_pin})) '
                    f'(stroke (width 0) (type default)) '
                    f'(uuid "{det_uuid(self.project_name, f"w_{comp.ref}_{pin.number}")}"))'
                )
                sch_lines.append(
                    f'  (global_label "{pin.net}" (shape bidirectional) (at {end_x} {sy_pin} {lbl_angle}) '
                    f'(fields_autoplaced yes) (effects (font (size 0.9 0.9))) '
                    f'(uuid "{det_uuid(self.project_name, f"gl_{comp.ref}_{pin.number}")}"))'
                )

        sch_lines.extend([
            "  (sheet_instances",
            '    (path "/" (page "1"))',
            "  )",
            "  (embedded_fonts no)",
            ")",
        ])

        sch_path = project_dir / f"{self.project_name}.kicad_sch"
        write_utf8(sch_path, "\n".join(sch_lines) + "\n")
        return sch_path, sym_lib_path


# ---------------------------------------------------------------------------
# PCB Footprint & Layout Builder (Canonical KiCad 10 + Lockstep .kicad_mod)
# ---------------------------------------------------------------------------


@dataclass
class PadDef:
    number: str
    pad_type: str      # "smd" or "thru_hole" or "np_thru_hole"
    shape: str         # "rect", "roundrect", "circle", "oval"
    x: float
    y: float
    w: float
    h: float
    drill: float = 0.0
    layers: Tuple[str, ...] = ("F.Cu", "F.Mask", "F.Paste")


@dataclass
class FootprintDef:
    name: str
    attr: str          # "smd" or "through_hole"
    pads: List[PadDef]
    body_w: float
    body_h: float
    model_rel_path: Optional[str] = None  # relative to KICAD10_3DMODEL_DIR


@dataclass
class PcbComponent:
    ref: str
    value: str
    fp_def: FootprintDef
    x: float
    y: float
    angle: float = 0.0
    pad_nets: Dict[str, str] = field(default_factory=dict)
    sch_uuid: str = ""
    extra_fields: Dict[str, str] = field(default_factory=dict)


class PCBBuilder:
    """Builds KiCad 10 .kicad_pcb and matching footprints/<lib>.pretty/*.kicad_mod."""

    def __init__(
        self,
        project_name: str,
        lib_name: str,
        width_mm: float,
        height_mm: float,
        silk_banner: str = "",
        root_sch_uuid: str = "",
    ) -> None:
        self.project_name = project_name
        self.lib_name = lib_name
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.silk_banner = silk_banner or f"{project_name.upper()} v1.0"
        self.root_sch_uuid = root_sch_uuid or det_uuid(project_name, "root_schematic")
        self.components: List[PcbComponent] = []
        self.tracks: List[Tuple[str, float, List[Tuple[float, float]], str]] = []  # (net, width, pts, layer)
        self.vias: List[Tuple[str, float, float, float, float]] = []              # (net, x, y, size, drill)
        self.net_list: List[str] = [""]
        self.net_ids: Dict[str, int] = {"": 0}

    def register_net(self, net_name: str) -> int:
        if not net_name:
            return 0
        if net_name not in self.net_ids:
            idx = len(self.net_list)
            self.net_list.append(net_name)
            self.net_ids[net_name] = idx
        return self.net_ids[net_name]

    def add_component(self, comp: PcbComponent) -> None:
        if not comp.sch_uuid:
            comp.sch_uuid = det_uuid(self.project_name, f"sch_sym_{comp.ref}")
        for pad in comp.fp_def.pads:
            net = comp.pad_nets.get(pad.number, "")
            self.register_net(net)
        self.components.append(comp)

    def add_track(self, net_name: str, width: float, pts: List[Tuple[float, float]], layer: str = "F.Cu") -> None:
        self.register_net(net_name)
        self.tracks.append((net_name, width, pts, layer))

    def add_via(self, net_name: str, x: float, y: float, size: float = 0.7, drill: float = 0.35) -> None:
        self.register_net(net_name)
        self.vias.append((net_name, x, y, size, drill))

    def _calc_ref_y(self, fp: FootprintDef) -> float:
        """Place Reference text safely outside both body and all pad solder-mask apertures."""
        min_y = -fp.body_h / 2.0
        for p in fp.pads:
            min_y = min(min_y, p.y - p.h / 2.0)
        return round(min_y - 1.0, 2)

    def _format_footprint_mod(self, fp: FootprintDef, cfg: dict) -> str:
        """Generate standalone .kicad_mod matching the PCB instance 1:1."""
        ref_y = self._calc_ref_y(fp)
        val_y = round(-ref_y, 2)
        hw = round(fp.body_w / 2.0, 2)
        hh = round(fp.body_h / 2.0, 2)
        cy_hw = round(hw + 0.35, 2)
        cy_hh = round(max(hh + 0.35, abs(ref_y) + 0.55), 2)
        ref_layer = "F.Fab" if fp.name.startswith("MountingHole") else "F.SilkS"

        lines = [
            f'(footprint "{fp.name}"',
            "  (version 20260206)",
            '  (generator "kicad_toolkit")',
            '  (generator_version "10.0")',
            '  (layer "F.Cu")',
            f'  (property "Reference" "REF**" (at 0 {ref_y} 0) (layer "{ref_layer}") (effects (font (size 0.8 0.8) (thickness 0.14))))',
            f'  (property "Value" "{fp.name}" (at 0 {val_y} 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
            f"  (attr {fp.attr})",
            "  (duplicate_pad_numbers_are_jumpers no)",
            f'  (fp_rect (start -{cy_hw} -{cy_hh}) (end {cy_hw} {cy_hh}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
            f'  (fp_rect (start -{hw} -{hh}) (end {hw} {hh}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        ]
        for p in fp.pads:
            layers_str = " ".join(f'"{ly}"' for ly in p.layers)
            rr = " (roundrect_rratio 0.25)" if p.shape == "roundrect" else ""
            drl = f" (drill {p.drill})" if p.drill > 0 else ""
            lines.append(
                f'  (pad "{p.number}" {p.pad_type} {p.shape} (at {round(p.x, 3)} {round(p.y, 3)}) '
                f'(size {round(p.w, 3)} {round(p.h, 3)}){drl} (layers {layers_str}){rr})'
            )
        lines.append("  (embedded_fonts no)")
        if fp.model_rel_path:
            model_base = Path(cfg["kicad"]["libraries"]["3dmodels_dir"]) / fp.model_rel_path
            if model_base.exists():
                lines.extend([
                    f'  (model "${{KICAD10_3DMODEL_DIR}}/{fp.model_rel_path}"',
                    "    (offset (xyz 0 0 0))",
                    "    (scale (xyz 1 1 1))",
                    "    (rotate (xyz 0 0 0))",
                    "  )",
                ])
        lines.append(")")
        return "\n".join(lines) + "\n"

    def _format_footprint_pcb(self, comp: PcbComponent, cfg: dict) -> str:
        """Generate footprint block embedded inside .kicad_pcb in exact lockstep."""
        fp = comp.fp_def
        ref_y = self._calc_ref_y(fp)
        val_y = round(-ref_y, 2)
        hw = round(fp.body_w / 2.0, 2)
        hh = round(fp.body_h / 2.0, 2)
        cy_hw = round(hw + 0.35, 2)
        cy_hh = round(max(hh + 0.35, abs(ref_y) + 0.55), 2)
        ref_layer = "F.Fab" if fp.name.startswith("MountingHole") else "F.SilkS"
        fp_uuid = det_uuid(self.project_name, f"pcb_fp_{comp.ref}")

        prop_ang = round(comp.angle % 360.0, 3)
        if abs(prop_ang - 360.0) < 1e-3:
            prop_ang = 0.0

        lines = [
            f'  (footprint "{self.lib_name}:{fp.name}"',
            '    (layer "F.Cu")',
            f'    (uuid "{fp_uuid}")',
            f"    (at {round(comp.x, 3)} {round(comp.y, 3)} {comp.angle})",
            f'    (property "Reference" "{comp.ref}" (at 0 {ref_y} {prop_ang}) (layer "{ref_layer}") (uuid "{det_uuid(self.project_name, f"pref_{comp.ref}")}") (effects (font (size 0.8 0.8) (thickness 0.14))))',
            f'    (property "Value" "{comp.value}" (at 0 {val_y} {prop_ang}) (layer "F.Fab") (uuid "{det_uuid(self.project_name, f"pval_{comp.ref}")}") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        ]
        for fk, fv in comp.extra_fields.items():
            if fv:
                lines.append(
                    f'    (property "{fk}" "{fv}" (at 0 0 {prop_ang}) (layer "F.Fab") (hide yes) '
                    f'(uuid "{det_uuid(self.project_name, f"pf_{comp.ref}_{fk}")}") (effects (font (size 0.8 0.8) (thickness 0.12))))'
                )
        lines.extend([
            f'    (path "/{self.root_sch_uuid}/{comp.sch_uuid}")',
            f"    (attr {fp.attr})",
            "    (duplicate_pad_numbers_are_jumpers no)",
            f'    (fp_rect (start -{cy_hw} -{cy_hh}) (end {cy_hw} {cy_hh}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{det_uuid(self.project_name, f"cy_{comp.ref}")}"))',
            f'    (fp_rect (start -{hw} -{hh}) (end {hw} {hh}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "{det_uuid(self.project_name, f"fab_{comp.ref}")}"))',
        ])
        for idx, p in enumerate(fp.pads):
            layers_str = " ".join(f'"{ly}"' for ly in p.layers)
            rr = " (roundrect_rratio 0.25)" if p.shape == "roundrect" else ""
            drl = f" (drill {p.drill})" if p.drill > 0 else ""
            net_name = comp.pad_nets.get(p.number, "")
            net_id = self.register_net(net_name) if net_name else 0
            net_clause = f' (net {net_id} "{net_name}")' if net_name else ' (net 0 "")'
            pad_uuid = det_uuid(self.project_name, f"pad_{comp.ref}_{p.number}_{idx}")
            lines.append(
                f'    (pad "{p.number}" {p.pad_type} {p.shape} (at {round(p.x, 3)} {round(p.y, 3)}) '
                f'(size {round(p.w, 3)} {round(p.h, 3)}){drl} (layers {layers_str}){rr}{net_clause} (uuid "{pad_uuid}"))'
            )
        if fp.model_rel_path:
            model_base = Path(cfg["kicad"]["libraries"]["3dmodels_dir"]) / fp.model_rel_path
            if model_base.exists():
                lines.extend([
                    f'    (model "${{KICAD10_3DMODEL_DIR}}/{fp.model_rel_path}"',
                    "      (offset (xyz 0 0 0))",
                    "      (scale (xyz 1 1 1))",
                    "      (rotate (xyz 0 0 0))",
                    "    )",
                ])
        lines.append("  )")
        return "\n".join(lines)

    def pad_abs_xy(self, ref: str, pad_number: str) -> Tuple[float, float]:
        """Compute absolute PCB board coordinate of a pad accounting for component rotation."""
        for comp in self.components:
            if comp.ref == ref:
                for p in comp.fp_def.pads:
                    if p.number == pad_number:
                        rad = math.radians(-comp.angle)  # KiCad rotation is CCW positive
                        rx = p.x * math.cos(rad) - p.y * math.sin(rad)
                        ry = p.x * math.sin(rad) + p.y * math.cos(rad)
                        return round(comp.x + rx, 3), round(comp.y + ry, 3)
        raise KeyError(f"Pad {ref}.{pad_number} not found")

    def write(self, project_dir: Path, config: Optional[dict] = None) -> Path:
        """Write .kicad_pcb and all unique .kicad_mod files in footprints/<lib>.pretty/."""
        cfg = config or load_kicad_config()
        fp_dir = project_dir / "footprints" / f"{self.lib_name}.pretty"
        fp_dir.mkdir(parents=True, exist_ok=True)

        unique_fps: Dict[str, FootprintDef] = {}
        for comp in self.components:
            unique_fps[comp.fp_def.name] = comp.fp_def
        for fp_name, fp_def in unique_fps.items():
            write_utf8(fp_dir / f"{fp_name}.kicad_mod", self._format_footprint_mod(fp_def, cfg))

        lines = [
            "(kicad_pcb",
            "  (version 20260206)",
            '  (generator "pcbnew")',
            '  (generator_version "10.0")',
            "  (general (thickness 1.6) (legacy_teardrops no))",
            '  (paper "A4")',
            "  (layers",
            '    (0 "F.Cu" signal)',
            '    (31 "B.Cu" signal)',
            '    (32 "B.Adhes" user "B.Adhesive")',
            '    (33 "F.Adhes" user "F.Adhesive")',
            '    (34 "B.Paste" user)',
            '    (35 "F.Paste" user)',
            '    (36 "B.SilkS" user "B.Silkscreen")',
            '    (37 "F.SilkS" user "F.Silkscreen")',
            '    (38 "B.Mask" user)',
            '    (39 "F.Mask" user)',
            '    (44 "Edge.Cuts" user)',
            '    (46 "B.CrtYd" user "B.Courtyard")',
            '    (47 "F.CrtYd" user "F.Courtyard")',
            '    (48 "B.Fab" user)',
            '    (49 "F.Fab" user)',
            "  )",
            "  (setup",
            "    (stackup",
            '      (layer "F.SilkS" (type "Top Silk Screen"))',
            '      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))',
            '      (layer "F.Cu" (type "copper") (thickness 0.035))',
            '      (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))',
            '      (layer "B.Cu" (type "copper") (thickness 0.035))',
            '      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))',
            '      (layer "B.SilkS" (type "Bottom Silk Screen"))',
            '      (copper_finish "ENIG")',
            "    )",
            "    (pad_to_mask_clearance 0.05)",
            "    (allow_soldermask_bridges_in_footprints no)",
            "    (pcbplotparams",
            "      (layerselection 0x00010fc_ffffffff)",
            "      (plot_on_all_layers_selection 0x0000000_00000000)",
            "      (usegerberextensions true)",
            "      (usegerberattributes true)",
            "      (usegerberadvancedattributes true)",
            "      (subtractmaskfromsilk true)",
            "      (outputformat 1)",
            '      (outputdirectory "gerbers/")',
            "    )",
            "  )",
        ]

        for idx, nname in enumerate(self.net_list):
            lines.append(f'  (net {idx} "{nname}")')

        # Board outline (Edge.Cuts)
        lines.append(
            f'  (gr_rect (start 0 0) (end {self.width_mm} {self.height_mm}) '
            f'(stroke (width 0.15) (type solid)) (fill none) (layer "Edge.Cuts") '
            f'(uuid "{det_uuid(self.project_name, "edge_cuts")}"))'
        )
        # Silkscreen Banner on B.SilkS (auto-placed clear of all B.Mask THT/mounted pad apertures)
        banner_w = max(20.0, len(self.silk_banner) * 0.95)
        bx_cand = round(self.width_mm / 2.0, 2)
        by_chosen = 2.0
        for by_try in [3.0, round(self.height_mm - 2.5, 2), round(self.height_mm / 2.0, 2), 18.0, 32.0, 50.0, 68.0, 12.0]:
            if by_try < 1.8 or by_try > self.height_mm - 1.8:
                continue
            bx_min, bx_max = bx_cand - banner_w / 2.0 - 0.8, bx_cand + banner_w / 2.0 + 0.8
            by_min, by_max = by_try - 0.9, by_try + 0.9
            hit = False
            for comp in self.components:
                rad = math.radians(-comp.angle)
                ca, sa = math.cos(rad), math.sin(rad)
                for p in comp.fp_def.pads:
                    if p.pad_type == "smd" and "B.Mask" not in p.layers:
                        continue
                    px = comp.x + (p.x * ca - p.y * sa)
                    py = comp.y + (p.x * sa + p.y * ca)
                    pr = max(p.w, p.h) / 2.0 + 0.8
                    if not (px + pr < bx_min or px - pr > bx_max or py + pr < by_min or py - pr > by_max):
                        hit = True
                        break
                if hit:
                    break
            if not hit:
                by_chosen = by_try
                break
        lines.append(
            f'  (gr_text "{self.silk_banner}" (at {bx_cand} {by_chosen} 0) '
            f'(layer "B.SilkS") (uuid "{det_uuid(self.project_name, "banner")}") '
            f'(effects (font (size 0.8 0.8) (thickness 0.14)) (justify mirror)))'
        )

        # Footprints
        for comp in self.components:
            lines.append(self._format_footprint_pcb(comp, cfg))

        # Routed tracks (polyline pairs -> segments)
        seg_idx = 0
        for net_name, width, pts, layer in self.tracks:
            nid = self.register_net(net_name)
            for i in range(len(pts) - 1):
                x1, y1 = pts[i]
                x2, y2 = pts[i + 1]
                if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
                    continue
                seg_idx += 1
                lines.append(
                    f"  (segment (start {round(x1, 3)} {round(y1, 3)}) (end {round(x2, 3)} {round(y2, 3)}) "
                    f'(width {round(width, 3)}) (layer "{layer}") (net {nid}) '
                    f'(uuid "{det_uuid(self.project_name, f"seg_{seg_idx}")}"))'
                )

        # Vias
        for v_idx, (net_name, vx, vy, vsize, vdrill) in enumerate(self.vias):
            nid = self.register_net(net_name)
            lines.append(
                f'  (via (at {round(vx, 3)} {round(vy, 3)}) (size {round(vsize, 3)}) '
                f'(drill {round(vdrill, 3)}) (layers "F.Cu" "B.Cu") (net {nid}) '
                f'(uuid "{det_uuid(self.project_name, f"via_{v_idx}")}"))'
            )

        # Solid Ground Pour Zone on B.Cu if GND net exists
        if "GND" in self.net_ids:
            gnd_id = self.net_ids["GND"]
            pad = 0.6
            for z_idx, z_layer in enumerate(["B.Cu"]):
                lines.extend([
                    f'  (zone (net {gnd_id}) (net_name "GND") (layer "{z_layer}") '
                    f'(uuid "{det_uuid(self.project_name, f"gnd_zone_{z_idx}")}") '
                    f"(hatch edge 0.5)",
                    "    (connect_pads yes (clearance 0.25))",
                    "    (min_thickness 0.2)",
                    "    (filled_areas_thickness no)",
                    "    (fill yes (thermal_gap 0.3) (thermal_bridge_width 0.35) (island_removal_mode 0))",
                    "    (polygon",
                    "      (pts",
                    f"        (xy {pad} {pad}) (xy {round(self.width_mm - pad, 2)} {pad}) "
                    f"(xy {round(self.width_mm - pad, 2)} {round(self.height_mm - pad, 2)}) (xy {pad} {round(self.height_mm - pad, 2)})",
                    "      )",
                    "    )",
                    "  )",
                ])

        lines.extend(["  (embedded_fonts no)", ")"])
        pcb_path = project_dir / f"{self.project_name}.kicad_pcb"
        write_utf8(pcb_path, "\n".join(lines) + "\n")
        return pcb_path


def sync_pcb_with_schematic(sb: SchematicBuilder, pb: PCBBuilder) -> None:
    """Sync MPN/Manufacturer/Rating/Origin fields and unconnected-(...) net names for 0-parity DRC."""
    sch_by_ref = {c.ref: c for c in sb.components}
    for pc in pb.components:
        sc = sch_by_ref.get(pc.ref)
        if sc is None:
            continue
        pc.sch_uuid = sc.uuid_str
        pc.value = sc.value
        for fk, fv in [("MPN", sc.mpn), ("Manufacturer", sc.manufacturer), ("Rating", sc.rating), ("Origin", sc.origin)]:
            if fv:
                pc.extra_fields[fk] = fv
        for pin in sc.pins:
            if not pin.net or pin.net.upper().startswith("NC") or pin.etype == "no_connect":
                esc_name = pin.name.replace("/", "{slash}")
                unconn_net = f"unconnected-({pc.ref}-{esc_name}-Pad{pin.number})"
                pc.pad_nets[pin.number] = unconn_net
                pb.register_net(unconn_net)


def check_courtyards(pb: PCBBuilder) -> List[str]:
    """Detect courtyard overlaps (including Reference silk margin) before routing."""
    overlaps: List[str] = []
    boxes = []
    for c in pb.components:
        rad = math.radians(-c.angle)
        ca, sa = abs(math.cos(rad)), abs(math.sin(rad))
        ref_y = pb._calc_ref_y(c.fp_def)
        raw_hw = c.fp_def.body_w / 2.0 + 0.35
        raw_hh = max(c.fp_def.body_h / 2.0 + 0.35, abs(ref_y) + 0.55)
        hw = raw_hw * ca + raw_hh * sa
        hh = raw_hw * sa + raw_hh * ca
        boxes.append((c.ref, c.x - hw, c.y - hh, c.x + hw, c.y + hh))
    for i in range(len(boxes)):
        r1, x1a, y1a, x1b, y1b = boxes[i]
        for j in range(i + 1, len(boxes)):
            r2, x2a, y2a, x2b, y2b = boxes[j]
            if x1a < x2b and x1b > x2a and y1a < y2b and y1b > y2a:
                overlaps.append(f"{r1}<->{r2}")
    return overlaps


class AutoRouter2Layer:
    """Exact-clearance spatial-indexed grid A* 2-layer (F.Cu / B.Cu) PCB router."""

    def __init__(self, pcb: PCBBuilder, grid_mm: float = 0.5, clearance_mm: float = 0.20) -> None:
        self.pcb = pcb
        self.grid = grid_mm
        self.clearance = clearance_mm
        self.cols = int(math.floor(pcb.width_mm / grid_mm)) + 1
        self.rows = int(math.floor(pcb.height_mm / grid_mm)) + 1
        self.pads: List[Tuple[str, float, float, float, float, bool]] = []
        self.pad_cells: List[Dict[Tuple[int, int], List[Tuple[str, float, float, float, float, bool]]]] = [{}, {}]
        self.fine_pad_escape: Dict[Tuple[float, float], Tuple[float, float]] = {}

        for comp in pcb.components:
            rad = math.radians(-comp.angle)
            ca, sa = math.cos(rad), math.sin(rad)
            comp_pts: List[Tuple[PadDef, float, float, float, float]] = []
            for p in comp.fp_def.pads:
                px = comp.x + (p.x * ca - p.y * sa)
                py = comp.y + (p.x * sa + p.y * ca)
                pw = abs(p.w * ca) + abs(p.h * sa)
                ph = abs(p.w * sa) + abs(p.h * ca)
                comp_pts.append((p, px, py, pw, ph))

            for idx_p, (p, px, py, pw, ph) in enumerate(comp_pts):
                net = comp.pad_nets.get(p.number, "")
                is_th = p.pad_type != "smd"
                self.pads.append((net, px, py, pw, ph, is_th))

                # Spatial index covers all possible track widths up to ~1.0 mm
                margin_x = pw / 2.0 + self.clearance + 0.65
                margin_y = ph / 2.0 + self.clearance + 0.65
                gx0 = max(0, int(math.floor((px - margin_x) / self.grid)))
                gx1 = min(self.cols - 1, int(math.ceil((px + margin_x) / self.grid)))
                gy0 = max(0, int(math.floor((py - margin_y) / self.grid)))
                gy1 = min(self.rows - 1, int(math.ceil((py + margin_y) / self.grid)))
                rec = (net, px, py, pw, ph, is_th)
                for gx in range(gx0, gx1 + 1):
                    for gy in range(gy0, gy1 + 1):
                        self.pad_cells[0].setdefault((gx, gy), []).append(rec)
                        if is_th:
                            self.pad_cells[1].setdefault((gx, gy), []).append(rec)

                # Detect fine-pitch SMD pads (< 1.05 mm pitch) and store outward escape unit vector
                if not is_th and len(comp_pts) >= 3:
                    min_d = 1e9
                    for idx_q, (_, qx, qy, _, _) in enumerate(comp_pts):
                        if idx_q != idx_p:
                            min_d = min(min_d, math.hypot(px - qx, py - qy))
                    if min_d < 1.05:
                        if abs(p.x) >= abs(p.y):
                            lx, ly = (1.0 if p.x >= 0 else -1.0), 0.0
                        else:
                            lx, ly = 0.0, (1.0 if p.y >= 0 else -1.0)
                        ox = round(lx * ca - ly * sa, 4)
                        oy = round(lx * sa + ly * ca, 4)
                        self.fine_pad_escape[(round(px, 3), round(py, 3))] = (ox, oy)

        self.segs: List[List[Tuple[Tuple[float, float], Tuple[float, float], str, float]]] = [[], []]
        self.seg_buckets: List[Dict[Tuple[int, int], List[Tuple[Tuple[float, float], Tuple[float, float], str, float]]]] = [{}, {}]
        self.vias: List[Tuple[float, float, str, float]] = []
        self.via_buckets: Dict[Tuple[int, int], List[Tuple[float, float, str, float]]] = {}

        for net, width, pts, layer in pcb.tracks:
            li = 0 if layer == "F.Cu" else 1
            for i in range(len(pts) - 1):
                self._commit_segment(li, pts[i], pts[i + 1], net, width)
        for net, vx, vy, vsize, _ in pcb.vias:
            self._commit_via(vx, vy, net, vsize)

    def _to_grid(self, x: float, y: float) -> Tuple[int, int]:
        return int(round(x / self.grid)), int(round(y / self.grid))

    def _to_mm(self, gx: int, gy: int) -> Tuple[float, float]:
        return round(gx * self.grid, 3), round(gy * self.grid, 3)

    @staticmethod
    def _pt_seg_dist(px: float, py: float, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        vx, vy = b[0] - a[0], b[1] - a[1]
        wx, wy = px - a[0], py - a[1]
        c1 = vx * wx + vy * wy
        if c1 <= 0.0:
            return math.hypot(px - a[0], py - a[1])
        c2 = vx * vx + vy * vy
        if c2 <= c1:
            return math.hypot(px - b[0], py - b[1])
        t = c1 / c2
        return math.hypot(px - (a[0] + t * vx), py - (a[1] + t * vy))

    @classmethod
    def _seg_seg_dist(cls, a1: Tuple[float, float], a2: Tuple[float, float], b1: Tuple[float, float], b2: Tuple[float, float]) -> float:
        def ccw(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
            return (p3[1] - p1[1]) * (p2[0] - p1[0]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

        d1 = ccw(b1, b2, a1)
        d2 = ccw(b1, b2, a2)
        d3 = ccw(a1, a2, b1)
        d4 = ccw(a1, a2, b2)
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return 0.0
        return min(
            cls._pt_seg_dist(a1[0], a1[1], b1, b2),
            cls._pt_seg_dist(a2[0], a2[1], b1, b2),
            cls._pt_seg_dist(b1[0], b1[1], a1, a2),
            cls._pt_seg_dist(b2[0], b2[1], a1, a2),
        )

    def _commit_segment(self, layer_idx: int, p1: Tuple[float, float], p2: Tuple[float, float], net: str, width: float) -> None:
        seg = (p1, p2, net, width)
        self.segs[layer_idx].append(seg)
        pad_r = width / 2.0 + self.clearance + 0.70
        bx0 = int(math.floor((min(p1[0], p2[0]) - pad_r) / 2.0))
        bx1 = int(math.floor((max(p1[0], p2[0]) + pad_r) / 2.0))
        by0 = int(math.floor((min(p1[1], p2[1]) - pad_r) / 2.0))
        by1 = int(math.floor((max(p1[1], p2[1]) + pad_r) / 2.0))
        for bx in range(bx0, bx1 + 1):
            for by in range(by0, by1 + 1):
                self.seg_buckets[layer_idx].setdefault((bx, by), []).append(seg)

    def _commit_via(self, vx: float, vy: float, net: str, vsize: float = 0.7) -> None:
        via_rec = (vx, vy, net, vsize)
        self.vias.append(via_rec)
        pad_r = vsize / 2.0 + self.clearance + 0.70
        bx0 = int(math.floor((vx - pad_r) / 2.0))
        bx1 = int(math.floor((vx + pad_r) / 2.0))
        by0 = int(math.floor((vy - pad_r) / 2.0))
        by1 = int(math.floor((vy + pad_r) / 2.0))
        for bx in range(bx0, bx1 + 1):
            for by in range(by0, by1 + 1):
                self.via_buckets.setdefault((bx, by), []).append(via_rec)

    def _segment_clear(self, layer_idx: int, p1: Tuple[float, float], p2: Tuple[float, float], net: str, width: float) -> bool:
        half = width / 2.0 + self.clearance + 0.01
        steps = max(2, int(math.ceil(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 0.25)))
        checked_pads: Set[Tuple[str, float, float, float, float, bool]] = set()
        pad_list = self.pads if width > 1.0 else None
        if pad_list is None:
            cand_pads: List[Tuple[str, float, float, float, float, bool]] = []
            gx0 = int(math.floor((min(p1[0], p2[0]) - half) / self.grid)) - 1
            gx1 = int(math.ceil((max(p1[0], p2[0]) + half) / self.grid)) + 1
            gy0 = int(math.floor((min(p1[1], p2[1]) - half) / self.grid)) - 1
            gy1 = int(math.ceil((max(p1[1], p2[1]) + half) / self.grid)) + 1
            for gx in range(gx0, gx1 + 1):
                for gy in range(gy0, gy1 + 1):
                    for rec in self.pad_cells[layer_idx].get((gx, gy), ()):
                        if rec not in checked_pads:
                            checked_pads.add(rec)
                            cand_pads.append(rec)
        else:
            cand_pads = pad_list

        for s in range(steps + 1):
            t = s / steps
            x = p1[0] + (p2[0] - p1[0]) * t
            y = p1[1] + (p2[1] - p1[1]) * t
            for pnet, px, py, pw, ph, is_th in cand_pads:
                if pnet == net:
                    continue
                if is_th or layer_idx == 0:
                    if abs(x - px) < (pw / 2.0 + half) and abs(y - py) < (ph / 2.0 + half):
                        return False

        bx0 = int(math.floor((min(p1[0], p2[0]) - half) / 2.0))
        bx1 = int(math.floor((max(p1[0], p2[0]) + half) / 2.0))
        by0 = int(math.floor((min(p1[1], p2[1]) - half) / 2.0))
        by1 = int(math.floor((max(p1[1], p2[1]) + half) / 2.0))

        seen_segs: Set[int] = set()
        for bx in range(bx0, bx1 + 1):
            for by in range(by0, by1 + 1):
                for seg in self.seg_buckets[layer_idx].get((bx, by), ()):
                    sid = id(seg)
                    if sid in seen_segs:
                        continue
                    seen_segs.add(sid)
                    s1, s2, snet, sw = seg
                    if snet != net and self._seg_seg_dist(p1, p2, s1, s2) < (width / 2.0 + sw / 2.0 + self.clearance + 0.01):
                        return False

        seen_vias: Set[int] = set()
        for bx in range(bx0, bx1 + 1):
            for by in range(by0, by1 + 1):
                for vrec in self.via_buckets.get((bx, by), ()):
                    vid = id(vrec)
                    if vid in seen_vias:
                        continue
                    seen_vias.add(vid)
                    vx, vy, vnet, vsize = vrec
                    if vnet != net and self._pt_seg_dist(vx, vy, p1, p2) < (width / 2.0 + vsize / 2.0 + self.clearance + 0.01):
                        return False
        return True

    def _cell_blocked(self, layer_idx: int, gx: int, gy: int, net: str, width: float) -> bool:
        x, y = gx * self.grid, gy * self.grid
        edge = 0.85 + width / 2.0
        if x < edge or x > self.pcb.width_mm - edge or y < edge or y > self.pcb.height_mm - edge:
            return True
        half = width / 2.0 + self.clearance + 0.01
        pads_to_check = self.pads if width > 1.0 else self.pad_cells[layer_idx].get((gx, gy), ())
        for pnet, px, py, pw, ph, is_th in pads_to_check:
            if pnet == net:
                continue
            if is_th or layer_idx == 0:
                if abs(x - px) < (pw / 2.0 + half) and abs(y - py) < (ph / 2.0 + half):
                    return True
        bx, by = int(math.floor(x / 2.0)), int(math.floor(y / 2.0))
        for s1, s2, snet, sw in self.seg_buckets[layer_idx].get((bx, by), ()):
            if snet != net and self._pt_seg_dist(x, y, s1, s2) < (width / 2.0 + sw / 2.0 + self.clearance + 0.01):
                return True
        for vx, vy, vnet, vsize in self.via_buckets.get((bx, by), ()):
            if vnet != net and math.hypot(x - vx, y - vy) < (width / 2.0 + vsize / 2.0 + self.clearance + 0.01):
                return True
        return False

    def _via_blocked(self, gx: int, gy: int, net: str, via_size: float = 0.7) -> bool:
        x, y = gx * self.grid, gy * self.grid
        edge = 1.1 + via_size / 2.0
        if x < edge or x > self.pcb.width_mm - edge or y < edge or y > self.pcb.height_mm - edge:
            return True
        half = via_size / 2.0 + self.clearance + 0.06
        for pnet, px, py, pw, ph, _ in self.pad_cells[0].get((gx, gy), ()):
            if pnet == net:
                if abs(x - px) < (pw / 2.0 + via_size / 2.0 + 0.15) and abs(y - py) < (ph / 2.0 + via_size / 2.0 + 0.15):
                    return True
            else:
                if abs(x - px) < (pw / 2.0 + half) and abs(y - py) < (ph / 2.0 + half):
                    return True
        bx, by = int(math.floor(x / 2.0)), int(math.floor(y / 2.0))
        for li in (0, 1):
            for s1, s2, snet, sw in self.seg_buckets[li].get((bx, by), ()):
                if snet != net and self._pt_seg_dist(x, y, s1, s2) < (via_size / 2.0 + sw / 2.0 + self.clearance + 0.02):
                    return True
        for vx, vy, vnet, vsize in self.via_buckets.get((bx, by), ()):
            min_vc = max(via_size / 2.0 + vsize / 2.0 + self.clearance + 0.12, 1.05)
            if math.hypot(x - vx, y - vy) < min_vc:
                return True
        return False

    def route_two_points(self, net: str, p1: Tuple[float, float], p2: Tuple[float, float], width: float = 0.25, allow_via: bool = True) -> bool:
        import heapq

        s_gx, s_gy = self._to_grid(p1[0], p1[1])
        t_gx, t_gy = self._to_grid(p2[0], p2[1])

        def is_tht(pt: Tuple[float, float]) -> bool:
            gx, gy = self._to_grid(pt[0], pt[1])
            return any(abs(pt[0] - px) < 0.15 and abs(pt[1] - py) < 0.15 and th for _, px, py, _, _, th in self.pad_cells[1].get((gx, gy), ()))

        def clear_entries(pt: Tuple[float, float], gx: int, gy: int) -> Tuple[List[Tuple[int, int, int]], Dict[Tuple[int, int, int], float]]:
            cands: List[Tuple[float, int, int, int, float]] = []
            seen: Set[Tuple[int, int, int]] = set()
            pt_is_th = is_tht(pt)
            f_dir = self.fine_pad_escape.get((round(pt[0], 3), round(pt[1], 3)))
            entry_w = min(width, 0.22) if f_dir is not None else width

            f_cands: List[Tuple[float, int, int, int, float]] = []
            b_cands: List[Tuple[float, int, int, int, float]] = []
            e_cands: List[Tuple[float, int, int, int, float]] = []

            if f_dir is not None:
                ox, oy = f_dir
                for dist in (2.0, 2.5, 3.0, 3.5):
                    ex, ey = pt[0] + ox * dist, pt[1] + oy * dist
                    cx, cy = self._to_grid(ex, ey)
                    if 1 <= cx < self.cols - 1 and 1 <= cy < self.rows - 1 and (0, cx, cy) not in seen:
                        mm_pt = self._to_mm(cx, cy)
                        if not self._cell_blocked(0, cx, cy, net, width) and self._segment_clear(0, pt, mm_pt, net, entry_w):
                            seen.add((0, cx, cy))
                            e_cands.append((dist * 0.5, 0, cx, cy, entry_w))

            for layer in (0, 1):
                if layer == 1 and not pt_is_th:
                    continue
                for r in range(0, 6):
                    for dx in range(-r, r + 1):
                        for dy in range(-r, r + 1):
                            if abs(dx) != r and abs(dy) != r:
                                continue
                            cx, cy = gx + dx, gy + dy
                            if not (1 <= cx < self.cols - 1 and 1 <= cy < self.rows - 1):
                                continue
                            if (layer, cx, cy) in seen:
                                continue
                            mm_pt = self._to_mm(cx, cy)
                            use_w = entry_w if (f_dir is not None and math.hypot(mm_pt[0] - pt[0], mm_pt[1] - pt[1]) <= 3.6) else width
                            if self._cell_blocked(layer, cx, cy, net, width):
                                continue
                            if self._segment_clear(layer, pt, mm_pt, net, use_w):
                                seen.add((layer, cx, cy))
                                d = math.hypot(mm_pt[0] - pt[0], mm_pt[1] - pt[1])
                                if layer == 0:
                                    f_cands.append((d, layer, cx, cy, use_w))
                                else:
                                    b_cands.append((d, layer, cx, cy, use_w))
            f_cands.sort()
            b_cands.sort()
            e_cands.sort()
            chosen = e_cands[:4] + f_cands[:6] + b_cands[:6]
            return [(ly, cx, cy) for _, ly, cx, cy, _ in chosen], {(ly, cx, cy): uw for _, ly, cx, cy, uw in chosen}

        starts, start_w = clear_entries(p1, s_gx, s_gy)
        goal_list, goal_w = clear_entries(p2, t_gx, t_gy)
        goals = set(goal_list)
        if not starts or not goals:
            return False

        pq: List[Tuple[float, Tuple[int, int, int]]] = []
        cost: Dict[Tuple[int, int, int], float] = {}
        parent: Dict[Tuple[int, int, int], Optional[Tuple[int, int, int]]] = {}

        for st in starts:
            cost[st] = 0.0
            parent[st] = None
            h = min(abs(st[1] - g[1]) + abs(st[2] - g[2]) for g in goal_list)
            heapq.heappush(pq, (h * 1.1, st))

        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        iters = 0
        found: Optional[Tuple[int, int, int]] = None

        while pq and iters < 80000:
            iters += 1
            _, cur = heapq.heappop(pq)
            if cur in goals:
                found = cur
                break
            cl, cx, cy = cur
            cc = cost[cur]
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if not (1 <= nx < self.cols - 1 and 1 <= ny < self.rows - 1):
                    continue
                if self._cell_blocked(cl, nx, ny, net, width):
                    continue
                nxt = (cl, nx, ny)
                step_cost = 1.0 + (0.15 if (cl == 0 and dy != 0) or (cl == 1 and dx != 0) else 0.0)
                nc = cc + step_cost
                if nc < cost.get(nxt, 1e18):
                    cost[nxt] = nc
                    parent[nxt] = cur
                    h = min(abs(nx - g[1]) + abs(ny - g[2]) for g in goal_list)
                    heapq.heappush(pq, (nc + h * 1.1, nxt))
            if allow_via and not self._via_blocked(cx, cy, net):
                nl = 1 - cl
                nxt = (nl, cx, cy)
                nc = cc + 7.0
                if nc < cost.get(nxt, 1e18):
                    cost[nxt] = nc
                    parent[nxt] = cur
                    h = min(abs(cx - g[1]) + abs(cy - g[2]) for g in goal_list)
                    heapq.heappush(pq, (nc + h * 1.1, nxt))

        if found is None:
            return False

        path: List[Tuple[int, int, int]] = []
        node: Optional[Tuple[int, int, int]] = found
        while node is not None:
            path.append(node)
            node = parent[node]
        path.reverse()

        def emit_chain(layer_idx: int, pts_list: List[Tuple[float, float]], seg_w: float) -> None:
            if len(pts_list) < 2:
                return
            simp = [pts_list[0]]
            for pt in pts_list[1:-1]:
                if math.hypot(pt[0] - simp[-1][0], pt[1] - simp[-1][1]) >= 0.05:
                    simp.append(pt)
            simp.append(pts_list[-1])
            lname = "F.Cu" if layer_idx == 0 else "B.Cu"
            self.pcb.add_track(net, seg_w, simp, lname)
            for idx_s in range(len(simp) - 1):
                self._commit_segment(layer_idx, simp[idx_s], simp[idx_s + 1], net, seg_w)

        st_node = path[0]
        ed_node = path[-1]
        sw_entry = start_w.get(st_node, width)
        ew_entry = goal_w.get(ed_node, width)
        st_mm = self._to_mm(st_node[1], st_node[2])
        ed_mm = self._to_mm(ed_node[1], ed_node[2])

        if sw_entry < width - 1e-3 and math.hypot(st_mm[0] - p1[0], st_mm[1] - p1[1]) >= 0.05:
            emit_chain(st_node[0], [p1, st_mm], sw_entry)
            seg_pts: List[Tuple[float, float]] = [st_mm]
        else:
            seg_pts = [p1]

        cur_layer = st_node[0]
        for li, gx, gy in path:
            mm_pt = self._to_mm(gx, gy)
            if li != cur_layer:
                emit_chain(cur_layer, seg_pts, width)
                if not any(math.hypot(mm_pt[0] - vx, mm_pt[1] - vy) < 0.25 for vx, vy, _, _ in self.vias):
                    self.pcb.add_via(net, mm_pt[0], mm_pt[1], 0.7, 0.35)
                    self._commit_via(mm_pt[0], mm_pt[1], net, 0.7)
                cur_layer = li
                seg_pts = [mm_pt]
            else:
                seg_pts.append(mm_pt)

        if ew_entry < width - 1e-3 and math.hypot(p2[0] - ed_mm[0], p2[1] - ed_mm[1]) >= 0.05:
            emit_chain(cur_layer, seg_pts, width)
            emit_chain(ed_node[0], [ed_mm, p2], ew_entry)
        else:
            seg_pts.append(p2)
            emit_chain(cur_layer, seg_pts, width)
        return True

    def route_all(self, net_widths: Optional[Dict[str, float]] = None) -> Dict[str, List[str]]:
        """Route non-GND nets first, then GND tree and B.Cu stitching vias for SMD GND pads."""
        net_widths = net_widths or {}
        by_net: Dict[str, List[Tuple[float, float, bool]]] = {}
        for comp in self.pcb.components:
            rad = math.radians(-comp.angle)
            ca, sa = math.cos(rad), math.sin(rad)
            for p in comp.fp_def.pads:
                net = comp.pad_nets.get(p.number, "")
                if not net or net.startswith("unconnected-("):
                    continue
                px = round(comp.x + (p.x * ca - p.y * sa), 3)
                py = round(comp.y + (p.x * sa + p.y * ca), 3)
                is_th = p.pad_type != "smd"
                by_net.setdefault(net, []).append((px, py, is_th))

        failed: List[str] = []

        # 1. Route short/fine-pitch SMD nets first, then wide power nets, then remaining signals
        other_nets = [n for n, pts in by_net.items() if n != "GND" and len(pts) >= 2]

        def net_sort_key(n: str) -> Tuple[int, float, int]:
            pts = by_net[n]
            touches_fine = any((round(x, 3), round(y, 3)) in self.fine_pad_escape for x, y, _ in pts)
            all_smd_short = len(pts) == 2 and not pts[0][2] and not pts[1][2] and math.hypot(pts[0][0] - pts[1][0], pts[0][1] - pts[1][1]) < 15.0
            prio = 0 if (all_smd_short or touches_fine) else 1
            return (prio, -net_widths.get(n, 0.25), len(pts))

        other_nets.sort(key=net_sort_key)

        def route_net_kruskal(net: str, w: float, pts_all: List[Tuple[float, float, bool]], pre_linked_base: bool = False) -> None:
            uniq: List[Tuple[float, float, bool]] = []
            for x, y, th in pts_all:
                if all(math.hypot(x - ux, y - uy) > 0.05 for ux, uy, _ in uniq):
                    uniq.append((x, y, th))
            n_u = len(uniq)
            if n_u < 2:
                return
            parent = list(range(n_u))

            def find(i: int) -> int:
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i

            def union(i: int, j: int) -> None:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj

            # Pre-union pad clusters already joined by manual pcb.tracks / pcb.vias on this net
            segs_pre: List[Tuple[int, Tuple[float, float], Tuple[float, float]]] = []
            for t_net, _, t_pts, t_layer in self.pcb.tracks:
                if t_net == net:
                    li = 0 if t_layer == "F.Cu" else 1
                    for pk in range(len(t_pts) - 1):
                        segs_pre.append((li, (t_pts[pk][0], t_pts[pk][1]), (t_pts[pk + 1][0], t_pts[pk + 1][1])))
            vias_pre = [(vx, vy) for v_net, vx, vy, _, _ in self.pcb.vias if v_net == net]
            if segs_pre:
                def pt_on_seg(px: float, py: float, a: Tuple[float, float], b: Tuple[float, float]) -> bool:
                    dx, dy = b[0] - a[0], b[1] - a[1]
                    l2 = dx * dx + dy * dy
                    if l2 < 1e-9:
                        return math.hypot(px - a[0], py - a[1]) <= 0.15
                    t_p = max(0.0, min(1.0, ((px - a[0]) * dx + (py - a[1]) * dy) / l2))
                    return math.hypot(px - (a[0] + t_p * dx), py - (a[1] + t_p * dy)) <= 0.15

                n_s = len(segs_pre)
                s_par = list(range(n_s))

                def s_find(x: int) -> int:
                    while s_par[x] != x:
                        s_par[x] = s_par[s_par[x]]
                        x = s_par[x]
                    return x

                def s_union(a: int, b: int) -> None:
                    ra, rb = s_find(a), s_find(b)
                    if ra != rb:
                        s_par[ra] = rb

                for sa_i in range(n_s):
                    la, a0, a1 = segs_pre[sa_i]
                    for sb_i in range(sa_i + 1, n_s):
                        lb, b0, b1 = segs_pre[sb_i]
                        if la == lb and (pt_on_seg(b0[0], b0[1], a0, a1) or pt_on_seg(b1[0], b1[1], a0, a1) or pt_on_seg(a0[0], a0[1], b0, b1) or pt_on_seg(a1[0], a1[1], b0, b1)):
                            s_union(sa_i, sb_i)
                        elif la != lb and any(pt_on_seg(vx, vy, a0, a1) and pt_on_seg(vx, vy, b0, b1) for vx, vy in vias_pre):
                            s_union(sa_i, sb_i)

                by_scomp: Dict[int, List[int]] = {}
                for idx_u, (ux, uy, th) in enumerate(uniq):
                    for sa_i, (la, a0, a1) in enumerate(segs_pre):
                        if (la == 0 or th) and pt_on_seg(ux, uy, a0, a1):
                            by_scomp.setdefault(s_find(sa_i), []).append(idx_u)
                for grp in by_scomp.values():
                    for k_u in grp[1:]:
                        union(grp[0], k_u)

            # For GND: all THT pads and vias already join on the solid B.Cu copper pour zone
            if pre_linked_base:
                first_th = None
                for idx_u, (_, _, th) in enumerate(uniq):
                    if th:
                        if first_th is None:
                            first_th = idx_u
                        else:
                            union(first_th, idx_u)

            edges: List[Tuple[float, int, int]] = []
            for i in range(n_u):
                for j in range(i + 1, n_u):
                    if find(i) != find(j):
                        edges.append((math.hypot(uniq[i][0] - uniq[j][0], uniq[i][1] - uniq[j][1]), i, j))
            edges.sort()

            fail_pair_count: Dict[Tuple[int, int], int] = {}
            for _, i, j in edges:
                ri, rj = find(i), find(j)
                if ri != rj:
                    pair_key = (min(ri, rj), max(ri, rj))
                    if fail_pair_count.get(pair_key, 0) >= 3:
                        continue
                    p_a = (uniq[i][0], uniq[i][1])
                    p_b = (uniq[j][0], uniq[j][1])
                    if self.route_two_points(net, p_a, p_b, width=w, allow_via=True):
                        union(i, j)
                    else:
                        fail_pair_count[pair_key] = fail_pair_count.get(pair_key, 0) + 1

            # Second pass for any remaining islands using neckdown width min(w, 0.22)
            rem_edges = [(d, i, j) for d, i, j in edges if find(i) != find(j)]
            if rem_edges:
                fb_w = min(w, 0.22)
                fb_fail: Dict[Tuple[int, int], int] = {}
                for _, i, j in rem_edges:
                    ri, rj = find(i), find(j)
                    if ri != rj:
                        pair_key = (min(ri, rj), max(ri, rj))
                        if fb_fail.get(pair_key, 0) >= 2:
                            continue
                        p_a = (uniq[i][0], uniq[i][1])
                        p_b = (uniq[j][0], uniq[j][1])
                        if self.route_two_points(net, p_a, p_b, width=fb_w, allow_via=True):
                            union(i, j)
                        else:
                            fb_fail[pair_key] = fb_fail.get(pair_key, 0) + 1

            roots = {find(i) for i in range(n_u)}
            if len(roots) > 1:
                for _, i, j in edges:
                    if find(i) != find(j):
                        failed.append(f"{net}:{(uniq[i][0], uniq[i][1])}->{(uniq[j][0], uniq[j][1])}")
                        union(i, j)

        for net in other_nets:
            route_net_kruskal(net, net_widths.get(net, 0.25), by_net[net], pre_linked_base=False)

        # 2. Route GND as a single connected spanning tree while B.Cu pour floods open copper
        if "GND" in by_net:
            route_net_kruskal("GND", 0.22, by_net["GND"], pre_linked_base=False)

        return {"failed": failed}




# ---------------------------------------------------------------------------
# Standard Footprint Templates (Matching KiCad 10 Pad Geometry & Rules)
# ---------------------------------------------------------------------------


def fp_smd_2pin(name: str, pitch_x: float, pad_w: float, pad_h: float, model_rel: Optional[str] = None) -> FootprintDef:
    return FootprintDef(
        name=name,
        attr="smd",
        pads=[
            PadDef("1", "smd", "roundrect", -pitch_x / 2.0, 0.0, pad_w, pad_h),
            PadDef("2", "smd", "roundrect", +pitch_x / 2.0, 0.0, pad_w, pad_h),
        ],
        body_w=pitch_x + pad_w + 0.4,
        body_h=max(pad_h + 0.4, 1.5),
        model_rel_path=model_rel,
    )


def fp_pin_header_1xN(
    name: str, count: int, pitch: float = 2.54, pad_d: float = 1.7, drill: float = 1.0,
    model_rel: Optional[str] = None, horizontal: bool = False
) -> FootprintDef:
    start = -((count - 1) * pitch) / 2.0
    pads = []
    for i in range(count):
        shape = "rect" if i == 0 else "circle"
        pos = round(start + i * pitch, 3)
        px, py = (pos, 0.0) if horizontal else (0.0, pos)
        pads.append(PadDef(str(i + 1), "thru_hole", shape, px, py, pad_d, pad_d, drill, ("*.Cu", "*.Mask")))
    return FootprintDef(
        name=name,
        attr="through_hole",
        pads=pads,
        body_w=(count * pitch) if horizontal else 2.54,
        body_h=2.54 if horizontal else (count * pitch),
        model_rel_path=model_rel,
    )


def fp_dual_row_module(name: str, pins_per_side: int, row_spacing: float, pitch: float = 2.54, pad_d: float = 1.65, drill: float = 1.0) -> FootprintDef:
    start_y = -((pins_per_side - 1) * pitch) / 2.0
    pads = []
    for i in range(pins_per_side):
        shape = "rect" if i == 0 else "circle"
        pads.append(PadDef(str(i + 1), "thru_hole", shape, -row_spacing / 2.0, round(start_y + i * pitch, 3), pad_d, pad_d, drill, ("*.Cu", "*.Mask")))
    for i in range(pins_per_side):
        pnum = pins_per_side + i + 1
        pads.append(PadDef(str(pnum), "thru_hole", "circle", +row_spacing / 2.0, round(-start_y - i * pitch, 3), pad_d, pad_d, drill, ("*.Cu", "*.Mask")))
    return FootprintDef(
        name=name,
        attr="through_hole",
        pads=pads,
        body_w=row_spacing + 2.54,
        body_h=pins_per_side * pitch + 2.0,
    )


def fp_sot23_3(name: str = "SOT-23") -> FootprintDef:
    return FootprintDef(
        name=name,
        attr="smd",
        pads=[
            PadDef("1", "smd", "roundrect", -1.1, -0.95, 0.9, 0.65),
            PadDef("2", "smd", "roundrect", -1.1, +0.95, 0.9, 0.65),
            PadDef("3", "smd", "roundrect", +1.1, 0.0, 0.9, 0.65),
        ],
        body_w=3.2,
        body_h=2.9,
        model_rel_path="Package_TO_SOT_SMD.3dshapes/SOT-23.step",
    )


def fp_sot23_5(name: str = "SOT-23-5") -> FootprintDef:
    return FootprintDef(
        name=name,
        attr="smd",
        pads=[
            PadDef("1", "smd", "roundrect", -1.35, -0.95, 1.0, 0.58),
            PadDef("2", "smd", "roundrect", -1.35, 0.0, 1.0, 0.58),
            PadDef("3", "smd", "roundrect", -1.35, +0.95, 1.0, 0.58),
            PadDef("4", "smd", "roundrect", +1.35, +0.95, 1.0, 0.58),
            PadDef("5", "smd", "roundrect", +1.35, -0.95, 1.0, 0.58),
        ],
        body_w=3.8,
        body_h=3.0,
        model_rel_path="Package_TO_SOT_SMD.3dshapes/SOT-23-5.step",
    )


def fp_sot223_tab(name: str = "SOT-223-3_TabPin2") -> FootprintDef:
    return FootprintDef(
        name=name,
        attr="smd",
        pads=[
            PadDef("1", "smd", "roundrect", -2.3, +3.1, 1.2, 2.0),
            PadDef("2", "smd", "roundrect", 0.0, +3.1, 1.2, 2.0),
            PadDef("3", "smd", "roundrect", +2.3, +3.1, 1.2, 2.0),
            PadDef("2", "smd", "roundrect", 0.0, -3.1, 3.8, 2.0),
        ],
        body_w=7.0,
        body_h=8.2,
        model_rel_path="Package_TO_SOT_SMD.3dshapes/SOT-223-3_TabPin2.step",
    )


def fp_soic_dual(name: str, total_pins: int, pitch: float = 1.27, row_span: float = 5.4, pad_w: float = 1.5, pad_h: float = 0.6, model_rel: Optional[str] = None) -> FootprintDef:
    half = total_pins // 2
    start_y = -((half - 1) * pitch) / 2.0
    pads = []
    for i in range(half):
        pads.append(PadDef(str(i + 1), "smd", "roundrect", -row_span / 2.0, round(start_y + i * pitch, 3), pad_w, pad_h))
    for i in range(half):
        pads.append(PadDef(str(half + i + 1), "smd", "roundrect", +row_span / 2.0, round(-start_y - i * pitch, 3), pad_w, pad_h))
    return FootprintDef(
        name=name,
        attr="smd",
        pads=pads,
        body_w=row_span + pad_w + 0.4,
        body_h=half * pitch + 1.2,
        model_rel_path=model_rel,
    )


def fp_vssop10(name: str = "VSSOP-10_3x3mm_P0.5mm") -> FootprintDef:
    # 0.50 mm pitch -> 0.28 mm pad height leaves 0.22 mm clearance (>= 0.20 mm DRC rule!)
    return fp_soic_dual(
        name=name,
        total_pins=10,
        pitch=0.50,
        row_span=4.35,
        pad_w=1.35,
        pad_h=0.28,
        model_rel="Package_SO.3dshapes/VSSOP-10_3x3mm_P0.5mm.step",
    )


def fp_mounting_hole(name: str = "MountingHole_3.2mm_M3_Pad_Via") -> FootprintDef:
    return FootprintDef(
        name=name,
        attr="through_hole",
        pads=[PadDef("1", "thru_hole", "circle", 0.0, 0.0, 5.2, 5.2, 3.2, ("*.Cu", "*.Mask"))],
        body_w=5.5,
        body_h=5.5,
    )


def fp_xt60(name: str = "AMASS_XT60_Vertical") -> FootprintDef:
    return FootprintDef(
        name=name,
        attr="through_hole",
        pads=[
            PadDef("1", "thru_hole", "circle", 0.0, -3.6, 5.6, 5.6, 3.8, ("*.Cu", "*.Mask")),
            PadDef("2", "thru_hole", "circle", 0.0, +3.6, 5.6, 5.6, 3.8, ("*.Cu", "*.Mask")),
        ],
        body_w=8.5,
        body_h=15.5,
    )


def fp_kelvin_shunt_4wire(name: str = "R_Shunt_4Wire_CSS4J_4026") -> FootprintDef:
    return FootprintDef(
        name=name,
        attr="smd",
        pads=[
            PadDef("1", "smd", "roundrect", -4.2, -1.2, 2.8, 3.8),
            PadDef("2", "smd", "roundrect", +4.2, -1.2, 2.8, 3.8),
            PadDef("3", "smd", "roundrect", -1.6, +2.0, 1.1, 1.4),
            PadDef("4", "smd", "roundrect", +1.6, +2.0, 1.1, 1.4),
        ],
        body_w=11.5,
        body_h=7.0,
    )


# ---------------------------------------------------------------------------
# Verification, Export & Validation Report Runner
# ---------------------------------------------------------------------------


def build_and_verify_project(
    project_dir: Path,
    project_name: str,
    gerber_dir: Optional[Path] = None,
    bom_out_path: Optional[Path] = None,
    models_out_dir: Optional[Path] = None,
    write_report: bool = True,
    config: Optional[dict] = None,
) -> dict:
    """Run ERC, DRC (--refill-zones --save-board --schematic-parity), Netlist, Gerbers, Drill, BOM, 3D exports."""
    cfg = config or load_kicad_config()
    sch_path = project_dir / f"{project_name}.kicad_sch"
    pcb_path = project_dir / f"{project_name}.kicad_pcb"
    g_dir = gerber_dir or (project_dir / "gerbers")
    g_dir.mkdir(parents=True, exist_ok=True)
    m_dir = models_out_dir or (project_dir / "3d-models")
    m_dir.mkdir(parents=True, exist_ok=True)

    erc_json_path = g_dir / f"{project_name}_erc.json"
    erc_rpt_path = g_dir / f"{project_name}_erc.txt"
    drc_json_path = g_dir / f"{project_name}_drc.json"
    drc_rpt_path = g_dir / f"{project_name}_drc.txt"
    net_path = project_dir / f"{project_name}.net"

    # 1. ERC (Report + JSON)
    run_cli(["sch", "erc", "--severity-all", "--format", "report", "--output", str(erc_rpt_path), str(sch_path)], cfg)
    run_cli(["sch", "erc", "--severity-all", "--format", "json", "--output", str(erc_json_path), str(sch_path)], cfg)
    erc_data = json.loads(erc_json_path.read_text(encoding="utf-8"))
    erc_violations = sum(len(s.get("violations", [])) for s in erc_data.get("sheets", []))

    # 2. Netlist
    run_cli(["sch", "export", "netlist", "--format", "kicadsexpr", "--output", str(net_path), str(sch_path)], cfg, check=True)

    # 3. DRC with Zone Refill + Save Board + Schematic Parity
    run_cli(
        ["pcb", "drc", "--refill-zones", "--save-board", "--schematic-parity", "--severity-all", "--format", "report", "--output", str(drc_rpt_path), str(pcb_path)],
        cfg,
    )
    run_cli(
        ["pcb", "drc", "--refill-zones", "--schematic-parity", "--severity-all", "--format", "json", "--output", str(drc_json_path), str(pcb_path)],
        cfg,
    )
    drc_data = json.loads(drc_json_path.read_text(encoding="utf-8"))
    drc_violations = len(drc_data.get("violations", []))
    drc_unconnected = len(drc_data.get("unconnected_items", []))
    drc_parity = len(drc_data.get("schematic_parity", []))

    # 4. Gerbers + Drill
    run_cli(
        [
            "pcb", "export", "gerbers",
            "--check-zones",
            "--subtract-soldermask",
            "-l", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
            "--output", str(g_dir) + "/",
            str(pcb_path),
        ],
        cfg,
        check=True,
    )
    run_cli(
        [
            "pcb", "export", "drill",
            "--excellon-units", "mm",
            "--excellon-separate-th",
            "--generate-map",
            "--output", str(g_dir) + "/",
            str(pcb_path),
        ],
        cfg,
        check=True,
    )

    # 5. BOM (KiCad CLI native + enriched)
    if bom_out_path is not None:
        run_cli(
            [
                "sch", "export", "bom",
                "--fields", "Reference,Value,Footprint,MPN,Manufacturer,Rating,Origin,QUANTITY",
                "--labels", "Designator,Value,Footprint,MPN,Manufacturer,Rating,Origin,Qty",
                "--output", str(bom_out_path),
                str(sch_path),
            ],
            cfg,
            check=True,
        )

    # 6. 3D Exports (STEP + GLB + PNG Render Top & Iso)
    step_path = m_dir / f"{project_name}.step"
    glb_path = m_dir / f"{project_name}.glb"
    png_top = m_dir / f"{project_name}_top.png"
    png_iso = m_dir / f"{project_name}_iso.png"
    run_cli(["pcb", "export", "step", "--subst-models", "--output", str(step_path), str(pcb_path)], cfg)
    run_cli(["pcb", "export", "glb", "--subst-models", "--output", str(glb_path), str(pcb_path)], cfg)
    run_cli(["pcb", "render", "--side", "top", "--width", "1200", "--height", "900", "--output", str(png_top), str(pcb_path)], cfg)
    run_cli(["pcb", "render", "--side", "top", "--perspective", "--rotate", "-35,0,25", "--width", "1200", "--height", "900", "--output", str(png_iso), str(pcb_path)], cfg)

    summary = {
        "project": project_name,
        "kicad_version": cfg["kicad"]["version"],
        "erc_violations": erc_violations,
        "drc_violations": drc_violations,
        "drc_unconnected": drc_unconnected,
        "drc_parity_issues": drc_parity,
        "step_exported": step_path.exists(),
        "glb_exported": glb_path.exists(),
        "render_top": str(png_top),
        "render_iso": str(png_iso),
        "erc_report": str(erc_rpt_path),
        "drc_report": str(drc_rpt_path),
    }

    if write_report:
        rpt_md = (
            f"# {project_name} KiCad {cfg['kicad']['version']} Design Validation Report\n\n"
            f"- **ERC Violations**: `{erc_violations}`\n"
            f"- **DRC Violations**: `{drc_violations}`\n"
            f"- **Unconnected Pads**: `{drc_unconnected}`\n"
            f"- **Schematic-to-PCB Parity Issues**: `{drc_parity}`\n"
            f"- **3D STEP Model**: `{step_path.name}` ({'OK' if step_path.exists() else 'Missing'})\n"
            f"- **3D GLB Model**: `{glb_path.name}` ({'OK' if glb_path.exists() else 'Missing'})\n"
            f"- **3D Renders**: `{png_top.name}`, `{png_iso.name}`\n"
        )
        write_utf8(project_dir / "DESIGN-VALIDATION-REPORT.md", rpt_md)

    return summary
