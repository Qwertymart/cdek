import React from "react";
import { Response } from "@/types/response";
import { ImageGallery } from "./ImageGallery";

interface AnalyticsResultsProps {
  data: Response;
}

const AnalyticsResults: React.FC<AnalyticsResultsProps> = ({ data }) => {
  const { items, tables, images, pdf_data, pdf_full_data, success, error } =
    data;

  if (!success && error) {
    return (
      <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
        <h2 className="text-xl font-semibold text-red-800 mb-2">Ошибка</h2>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Результаты анализа</h2>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 rounded bg-blue-50">
          <h3 className="font-medium text-blue-800">Зарплаты</h3>
          <div className="mt-2">
            <p className="text-sm text-gray-600">
              Всего: <span className="font-semibold">{items.total_number}</span>
            </p>
            <p className="text-sm text-gray-600">
              Среднее: <span className="font-semibold">{items.average} ₽</span>
            </p>
            <p className="text-sm text-gray-600">
              Медиана: <span className="font-semibold">{items.median} ₽</span>
            </p>
          </div>
        </div>
      </div>

      {/* Графики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <ImageGallery images={images} />
        {/* {images.map((img, index) => (
          <div key={index} className="bg-gray-100 p-2 rounded">
            <h4 className="text-sm font-medium text-gray-700 mb-2">
              {img.name}
            </h4>
            <img
              src={`data:image/png;base64,${img.data}`}
              alt={img.name}
              className="w-full h-auto rounded"
            />
            <p className="text-xs text-gray-500 mt-1">
              Размер: {(img.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ))} */}
      </div>

      {/* Ссылка на PDF */}
      {pdf_data && (
        <div className="mb-6">
          <a
            href={`data:application/pdf;base64,${pdf_data}`}
            download="analytics-report.pdf"
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                clipRule="evenodd"
              />
            </svg>
            Скачать отчет (PDF) (только графики и аналитика)
          </a>
        </div>
      )}
      {!pdf_data && (
        <div className="mb-6">
          <p className="inline-flex items-center text-red-600 hover:text-red-800">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                clipRule="evenodd"
              />
            </svg>
            Не удалось сгенерировать отчет :(
          </p>
        </div>
      )}

      {/* Ссылка на PDF полного отчета */}
      {pdf_full_data && (
        <div className="mb-6">
          <a
            href={`data:application/pdf;base64,${pdf_full_data}`}
            download="analytics-report.pdf"
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                clipRule="evenodd"
              />
            </svg>
            Скачать полный отчет (PDF)
          </a>
        </div>
      )}
      {!pdf_full_data && (
        <div className="mb-6">
          <p className="inline-flex items-center text-red-600 hover:text-red-800">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                clipRule="evenodd"
              />
            </svg>
            Не удалось сгенерировать полный отчет :(
          </p>
        </div>
      )}

      {/* Таблица вакансий */}
      <h3 className="text-lg font-medium mb-3">Отфильтрованные вакансии</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Должность
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ссылка
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Зарплата
              </th>
              {/* <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Опыт
              </th> */}
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Регион
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tables.map((vacancy, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">
                    {vacancy.name}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600">
                  <a
                    href={vacancy.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-800"
                  >
                    Открыть вакансию
                  </a>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {vacancy.salary.toLocaleString()} ₽
                </td>
                {/* <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {vacancy.experience} лет
                </td> */}
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {vacancy.region}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AnalyticsResults;
