#!/usr/bin/env python3
"""Populate hff_test3 with plausible-but-invented archaeological records.

Usage:
    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/standalone/populate_hff_test3.py

Creates:
    - 10 site_table rows                (parents for the rest)
    - 10 site_point rows                (geometry, Lebanese coast)
    - 10 dive_log rows                  (UW)
    - 50 artefact_log rows
    - 50 pottery_table rows
    - 50 anchor_table rows
    - 10 shipwreck_table rows
    - 10 shipwreck_location rows        (geometry)
"""
from __future__ import annotations

import random
from datetime import date, timedelta

import psycopg2
from psycopg2.extras import execute_values


DSN = dict(host='localhost', port=5433, user='postgres', password='postgres', dbname='hff_test3')

random.seed(42)  # reproducible


def biblio_list(loc):
    """Fields backed by tableWidget_rif_biblio store a list-of-lists string
    shaped like [[author, year, title, publisher], ...]."""
    return str([
        [f'Doe J.', '2023', f'Underwater Survey at {loc}', 'JMA 18'],
        [f'Smith R.', '2021', f'Finds from {loc}', 'BAR 2991'],
    ])


def storage_list(depot):
    """Storage tracking as list-of-lists [[location, container, shelf, date], ...]."""
    return str([
        [f'Depot HFF-{depot}', f'box {random.randint(1, 30)}',
         f'shelf {chr(65 + random.randint(0, 9))}', '2024-08-15'],
    ])


def samples_list():
    """Sample list [[sample_id, type, date, analyst], ...]."""
    return str([
        [f'SMP-{random.randint(1, 999):03d}',
         random.choice(['OSL', 'C14', 'thin-section', 'XRF']),
         '2024-09-01', 'Lab HFF'],
    ])


SITES = [
    ('Tyre Harbour', 'Tyre', 'Sour'),
    ('Sidon Castle', 'Sidon', 'Saida'),
    ('Byblos Port', 'Byblos', 'Jbeil'),
    ('Beirut North Bay', 'Beirut', 'Mina el-Hosn'),
    ('Tripoli Mina', 'Tripoli', 'Mina'),
    ('Batroun Cove', 'Batroun', 'Old Harbour'),
    ('Anfeh Peninsula', 'Anfeh', 'Ras Anfeh'),
    ('Jieh Bay', 'Jieh', 'Chouf'),
    ('Chekka Shore', 'Chekka', 'Koura'),
    ('Amchit Reef', 'Amchit', 'Kesrouane'),
]

PERIODS = ['Phoenician', 'Roman', 'Byzantine', 'Crusader', 'Mamluk', 'Ottoman']
MATERIALS = ['ceramic', 'stone', 'metal', 'glass', 'bone', 'wood']
ANCHOR_TYPES = ['composite', 'single-hole', 'admiralty', 'grapnel', 'stockless']
STONES = ['limestone', 'basalt', 'sandstone', 'granite', 'marble']
POT_FORMS = ['amphora', 'bowl', 'jar', 'jug', 'cooking pot', 'plate', 'lamp']
OBJS = ['amphora', 'anchor', 'lamp', 'coin', 'ingot', 'tile', 'pipe', 'fishing-weight']
WRECK_CAUSES = ['storm', 'fire', 'battle', 'grounding', 'scuttled', 'unknown']
PROPULSIONS = ['sail', 'oar', 'steam', 'motor', 'mixed']


def coord_lebanon():
    """Roughly offshore Lebanon."""
    lon = round(random.uniform(35.10, 35.60), 6)
    lat = round(random.uniform(33.50, 34.70), 6)
    return lon, lat


def d(start='2020-01-01', end='2024-12-31'):
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return (s + timedelta(days=random.randint(0, (e - s).days))).isoformat()


def pick(seq):
    return random.choice(seq)


