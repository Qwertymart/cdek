from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class Vacancy:
    # Обязательные поля (без значений по умолчанию)
    external_id: str
    title: str
    created_at: datetime

    # Необязательные поля (со значениями по умолчанию)
    company_name: Optional[str] = None
    location_city: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_avg: Optional[float] = None
    salary_median: Optional[float] = None
    currency: Optional[str] = None
    experience_required: Optional[str] = None
    experience_years: Optional[Tuple[int, int]] = None  # Диапазон опыта (от, до)
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    employment_type: Optional[str] = None
    work_format: Optional[str] = None