import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import autoTable from 'jspdf-autotable';

// Base64-шрифт Roboto с поддержкой кириллицы (из src/fonts/Roboto-Regular-normal.js)
import { RobotoRegular } from '@/fonts/Roboto-Regular-normal';

import { SalaryData, RegionData, FilterParams } from '@/types';

export async function generatePDFReport(
    data: SalaryData[],
    regionData: RegionData[],
    filters: FilterParams,
    recommendations: string[] = []
) {
    // 1. Инициализация jsPDF и встраивание шрифта Roboto
    const doc = new jsPDF('p', 'mm', 'a4');
    doc.addFileToVFS('Roboto-Regular.ttf', RobotoRegular);
    doc.addFont('Roboto-Regular.ttf', 'Roboto', 'normal');
    doc.setFont('Roboto', 'normal');

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    let y = 10;

    doc.setFontSize(16);
    doc.text('Аналитика зарплат', pageWidth / 2, y, { align: 'center' });
    y += 10;

    doc.setFontSize(12);
    doc.text('Выбранные фильтры:', 10, y);
    y += 6;

    doc.setFontSize(10);
    doc.text(
        `Зарплата: ${filters.salaryRange[0].toLocaleString()}₽ - ${filters.salaryRange[1].toLocaleString()}₽`,
        10,
        y
    );
    y += 5;
    doc.text(`Должности: ${filters.positions.join(', ') || 'Все'}`, 10, y);
    y += 5;
    doc.text(`Опыт: ${filters.experience.join(', ') || 'Все'}`, 10, y);
    y += 5;
    doc.text(`Регионы: ${filters.regions.join(', ') || 'Все'}`, 10, y);
    y += 10;

    if (recommendations.length > 0) {
        doc.setFontSize(12);
        doc.text('Рекомендации:', 10, y);
        y += 6;

        doc.setFontSize(10);
        const maxWidth = pageWidth - 20;
        for (const rec of recommendations) {
            const lines = doc.splitTextToSize(`- ${rec}`, maxWidth);
            for (const line of lines as string[]) {
                if (y > 280) {
                    doc.addPage();
                    y = 10;
                }
                doc.text(line, 12, y);
                y += 5;
            }
            y += 2;
        }
        y += 5;
    }

    // 5. Таблица "Распределение по регионам"
    if (regionData.length > 0) {
        doc.setFontSize(12);
        doc.text('Распределение по регионам:', 10, y);
        y += 6;


        autoTable(doc, {
            startY: y,
            head: [['Регион', 'Средняя', 'Медиана', 'Кол-во']],
            body: regionData.map(d => [
                d.region,
                `${d.avgSalary.toLocaleString()}₽`,
                `${d.median.toLocaleString()}₽`,
                d.count.toLocaleString()
            ]),
            theme: 'grid',
            styles: {
                font: 'Roboto', // основной шрифт
                fontSize: 9
            },
            headStyles: {
                fillColor: [41, 128, 185],
                font: 'Roboto', // шрифт заголовков
                fontStyle: 'normal'
            },
            bodyStyles: {
                font: 'Roboto' // шрифт тела таблицы
            },
            columnStyles: {
                0: { font: 'Roboto' } // явное указание для колонки с регионами
            }
        });

        y = (doc as any).lastAutoTable.finalY + 10;
    }

    // 6. Таблица "Детализация данных"
    if (data.length > 0) {
        doc.setFontSize(12);
        doc.text('Детализация данных:', 10, y);
        y += 6;

        autoTable(doc, {
            startY: y,
            head: [['Должность', 'Зарплата', 'Регион', 'Опыт', 'Дата']],
            body: data.map(d => [
                d.position,
                `${d.salary.toLocaleString()}₽`,
                d.region,
                d.experience,
                d.date
            ]),
            theme: 'grid',
            styles: {
                font: 'Roboto', // основной шрифт
                fontSize: 8
            },
            headStyles: {
                fillColor: [39, 174, 96],
                font: 'Roboto', // шрифт заголовков
                fontStyle: 'normal'
            },
            bodyStyles: {
                font: 'Roboto' // шрифт тела таблицы
            },
            columnStyles: {
                0: { font: 'Roboto' }, // должность
                1: { cellWidth: 25 },
                2: { font: 'Roboto' }, // регион
                4: { cellWidth: 20 }
            }
        });

        y = (doc as any).lastAutoTable.finalY + 10;
    }

    // 7. Вставка графиков
    await addChartsToPDF(doc, y);

    // 8. Сохранение PDF
    doc.save('report.pdf');
}

