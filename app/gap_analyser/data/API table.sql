-- Create API table
CREATE TABLE api (
    api_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_name TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_section (
    section_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_id INTEGER NOT NULL,
    section_name TEXT NOT NULL,
    section_display_name TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (api_id) REFERENCES api(api_id)
);


-- Create Pattern Details table
CREATE TABLE pattern_details (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL UNIQUE,
    pattern_description TEXT,
    pattern_prompt TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Create Section-Pattern Mapping table
CREATE TABLE section_pattern_mapping (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pattern_id) REFERENCES pattern_details(pattern_id),
    FOREIGN KEY (section_id) REFERENCES api_section(section_id)
);

INSERT INTO api (api_name) VALUES ('LATAM_OVRS');


INSERT INTO api_section (api_id, section_name, section_display_name)
VALUES ((SELECT api_id FROM api WHERE api_name = 'LATAM_OVRS'), 'passenger_list', 'paxList');

INSERT INTO api_section (api_id, section_name, section_display_name)
VALUES ((SELECT api_id FROM api WHERE api_name = 'LATAM_OVRS'), 'passenger_list', 'PassengerList');


INSERT INTO pattern_details (pattern_name, pattern_description, pattern_prompt)
VALUES ('INF_IN_ADT', 'In PaxList/Pax, reference of INF passenger is returned in ADT passenger inside <PaxRefID>', NULL);

select a.api_id from api a, api_section aps, pattern_details pd, section_pattern_mapping spm
where a.api_id = aps.api_id
and aps.section_id = spm.section_id
and spm.pattern_id = pd.pattern_id
and aps.section_display_name = 'paxList';