# ---------------------------------------------------------------------------
# INSERTERS
# ---------------------------------------------------------------------------
def insert_sites(cur):
    rows = []
    for loc, city, village in SITES:
        rows.append((
            loc, 'Mount Lebanon', city, village, f'Old {loc}',
            pick(['coastal', 'harbour', 'underwater']),
            0, '/paths/placeholder', 'HFF Test Project', 'HFFTEST',
            'POINT', loc, f'A{random.randint(1, 5)}', '2024-06-01', '2024-09-30',
            pick(['I', 'II', 'III']), 'yes', 'surface', 'certain',
            'Test Supervisor', d(), 'sandy-clay', 'coastal flat', 'good', 'stable',
            'scattered blocks, column fragments', 'fishing nets, modern debris',
            f'{random.randint(0, 359)}', round(random.uniform(5, 50), 2),
            round(random.uniform(5, 20), 2), round(random.uniform(1, 12), 2),
            round(random.uniform(0.5, 5), 2), pick(MATERIALS),
            'dressed', 'regular courses', 'E-W', 'mortar',
        ))
    execute_values(cur, """
        INSERT INTO site_table (location_, mouhafasat, casa, village, antique_name, definition,
            find_check, sito_path, proj_name, proj_code, geometry_collection, name_site,
            area, date_start, date_finish, type_class, grab, survey_type, certainties,
            supervisor, date_fill, soil_type, topographic_setting, visibility, condition_state,
            features, disturbance, orientation, length_, width_, depth_, height_,
            material, finish_stone, coursing, direction_face, bonding_material)
        VALUES %s RETURNING id_sito, location_""", rows)
    return cur.fetchall()


def insert_site_points(cur, sites):
    for _, loc in sites:
        lon, lat = coord_lebanon()
        cur.execute("""
            INSERT INTO site_point (location, name_f_p, the_geom, coord)
            VALUES (%s, %s, ST_GeomFromEWKT(%s), %s)
        """, (loc, loc, f'SRID=4326;POINT({lon} {lat})', f'{lon},{lat}'))


def insert_dives(cur, sites):
    rows = []
    for i in range(10):
        loc = pick(sites)[1]
        rows.append((
            f'A{random.randint(1, 5)}', f'Diver Alpha {i+1}', f'Diver Beta {i+1}',
            f'Aux Diver {i+1}', f'Standby {i+1}',
            'Photographic documentation of the scattered amphorae field',
            'Recovered 3 diagnostic sherds; logged site condition',
            'Supervisor Marine', '200 bar', '80 bar',
            f'{random.randint(15, 24)} C', f'{random.randint(2, 15)} m',
            pick(['slight', 'moderate', 'strong']),
            f'{random.randint(5, 25)} kn {pick(["N", "NW", "NE", "W"])}',
            'air', f'{random.randint(8, 40)} m', '15 min',
            f'Survey transect {i+1} completed without incident',
            f'{random.randint(20, 55)} min',
            random.randint(20, 120), random.randint(0, 5),
            'Nikon D500 + Ikelite housing', '09:30', '10:25',
            d(), i + 1, 2024, '190 bar',
            '{"IMG_001.jpg", "IMG_002.jpg"}', '{"VID_001.mp4"}',
            loc, 'Layer I', '200 bar', '80 bar', '190 bar',
            biblio_list(loc), storage_list('UW'),
        ))
    execute_values(cur, """
        INSERT INTO dive_log (area_id, diver_1, diver_2, additional_diver, standby_diver,
            task, result, dive_supervisor, bar_start_diver1, bar_end_diver1,
            uw_temperature, uw_visibility, uw_current_, wind, breathing_mix,
            max_depth, surface_interval, comments_, bottom_time, photo_nbr, video_nbr,
            camera, time_in, time_out, date_, id_dive, years, dp_diver1,
            photo_id, video_id, site, layer, bar_start_diver2, bar_end_diver2, dp_diver2,
            biblio, storage_)
        VALUES %s RETURNING divelog_id""", rows)
    return [r[0] for r in cur.fetchall()]


