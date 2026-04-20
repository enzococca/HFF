#!/usr/bin/env python3
"""Harmonize fonts and icon sizes across all Qt .ui files.

Passes:
  1. Remove every <property name="font"> block so widgets inherit the
     QGIS application font.
  2. Normalize button icon sizes on QToolButton / QPushButton widgets
     that carry an icon:
        - iconSize   -> 24x24
        - minimumSize / maximumSize -> 32x32 (only when already set)

Usage:
    python3 scripts/harmonize_ui.py          # apply changes
    python3 scripts/harmonize_ui.py --dry    # report only
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import xml.etree.ElementTree as ET


PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
UI_DIR = PLUGIN_ROOT / 'gui' / 'ui'

ICON_BUTTON_CLASSES = {'QToolButton', 'QPushButton'}
TARGET_ICON_SIZE = (24, 24)
TARGET_BUTTON_SIZE = (32, 32)


def _strip_fonts(root: ET.Element) -> int:
    removed = 0
    for parent in root.iter():
        for prop in list(parent.findall('property')):
            if prop.get('name') == 'font':
                parent.remove(prop)
                removed += 1
    return removed


def _set_size(prop: ET.Element, w: int, h: int) -> bool:
    size = prop.find('size')
    if size is None:
        return False
    wt = size.find('width')
    ht = size.find('height')
    if wt is None or ht is None:
        return False
    changed = False
    if wt.text != str(w):
        wt.text = str(w)
        changed = True
    if ht.text != str(h):
        ht.text = str(h)
        changed = True
    return changed


def _ensure_size_property(widget: ET.Element, name: str, w: int, h: int) -> ET.Element:
    """Find-or-create a <property name="..."><size>...</size></property> block."""
    for prop in widget.findall('property'):
        if prop.get('name') == name:
            _set_size(prop, w, h)
            return prop
    prop = ET.SubElement(widget, 'property', {'name': name})
    size = ET.SubElement(prop, 'size')
    ET.SubElement(size, 'width').text = str(w)
    ET.SubElement(size, 'height').text = str(h)
    return prop


def _normalize_icon_widgets(root: ET.Element) -> int:
    changed = 0
    for widget in root.iter('widget'):
        if widget.get('class') not in ICON_BUTTON_CLASSES:
            continue
        props = {p.get('name'): p for p in widget.findall('property')}
        if 'icon' not in props:
            continue
        # iconSize: force-set, create if missing
        _ensure_size_property(widget, 'iconSize', *TARGET_ICON_SIZE)
        changed += 1
        # min/maxSize: force-set, create if missing
        for key in ('minimumSize', 'maximumSize'):
            _ensure_size_property(widget, key, *TARGET_BUTTON_SIZE)
            changed += 1
    return changed


def process(path: pathlib.Path, dry: bool) -> tuple[int, int]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        print(f'  SKIP (parse error): {path.name}: {exc}', file=sys.stderr)
        return (0, 0)
    root = tree.getroot()
    fonts = _strip_fonts(root)
    icons = _normalize_icon_widgets(root)
    if (fonts or icons) and not dry:
        tree.write(path, encoding='UTF-8', xml_declaration=True)
    return (fonts, icons)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry', action='store_true', help='report only, do not write')
    args = parser.parse_args()

    if not UI_DIR.is_dir():
        print(f'UI dir not found: {UI_DIR}', file=sys.stderr)
        return 1

    total_fonts = 0
    total_icons = 0
    files_changed = 0
    for ui in sorted(UI_DIR.glob('*.ui')):
        fonts, icons = process(ui, args.dry)
        if fonts or icons:
            files_changed += 1
            print(f'  {ui.name}: -{fonts} font(s), ~{icons} icon prop(s)')
        total_fonts += fonts
        total_icons += icons

    action = 'would remove' if args.dry else 'removed'
    action2 = 'would normalize' if args.dry else 'normalized'
    print()
    print(f'{action} {total_fonts} <font> blocks')
    print(f'{action2} {total_icons} icon/size properties')
    print(f'files changed: {files_changed}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
