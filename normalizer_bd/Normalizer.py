import json
import psycopg2

with open("result_06172648/hh_vacancies_part37.json", encoding='utf-8') as f:
    data = json.load(f)

conn = psycopg2.connect(
    dbname="vacancies",
    user="postgres",
    password="42264",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS companies (
  id TEXT PRIMARY KEY,
  name TEXT,
  name_variations JSONB,
  industry TEXT,
  size TEXT,
  is_foreign BOOLEAN,
  location_city TEXT,
  location_radius_km INTEGER
);''')

cur.execute('''CREATE TABLE IF NOT EXISTS benefits (
  id TEXT PRIMARY KEY,
  health_insurance BOOLEAN,
  fuel_compensation BOOLEAN,
  mobile_compensation BOOLEAN,
  free_meals BOOLEAN,
  other_benefits JSONB,
  new_column BOOLEAN
);''')

cur.execute('''CREATE TABLE IF NOT EXISTS compensations (
  id TEXT PRIMARY KEY,
  salary_min NUMERIC,
  salary_max NUMERIC,
  salary_median NUMERIC,
  salary_avg NUMERIC,
  salary_net BOOLEAN,
  currency TEXT,
  bonuses TEXT,
  payment_frequency TEXT,
  payment_type TEXT
);''')

cur.execute('''CREATE TABLE IF NOT EXISTS vacancies ( 
  external_id TEXT PRIMARY KEY,
  title TEXT,
  description TEXT,
  requirements TEXT,
  work_format TEXT,
  employment_type TEXT,
  schedule TEXT,
  experience_required TEXT,
  source_url TEXT,
  source_name TEXT,
  publication_date DATE,
  is_relevant BOOLEAN,
  company_id TEXT REFERENCES companies(id),
  compensation_id TEXT,
  benefits_id TEXT REFERENCES benefits(id),
  created_at TIMESTAMP,
  similar_titles JSONB,
  exclude_keywords JSONB
);''')

with open("job_title_mappings.json", encoding='utf-8') as f:
    title_mapping_raw = json.load(f)

# Построим "обратный" словарь: синоним -> основной тайтл
title_mapping = {}
for main_title, synonyms in title_mapping_raw.items():
    for synonym in synonyms:
        title_mapping[synonym.strip()] = main_title

for entry in data:
    # Insert or skip company
    c = entry['companies']
    cur.execute("""
        INSERT INTO companies (id, name, industry, size, is_foreign, location_city, location_radius_km)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (c['id'], c['name'], c['industry'], c['size'], c['is_foreign'], c['location_city'], c['location_radius_km']))

    # Insert or skip benefits
    b = entry['benefits']
    cur.execute("""
        INSERT INTO benefits (id, health_insurance, fuel_compensation, mobile_compensation, free_meals, other_benefits, new_column)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (b['id'], b['health_insurance'], b['fuel_compensation'], b['mobile_compensation'], b['free_meals'], b['other_benefits'], b['new_column']))

    # Insert or skip compensation (can be null)
    comp = entry['compensations']
    if comp['id'] is not None:
        cur.execute("""
            INSERT INTO compensations (id, salary_min, salary_max, salary_median, salary_avg, salary_net,
                                       currency, bonuses, payment_frequency, payment_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (comp['id'], comp['salary_min'], comp['salary_max'], comp['salary_median'],
              comp['salary_avg'], comp['salary_net'], comp['currency'], comp['bonuses'],
              comp['payment_frequency'], comp['payment_type']))

    # Insert vacancy
    v = entry['vacancies']

    original_title = v['title'].strip()
    v['title'] = title_mapping.get(original_title, original_title)

    cur.execute("""
        INSERT INTO vacancies (external_id, title, description, requirements, work_format, employment_type, schedule,
                               experience_required, source_url, source_name, publication_date, is_relevant,
                               company_id, compensation_id, benefits_id, created_at, similar_titles, exclude_keywords)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (external_id) DO UPDATE SET
            title = EXCLUDED.title,
            similar_titles = EXCLUDED.similar_titles,
            exclude_keywords = EXCLUDED.exclude_keywords;
    """, (v['external_id'], v['title'], v['description'], v['requirements'], v['work_format'],
          v['employment_type'], v['schedule'], v['experience_required'], v['source_url'],
          v['source_name'], v['publication_date'], v['is_relevant'], v['company_id'],
          v['compensation_id'], v['benefits_id'], v['created_at'], v['similar_titles'], v['exclude_keywords']))

conn.commit()
cur.close()
conn.close()
