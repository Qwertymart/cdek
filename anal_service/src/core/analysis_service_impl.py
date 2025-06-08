from __future__ import annotations

import statistics
import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime
from collections import Counter

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

# gRPC imports
from proto import dashboard_anal_pb2_grpc
from proto import dashboard_anal_pb2
from src.repositories.vacancy import VacancyRepository # Предполагается, что этот репозиторий существует

warnings.filterwarnings(action='once')

# --- Настройка стилей для графиков Matplotlib ---
plt.style.use('default')
sns.set_theme(style="whitegrid", palette="husl")

# Глобальные параметры для Matplotlib
large = 22
med = 16
small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'xtick.labelsize': small,
          'ytick.labelsize': small,
          'figure.titlesize': large}
plt.rcParams.update(params)

# --- Регистрация шрифтов для ReportLab (для поддержки кириллицы) ---
# Убедитесь, что файлы FreeSans.ttf и FreeSansBold.ttf находятся
# в том же каталоге, что и этот скрипт, или укажите полный путь к ним.
try:
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    pdfmetrics.registerFont(TTFont('FreeSans-Bold', 'FreeSansBold.ttf'))
    DEFAULT_FONT = 'FreeSans'
    BOLD_FONT = 'FreeSans-Bold'
except Exception as e:
    print(f"Ошибка при регистрации шрифта: {e}. Используем Helvetica.")
    # Если шрифт не найден, возвращаемся к стандартным шрифтам ReportLab,
    # но они могут не поддерживать кириллицу.
    DEFAULT_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'

