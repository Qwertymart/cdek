import React, { useState } from "react";
import { FilterParams, FilterSource } from "@/types";
import { Response } from "@/types/response";

interface FilterPanelProps {
  positions: string[];
  regions: string[];
  sources: FilterSource[];
  companies: string[];
  onResults: (results: Response) => void;
  onLoading: (isLoading: boolean) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  positions,
  regions,
  sources,
  companies,
  onResults,
  onLoading,
}) => {
  const [filters, setFilters] = useState<FilterParams>({
    salaryRange: [50000, 200000],
    positions: "",
    experience: [0, 5],
    regions: [],
    companies: [],
    sources: [],
  });

  const handleSalaryChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    index: number
  ) => {
    const newRange = [...filters.salaryRange] as [number, number];
    newRange[index] = Number(e.target.value);
    setFilters((prev) => ({ ...prev, salaryRange: newRange }));
  };

  const handleExperienceChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    index: number
  ) => {
    const newRange = [...filters.experience] as [number, number];
    newRange[index] = Number(e.target.value);
    setFilters((prev) => ({ ...prev, experience: newRange }));
  };

  const handleSelectChange = (
    e: React.ChangeEvent<HTMLSelectElement>,
    field: keyof FilterParams
  ) => {
    const options = Array.from(
      e.target.selectedOptions,
      (option) => option.value
    );
    setFilters((prev) => ({ ...prev, [field]: options }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    onLoading(true);

    try {
      const response = await fetch("/api/analytics", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(filters),
      });

      if (!response.ok) {
        throw new Error("Ошибка при получении данных");
      }

      const data: Response = await response.json();
      onResults(data);
    } catch (error) {
      console.error("Ошибка:", error);
    } finally {
      onLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-4 rounded-lg shadow mb-6"
    >
      <h2 className="text-lg font-semibold mb-4">Фильтры</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Диапазон зарплат */}
        <div>
          <label className="block mb-2 font-medium">Зарплата (₽)</label>
          <div className="space-y-2">
            <div>
              <span>От: </span>
              <input
                type="range"
                min="30000"
                max="500000"
                step="10000"
                value={filters.salaryRange[0]}
                onChange={(e) => handleSalaryChange(e, 0)}
                className="w-full"
              />
              <span>{filters.salaryRange[0].toLocaleString()}</span>
            </div>
            <div>
              <span>До: </span>
              <input
                type="range"
                min="30000"
                max="500000"
                step="10000"
                value={filters.salaryRange[1]}
                onChange={(e) => handleSalaryChange(e, 1)}
                className="w-full"
              />
              <span>{filters.salaryRange[1].toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Должности */}
        <div>
          <label className="block mb-2 font-medium">Должности</label>
          <select
            // multiple
            className="w-full border rounded p-2 h-32"
            value={filters.positions}
            onChange={(e) => handleSelectChange(e, "positions")}
          >
            {positions.map((position) => (
              <option key={position} value={position}>
                {position}
              </option>
            ))}
          </select>
        </div>

        {/* Регионы */}
        <div>
          <label className="block mb-2 font-medium">Регионы</label>
          <select
            multiple
            className="w-full border rounded p-2 h-32"
            value={filters.regions}
            onChange={(e) => handleSelectChange(e, "regions")}
          >
            {regions.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </div>

        {/* Компании */}
        <div>
          <label className="block mb-2 font-medium">Компании</label>
          <select
            multiple
            className="w-full border rounded p-2 h-32"
            value={filters.companies}
            onChange={(e) => handleSelectChange(e, "companies")}
          >
            {companies.map((company) => (
              <option key={company} value={company}>
                {company}
              </option>
            ))}
          </select>
        </div>

        {/* Источники */}
        <div>
          <label className="block mb-2 font-medium">Источники</label>
          <select
            multiple
            className="w-full border rounded p-2 h-32"
            value={filters.sources}
            onChange={(e) => handleSelectChange(e, "sources")}
          >
            {sources.map((source) => (
              <option key={source.id} value={source.name}>
                {source.name}
              </option>
            ))}
          </select>
        </div>

        {/* Опыт работы */}
        <div>
          <label className="block mb-2 font-medium">Опыт (лет)</label>
          <div className="space-y-2">
            <div>
              <span>От: </span>
              <input
                type="range"
                min="0"
                max="20"
                step="1"
                value={filters.experience[0]}
                onChange={(e) => handleExperienceChange(e, 0)}
                className="w-full"
              />
              <span>{filters.experience[0]}</span>
            </div>
            <div>
              <span>До: </span>
              <input
                type="range"
                min="0"
                max="20"
                step="1"
                value={filters.experience[1]}
                onChange={(e) => handleExperienceChange(e, 1)}
                className="w-full"
              />
              <span>{filters.experience[1]}</span>
            </div>
          </div>
        </div>

        {/* Кнопка отправки */}
        <div className="mt-4">
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md shadow transition-colors"
          >
            Применить фильтры
          </button>
        </div>
      </div>
    </form>
  );
};

export default FilterPanel;
