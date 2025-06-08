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

  // рассчитываем проценты ползунка зарплаты: 1000000 - max; 30000 - min
  const percent = (value: number) =>
    ((value - 30000) / (1000000 - 30000)) * 100;

  // рассчитываем проценты ползунка стажа: 20 - max; 0 - min
  const percentExp = (value: number) => ((value - 0) / (20 - 0)) * 100;

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
                max="1000000"
                step="10000"
                value={filters.salaryRange[0]}
                onChange={(e) => handleSalaryChange(e, 0)}
                className="salary-slider_0 flex-1 w-full h-2 rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(
      to right,
      #22c55e 0%,
      #22c55e ${percent(filters.salaryRange[0])}%,
rgb(255, 255, 255) ${percent(filters.salaryRange[0])}%,
      #e5e7eb 100%
    )`,
                }}
              />
              <style jsx>{`
                .salary-slider_0::-webkit-slider-thumb {
                  -webkit-appearance: none;
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .salary-slider_0::-moz-range-thumb {
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
              `}</style>
              {/*accent-green-500 focus:accent-green-500*/}
              <span className="text-sm w-24">
                {filters.salaryRange[0].toLocaleString()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm w-10">До:</span>
              <input
                type="range"
                min="30000"
                max="1000000"
                step="10000"
                value={filters.salaryRange[1]}
                onChange={(e) => handleSalaryChange(e, 1)}
                className="salary-slider_1 flex-1 w-full h-2 rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(
      to right,
      #22c55e 0%,
      #22c55e ${percent(filters.salaryRange[1])}%,
rgb(255, 255, 255) ${percent(filters.salaryRange[1])}%,
      #e5e7eb 100%
    )`,
                }}
              />
              <style jsx>{`
                .salary-slider_1::-webkit-slider-thumb {
                  -webkit-appearance: none;
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .salary-slider_1::-moz-range-thumb {
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
              `}</style>
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
          label="Должность"
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
                className="exp-slider_0 flex-1 w-full h-2 rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(
      to right,
      #22c55e 0%,
      #22c55e ${percentExp(filters.experience[0])}%,
rgb(255, 255, 255) ${percentExp(filters.experience[0])}%,
      #e5e7eb 100%
    )`,
                }}
              />
              <style jsx>{`
                .exp-slider_0::-webkit-slider-thumb {
                  -webkit-appearance: none;
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .exp-slider_0::-moz-range-thumb {
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
              `}</style>
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
                className="exp-slider_1 flex-1 w-full h-2 rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(
      to right,
      #22c55e 0%,
      #22c55e ${percentExp(filters.experience[1])}%,
rgb(255, 255, 255) ${percentExp(filters.experience[1])}%,
      #e5e7eb 100%
    )`,
                }}
              />
              <style jsx>{`
                .exp-slider_1::-webkit-slider-thumb {
                  -webkit-appearance: none;
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .exp-slider_1::-moz-range-thumb {
                  width: 24px;
                  height: 24px;
                  border-radius: 50%;
                  background: white;
                  border: 2px solid #22c55e;
                  cursor: pointer;
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
              `}</style>
              {/* <input
                type="range"
                min="0"
                max="20"
                step="1"
                value={filters.experience[1]}
                onChange={(e) => handleExperienceChange(e, 1)}
                className="flex-1"
              /> */}
              <span className="text-sm w-4">{filters.experience[1]}</span>
            </div>
          </div>
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            style={{ backgroundColor: "#1ab248", color: "white" }}
            className="w-full text-white px-6 py-2 rounded-md shadow transition-colors"
          >
            Применить фильтры
          </button>
        </div>
      </div>
    </form>
  );
};

export default FilterPanel;
