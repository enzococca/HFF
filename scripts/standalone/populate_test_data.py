# -*- coding: utf-8 -*-
"""
Script to populate HFF database with test data for all forms.
"""

import psycopg2
from datetime import datetime, date
import random

# Database connection
DB_CONFIG = {
    'dbname': 'hff',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def populate_site(cursor):
    """Insert 1 site record."""
    print("Populating site_table...")

    cursor.execute("""
        INSERT INTO site_table (
            location_, name_site, area, country, mouhafasat, village,
            date_start, date_finish, type_class, grab, survey_type,
            sito_path, definition, description, supervisor, visibility,
            condition_state, features, interpretation, proj_name, proj_code
        ) VALUES (
            'Mediterranean Coast', 'Test Archaeological Site Alpha', 'Area A',
            'Italy', 'Coastal Province', 'Porto Antico',
            '2023-01-15', '2023-12-20', 'Maritime', 'Yes', 'Underwater Survey',
            '/path/to/site', 'Archaeological Maritime Site',
            'Primary test site for underwater archaeological survey with multiple shipwreck finds',
            'Dr. Marco Rossi', 'Good', 'Stable',
            'Multiple shipwrecks, anchor deposits, scattered artifacts',
            'Major ancient harbor with evidence of maritime trade',
            'HFF Maritime Survey', 'HFF-2023-001'
        )
        ON CONFLICT DO NOTHING
        RETURNING id_sito
    """)

    result = cursor.fetchone()
    if result:
        print(f"  Created site with ID: {result[0]}")
    else:
        print("  Site already exists or conflict")

def populate_shipwreck(cursor):
    """Insert 10 shipwreck records."""
    print("Populating shipwreck_table...")

    shipwrecks = [
        ('SW-001', 'Merchant Alpha', 'Shipyard A', 'Area A', 'Merchant', 'High', 'Sail', 'Wood', 'Greek', 'Cargo Vessel', 'Unknown', 'Trade', 'Greek Shipyard', 'Storm', 'Team Alpha', 'Intact', 'Timber', '15 degrees', '25-28m', 'GPS', '35.5123', 'Good', '14.2345', 'Prof. Smith', 45.5, 8.2, 3.5, 2.1, 42.0, 7.8, 3.2, 'The Greek Trader', '320 BC', '280 BC', 'Well-preserved Greek merchant vessel with amphora cargo', 'Discovered in 1995, systematic excavation ongoing', 'Amphora, anchors, hull timbers', 'WreckAlpha', 'Active excavation', 'Smith 2020, Jones 2018', 'Underwater storage'),
        ('SW-002', 'Warship Beta', 'Naval Arsenal', 'Area B', 'Military', 'Medium', 'Oar', 'Wood', 'Roman', 'Trireme', 'Roman Navy', 'Military', 'Roman Arsenal', 'Battle', 'Team Beta', 'Scattered', 'Oak', '30 degrees', '32-35m', 'Survey', '35.5234', 'Medium', '14.2456', 'Dr. Brown', 35.0, 5.5, 2.8, 1.5, 32.0, 5.0, 2.5, 'The Roman Warrior', '120 BC', '90 BC', 'Roman warship remains with bronze ram', 'Battle damage evident, ram recovered 2010', 'Ram, oars, weapons', 'WreckBeta', 'Protected site', 'Brown 2015', 'Museum storage'),
        ('SW-003', 'Fisher Gamma', 'Local Yard', 'Area A', 'Fishing', 'Low', 'Sail', 'Wood', 'Phoenician', 'Fishing Boat', 'Local Fisher', 'Fishing', 'Local Builder', 'Weather', 'Team Alpha', 'Fragmentary', 'Cedar', 'Flat', '18-20m', 'GPS', '35.5345', 'Good', '14.2567', 'Dr. White', 12.0, 3.5, 1.2, 0.8, 11.5, 3.2, 1.0, 'Little Fisher', '480 BC', '450 BC', 'Small Phoenician fishing vessel', 'Net weights and fishing gear found', 'Nets, weights, hooks', 'WreckGamma', 'Documented', 'White 2019', 'On-site'),
        ('SW-004', 'Cargo Delta', 'Byzantine Yard', 'Area C', 'Merchant', 'High', 'Sail', 'Wood', 'Byzantine', 'Round Ship', 'Byzantine Merchant', 'Trade', 'Constantinople', 'Fire', 'Team Beta', 'Well Preserved', 'Pine', '10 degrees', '42-48m', 'GPS', '35.5456', 'Excellent', '14.2678', 'Prof. Green', 28.0, 9.5, 4.2, 2.8, 26.5, 9.0, 4.0, 'The Byzantine Star', '620 AD', '680 AD', 'Byzantine merchant with intact cargo hold', 'Fire damage on deck, cargo preserved', 'Amphorae, coins, tools', 'WreckDelta', 'Ongoing survey', 'Green 2021', 'Protected area'),
        ('SW-005', 'Transport Epsilon', 'Ottoman Yard', 'Area B', 'Transport', 'Medium', 'Sail', 'Wood', 'Ottoman', 'Galley', 'Ottoman Navy', 'Military Transport', 'Istanbul', 'Grounding', 'Team Alpha', 'Partial', 'Oak', '25 degrees', '26-30m', 'Survey', '35.5567', 'Good', '14.2789', 'Dr. Black', 38.0, 7.0, 3.0, 2.0, 35.5, 6.5, 2.8, 'Sultan Express', '1620 AD', '1680 AD', 'Ottoman military transport vessel', 'Cannons and supplies cargo', 'Cannons, supplies, rigging', 'WreckEpsln', 'Protected', 'Black 2017', 'Naval museum'),
        ('SW-006', 'Galley Zeta', 'Venetian Arsenal', 'Area A', 'Military', 'High', 'Oar/Sail', 'Wood', 'Venetian', 'War Galley', 'Venice Republic', 'Patrol', 'Venice', 'Combat', 'Team Beta', 'Scattered', 'Larch', '45 degrees', '15-18m', 'GPS', '35.5678', 'Medium', '14.2890', 'Prof. Blue', 42.0, 6.0, 2.5, 1.8, 40.0, 5.5, 2.2, 'Lion of Venice', '1420 AD', '1480 AD', 'Venetian war galley with oar remains', 'Battle damage, oars scattered', 'Oars, weapons, armor', 'WreckZeta', 'Survey complete', 'Blue 2014', 'Archive'),
        ('SW-007', 'Barge Eta', 'River Yard', 'Area C', 'Cargo', 'Low', 'None', 'Wood', 'Roman', 'River Barge', 'Roman State', 'Stone Transport', 'Local', 'Overload', 'Team Alpha', 'Intact Hull', 'Oak', 'Flat', '20-22m', 'GPS', '35.5789', 'Good', '14.2901', 'Dr. Gray', 25.0, 8.0, 1.5, 1.0, 24.0, 7.5, 1.2, 'Stone Carrier', '180 AD', '240 AD', 'Roman stone transport barge', 'Marble blocks still in cargo hold', 'Marble, tools, ropes', 'WreckEta', 'Protected', 'Gray 2016', 'On-site'),
        ('SW-008', 'Trader Theta', 'Arab Shipyard', 'Area B', 'Merchant', 'Medium', 'Sail', 'Wood', 'Arab', 'Dhow', 'Arab Merchant', 'Trade', 'Alexandria', 'Storm', 'Team Beta', 'Partial', 'Teak', '20 degrees', '35-38m', 'Survey', '35.5890', 'Medium', '14.3012', 'Prof. Red', 22.0, 6.5, 2.8, 1.5, 20.5, 6.0, 2.5, 'Desert Wind', '820 AD', '880 AD', 'Arab trading vessel with glass cargo', 'Excellent glass preservation', 'Glass, ceramics, spices', 'WreckTheta', 'Active excavation', 'Red 2022', 'Climate storage'),
        ('SW-009', 'Galleon Iota', 'Spanish Yard', 'Area A', 'Military', 'High', 'Sail', 'Wood', 'Spanish', 'Galleon', 'Spanish Crown', 'Escort', 'Cadiz', 'Battle', 'Team Alpha', 'Scattered', 'Oak', '35 degrees', '52-58m', 'GPS', '35.5901', 'Good', '14.3123', 'Dr. Gold', 55.0, 12.0, 5.5, 3.5, 52.0, 11.5, 5.0, 'Santa Maria II', '1560 AD', '1620 AD', 'Spanish galleon with armament', 'Cannons and treasure reported', 'Cannons, coins, navigation', 'WreckIota', 'Protected', 'Gold 2020', 'Naval museum'),
        ('SW-010', 'Fisher Kappa', 'Local Yard', 'Area C', 'Fishing', 'Low', 'Sail', 'Wood', 'Local', 'Traditional', 'Local Family', 'Fishing', 'Local', 'Storm', 'Team Beta', 'Complete', 'Pine', '5 degrees', '10-14m', 'GPS', '35.6012', 'Excellent', '14.3234', 'Prof. Silver', 10.0, 3.0, 1.0, 0.6, 9.5, 2.8, 0.8, 'Morning Star', '1820 AD', '1880 AD', 'Traditional fishing boat well preserved', 'Recent wreck with equipment', 'Nets, pots, tools', 'WreckKappa', 'Documented', 'Silver 2023', 'Local museum'),
    ]

    for s in shipwrecks:
        cursor.execute("""
            INSERT INTO shipwreck_table (
                code_id, name_vessel, yard, area, category, confidence, propulsion, material,
                nationality, type, owner, purpose, builder, cause, divers, wreck, composition,
                inclination, depth_max_min, depth_quality, latitude, position_quality_1, longitude,
                consulties, l, w, d, t, cl, cw, cd, nickname, date_built, date_lost,
                description, history, list, name, status, biblio, storage_
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, s)

    print(f"  Inserted {len(shipwrecks)} shipwreck records")

def populate_anchor(cursor):
    """Insert 10 anchor records."""
    print("Populating anchor_table...")

    anchors = [
        ('Mediterranean Coast', 1, 'ANC-001', 'Limestone', 'Stone Anchor', 'Triangular', 'Single', 'MARE DEUS', 'Micritic limestone', '85.5', 'Local', 'Similar to Byblos type', 'Type A1', 'Yes', 'Yes', 'Yes', 2023, '2023-06-15', 25.5, 'Chisel marks', 'Well-preserved limestone anchor', 'Standard Mediterranean', 85.0, 80.0, 75.0, 45.0, 42.0, 40.0, 12.0, 11.0, 10.0, 9.0, 8.0, 7.0, 15.0, 14.0, 13.0, 5.0, 4.5, 4.0, 6.0, 5.5, 5.0, 6.5, 6.0, 5.5, 7.0, 6.5, 6.0, 7.5, 7.0, 6.5, 'Area A', 8.0, 3.5, 8.5, 8.0, 9.0, 9.5, 1, 'Smith 2020', 'Storage A'),
        ('Mediterranean Coast', 2, 'ANC-002', 'Basalt', 'Stone Anchor', 'Pyramidal', 'Triple', '', 'Volcanic basalt', '120.0', 'Imported', 'Ugarit type', 'Type B2', 'No', 'Yes', 'No', 2023, '2023-06-16', 32.0, 'Rope grooves', 'Large basalt anchor with three holes', 'Levantine type', 95.0, 90.0, 85.0, 55.0, 52.0, 50.0, 18.0, 17.0, 16.0, 15.0, 14.0, 13.0, 20.0, 19.0, 18.0, 7.0, 6.5, 6.0, 8.0, 7.5, 7.0, 8.5, 8.0, 7.5, 9.0, 8.5, 8.0, 9.5, 9.0, 8.5, 'Area B', 10.0, 5.0, 10.5, 10.0, 11.0, 11.5, 1, 'Jones 2019', 'Storage B'),
        ('Mediterranean Coast', 3, 'ANC-003', 'Granite', 'Stone Anchor', 'Rectangular', 'Double', '', 'Pink granite', '95.0', 'Egypt', 'Egyptian type', 'Type C1', 'Yes', 'Yes', 'Yes', 2023, '2023-06-17', 18.5, 'Polish marks', 'Egyptian granite anchor', 'Nile delta origin', 70.0, 68.0, 65.0, 38.0, 36.0, 34.0, 10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 12.0, 11.5, 11.0, 4.0, 3.8, 3.5, 5.0, 4.8, 4.5, 5.5, 5.2, 5.0, 6.0, 5.8, 5.5, 6.5, 6.2, 6.0, 'Area A', 7.0, 3.0, 7.5, 7.2, 8.0, 8.5, 1, 'Brown 2021', 'Storage A'),
        ('Mediterranean Coast', 4, 'ANC-004', 'Sandstone', 'Stone Anchor', 'Irregular', 'Single', '', 'Red sandstone', '65.0', 'Local', 'Local type', 'Type D1', 'No', 'No', 'No', 2023, '2023-06-18', 45.0, 'Natural shape', 'Simple sandstone weight', 'Expedient anchor', 55.0, 52.0, 50.0, 30.0, 28.0, 26.0, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 10.0, 9.5, 9.0, 3.0, 2.8, 2.5, 4.0, 3.8, 3.5, 4.5, 4.2, 4.0, 5.0, 4.8, 4.5, 5.5, 5.2, 5.0, 'Area C', 6.0, 2.5, 6.5, 6.2, 7.0, 7.5, 1, 'White 2022', 'On-site'),
        ('Mediterranean Coast', 5, 'ANC-005', 'Marble', 'Stone Anchor', 'Trapezoidal', 'Double', 'POSEIDON', 'White marble', '150.0', 'Greece', 'Greek votive', 'Type E1', 'Yes', 'Yes', 'Yes', 2023, '2023-06-19', 28.0, 'Carved inscription', 'Votive marble anchor with inscription', 'Dedicatory anchor', 100.0, 95.0, 90.0, 60.0, 58.0, 55.0, 15.0, 14.5, 14.0, 13.5, 13.0, 12.5, 18.0, 17.5, 17.0, 6.0, 5.8, 5.5, 7.0, 6.8, 6.5, 7.5, 7.2, 7.0, 8.0, 7.8, 7.5, 8.5, 8.2, 8.0, 'Area A', 9.0, 4.0, 9.5, 9.2, 10.0, 10.5, 1, 'Green 2020', 'Museum'),
        ('Mediterranean Coast', 6, 'ANC-006', 'Lead Stock', 'Composite', 'Bar Shape', 'None', '', 'Cast lead', '45.0', 'Roman', 'Roman admiralty', 'Type F1', 'Yes', 'Yes', 'No', 2023, '2023-06-20', 15.0, 'Casting seams', 'Roman lead anchor stock', 'Removable stock type', 95.0, 90.0, 88.0, 15.0, 14.0, 13.0, 8.0, 7.8, 7.5, 7.0, 6.8, 6.5, 10.0, 9.8, 9.5, 2.5, 2.3, 2.0, 3.5, 3.3, 3.0, 4.0, 3.8, 3.5, 4.5, 4.3, 4.0, 5.0, 4.8, 4.5, 'Area B', 5.5, 2.0, 6.0, 5.8, 6.5, 7.0, 2, 'Black 2018', 'Storage B'),
        ('Mediterranean Coast', 7, 'ANC-007', 'Iron', 'Metal Anchor', 'Admiralty', 'Fixed Stock', '', 'Wrought iron', '280.0', 'European', 'Post-medieval', 'Type G1', 'No', 'Yes', 'No', 2023, '2023-06-21', 38.0, 'Forge marks', 'Large iron anchor heavily corroded', 'European admiralty type', 180.0, 175.0, 170.0, 120.0, 115.0, 110.0, 25.0, 24.0, 23.0, 22.0, 21.0, 20.0, 30.0, 29.0, 28.0, 10.0, 9.5, 9.0, 12.0, 11.5, 11.0, 13.0, 12.5, 12.0, 14.0, 13.5, 13.0, 15.0, 14.5, 14.0, 'Area A', 16.0, 8.0, 17.0, 16.5, 18.0, 19.0, 1, 'Gray 2019', 'Conservation'),
        ('Mediterranean Coast', 8, 'ANC-008', 'Bronze', 'Metal Anchor', 'Fluked', 'Hinged', '', 'Cast bronze', '35.0', 'Greek', 'Hellenistic type', 'Type H1', 'Yes', 'Yes', 'Yes', 2023, '2023-06-22', 22.0, 'Decorative', 'Ornate bronze anchor', 'Ceremonial or small vessel', 60.0, 58.0, 55.0, 35.0, 33.0, 31.0, 6.0, 5.8, 5.5, 5.0, 4.8, 4.5, 8.0, 7.8, 7.5, 2.0, 1.8, 1.5, 3.0, 2.8, 2.5, 3.5, 3.2, 3.0, 4.0, 3.8, 3.5, 4.5, 4.2, 4.0, 'Area C', 5.0, 1.5, 5.5, 5.2, 6.0, 6.5, 1, 'Blue 2021', 'Museum'),
        ('Mediterranean Coast', 9, 'ANC-009', 'Wood/Stone', 'Composite', 'Traditional', 'Weighted', '', 'Oak and limestone', '55.0', 'Byzantine', 'Byzantine type', 'Type I1', 'No', 'No', 'No', 2023, '2023-06-23', 55.0, 'Lashing holes', 'Byzantine composite anchor', 'Stone weight with wooden frame', 75.0, 72.0, 70.0, 40.0, 38.0, 36.0, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 14.0, 13.5, 13.0, 4.5, 4.2, 4.0, 5.5, 5.2, 5.0, 6.0, 5.8, 5.5, 6.5, 6.2, 6.0, 7.0, 6.8, 6.5, 'Area B', 7.5, 3.5, 8.0, 7.8, 8.5, 9.0, 1, 'Red 2022', 'On-site'),
        ('Mediterranean Coast', 10, 'ANC-010', 'Iron Stockless', 'Metal Anchor', 'Stockless', 'Pivot', '', 'Cast iron', '450.0', 'Modern', 'Modern commercial', 'Type J1', 'No', 'Yes', 'No', 2023, '2023-06-24', 12.0, 'Foundry marks', 'Modern stockless anchor', 'Recent loss', 200.0, 195.0, 190.0, 150.0, 145.0, 140.0, 35.0, 34.0, 33.0, 32.0, 31.0, 30.0, 40.0, 39.0, 38.0, 15.0, 14.5, 14.0, 18.0, 17.5, 17.0, 19.0, 18.5, 18.0, 20.0, 19.5, 19.0, 21.0, 20.5, 20.0, 'Area A', 22.0, 12.0, 23.0, 22.5, 24.0, 25.0, 1, 'Gold 2023', 'Port authority'),
    ]

    for a in anchors:
        cursor.execute("""
            INSERT INTO anchor_table (
                site, divelog_id, anchors_id, stone_type, anchor_type, anchor_shape, type_hole,
                inscription, petrography, weight, origin, comparison, typology, recovered,
                photographed, conservation_completed, years, date_, depth, tool_markings,
                description_i, petrography_r, ll, rl, ml, tw, bw, mw, rtt, ltt, rtb, ltb,
                tt, bt, td, rd, ld, tde, rde, lde, tfl, rfl, lfl, tfr, rfr, lfr, tfb, rfb, lfb,
                tft, rft, lft, area, bd, bde, bfl, bfr, bfb, bft, qty, biblio, storage_
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, a)

    print(f"  Inserted {len(anchors)} anchor records")

def populate_artefact(cursor):
    """Insert 10 artefact records."""
    print("Populating artefact_log...")

    artefacts = [
        (1, 'ART-001', 'Ceramic', 'Desalination', 'Amphora handle with merchant stamp', 'Yes', 1, 'Yes', 'Yes', 2023, '2023-07-01', 'Amphora Handle', 'Ovoid', 25.5, 'Stamp impression', 8.5, 12.0, 4.0, 6.0, 1.5, 2.5, 'Smith 2020', 'Storage A', 1, 'Yes', 'Mediterranean Coast', 'Area A'),
        (2, 'ART-002', 'Metal', 'Electrolysis', 'Bronze coin Roman sestertius', 'Yes', 2, 'Yes', 'Yes', 2023, '2023-07-02', 'Coin', 'Circular', 18.5, 'Mint mark visible', 2.5, 2.8, 2.5, 2.8, 0.2, 0.3, 'Jones 2019', 'Numismatic cab', 2, 'Yes', 'Mediterranean Coast', 'Area A'),
        (3, 'ART-003', 'Metal', 'Stabilization', 'Lead fishing net weight conical', 'No', 3, 'Yes', 'No', 2023, '2023-07-03', 'Net Weight', 'Conical', 32.0, 'Rope groove', 5.0, 6.5, 3.0, 4.0, 3.0, 4.0, 'Brown 2021', 'Storage B', 3, 'No', 'Mediterranean Coast', 'Area B'),
        (4, 'ART-004', 'Glass', 'Consolidation', 'Glass unguentarium perfume bottle', 'Yes', 4, 'Yes', 'Yes', 2023, '2023-07-04', 'Unguentarium', 'Fusiform', 22.0, 'Blown glass', 10.0, 12.0, 2.5, 3.0, 2.5, 3.0, 'White 2022', 'Glass cabinet', 4, 'Yes', 'Mediterranean Coast', 'Area A'),
        (5, 'ART-005', 'Metal', 'Desalination', 'Copper ship nail for hull planking', 'No', 5, 'No', 'No', 2023, '2023-07-05', 'Ship Nail', 'Tapered', 28.0, 'Hammer marks', 12.0, 15.0, 0.8, 1.2, 0.8, 1.2, 'Green 2020', 'Storage C', 5, 'No', 'Mediterranean Coast', 'Area C'),
        (6, 'ART-006', 'Organic', 'Freeze-dry', 'Bone sewing needle complete', 'Yes', 6, 'Yes', 'Yes', 2023, '2023-07-06', 'Needle', 'Elongated', 15.0, 'Polish wear', 6.5, 7.0, 0.3, 0.4, 0.2, 0.3, 'Black 2018', 'Organic storage', 6, 'Yes', 'Mediterranean Coast', 'Area A'),
        (7, 'ART-007', 'Stone', 'Cleaning', 'Stone rotary quern fragment', 'No', 7, 'Yes', 'No', 2023, '2023-07-07', 'Quern', 'Disc', 20.0, 'Grinding surface', 25.0, 30.0, 25.0, 30.0, 8.0, 12.0, 'Gray 2019', 'Storage B', 7, 'No', 'Mediterranean Coast', 'Area B'),
        (8, 'ART-008', 'Metal', 'Electrolysis', 'Bronze fibula bow type', 'Yes', 8, 'Yes', 'Yes', 2023, '2023-07-08', 'Fibula', 'Bow', 18.0, 'Incised decoration', 5.5, 6.0, 2.0, 2.5, 0.5, 0.8, 'Blue 2021', 'Metal cabinet', 8, 'Yes', 'Mediterranean Coast', 'Area A'),
        (9, 'ART-009', 'Ceramic', 'Desalination', 'Oil lamp Roman type with maker mark', 'Yes', 9, 'Yes', 'Yes', 2023, '2023-07-09', 'Lamp', 'Volute', 12.0, 'Maker stamp', 9.0, 10.0, 6.5, 7.0, 2.5, 3.0, 'Red 2022', 'Lamp cabinet', 9, 'Yes', 'Mediterranean Coast', 'Area C'),
        (10, 'ART-010', 'Metal', 'Stabilization', 'Iron knife blade utility type', 'No', 10, 'Yes', 'No', 2023, '2023-07-10', 'Knife', 'Blade', 35.0, 'Forge scale', 15.0, 18.0, 3.0, 4.0, 0.4, 0.8, 'Gold 2023', 'Storage C', 10, 'No', 'Mediterranean Coast', 'Area B'),
    ]

    for a in artefacts:
        cursor.execute("""
            INSERT INTO artefact_log (
                divelog_id, artefact_id, material, treatment, description, recovered, list,
                photographed, conservation_completed, years, date_, obj, shape, depth,
                tool_markings, lmin, lmax, wmin, wmax, tmin, tmax, biblio, storage_, box,
                washed, site, area
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, a)

    print(f"  Inserted {len(artefacts)} artefact records")

def populate_pottery(cursor):
    """Insert 10 pottery records."""
    print("Populating pottery_table...")

    pottery = [
        (1, 'Mediterranean Coast', '2023-08-01', 'POT-001', 'Yes', 'Yes', 'Yes', 'Calcite', '10%', 'Handle', 'Amphora', 'Dressel 1A', 'Italy', '5YR 6/6', 'Slip', 'Complete', '25.5', 'Storage A', 'Late Republican', 'Good', 'Fabric sample', 'Yes', '35', '8', '8', '1.2', '28', '6', '0.8', '1.5', 2023, 1, 'Smith 2020', 'Transport amphora handle with stamp', 'Area A', '5YR 7/4', 'Transport', 'Yes', 1),
        (2, 'Mediterranean Coast', '2023-08-02', 'POT-002', 'Yes', 'Yes', 'No', 'Fine sand', '5%', 'Rim', 'Bowl', 'Terra Sigillata', 'Arezzo', '2.5YR 5/8', 'Gloss', 'Fragment', '18.5', 'Storage B', 'Early Imperial', 'Fair', 'XRF done', 'Yes', '22', '22', '18', '0.6', '4', '3', '0.4', '0.8', 2023, 2, 'Jones 2019', 'Fine ware bowl rim with stamp', 'Area A', '2.5YR 4/8', 'Table Ware', 'Yes', 2),
        (3, 'Mediterranean Coast', '2023-08-03', 'POT-003', 'No', 'No', 'No', 'Volcanic', '15%', 'Body', 'Cooking Pot', 'Local', 'Local', '7.5YR 5/4', 'Burnish', 'Sherd', '32.0', 'On-site', 'Hellenistic', 'Poor', 'None', 'No', '8', '6', '7', '0.9', '0', '0', '0.7', '1.1', 2023, 3, 'Brown 2021', 'Coarse ware cooking pot body sherd', 'Area B', '7.5YR 4/2', 'Cooking', 'No', 3),
        (4, 'Mediterranean Coast', '2023-08-04', 'POT-004', 'Yes', 'Yes', 'Yes', 'Ite', '8%', 'Rim/Handle', 'Jug', 'Pompeian Red', 'Campania', '10R 5/8', 'Paint', 'Partial', '22.0', 'Storage A', 'Imperial', 'Good', 'Thin section', 'Yes', '18', '12', '10', '0.5', '15', '8', '0.4', '0.7', 2023, 4, 'White 2022', 'Red slip jug with vertical handle', 'Area A', '10R 4/6', 'Table Ware', 'Yes', 1),
        (5, 'Mediterranean Coast', '2023-08-05', 'POT-005', 'Yes', 'Yes', 'No', 'Quartz', '12%', 'Complete', 'Plate', 'African Red Slip', 'Tunisia', '2.5YR 6/8', 'Slip', 'Complete', '15.0', 'Museum', 'Late Roman', 'Excellent', 'Published', 'Yes', '28', '28', '24', '0.7', '3', '2', '0.5', '0.9', 2023, 5, 'Green 2020', 'Complete ARS plate with stamp', 'Area C', '2.5YR 5/8', 'Table Ware', 'Yes', 1),
        (6, 'Mediterranean Coast', '2023-08-06', 'POT-006', 'No', 'No', 'No', 'Grog', '20%', 'Base', 'Storage Jar', 'LRA 1', 'Eastern Med', '5YR 5/6', 'Combed', 'Base', '28.0', 'Storage B', 'Byzantine', 'Fair', 'None', 'No', '15', '15', '12', '1.5', '0', '0', '1.2', '1.8', 2023, 6, 'Black 2018', 'Large storage jar base with combing', 'Area B', '5YR 5/4', 'Storage', 'No', 5),
        (7, 'Mediterranean Coast', '2023-08-07', 'POT-007', 'Yes', 'Yes', 'Yes', 'Fine', '3%', 'Complete', 'Lamp', 'Ephesus Type', 'Asia Minor', '7.5YR 6/4', 'Glaze', 'Complete', '20.0', 'Lamp cabinet', 'Hellenistic', 'Excellent', 'Published', 'Yes', '10', '10', '8', '0.4', '3', '2', '0.3', '0.5', 2023, 7, 'Gray 2019', 'Complete mold-made lamp with relief', 'Area A', '7.5YR 5/4', 'Lighting', 'Yes', 1),
        (8, 'Mediterranean Coast', '2023-08-08', 'POT-008', 'Yes', 'No', 'No', 'Micaceous', '7%', 'Neck', 'Unguentarium', 'Fusiform', 'Eastern', '10YR 7/3', 'Slip', 'Neck', '35.0', 'Storage A', 'Hellenistic', 'Good', 'None', 'Yes', '5', '4', '3', '0.3', '8', '0', '0.2', '0.4', 2023, 8, 'Blue 2021', 'Unguentarium neck fragment slipped', 'Area A', '10YR 6/3', 'Container', 'Yes', 2),
        (9, 'Mediterranean Coast', '2023-08-09', 'POT-009', 'Yes', 'Yes', 'No', 'Coarse', '25%', 'Rim', 'Mortarium', 'Italian', 'Central Italy', '5YR 6/4', 'Gritted', 'Rim', '12.0', 'Storage B', 'Imperial', 'Fair', 'Use-wear', 'Yes', '12', '12', '35', '1.8', '6', '0', '1.5', '2.2', 2023, 9, 'Red 2022', 'Mortarium rim with gritted interior', 'Area B', '5YR 5/4', 'Processing', 'Yes', 4),
        (10, 'Mediterranean Coast', '2023-08-10', 'POT-010', 'No', 'No', 'No', 'Very coarse', '30%', 'Body', 'Pithos', 'Local', 'Local', '7.5YR 5/4', 'Rope', 'Large sherd', '8.0', 'On-site', 'Iron Age', 'Poor', 'None', 'No', '25', '18', '20', '2.5', '0', '0', '2.0', '3.0', 2023, 10, 'Gold 2023', 'Large pithos body with rope decoration', 'Area C', '7.5YR 4/4', 'Storage', 'No', 8),
    ]

    for p in pottery:
        cursor.execute("""
            INSERT INTO pottery_table (
                divelog_id, site, date_, artefact_id, photographed, drawing, retrieved,
                inclusions, percent_inclusion, specific_part, form, typology, provenance,
                munsell_clay, surf_treatment, conservation, depth, storage_, period, state,
                samples, washed, dm, dr, db, th, ph, bh, thickmin, thickmax, years, box,
                biblio, description, area, munsell_surf, category, wheel_made, qty
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, p)

    print(f"  Inserted {len(pottery)} pottery records")

def populate_uw(cursor):
    """Insert 10 underwater (dive log) records."""
    print("Populating dive_log...")

    dives = [
        (1, 'Area A', 'John Smith', 'Maria Garcia', 'Tom Wilson', 'Paul Brown', 'Initial site survey and reconnaissance', 'Multiple artifacts located, site boundaries defined', 'Dr. James', '200', '80', '18.5', 'Good 15m', 'Weak', 'Light NW', 'Air', '25.5', '2:30', 'Excellent conditions for survey work', '75', 15, 8, 'Canon 5D', '09:30', '10:45', '2023-06-15', 2023, '12', 'PHOTO-001-010', 'VID-001-003', 'Mediterranean Coast', 'Layer 1', '200', '85', '10', 'Smith 2020', 'Equipment shed'),
        (2, 'Area A', 'Maria Garcia', 'John Smith', 'Lisa Chen', 'Mark Davis', 'Photogrammetric documentation of wreck', 'Complete 3D model dataset acquired', 'Dr. James', '210', '75', '19.0', 'Excellent 20m', 'None', 'Calm', 'Air', '32.0', '3:00', 'Perfect visibility for photogrammetry', '90', 45, 12, 'Sony A7R', '10:00', '11:30', '2023-06-16', 2023, '15', 'PHOTO-011-055', 'VID-004-008', 'Mediterranean Coast', 'Layer 1', '205', '70', '14', 'Jones 2019', 'Equipment shed'),
        (3, 'Area B', 'Tom Wilson', 'Paul Brown', 'John Smith', 'Maria Garcia', 'Test trench excavation north sector', 'Ceramic layer exposed, samples collected', 'Dr. White', '190', '90', '18.0', 'Good 12m', 'Weak', 'Light swell', 'Air', '18.5', '2:15', 'Some sediment disturbance from swell', '75', 8, 5, 'GoPro Hero', '08:45', '10:00', '2023-06-17', 2023, '8', 'PHOTO-056-063', 'VID-009-011', 'Mediterranean Coast', 'Layer 2', '185', '85', '7', 'Brown 2021', 'Conservation lab'),
        (4, 'Area C', 'Lisa Chen', 'Mark Davis', 'Tom Wilson', 'Paul Brown', 'Deep area reconnaissance survey', 'New wreck area identified at depth', 'Dr. James', '220', '60', '17.5', 'Moderate 8m', 'Moderate', 'Moderate chop', 'Nitrox 32', '45.0', '1:45', 'Technical dive to assess deep area', '45', 5, 3, 'Canon G7X', '14:00', '15:15', '2023-06-18', 2023, '25', 'PHOTO-064-068', 'VID-012-013', 'Mediterranean Coast', 'Layer 3', '215', '55', '22', 'White 2022', 'Equipment shed'),
        (5, 'Area A', 'John Smith', 'Lisa Chen', 'Maria Garcia', 'Tom Wilson', 'Artifact recovery operation', 'Three ceramic vessels raised safely', 'Dr. White', '195', '85', '19.5', 'Good 15m', 'Weak', 'Calm', 'Air', '28.0', '2:30', 'Successful recovery with lift bags', '90', 12, 6, 'Canon 5D', '09:00', '10:30', '2023-06-19', 2023, '10', 'PHOTO-069-080', 'VID-014-017', 'Mediterranean Coast', 'Layer 1', '190', '80', '9', 'Green 2020', 'Conservation lab'),
        (6, 'Area A', 'Maria Garcia', 'Tom Wilson', 'Lisa Chen', 'John Smith', 'In-situ conservation assessment', 'Treatment plan developed for anchor', 'Dr. James', '200', '90', '20.0', 'Excellent 18m', 'None', 'Calm', 'Air', '15.0', '1:30', 'Detailed condition recording completed', '60', 25, 10, 'Sony A7R', '11:00', '12:00', '2023-06-20', 2023, '5', 'PHOTO-081-105', 'VID-018-022', 'Mediterranean Coast', 'Layer 1', '195', '85', '4', 'Black 2018', 'Archive'),
        (7, 'Area B', 'Paul Brown', 'John Smith', 'Mark Davis', 'Lisa Chen', 'Video documentation of excavation', 'Full HD video record of context', 'Dr. White', '185', '80', '18.5', 'Good 14m', 'Weak', 'Light swell', 'Air', '38.0', '2:30', 'Complete video coverage achieved', '90', 3, 25, 'RED Cinema', '08:30', '10:00', '2023-06-21', 2023, '12', 'PHOTO-106-108', 'VID-023-047', 'Mediterranean Coast', 'Layer 2', '180', '75', '10', 'Gray 2019', 'Media archive'),
        (8, 'Area A', 'Tom Wilson', 'Maria Garcia', 'Paul Brown', 'Mark Davis', 'Main excavation area grid work', 'Grid sectors A1-A6 completed', 'Dr. James', '210', '70', '17.0', 'Moderate 10m', 'Moderate', 'Choppy', 'Air', '22.0', '1:45', 'Reduced visibility but grid completed', '75', 18, 8, 'Canon 5D', '10:30', '11:45', '2023-06-22', 2023, '8', 'PHOTO-109-126', 'VID-048-055', 'Mediterranean Coast', 'Layer 2', '205', '65', '7', 'Blue 2021', 'Equipment shed'),
        (9, 'Area C', 'Mark Davis', 'Lisa Chen', 'John Smith', 'Maria Garcia', 'Technical deep survey dive', 'Deep wreck fully mapped', 'Dr. White', '230', '50', '16.5', 'Good 12m', 'Weak', 'Calm', 'Trimix', '55.0', '1:30', 'Successful technical dive to 55m', '35', 8, 4, 'GoPro Hero', '09:15', '10:30', '2023-06-23', 2023, '35', 'PHOTO-127-134', 'VID-056-059', 'Mediterranean Coast', 'Layer 3', '225', '45', '30', 'Red 2022', 'Tech storage'),
        (10, 'Area A', 'Lisa Chen', 'Paul Brown', 'Tom Wilson', 'John Smith', 'New team member training dive', 'Training objectives met', 'Dr. James', '200', '120', '21.0', 'Excellent 20m', 'None', 'Calm', 'Air', '12.0', '1:45', 'Excellent training conditions', '75', 5, 2, 'Canon G7X', '13:00', '14:15', '2023-06-24', 2023, '5', 'PHOTO-135-139', 'VID-060-061', 'Mediterranean Coast', 'Layer 1', '195', '115', '4', 'Gold 2023', 'Training room'),
    ]

    for d in dives:
        cursor.execute("""
            INSERT INTO dive_log (
                divelog_id, area_id, diver_1, diver_2, additional_diver, standby_diver,
                task, result, dive_supervisor, bar_start_diver1, bar_end_diver1,
                uw_temperature, uw_visibility, uw_current_, wind, breathing_mix, max_depth,
                surface_interval, comments_, bottom_time, photo_nbr, video_nbr, camera,
                time_in, time_out, date_, years, dp_diver1, photo_id, video_id, site, layer,
                bar_start_diver2, bar_end_diver2, dp_diver2, biblio, storage_
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, d)

    print(f"  Inserted {len(dives)} dive log records")

def populate_anchor_con(cursor):
    """Insert 10 anchor conservation records."""
    print("Populating anchor_con...")

    records = [
        ('Mediterranean Coast', 'ANC-001', 'Complete anchor', 'Dr. Smith', '2023-07-01', '2023-08-15', 'Stable', 'Initial assessment complete', 'Standard dimensions recorded', 'Minor surface erosion', 'Light marine growth', 'Barnacles, algae', 'Mechanical cleaning', '2023-07-10'),
        ('Mediterranean Coast', 'ANC-002', 'Anchor body', 'Dr. Jones', '2023-07-05', '2023-09-01', 'In treatment', 'Desalination in progress', 'Conductivity monitored weekly', 'Surface pitting', 'Heavy concretion', 'Oysters, serpulids', 'Chemical treatment', '2023-07-15'),
        ('Mediterranean Coast', 'ANC-003', 'Upper section', 'Dr. Smith', '2023-07-10', '2023-08-20', 'Treated', 'Consolidation complete', 'PEG treatment documented', 'Stable', 'Removed', 'None remaining', 'Wax coating', '2023-07-08'),
        ('Mediterranean Coast', 'ANC-004', 'Fragment A', 'Dr. Brown', '2023-07-12', '', 'In treatment', 'Mechanical cleaning ongoing', 'Air scribe in use', 'Active deterioration', 'Thick calcareous', 'Coral growth', 'Air abrasion', '2023-07-20'),
        ('Mediterranean Coast', 'ANC-005', 'Inscribed face', 'Dr. Jones', '2023-07-15', '2023-08-30', 'Documented', '3D scanning complete', 'RTI imaging done', 'Weathered inscription', 'Light patina', 'Biofilm only', 'Laser cleaning', '2023-07-12'),
        ('Mediterranean Coast', 'ANC-006', 'Lead stock only', 'Dr. Smith', '2023-07-18', '', 'In treatment', 'Electrolytic reduction', 'Current monitored daily', 'Lead corrosion', 'Minimal', 'None', 'Electrolysis', '2023-07-25'),
        ('Mediterranean Coast', 'ANC-007', 'Iron anchor complete', 'Dr. Brown', '2023-07-20', '2023-10-15', 'Treated', 'Treatment complete', 'Tannic acid applied', 'Heavy corrosion', 'Iron corrosion products', 'Marine fouling', 'Phosphate conversion', '2023-08-01'),
        ('Mediterranean Coast', 'ANC-008', 'Bronze anchor', 'Dr. Jones', '2023-07-22', '2023-08-10', 'Stable', 'Assessment only', 'Bronze stable', 'Patina formation', 'Green patina', 'Cuprite layer', 'Benzotriazole', '2023-07-05'),
        ('Mediterranean Coast', 'ANC-009', 'Composite remains', 'Dr. Smith', '2023-07-25', '', 'In treatment', 'Wood conservation ongoing', 'PEG impregnation active', 'Wood degradation', 'Marine borer damage', 'Teredo damage', 'PEG treatment', '2023-07-18'),
        ('Mediterranean Coast', 'ANC-010', 'Modern anchor', 'Dr. Brown', '2023-07-28', '2023-08-05', 'Stable', 'Minimal treatment needed', 'Documentation only', 'Surface rust', 'Light rust', 'Paint remnants', 'Rust conversion', '2023-07-02'),
    ]

    for r in records:
        cursor.execute("""
            INSERT INTO anchor_con (
                site, anchor_id, obj_partial, author, star_date, end_date,
                state_conservation, observation, measure, damage, concretion, bio,
                procedure, desalination_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, r)

    print(f"  Inserted {len(records)} anchor conservation records")

def populate_artefact_con(cursor):
    """Insert 10 artefact conservation records."""
    print("Populating artefact_con...")

    records = [
        ('Mediterranean Coast', 'ART-001', 'Complete handle', 'Cons. A', '2023-08-01', '2023-08-20', 'Good', 'Soft brush cleaning complete', 'Minor salt damage', 'Active corrosion', 'Light marine growth', 'Barnacles', 'Mechanical cleaning', '2023-08-05'),
        ('Mediterranean Coast', 'ART-002', 'Coin obverse', 'Cons. B', '2023-08-03', '', 'In treatment', 'Electrolytic cleaning', 'Bronze disease active', 'Chloride corrosion', 'Cuprite crust', 'None', 'Electrolysis', '2023-08-08'),
        ('Mediterranean Coast', 'ART-003', 'Weight complete', 'Cons. A', '2023-08-05', '2023-08-15', 'Treated', 'Lead stabilized', 'Surface lead carbonate', 'Lead corrosion', 'White crust', 'None', 'Chelation', '2023-08-02'),
        ('Mediterranean Coast', 'ART-004', 'Glass vessel', 'Cons. C', '2023-08-08', '', 'In treatment', 'Fragment joining', 'Glass devitrification', 'Iridescence', 'Surface weathering', 'None', 'Paraloid consolidation', '2023-08-10'),
        ('Mediterranean Coast', 'ART-005', 'Nail shaft', 'Cons. B', '2023-08-10', '2023-09-01', 'Documented', 'X-ray completed', 'Copper corrosion', 'Active corrosion', 'Corrosion crust', 'None', 'Documentation only', '2023-08-01'),
        ('Mediterranean Coast', 'ART-006', 'Bone needle', 'Cons. A', '2023-08-12', '2023-08-25', 'Treated', 'Freeze-dry complete', 'Protein degradation', 'None', 'None', 'Bacterial', 'Freeze-drying', '2023-08-15'),
        ('Mediterranean Coast', 'ART-007', 'Quern fragment', 'Cons. C', '2023-08-15', '2023-08-22', 'Stable', 'Mechanical cleaning done', 'Salt efflorescence', 'None', 'Calcium carbonate', 'Algae', 'Desalination', '2023-08-18'),
        ('Mediterranean Coast', 'ART-008', 'Fibula complete', 'Cons. B', '2023-08-18', '', 'Under study', 'XRF analysis scheduled', 'Bronze patina stable', 'Stable patina', 'Green patina', 'None', 'BTA treatment', '2023-08-12'),
        ('Mediterranean Coast', 'ART-009', 'Lamp complete', 'Cons. A', '2023-08-20', '2023-09-05', 'Treated', 'Conservation complete', 'Soot deposits interior', 'None', 'Light calcite', 'None', 'Cleaning', '2023-08-22'),
        ('Mediterranean Coast', 'ART-010', 'Blade fragment', 'Cons. C', '2023-08-22', '', 'In treatment', 'Ongoing treatment', 'Iron corrosion severe', 'Heavy corrosion', 'Rust concretion', 'None', 'Electrolysis', '2023-08-25'),
    ]

    for r in records:
        cursor.execute("""
            INSERT INTO artefact_con (
                site, artefact_id, obj_partial, author, star_date, end_date,
                state_conservation, observation, damage, corrosion, concretion, bio,
                procedure, desalination_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, r)

    print(f"  Inserted {len(records)} artefact conservation records")

def populate_pottery_con(cursor):
    """Insert 10 pottery conservation records."""
    print("Populating pottery_con...")

    records = [
        ('Mediterranean Coast', 'POT-001', 'Handle with stamp', 'Cer. Spec. A', '2023-09-01', '2023-09-20', 'Good', 'Desalination complete', 'Handle attachment', 'Salt crystallization', 'Marine growth', 'Encrustation', 'Fresh water baths', '2023-09-05'),
        ('Mediterranean Coast', 'POT-002', 'Rim fragment', 'Cer. Spec. B', '2023-09-05', '', 'In treatment', 'Slow drying in progress', 'Slip preservation', 'Spalling risk', 'None', 'None', 'Controlled drying', '2023-09-08'),
        ('Mediterranean Coast', 'POT-003', 'Body sherd', 'Cer. Spec. A', '2023-09-10', '2023-09-15', 'Stable', 'Documentation only', 'Complete sherd', 'Weathered surface', 'Light marine', 'Algae', 'Cleaning', '2023-09-02'),
        ('Mediterranean Coast', 'POT-004', 'Reconstructed vessel', 'Cer. Spec. C', '2023-09-12', '', 'In treatment', 'Gap filling ongoing', 'Multiple joins', 'Edge damage', 'None', 'None', 'Plaster fills', '2023-09-15'),
        ('Mediterranean Coast', 'POT-005', 'Complete plate', 'Cer. Spec. B', '2023-09-15', '2023-09-25', 'Treated', 'Conservation complete', 'Complete vessel', 'Minor chips', 'None', 'None', 'Minimal intervention', '2023-09-10'),
        ('Mediterranean Coast', 'POT-006', 'Storage jar base', 'Cer. Spec. A', '2023-09-18', '2023-10-01', 'Treated', 'Consolidation done', 'Base only', 'Friable fabric', 'Calcium deposits', 'Algae', 'Primal consolidation', '2023-09-20'),
        ('Mediterranean Coast', 'POT-007', 'Complete lamp', 'Cer. Spec. C', '2023-09-20', '2023-09-28', 'Excellent', 'Display ready', 'Complete with soot', 'None', 'None', 'None', 'Light cleaning', '2023-09-12'),
        ('Mediterranean Coast', 'POT-008', 'Neck fragment', 'Cer. Spec. B', '2023-09-22', '', 'Under study', 'Analysis pending', 'Neck only', 'Surface wear', 'Light deposits', 'None', 'Sampling', '2023-09-25'),
        ('Mediterranean Coast', 'POT-009', 'Mortarium rim', 'Cer. Spec. A', '2023-09-25', '2023-10-05', 'Treated', 'Treatment complete', 'Rim section', 'Use wear', 'Gritted surface', 'None', 'Cleaning', '2023-09-28'),
        ('Mediterranean Coast', 'POT-010', 'Pithos sherd', 'Cer. Spec. C', '2023-09-28', '2023-10-02', 'Stable', 'Storage ready', 'Large body sherd', 'Weathered', 'Heavy deposits', 'Marine boring', 'Desalination', '2023-09-18'),
    ]

    for r in records:
        cursor.execute("""
            INSERT INTO pottery_con (
                site, pottery_id, obj_partial, author, star_date, end_date,
                state_conservation, observation, conserved_element, damage, concretion, bio,
                procedure, desalination_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, r)

    print(f"  Inserted {len(records)} pottery conservation records")

def main():
    print("=" * 60)
    print("HFF Database Test Data Population Script")
    print("=" * 60)
    print(f"\nConnecting to database: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        print("\nPopulating tables...\n")

        # Populate all tables
        populate_site(cursor)
        populate_shipwreck(cursor)
        populate_anchor(cursor)
        populate_artefact(cursor)
        populate_pottery(cursor)
        populate_uw(cursor)
        populate_anchor_con(cursor)
        populate_artefact_con(cursor)
        populate_pottery_con(cursor)

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        print("SUCCESS: All test data has been inserted!")
        print("=" * 60)

        # Show record counts
        print("\nRecord counts:")
        tables = [
            ('site_table', 'Site'),
            ('shipwreck_table', 'Shipwreck'),
            ('anchor_table', 'Anchor'),
            ('artefact_log', 'Artefact'),
            ('pottery_table', 'Pottery'),
            ('dive_log', 'Dive Log (UW)'),
            ('anchor_con', 'Anchor Conservation'),
            ('artefact_con', 'Artefact Conservation'),
            ('pottery_con', 'Pottery Conservation'),
        ]

        for table_name, display_name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {display_name}: {count} records")
            except Exception as e:
                print(f"  {display_name}: Error - {e}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
