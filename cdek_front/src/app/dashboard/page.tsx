"use client";

import React, { useState } from "react";
import FilterPanel from "@/components/FilterPanel";
import AnalyticsResults from "@/components/AnalyticsResults";
import type { Response } from "@/types/response";
import { FilterSource } from "@/types";

const Dashboard: React.FC = () => {
  const [results, setResults] = useState<Response | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const positions = ["Frontend Developer", "Backend Developer", "DevOps"];
  const regions = ["Москва", "Санкт-Петербург", "Новосибирск"];
  const companies = ["Яндекс", "Сбер", "Тинькофф"];
  const sources: FilterSource[] = [
    { id: 1, name: "hh.ru", url: "https://hh.ru" },
    { id: 2, name: "habr.com", url: "https://career.habr.com" },
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
