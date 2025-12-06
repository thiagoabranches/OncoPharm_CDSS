-- Tabela: EPISODE (Baseado no OMOP Oncology Extension)
CREATE TABLE IF NOT EXISTS episode (
    episode_id                  INTEGER PRIMARY KEY, -- Adaptado para SQLite
    person_id                   BIGINT       NOT NULL,
    episode_concept_id          INTEGER      NOT NULL,
    episode_start_date          DATE         NOT NULL,
    episode_start_datetime      TIMESTAMP,
    episode_end_date            DATE,
    episode_end_datetime        TIMESTAMP,
    episode_parent_id           BIGINT,
    episode_number              INTEGER,
    episode_object_concept_id   INTEGER      NOT NULL,
    episode_type_concept_id     INTEGER      NOT NULL,
    episode_source_value        VARCHAR(50),
    episode_source_concept_id   INTEGER
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_episode_person_id ON episode (person_id);