def insert_artefacts(cur, sites, dives):
    rows = []
    for i in range(50):
        dive = random.choice(dives)
        loc = pick(sites)[1]
        lmin = round(random.uniform(2.0, 25.0), 1)
        rows.append((
            dive, f'ART-{i+1:03d}', pick(MATERIALS),
            'consolidation + cleaning',
            f'Fragment of {pick(OBJS)} from {pick(PERIODS)} period',
            pick(['yes', 'no']),
            i + 1, pick(['yes', 'no']), pick(['yes', 'no']),
            2024, d(), i + 1, pick(OBJS), pick(['conical', 'globular', 'ovoid', 'flat']),
            round(random.uniform(0.5, 3.5), 2), 'chisel marks',
            lmin, round(lmin + random.uniform(0.5, 5.0), 1),
            round(random.uniform(1.0, 10.0), 1), round(random.uniform(10.0, 20.0), 1),
            round(random.uniform(0.2, 2.0), 1), round(random.uniform(2.0, 6.0), 1),
            biblio_list(loc), storage_list('F'),
            random.randint(1, 30), pick(['yes', 'no']),
            loc, f'A{random.randint(1, 5)}',
        ))
    execute_values(cur, """
        INSERT INTO artefact_log (divelog_id, artefact_id, material, treatment, description,
            recovered, list, photographed, conservation_completed, years, date_, id_art,
            obj, shape, depth, tool_markings, lmin, lmax, wmin, wmax, tmin, tmax,
            biblio, storage_, box, washed, site, area)
        VALUES %s""", rows)


def insert_pottery(cur, sites, dives):
    rows = []
    for i in range(50):
        dive = random.choice(dives)
        loc = pick(sites)[1]
        form = pick(POT_FORMS)
        rows.append((
            dive, loc, d(), f'POT-{i+1:03d}', pick(['yes', 'no']), pick(['yes', 'no']),
            pick(['yes', 'no']), pick(['quartz', 'calcite', 'grog', 'mica']),
            f'{random.randint(5, 40)}%', pick(['rim', 'body', 'handle', 'base']),
            form, f'Hayes {random.randint(1, 100)}', loc,
            pick(['5YR 5/6', '7.5YR 6/4', '10YR 7/3', '2.5Y 8/2']),
            pick(['slipped', 'burnished', 'glazed', 'painted', 'plain']),
            'fair', f'{round(random.uniform(0.3, 8.0), 1)} m',
            storage_list('Pot'),
            pick(PERIODS), pick(['complete', 'fragmentary', 'restored']),
            samples_list(), pick(['yes', 'no']),
            str(round(random.uniform(5, 30), 1)),
            str(round(random.uniform(2, 20), 1)),
            str(round(random.uniform(3, 22), 1)),
            str(round(random.uniform(0.3, 2.0), 1)),
            str(round(random.uniform(1, 15), 1)),
            str(round(random.uniform(0.5, 10), 1)),
            str(round(random.uniform(0.2, 1.2), 1)),
            str(round(random.uniform(0.5, 2.0), 1)),
            2024, random.randint(1, 20),
            biblio_list(loc),
            f'Body sherd with wheel-turned ribs; {form} profile.',
            f'A{random.randint(1, 5)}',
            pick(['5YR 6/6', '10YR 7/3']),
            pick(['tableware', 'transport', 'cookware', 'storage']),
        ))
    execute_values(cur, """
        INSERT INTO pottery_table (divelog_id, site, date_, artefact_id, photographed,
            drawing, retrieved, inclusions, percent_inclusion, specific_part, form,
            typology, provenance, munsell_clay, surf_treatment, conservation, depth,
            storage_, period, state, samples, washed, dm, dr, db, th, ph, bh,
            thickmin, thickmax, years, box, biblio, description, area, munsell_surf, category)
        VALUES %s""", rows)


