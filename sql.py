import sqlite3
# NOT NULL UNIQUE
users = """
CREATE TABLE users (
  user_id          INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id           INTEGER,
  name             VARCHAR(100)      NOT NULL,
  appeal           TEXT             DEFAULT NULL,
  degree          VARCHAR(3)        DEFAULT NULL,
  email            VARCHAR(320)      DEFAULT NULL,
  telephone        VARCHAR(20)       DEFAULT NULL,
  resume           MEDIUMBLOB        DEFAULT NULL,
  abstract1_titel  VARCHAR(300)      DEFAULT NULL,
  abstract1        TEXT              DEFAULT NULL,
  abstract2_titel  VARCHAR(300)      DEFAULT NULL,
  abstract2        TEXT              DEFAULT NULL,
  abstract3_titel  VARCHAR(300)      DEFAULT NULL,
  abstract3        TEXT              DEFAULT NULL,
  job_abst1_score   FLOAT             DEFAULT NULL,
  job_abst2_score   FLOAT             DEFAULT NULL,
  job_abst3_score   FLOAT             DEFAULT NULL,
  job_abst4_score   FLOAT             DEFAULT NULL,
  job_appeal_score  FLOAT             DEFAULT NULL,
  total_score       FLOAT             DEFAULT NULL
  );
"""

project="""
CREATE TABLE jobs (
  job_id          INTEGER PRIMARY KEY AUTOINCREMENT,
  titel           VARCHAR(300)      DEFAULT NULL,
  job_overview    TEXT              DEFAULT NULL,
  degree          VARCHAR(3)        DEFAULT NULL,
  abstract1_titel  VARCHAR(300)      DEFAULT NULL,
  abstract1        TEXT              DEFAULT NULL,
  abstract2_titel  VARCHAR(300)      DEFAULT NULL,
  abstract2        TEXT              DEFAULT NULL,
  abstract3_titel  VARCHAR(300)      DEFAULT NULL,
  abstract3        TEXT              DEFAULT NULL,
  abstract4_titel  VARCHAR(300)      DEFAULT NULL,
  abstract4        TEXT              DEFAULT NULL
);
"""

# text: 65,535
dbname = 'TEST.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

cur.execute(project)
cur.execute(users)
conn.commit()
conn.close()

