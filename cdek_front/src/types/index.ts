import { Response } from "./response";
export interface SalaryData {
  id: number;
  position: string;
  salary: number;
  experience: number;
  region: string;
  date: string;
  company: string;
  source: string;
  skills: string[];
}

export interface FilterParams {
  salaryRange: [number, number];
  positions: string;
  experience: [number, number];
  regions: string[];
  companies: string[];
  sources: FilterSource[];
}

export interface FilterSource {
  id: number;
  name: string;
  url: string;
  availability: boolean; // флажок активности
}

export interface FilterPanelProps {
  positions: string[];
  regions: string[];
  sources: FilterSource[];
  companies: string[];
  onResults: (results: Response) => void;
  onLoading: (isLoading: boolean) => void;
}

export interface SearchableSelectProps {
  options: string[];
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  label: string;
  searchPlaceholder?: string;
  className?: string;
}

export interface MultiSelectProps {
  options: string[];
  value: string[];
  onChange: (value: string[]) => void;
  placeholder: string;
  label: string;
  searchPlaceholder?: string;
  className?: string;
}

export interface FilterSourceMultiSelectProps {
  options: FilterSource[];
  value: FilterSource[];
  onChange: (value: FilterSource[]) => void;
  placeholder: string;
  label: string;
  searchPlaceholder?: string;
  className?: string;
}
