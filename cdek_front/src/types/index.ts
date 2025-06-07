// types.ts
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

// export interface AnalyticsResult {
//   vacancies: SalaryData[];
//   statistics: {
//     averageSalary: number;
//     medianSalary: number;
//     vacancyCount: number;
//     minExperience: number;
//     maxExperience: number;
//     averageExperience: number;
//   };
//   images: string[];
//   pdfUrl: string;
// }

export interface FilterParams {
  salaryRange: [number, number];
  positions: string;
  experience: [number, number];
  regions: string[];
  companies: string[];
  sources: string[];
}

export interface FilterSource {
  id: number;
  name: string;
  url: string;
}
