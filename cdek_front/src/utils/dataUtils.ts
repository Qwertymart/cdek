// import { SalaryData, FilterParams } from "@/types";

// export const filterData = (
//   data: SalaryData[],
//   filters: FilterParams
// ): SalaryData[] => {
//   return data.filter((item) => {
//     // Фильтр по зарплате
//     if (
//       item.salary < filters.salaryRange[0] ||
//       item.salary > filters.salaryRange[1]
//     ) {
//       return false;
//     }

//     // Фильтр по должностям
//     if (
//       filters.positions.length > 0 &&
//       !filters.positions.includes(item.position)
//     ) {
//       return false;
//     }

//     // Фильтр по регионам
//     if (filters.regions.length > 0 && !filters.regions.includes(item.region)) {
//       return false;
//     }

//     // Фильтр по опыту
//     if (
//       filters.experience.length > 0 &&
//       !filters.experience.includes(item.experience)
//     ) {
//       return false;
//     }

//     // Фильтр по компаниям
//     if (
//       filters.companies.length > 0 &&
//       !filters.companies.includes(item.company || "")
//     ) {
//       return false;
//     }

//     // Фильтр по источникам
//     if (
//       filters.sources.length > 0 &&
//       !filters.sources.includes(item.source || "")
//     ) {
//       return false;
//     }

//     return true;
//   });
// };
