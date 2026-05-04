-- Patent Intelligence Data Pipeline - Database Schema

CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    filing_date TEXT,
    year INTEGER
);

CREATE TABLE inventors (
    inventor_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT
);

CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE patent_inventor_relationships (
    patent_id TEXT,
    inventor_id INTEGER,
    FOREIGN KEY(patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY(inventor_id) REFERENCES inventors(inventor_id),
    PRIMARY KEY(patent_id, inventor_id)
);

CREATE TABLE patent_company_relationships (
    patent_id TEXT,
    company_id INTEGER,
    FOREIGN KEY(patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY(company_id) REFERENCES companies(company_id),
    PRIMARY KEY(patent_id, company_id)
);

CREATE TABLE patent_abstracts (
    patent_id TEXT PRIMARY KEY,
    abstract TEXT,
    FOREIGN KEY(patent_id) REFERENCES patents(patent_id)
);