async function addChartsToPDF(doc: jsPDF, startY: number, pageHeight: number) {
    const chartIds = [
        { id: 'trend-chart', label: 'Динамика зарплат' },
        { id: 'comparison-chart', label: 'Сравнение с конкурентами' },
        { id: 'heatmap-chart', label: 'Тепловая карта по регионам' }
    ];

    let y = startY;
    const pageWidth = doc.internal.pageSize.getWidth() - 20;

    for (const { id, label } of chartIds) {
        const container = document.getElementById(id);
        if (!container) continue;

        // Проверка свободного места перед вставкой графика
        const spaceNeeded = 20; // Минимальное требуемое место
        if (y > pageHeight - spaceNeeded) {
            doc.addPage();
            y = 10;
        }

        // Добавление подписи
        doc.setFontSize(12);
        doc.text(label, 10, y);
        y += 6;

        // Обработка SVG
        const svgNode: SVGSVGElement | null =
            container.tagName === 'svg' ?
                container as SVGSVGElement :
                container.querySelector('svg');

        if (svgNode) {
            try {
                const svgString = new XMLSerializer().serializeToString(svgNode);
                const svgBlob = new Blob([svgString], { type: 'image/svg+xml' });
                const url = URL.createObjectURL(svgBlob);

                const img = new Image();
                await new Promise<void>((resolve, reject) => {
                    img.onload = async () => {
                        try {
                            // Рассчет пропорций
                            const imgWidth = img.width;
                            const imgHeight = img.height;
                            const aspectRatio = imgWidth / imgHeight;

                            // Максимальная доступная высота
                            const maxHeight = pageHeight - y - 10;
                            let pdfHeight = pageWidth / aspectRatio;

                            // Если график не помещается - масштабируем
                            if (pdfHeight > maxHeight) {
                                pdfHeight = maxHeight;
                            }

                            // Добавление на новую страницу если нужно
                            if (y + pdfHeight > pageHeight - 10) {
                                doc.addPage();
                                y = 10;
                            }

                            // Создание canvas для рендеринга
                            const canvas = document.createElement('canvas');
                            canvas.width = imgWidth;
                            canvas.height = imgHeight;
                            const ctx = canvas.getContext('2d')!;
                            ctx.drawImage(img, 0, 0, imgWidth, imgHeight);

                            // Вставка в PDF
                            const imgData = canvas.toDataURL('image/png');
                            doc.addImage(imgData, 'PNG', 10, y, pageWidth, pdfHeight);
                            y += pdfHeight + 10;

                            resolve();
                        } catch (error) {
                            reject(error);
                        } finally {
                            URL.revokeObjectURL(url);
                        }
                    };
                    img.onerror = reject;
                    img.src = url;
                });
            } catch (error) {
                console.error(`Ошибка обработки SVG (${id}):`, error);
            }
        } else {
            // Обработка других графиков через html2canvas
            try {
                const clone = container.cloneNode(true) as HTMLElement;
                clone.style.visibility = 'visible';
                document.body.appendChild(clone);

                const canvas = await html2canvas(clone, {
                    scale: 3,
                    backgroundColor: '#FFFFFF',
                    logging: false
                });

                const imgData = canvas.toDataURL('image/png');
                const aspectRatio = canvas.width / canvas.height;
                let pdfHeight = pageWidth / aspectRatio;

                // Проверка места на странице
                if (y + pdfHeight > pageHeight - 10) {
                    pdfHeight = pageHeight - y - 15;
                }

                doc.addImage(imgData, 'PNG', 10, y, pageWidth, pdfHeight);
                y += pdfHeight + 10;

                document.body.removeChild(clone);
            } catch (error) {
                console.error(`Ошибка обработки графика ${id}:`, error);
            }
        }
    }
}
