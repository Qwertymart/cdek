"use client";

import React, { useState } from "react";
import FilterPanel from "@/components/FilterPanel";
import AnalyticsResults from "@/components/AnalyticsResults";
import type { Response } from "@/types/response";
import { FilterSource } from "@/types";
import { fakeDb_positions } from "@/utils/fakeDb";

const Dashboard: React.FC = () => {
  const [results, setResults] = useState<Response | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  //   const positions = ["Frontend Developer", "Backend Developer", "DevOps"];
  const positions = fakeDb_positions;   
  const regions = ["Москва", "Санкт-Петербург", "Новосибирск"];
  const companies = ["Boxberry", "Почта России", "ЯндексДоставка"];
  const sources: FilterSource[] = [
    {
      id: 1,
      name: "HeadHunter",
      url: "https://hh.ru",
      availability: true,
    },
    {
      id: 2,
      name: "Habr",
      url: "https://career.habr.com",
      availability: false,
    },
    {
      id: 3,
      name: "Avito",
      url: "https://avito.ru/vakansii",
      availability: false,
    },
    {
      id: 4,
      name: "SuperJob",
      url: "https://superjob.ru",
      availability: true,
    },
  ];

  const handleResults = (data: Response) => {
    setResults(data as Response);
  };

  const handleLoading = (loading: boolean) => {
    setIsLoading(loading);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Аналитика вакансий</h1>

      <FilterPanel
        positions={positions}
        regions={regions}
        sources={sources}
        companies={companies}
        onResults={handleResults}
        onLoading={handleLoading}
      />

      {isLoading && <div className="text-center py-8">Загрузка данных...</div>}

      {results && !isLoading && <AnalyticsResults data={results} />}
    </div>
  );
};

export default Dashboard;
