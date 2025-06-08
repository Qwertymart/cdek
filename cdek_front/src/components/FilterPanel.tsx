import React, { useState } from "react";
import { FilterPanelProps, FilterParams, FilterSource } from "@/types";
import { Response } from "@/types/response";
import FilterSourceMultiSelect from "./FilterSourceMultiSelect";
import { MultiSelect } from "./MultiSelect";
import { SearchableSelect } from "./SearchableSelect";

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

  const handlePositionChange = (value: string) => {
    setFilters((prev) => ({ ...prev, positions: value }));
  };

  const handleRegionsChange = (value: string[]) => {
    setFilters((prev) => ({ ...prev, regions: value }));
  };

  const handleCompaniesChange = (value: string[]) => {
    setFilters((prev) => ({ ...prev, companies: value }));
  };

  const handleSourcesChange = (value: FilterSource[]) => {
    setFilters((prev) => ({ ...prev, sources: value }));
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
        <div>
          <label className="block mb-2 font-medium">Зарплата (₽)</label>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-sm w-10">От:</span>
              <input
                type="range"
                min="30000"
                max="500000"
                step="10000"
                value={filters.salaryRange[0]}
                onChange={(e) => handleSalaryChange(e, 0)}
                className="flex-1"
              />
              <span className="text-sm w-24">
                {filters.salaryRange[0].toLocaleString()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm w-10">До:</span>
              <input
                type="range"
                min="30000"
                max="500000"
                step="10000"
                value={filters.salaryRange[1]}
                onChange={(e) => handleSalaryChange(e, 1)}
                className="flex-1"
              />
              <span className="text-sm w-24">
                {filters.salaryRange[1].toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        <SearchableSelect
          options={positions}
          value={filters.positions}
          onChange={handlePositionChange}
          placeholder="Выберите должность"
          label="Должности"
          searchPlaceholder="Поиск должности..."
        />

        <MultiSelect
          options={regions}
          value={filters.regions}
          onChange={handleRegionsChange}
          placeholder="Выберите регионы..."
          label="Регионы"
          searchPlaceholder="Поиск региона..."
        />

        <MultiSelect
          options={companies}
          value={filters.companies}
          onChange={handleCompaniesChange}
          placeholder="Выберите компании..."
          label="Компании"
          searchPlaceholder="Поиск компании..."
        />

        <FilterSourceMultiSelect
          options={sources}
          value={filters.sources}
          onChange={handleSourcesChange}
          placeholder="Выберите источники..."
          label="Источники"
          searchPlaceholder="Поиск источника..."
        />

        <div>
          <label className="block mb-2 font-medium">Опыт (лет)</label>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-sm w-10">От:</span>
              <input
                type="range"
                min="0"
                max="20"
                step="1"
                value={filters.experience[0]}
                onChange={(e) => handleExperienceChange(e, 0)}
                className="flex-1"
              />
              <span className="text-sm w-4">{filters.experience[0]}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm w-10">До:</span>
              <input
                type="range"
                min="0"
                max="20"
                step="1"
                value={filters.experience[1]}
                onChange={(e) => handleExperienceChange(e, 1)}
                className="flex-1"
              />
              <span className="text-sm w-4">{filters.experience[1]}</span>
            </div>
          </div>
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            className="w-full bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md shadow transition-colors"
          >
            Применить фильтры
          </button>
        </div>
      </div>
    </form>
  );
};

export default FilterPanel;
