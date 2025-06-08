import { MultiSelectProps } from "@/types";
import { X, ChevronDown, Search, Check } from "lucide-react";
import React, { useState, useRef, useEffect } from "react";

export const MultiSelect: React.FC<MultiSelectProps> = ({
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
          onKeyDown={(e: React.KeyboardEvent<HTMLDivElement>) => {
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
                      onKeyDown={(e: React.KeyboardEvent<HTMLLIElement>) => {
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
