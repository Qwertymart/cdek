import React, { useState, useRef, useEffect, KeyboardEvent } from "react";
import { ChevronDown, X, Search, Check } from "lucide-react";
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

interface SearchableSelectProps {
  options: string[];
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  label: string;
  searchPlaceholder?: string;
  className?: string;
}

interface MultiSelectProps {
  options: string[];
  value: string[];
  onChange: (value: string[]) => void;
  placeholder: string;
  label: string;
  searchPlaceholder?: string;
  className?: string;
}

const SearchableSelect: React.FC<SearchableSelectProps> = ({
  options = [],
  value,
  onChange,
  placeholder = "Выберите опцию...",
  label,
  searchPlaceholder = "Поиск...",
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filteredOptions = options.filter((option) =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (event: globalThis.MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchTerm("");
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className={`relative ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}

      <div ref={dropdownRef} className="relative">
        <div
          tabIndex={0}
          role="button"
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          onClick={() => setIsOpen(!isOpen)}
          onKeyDown={(e: KeyboardEvent) => {
            if (e.key === "Enter" || e.key === " ") setIsOpen(!isOpen);
          }}
          className="relative w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-left shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none hover:border-gray-400 transition-all duration-200 cursor-pointer"
        >
          <span className={value ? "text-gray-900" : "text-gray-500"}>
            {value || placeholder}
          </span>
          <div className="flex items-center gap-2 absolute right-3 top-1/2 transform -translate-y-1/2">
            {value && (
              <div
                role="button"
                tabIndex={0}
                aria-label="Clear selection"
                onClick={(e) => {
                  e.stopPropagation();
                  onChange("");
                }}
                onKeyDown={(e: KeyboardEvent) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.stopPropagation();
                    onChange("");
                  }
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors focus:outline-none"
              >
                <X className="h-4 w-4" />
              </div>
            )}
            <ChevronDown
              className={`h-5 w-5 text-gray-400 transition-transform duration-200 ${
                isOpen ? "rotate-180" : ""
              }`}
            />
          </div>
        </div>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
            <div className="p-3 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={searchPlaceholder}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none"
                />
              </div>
            </div>

            <div className="max-h-60 overflow-y-auto">
              {filteredOptions.length === 0 ? (
                <div className="px-4 py-3 text-gray-500 text-center">
                  Ничего не найдено
                </div>
              ) : (
                <ul role="listbox">
                  {filteredOptions.map((option) => (
                    <li
                      key={option}
                      role="option"
                      aria-selected={value === option}
                      onClick={() => {
                        onChange(option);
                        setIsOpen(false);
                        setSearchTerm("");
                      }}
                      onKeyDown={(e: KeyboardEvent) => {
                        if (e.key === "Enter" || e.key === " ") {
                          onChange(option);
                          setIsOpen(false);
                          setSearchTerm("");
                        }
                      }}
                      tabIndex={0}
                      className={`w-full px-4 py-3 text-left hover:bg-blue-50 focus:bg-blue-50 focus:outline-none transition-colors duration-150 cursor-pointer ${
                        value === option
                          ? "bg-blue-100 text-blue-700"
                          : "text-gray-900"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span>{option}</span>
                        {value === option && (
                          <Check className="h-4 w-4 text-blue-600" />
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const MultiSelect: React.FC<MultiSelectProps> = ({
  options = [],
  value = [],
  onChange,
  placeholder = "Выберите опции...",
  label,
  searchPlaceholder = "Поиск...",
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filteredOptions = options.filter((option) =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (event: globalThis.MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchTerm("");
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleToggleOption = (optionValue: string) => {
    const newValue = value.includes(optionValue)
      ? value.filter((v) => v !== optionValue)
      : [...value, optionValue];
    onChange(newValue);
  };

  const removeOption = (
    e: React.MouseEvent | React.KeyboardEvent,
    optionValue: string
  ) => {
    e.stopPropagation();
    onChange(value.filter((v) => v !== optionValue));
  };

  return (
    <div className={`relative ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}

      <div ref={dropdownRef} className="relative">
        <div
          tabIndex={0}
          role="button"
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          onClick={() => setIsOpen(!isOpen)}
          onKeyDown={(e: KeyboardEvent) => {
            if (e.key === "Enter" || e.key === " ") setIsOpen(!isOpen);
          }}
          className="relative w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-left shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none hover:border-gray-400 transition-all duration-200 min-h-[48px] cursor-pointer"
        >
          <div className="flex flex-wrap gap-1 pr-8">
            {value.length === 0 ? (
              <span className="text-gray-500">{placeholder}</span>
            ) : (
              value.map((option) => (
                <span
                  key={option}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-md"
                >
                  {option}
                  <div
                    role="button"
                    tabIndex={0}
                    aria-label={`Remove ${option}`}
                    onClick={(e) => removeOption(e, option)}
                    onKeyDown={(e: React.KeyboardEvent) => {
                      if (e.key === "Enter" || e.key === " ") {
                        removeOption(e, option);
                      }
                    }}
                    className="hover:bg-blue-200 rounded-full p-0.5 transition-colors focus:outline-none"
                  >
                    <X className="h-3 w-3" />
                  </div>
                </span>
              ))
            )}
          </div>
          <ChevronDown
            className={`absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 transition-transform duration-200 ${
              isOpen ? "rotate-180" : ""
            }`}
          />
        </div>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
            <div className="p-3 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={searchPlaceholder}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none"
                />
              </div>
            </div>

            <div className="max-h-60 overflow-y-auto">
              {filteredOptions.length === 0 ? (
                <div className="px-4 py-3 text-gray-500 text-center">
                  Ничего не найдено
                </div>
              ) : (
                <ul role="listbox">
                  {filteredOptions.map((option) => (
                    <li
                      key={option}
                      role="option"
                      aria-selected={value.includes(option)}
                      onClick={() => handleToggleOption(option)}
                      onKeyDown={(e: KeyboardEvent) => {
                        if (e.key === "Enter" || e.key === " ") {
                          handleToggleOption(option);
                        }
                      }}
                      tabIndex={0}
                      className="w-full px-4 py-3 text-left hover:bg-blue-50 focus:bg-blue-50 focus:outline-none transition-colors duration-150 cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <span
                          className={
                            value.includes(option)
                              ? "text-blue-700"
                              : "text-gray-900"
                          }
                        >
                          {option}
                        </span>
                        {value.includes(option) && (
                          <Check className="h-4 w-4 text-blue-600" />
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

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

  const handleSourcesChange = (value: string[]) => {
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

  const sourceOptions = sources.map((source) => source.name);

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

        <MultiSelect
          options={sourceOptions}
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
