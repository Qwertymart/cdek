import psycopg2
from psycopg2 import pool
from src.models.vacancy import Vacancy
from src.config.db import DBConfig


class VacancyRepository:
    def __init__(self):
        """Инициализация репозитория с пулом соединений"""
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **DBConfig.as_dict()
        )

    def get_vacancies_by_filters(self, filters):
        """
        Получение вакансий по фильтрам
        :param filters: словарь с параметрами фильтрации
        :return: список объектов Vacancy
        """
        conn = None
        try:
            # Получаем соединение из пула
            conn = self.connection_pool.getconn()

            # Базовый SQL-запрос
            query = """
            SELECT v.external_id, v.title, c.name AS company_name, c.location_city,
                   comp.salary_min, comp.salary_max, comp.salary_avg, comp.salary_median,
                   comp.currency, v.experience_required, v.publication_date,
                   v.source_name, v.source_url, v.employment_type, v.work_format, v.experience_years
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            LEFT JOIN compensations comp ON v.compensation_id = comp.id
            WHERE 1=1
            """

            params = []

            # Фильтр по опыту работы (диапазон лет)
            if filters.get("experience_range"):
                min_exp, max_exp = filters["experience_range"]
                query += """
                    AND (
                        -- Диапазон вакансии пересекается с запрошенным диапазоном
                        (v.experience_years[1] <= %s AND v.experience_years[2] >= %s)
                    )
                """
                params.extend([max_exp, min_exp])

            # Фильтр по зарплате (среднее значение)
            if filters.get("salary") and len(filters["salary"]) == 2:
                query += " AND comp.salary_avg BETWEEN %s AND %s"
                params.extend(filters["salary"])

            # Фильтр по названию должности
            if filters.get("position"):
                query += " AND v.title ILIKE %s"
                params.append(f"%{filters['position']}%")

            # Фильтр по городам
            if filters.get("cities"):
                placeholders = ','.join(['%s'] * len(filters["cities"]))
                query += f" AND c.location_city IN ({placeholders})"
                params.extend(filters["cities"])

            # Фильтр по компаниям
            if filters.get("companies"):
                placeholders = ','.join(['%s'] * len(filters["companies"]))
                query += f" AND c.name IN ({placeholders})"
                params.extend(filters["companies"])

            # Фильтр по источникам вакансий
            if filters.get("sources"):
                placeholders = ','.join(['%s'] * len(filters["sources"]))
                query += f" AND v.source_name IN ({placeholders})"
                params.extend(filters["sources"])

            # Сортировка по дате публикации (новые сначала)
            query += " ORDER BY v.publication_date DESC"

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_vacancy_object(row) for row in rows]

        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            print(f"SQL: {query}")
            print(f"Параметры: {params}")
            raise
        finally:
            if conn:
                # Возвращаем соединение в пул вместо закрытия
                self.connection_pool.putconn(conn)

    def _row_to_vacancy_object(self, row) -> Vacancy:
        """Преобразование строки из БД в объект Vacancy"""
        return Vacancy(
            external_id=row[0],
            title=row[1],
            company_name=row[2],
            location_city=row[3],
            salary_min=row[4],
            salary_max=row[5],
            salary_avg=row[6],
            salary_median=row[7],
            currency=row[8],
            experience_required=row[9],
            created_at=row[10],
            source_name=row[11],
            source_url=row[12],
            employment_type=row[13],
            work_format=row[14],
            experience_years=row[15]
        )

    def __del__(self):
        """Закрываем пул соединений при уничтожении объекта"""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()