class AnalysisServiceImpl(dashboard_anal_pb2_grpc.AnalysisServiceServicer):
    """
    Реализация сервиса аналитики вакансий gRPC.
    Обрабатывает запросы на получение аналитических данных по вакансиям
    и генерирует отчеты в формате PDF с графиками.
    """
    def __init__(self):
        self.vacancy_repo = VacancyRepository()

    def _prepare_dataframe(self, vacancies: list) -> pd.DataFrame:
        """
        Подготавливает DataFrame из списка объектов вакансий.
        Преобразует данные из gRPC объектов в удобный для Pandas формат.
        """
        processed_data = []
        for v in vacancies:
            processed_data.append({
                'title': v.title if v.title else 'Не указано',
                'company': v.company_name if v.company_name else 'Не указано',
                'city': v.location_city if v.location_city else 'Не указано',
                'salary_min': v.salary_min if v.salary_min is not None else np.nan,
                'salary_max': v.salary_max if v.salary_max is not None else np.nan,
                'salary_avg': v.salary_avg if v.salary_avg is not None else np.nan,
                'salary_median': v.salary_median if v.salary_median is not None else np.nan,
                'currency': v.currency if v.currency else 'RUB',
                'experience': v.experience_required if v.experience_required else 'Не указано',
                'experience_years': tuple(v.experience_years) if v.experience_years else (0, 0),
                'created_at': v.created_at,
                'source': v.source_name if v.source_name else 'Не указано',
                'employment_type': v.employment_type if v.employment_type else 'Полная занятость',
                'work_format': v.work_format if v.work_format else 'Офис'
            })
        return pd.DataFrame(processed_data)

    def _prepare_vacancy_table(self, vacancies: list) -> list:
        """
        Подготавливает список объектов Table для gRPC ответа,
        содержащих ключевую информацию о вакансиях.
        """
        table_rows = []
        for vacancy in vacancies:
            exp_range = list(vacancy.experience_years) if hasattr(vacancy, 'experience_years') else [0, 0]
            table_row = dashboard_anal_pb2.Table(
                name=vacancy.title or "Не указано",
                salary=int(vacancy.salary_avg) if vacancy.salary_avg is not None else 0,
                link=vacancy.source_url or "Не указано",
                experience=exp_range,
                region=vacancy.location_city or "Не указано"
            )
            table_rows.append(table_row)
        return table_rows

    def _get_experience_category(self, max_experience: int) -> str:
        """
        Категоризирует опыт работы на основе максимального количества лет.
        """
        if max_experience < 1:
            return "Нет опыта"
        elif 1 <= max_experience <= 3:
            return "1-3 года"
        elif 3 < max_experience <= 6:
            return "3-6 лет"
        else:
            return "Более 6 лет"

    def _create_salary_distribution_chart(self, df: pd.DataFrame, main_profession: str) -> bytes | None:
        """
        Создает и возвращает изображение графика распределения зарплат в виде байтов PNG.
        """
        salary_df = df[df['salary_avg'].notna()].copy()
        if salary_df.empty:
            return None

        salary_df['salary_avg'] = salary_df['salary_avg'].astype(int)
        plt.figure(figsize=(16, 10))

        if len(salary_df) <= 5: # Для небольшого числа уникальных зарплат - гистограмма по значениям
            salary_counts = salary_df['salary_avg'].value_counts().sort_index()
            bars = plt.bar(range(len(salary_counts)), salary_counts.values,
                           color=plt.cm.plasma(np.linspace(0, 1, len(salary_counts))),
                           alpha=0.8, edgecolor='white', linewidth=1.5)
            for i, v in enumerate(salary_counts.values):
                plt.text(i, v + 0.05, str(v), ha='center', va='bottom', fontweight='bold', fontsize=12)
            plt.xticks(range(len(salary_counts)), [f'{int(sal):,}₽' for sal in salary_counts.index], rotation=45)
            plt.xlabel('Зарплата (руб)', fontweight='bold')
        else: # Для большого числа зарплат - гистограмма по диапазонам
            salary_bins = np.linspace(salary_df['salary_avg'].min(), salary_df['salary_avg'].max(), 15)
            # Добавляем observed=False для совместимости с будущими версиями Pandas
            salary_df['salary_range'] = pd.cut(salary_df['salary_avg'], bins=salary_bins, include_lowest=True)
            vacancy_count_by_salary = salary_df.groupby('salary_range', observed=False).size()

            bars = plt.bar(range(len(vacancy_count_by_salary)), vacancy_count_by_salary.values,
                           color=plt.cm.plasma(np.linspace(0, 1, len(vacancy_count_by_salary))),
                           alpha=0.8, edgecolor='white', linewidth=1.5)
            for i, v in enumerate(vacancy_count_by_salary.values):
                plt.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold', fontsize=12)
            labels = [f"{int(interval.left / 1000)}-{int(interval.right / 1000)}"
                      for interval in vacancy_count_by_salary.index]
            plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
            plt.xlabel('Диапазон зарплат (тыс. руб)', fontweight='bold')

        plt.title(f'Распределение вакансий по зарплате\nПрофессия: {main_profession}',
                  fontweight='bold', pad=20)
        plt.ylabel('Количество вакансий', fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        return buffer.getvalue()

    def _create_experience_salary_chart(self, df: pd.DataFrame, main_profession: str) -> bytes | None:
        """
        Создает и возвращает изображение графика зависимости зарплаты от опыта работы
        (boxplot с точками) в виде байтов PNG.
        """
        salary_df = df[df['salary_avg'].notna()].copy()
        if salary_df.empty:
            return None

        # Создаем категории опыта на основе числовых данных
        salary_df['experience_category'] = salary_df['experience_years'].apply(
            lambda x: self._get_experience_category(x[1]) # Берем верхнюю границу диапазона
        )

        # Упорядочиваем категории для корректного отображения на графике
        categories_order = ['Нет опыта', '1-3 года', '3-6 лет', 'Более 6 лет']
        salary_df['experience_category'] = pd.Categorical(
            salary_df['experience_category'],
            categories=categories_order,
            ordered=True
        )

        plt.figure(figsize=(16, 10))
        # Используем boxplot для отображения распределения и stripplot для отдельных точек
        sns.boxplot(
            data=salary_df,
            x='experience_category',
            y='salary_avg',
            hue='experience_category', # Разделение по категориям для разных цветов
            palette='viridis',
            showmeans=True, # Показать среднее значение
            legend=False, # Отключить легенду, т.к. hue используется для цвета, а не для отдельных групп
            meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black", "markersize": 10}
        )
        sns.stripplot(
            data=salary_df,
            x='experience_category',
            y='salary_avg',
            color='red', # Отдельный цвет для точек, чтобы они выделялись
            jitter=0.2, # Добавляем небольшое смещение, чтобы точки не накладывались
            alpha=0.6,
            size=6
        )

        plt.title(f'Зависимость зарплаты от опыта работы\nПрофессия: {main_profession}',
                  fontweight='bold', pad=20)
        plt.xlabel('Требуемый опыт работы', fontweight='bold')
        plt.ylabel('Зарплата (руб)', fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        return buffer.getvalue()

    def _create_source_analysis_chart(self, df: pd.DataFrame, main_profession: str) -> bytes | None:
        """
        Создает и возвращает изображение графика анализа источников вакансий (количество и средняя зарплата)
        в виде байтов PNG.
        """
        source_analysis = df.groupby('source').agg(
            vacancy_count=('title', 'count'),
            avg_salary=('salary_avg', 'mean')
        ).sort_values('vacancy_count', ascending=False)

        if source_analysis.empty:
            return None

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

        # График количества вакансий по источникам
        bars1 = ax1.bar(source_analysis.index, source_analysis['vacancy_count'],
                        color='skyblue', alpha=0.8, edgecolor='navy', linewidth=1.5)
        ax1.set_title(f'Распределение вакансий по источникам\nПрофессия: {main_profession}',
                      fontweight='bold', pad=20)
        ax1.set_ylabel('Количество вакансий', fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                     f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=10)

        # График средних зарплат по источникам
        salary_by_source = source_analysis[source_analysis['avg_salary'].notna()]
        if not salary_by_source.empty:
            bars2 = ax2.bar(salary_by_source.index, salary_by_source['avg_salary'],
                            color='lightcoral', alpha=0.8, edgecolor='darkred', linewidth=1.5)
            ax2.set_title('Средние зарплаты по источникам', fontweight='bold', pad=20)
            ax2.set_ylabel('Средняя зарплата (руб)', fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='y')
            for bar in bars2:
                height = bar.get_height()
                if not np.isnan(height):
                    ax2.text(bar.get_x() + bar.get_width() / 2., height + height * 0.01,
                             f'{int(height):,}₽', ha='center', va='bottom', fontweight='bold', fontsize=10)
        else:
            ax2.set_visible(False) # Скрыть второй график, если нет данных по зарплатам

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        return buffer.getvalue()

    def _create_work_formats_chart(self, df: pd.DataFrame, main_profession: str) -> bytes | None:
        """
        Создает и возвращает изображение круговых диаграмм для форматов работы и типов занятости
        в виде байтов PNG.
        """
        if df.empty:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

        # Диаграмма форматов работы
        work_format_counts = df['work_format'].value_counts()
        if not work_format_counts.empty:
            colors1 = plt.cm.Set3(np.linspace(0, 1, len(work_format_counts)))
            wedges1, texts1, autotexts1 = ax1.pie(work_format_counts.values, labels=work_format_counts.index,
                                                  autopct='%1.1f%%', colors=colors1, startangle=90,
                                                  wedgeprops=dict(width=0.4), pctdistance=0.75) # Добавлен donut-эффект
            ax1.set_title(f'Форматы работы\nПрофессия: {main_profession}', fontweight='bold', pad=20)
            for autotext in autotexts1:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
        else:
            ax1.set_visible(False) # Скрыть, если нет данных

        # Диаграмма типов занятости
        employment_counts = df['employment_type'].value_counts()
        if not employment_counts.empty:
            colors2 = plt.cm.Pastel1(np.linspace(0, 1, len(employment_counts)))
            wedges2, texts2, autotexts2 = ax2.pie(employment_counts.values, labels=employment_counts.index,
                                                  autopct='%1.1f%%', colors=colors2, startangle=90,
                                                  wedgeprops=dict(width=0.4), pctdistance=0.75) # Добавлен donut-эффект
            ax2.set_title(f'Типы занятости\nПрофессия: {main_profession}', fontweight='bold', pad=20)
            for autotext in autotexts2:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
        else:
            ax2.set_visible(False) # Скрыть, если нет данных

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        return buffer.getvalue()

    def _generate_pdf_report(self, df: pd.DataFrame, main_profession: str, salary_stats: dict, images_data: list = None) -> bytes:
        """
        Генерирует аналитический PDF-отчет с основной статистикой, таблицами и графиками.
        Использует зарегистрированные шрифты для корректного отображения кириллицы.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                                leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                                encoding='utf-8')

        styles = getSampleStyleSheet()

        # Определение стилей с использованием зарегистрированных шрифтов
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName=BOLD_FONT
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.darkred,
            spaceAfter=15,
            spaceBefore=20,
            fontName=BOLD_FONT
        )

        normal_style = ParagraphStyle(
            'NormalText',
            parent=styles['Normal'],
            fontName=DEFAULT_FONT,
            fontSize=12,
            leading=14
        )

        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=30,
            fontName=DEFAULT_FONT
        )

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontName=DEFAULT_FONT
        )

        # Стили для таблиц
        table_header_bg_color = colors.HexColor('#004d99') # Темно-синий
        table_row_even_bg_color = colors.HexColor('#e6f2ff') # Светло-голубой
        table_row_odd_bg_color = colors.whitesmoke # Белый

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), table_header_bg_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), BOLD_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [table_row_odd_bg_color, table_row_even_bg_color]),
        ])

        company_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006633')), # Темно-зеленый
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'), # Номера по центру
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'), # Числа по центру
            ('FONTNAME', (0, 0), (-1, 0), BOLD_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e6ffe6'), colors.whitesmoke]),
        ])


        content = []

        # Заголовок отчета
        content.append(Paragraph("АНАЛИТИЧЕСКИЙ ОТЧЕТ", title_style))
        content.append(Paragraph(f"По профессии: {main_profession}",
                                 ParagraphStyle('SubTitle', parent=styles['Normal'],
                                                fontSize=16, alignment=TA_CENTER,
                                                textColor=colors.blue, spaceAfter=20,
                                                fontName=BOLD_FONT)))

        # Дата создания отчета
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        content.append(Paragraph(f"Дата создания отчета: {current_date}", date_style))

        # Основная статистика
        content.append(Paragraph("ОСНОВНАЯ СТАТИСТИКА", heading_style))

        stats_data = [
            ['Показатель', 'Значение'],
            ['Всего проанализировано вакансий', str(len(df))],
            ['Вакансий с указанной зарплатой', str(len(df[df['salary_avg'].notna()]))],
            ['Средняя зарплата',
             f"{salary_stats.get('avg', 0):,.0f} руб" if salary_stats.get('avg') else 'Не указано'],
            ['Медианная зарплата',
             f"{salary_stats.get('median', 0):,.0f} руб" if salary_stats.get('median') else 'Не указано'],
            ['Максимальная зарплата',
             f"{salary_stats.get('max', 0):,.0f} руб" if salary_stats.get('max') else 'Не указано'],
            ['Минимальная зарплата',
             f"{salary_stats.get('min', 0):,.0f} руб" if salary_stats.get('min') else 'Не указано'],
            ['Количество уникальных компаний', str(df['company'].nunique())],
            ['Количество городов', str(df['city'].nunique())],
            ['Количество источников данных', str(df['source'].nunique())],
        ]

        stats_table = Table(stats_data, colWidths=[3.5 * inch, 2.5 * inch])
        stats_table.setStyle(table_style)
        content.append(stats_table)
        content.append(Spacer(1, 20))

        # Топ компаний
        content.append(Paragraph("ТОП-5 КОМПАНИЙ ПО КОЛИЧЕСТВУ ВАКАНСИЙ", heading_style))

        top_companies = df['company'].value_counts().head(5)
        company_data = [['№', 'Компания', 'Количество вакансий', '% от общего']]
        total_vacancies = len(df)

        for i, (company, count) in enumerate(top_companies.items(), 1):
            percentage = (count / total_vacancies) * 100
            company_data.append([
                str(i),
                company[:40] + "..." if len(company) > 40 else company,
                str(count),
                f"{percentage:.1f}%"
            ])

        company_table = Table(company_data, colWidths=[0.5 * inch, 3 * inch, 1.2 * inch, 1 * inch])
        company_table.setStyle(company_table_style)
        content.append(company_table)
        content.append(PageBreak()) # Переход на новую страницу перед графиками

        # ГРАФИКИ
        if images_data:
            content.append(Paragraph("АНАЛИТИЧЕСКИЕ ГРАФИКИ", title_style))

            chart_titles = {
                "salary_distribution": "1. РАСПРЕДЕЛЕНИЕ ВАКАНСИЙ ПО ЗАРПЛАТЕ",
                "experience_salary": "2. ЗАВИСИМОСТЬ ЗАРПЛАТЫ ОТ ОПЫТА РАБОТЫ",
                "source_analysis": "3. АНАЛИЗ ИСТОЧНИКОВ ДАННЫХ",
                "work_formats": "4. ФОРМАТЫ РАБОТЫ И ТИПЫ ЗАНЯТОСТИ"
            }

            for image_info in images_data:
                chart_name = image_info.name # Исправлено: обращаемся к атрибуту 'name'
                chart_data = image_info.image_data # Исправлено: обращаемся к атрибуту 'image_data'

                if chart_data and chart_name in chart_titles:
                    content.append(Paragraph(chart_titles[chart_name], heading_style))
                    try:
                        img_buffer = io.BytesIO(chart_data)
                        img_reader = ImageReader(img_buffer)
                        img_width, img_height = img_reader.getSize()

                        # Масштабирование изображения под ширину страницы
                        max_width = 7.0 * inch # Увеличена максимальная ширина для графиков
                        aspect_ratio = img_height / img_width
                        new_width = min(img_width, max_width)
                        new_height = new_width * aspect_ratio

                        # Проверка, помещается ли изображение на страницу, и регулировка высоты
                        # Допустимая высота страницы для контента, учитывая отступы
                        max_page_height = A4[1] - (doc.topMargin + doc.bottomMargin + 0.5 * inch)
                        if new_height > max_page_height:
                            scale_factor = max_page_height / new_height
                            new_height = max_page_height
                            new_width = new_width * scale_factor

                        img = Image(img_reader, width=new_width, height=new_height)
                        img.hAlign = 'CENTER'
                        content.append(img)
                        content.append(Spacer(1, 20))

                        # Добавляем разрыв страницы после каждого графика, кроме последнего
                        if chart_name != "work_formats":
                            content.append(PageBreak())

                    except Exception as e:
                        print(f"Ошибка при добавлении графика {chart_name}: {e}")
                        content.append(Paragraph(f"Ошибка загрузки графика: {chart_name}", normal_style))
                        content.append(Spacer(1, 20))

        # Заключительная страница с выводами
        content.append(PageBreak())
        content.append(Paragraph("ВЫВОДЫ И РЕКОМЕНДАЦИИ", title_style))

        conclusions = []

        if salary_stats.get('avg'):
            conclusions.append(
                f"• Средняя зарплата по профессии «{main_profession}» составляет {salary_stats['avg']:,.0f} рублей.")

        vacancies_with_salary = len(df[df['salary_avg'].notna()])
        if vacancies_with_salary > 0:
            salary_coverage = (vacancies_with_salary / len(df)) * 100
            conclusions.append(f"• Информация о зарплате указана в {salary_coverage:.1f}% вакансий.")
        else:
            conclusions.append(f"• Ни в одной из {len(df)} вакансий по профессии «{main_profession}» не указана зарплата.")


        if not df.empty:
            top_company_series = df['company'].value_counts()
            if not top_company_series.empty:
                top_company = top_company_series.index[0]
                top_company_count = top_company_series.iloc[0]
                conclusions.append(f"• Наибольшее количество вакансий ({top_company_count}) размещает компания «{top_company}».")

            top_city_series = df['city'].value_counts()
            if not top_city_series.empty:
                top_city = top_city_series.index[0]
                conclusions.append(f"• Больше всего вакансий размещено в городе: {top_city}.")
        else:
            conclusions.append("• Данные для выводов по компаниям и городам отсутствуют.")


        for conclusion in conclusions:
            content.append(Paragraph(conclusion, normal_style))
            content.append(Spacer(1, 10))

        content.append(Spacer(1, 30))
        content.append(Paragraph("Отчет сгенерирован автоматически системой аналитики вакансий", footer_style))

        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()

    # --- ГЛАВНЫЙ МЕТОД gRPC ---
    def GetAnalysisData(self, request, context):
        """
        Основной метод для обработки gRPC запроса, получения данных,
        выполнения анализа и генерации ответа.
        """
        filters = {
            "salary": list(request.salary),
            "position": request.position,
            "experience": list(request.experience),
            "regions": list(request.regions),
            "companies": list(request.companies),
            "sources": list(request.sources),
        }
        print("Полученные фильтры:", filters)

        try:
            vacancies = self.vacancy_repo.get_vacancies_by_filters(filters)
            if not vacancies:
                return dashboard_anal_pb2.AnalysisResponse(
                    success=False,
                    error="Вакансии не найдены по заданным фильтрам."
                )

            df = self._prepare_dataframe(vacancies)

            # Определяем основную профессию для детализированного анализа
            # Если DataFrame пуст или содержит только 'Не указано', используем пустую строку
            main_profession = 'Не указано'
            if not df['title'].empty:
                title_counts = df['title'].value_counts()
                if not title_counts.empty:
                    main_profession = title_counts.index[0]

            # Фильтруем DataFrame только по основной профессии для графиков
            # Это позволяет сосредоточиться на наиболее релевантных данных для графического анализа
            prof_df = df[df['title'] == main_profession].copy()
            if prof_df.empty:
                print(f"Внимание: нет данных для основной профессии '{main_profession}'. Графики могут быть пустыми.")
                prof_df = df.copy() # Если по главной профессии нет данных, используем весь DataFrame для графиков

            # Расчет статистик по зарплатам
            salaries = [v.salary_avg for v in vacancies if v.salary_avg is not None]

            total_number = len(vacancies)
            avg_salary = float(statistics.mean(salaries)) if salaries else 0.0
            median_salary = int(statistics.median(salaries)) if salaries else 0
            max_salary = max(salaries) if salaries else 0
            min_salary = min(salaries) if salaries else 0

            analysis_item = dashboard_anal_pb2.AnalysisItem(
                total_number=total_number,
                avg=avg_salary,
                median=median_salary
            )

            table_rows = self._prepare_vacancy_table(vacancies)

            # --- Генерация графиков ---
            images_list = []

            # 1. Распределение зарплат
            salary_chart_data = self._create_salary_distribution_chart(prof_df, main_profession)
            if salary_chart_data:
                images_list.append(dashboard_anal_pb2.AnalysisImage(
                    name="salary_distribution",
                    image_data=salary_chart_data
                ))

            # 2. Зависимость зарплаты от опыта
            experience_chart_data = self._create_experience_salary_chart(prof_df, main_profession)
            if experience_chart_data:
                images_list.append(dashboard_anal_pb2.AnalysisImage(
                    name="experience_salary",
                    image_data=experience_chart_data
                ))

            # 3. Анализ источников
            source_chart_data = self._create_source_analysis_chart(prof_df, main_profession)
            if source_chart_data:
                images_list.append(dashboard_anal_pb2.AnalysisImage(
                    name="source_analysis",
                    image_data=source_chart_data
                ))

            # 4. Форматы работы и типы занятости
            work_formats_chart_data = self._create_work_formats_chart(prof_df, main_profession)
            if work_formats_chart_data:
                images_list.append(dashboard_anal_pb2.AnalysisImage(
                    name="work_formats",
                    image_data=work_formats_chart_data
                ))

            # --- Генерация PDF отчета ---
            salary_stats_dict = {
                'avg': avg_salary,
                'median': median_salary,
                'max': max_salary,
                'min': min_salary
            }
            pdf_data = self._generate_pdf_report(prof_df, main_profession, salary_stats_dict, images_data=images_list)

            response = dashboard_anal_pb2.AnalysisResponse(
                success=True,
                items=analysis_item,
                images=images_list, # Это для gRPC ответа, если клиенту нужны изображения отдельно
                pdf_data=pdf_data,
                table=table_rows
            )
            return response

        except Exception as e:
            print(f"Ошибка в GetAnalysisData: {e}")
            import traceback
            traceback.print_exc() # Для более детального вывода ошибки в консоль
            return dashboard_anal_pb2.AnalysisResponse(
                success=False,
                error=f"Ошибка при создании аналитики: {str(e)}"
            )