def insert_anchors(cur, sites, dives):
    rows = []
    for i in range(50):
        dive = random.choice(dives)
        loc = pick(sites)[1]
        rows.append((
            loc, dive, f'ANC-{i+1:03d}', pick(STONES), pick(ANCHOR_TYPES),
            pick(['triangular', 'trapezoidal', 'rectangular']),
            pick(['single', 'paired', 'multiple']),
            pick(['none', 'greek letters', 'phoenician mark', 'cross']),
            pick(['calcareous', 'volcanic', 'metamorphic']),
            f'{random.randint(40, 400)} kg',
            pick(['local', 'Aegean', 'Cypriot', 'Egyptian']),
            f'Frost 1963 cat. {random.randint(1, 200)}',
            pick(['type A', 'type B', 'type C']),
            pick(['yes', 'no']), pick(['yes', 'no']), pick(['yes', 'no']),
            2024, d(),
            round(random.uniform(3, 45), 2), 'tool marks',
            f'Weathered surface, stone identified as {pick(STONES)}.',
            'petrography to be done',
            round(random.uniform(40, 120), 1), round(random.uniform(30, 90), 1),
            round(random.uniform(10, 25), 1), round(random.uniform(25, 60), 1),
            round(random.uniform(20, 50), 1), round(random.uniform(15, 40), 1),
            round(random.uniform(2, 10), 1), round(random.uniform(2, 10), 1),
            round(random.uniform(2, 10), 1), round(random.uniform(2, 10), 1),
            round(random.uniform(8, 20), 1), round(random.uniform(5, 15), 1),
            round(random.uniform(4, 12), 1), round(random.uniform(4, 12), 1),
            round(random.uniform(4, 12), 1),
        ))
    execute_values(cur, """
        INSERT INTO anchor_table (site, divelog_id, anchors_id, stone_type, anchor_type,
            anchor_shape, type_hole, inscription, petrography, weight, origin, comparison,
            typology, recovered, photographed, conservation_completed, years, date_,
            depth, tool_markings, description_i, petrography_r,
            ll, rl, ml, tw, bw, mw, rtt, ltt, rtb, ltb, tt, bt, td, rd, ld)
        VALUES %s""", rows)


def insert_shipwrecks(cur, sites):
    rows = []
    for i in range(10):
        loc = pick(sites)[1]
        rows.append((
            f'WRK-{i+1:03d}', f'The {pick(["Swan","Falcon","Star","Pearl","Dolphin"])} of {loc}',
            f'{pick(["Beirut","Alexandria","Genoa","Venice"])} Yard',
            f'A{random.randint(1, 5)}',
            pick(['military', 'merchant', 'fishing', 'passenger']),
            pick(['certain', 'probable', 'possible']),
            pick(PROPULSIONS), pick(['wood', 'iron', 'steel', 'composite']),
            pick(['Ottoman', 'Venetian', 'Genoese', 'French', 'British', 'Lebanese']),
            pick(['galley', 'brig', 'schooner', 'caravel', 'dhow']),
            f'Shipowner {i+1}', pick(['trade', 'war', 'transport']),
            f'Yard {random.randint(1, 9)}', pick(WRECK_CAUSES),
            f'Diver Team {i+1}', pick(['intact', 'broken', 'scattered']),
            pick(['wooden hull', 'metal hull', 'mixed']),
            f'{random.randint(0, 45)} deg',
            f'{random.randint(5, 50)}-{random.randint(50, 80)} m',
        ))
    execute_values(cur, """
        INSERT INTO shipwreck_table (code_id, name_vessel, yard, area, category, confidence,
            propulsion, material, nationality, type, owner, purpose, builder, cause,
            divers, wreck, composition, inclination, depth_max_min)
        VALUES %s RETURNING id_shipwreck, name_vessel""", rows)
    return cur.fetchall()


def insert_shipwreck_locations(cur, wrecks):
    for wid, name in wrecks:
        lon, lat = coord_lebanon()
        cur.execute("""
            INSERT INTO shipwreck_location (code, nationality, name_vessel, the_geom)
            VALUES (%s, %s, %s, ST_GeomFromEWKT(%s))
        """, (f'WRK-{wid:03d}', 'Lebanese', name, f'SRID=4326;POINT({lon} {lat})'))


def main():
    conn = psycopg2.connect(**DSN)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        print('→ sites…')
        sites = insert_sites(cur)
        print(f'   {len(sites)} sites')

        print('→ site geometries…')
        insert_site_points(cur, sites)

        print('→ dives…')
        dives = insert_dives(cur, sites)
        print(f'   {len(dives)} dives')

        print('→ 50 artefacts…')
        insert_artefacts(cur, sites, dives)

        print('→ 50 pottery…')
        insert_pottery(cur, sites, dives)

        print('→ 50 anchors…')
        insert_anchors(cur, sites, dives)

        print('→ 10 shipwrecks…')
        wrecks = insert_shipwrecks(cur, sites)

        print('→ shipwreck geometries…')
        insert_shipwreck_locations(cur, wrecks)

        conn.commit()
        print('\nOK — commit done.')
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
