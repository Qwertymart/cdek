import { NextRequest, NextResponse } from "next/server";
import { FilterParams } from "@/types";
import {
  //   AnalysisItemResponse,
  //   ImageResp,
  Response,
  //   TableResponse,
} from "@/types/response";

export async function POST(req: NextRequest) {
  try {
    const filters: FilterParams = await req.json();
    console.log(filters);

    // const mockImages: ImageResp[] = [
    //   {
    //     name: "salary_distribution.png",
    //     type: 1,
    //     data: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
    //     size: 1024,
    //   },
    //   {
    //     name: "experience_chart.png",
    //     type: 2,
    //     data: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    //     size: 2048,
    //   },
    //   {
    //     name: "region_analysis.png",
    //     type: 3,
    //     data: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP4z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
    //     size: 1536,
    //   },
    // ];

    // const mockAnalysisItems: AnalysisItemResponse = {
    //   total_number: 1247,
    //   average: 165000.5,
    //   median: 160000.0,
    // };

    // const mockTables: TableResponse[] = [
    //   {
    //     name: "Senior Frontend Developer",
    //     salary: 220000,
    //     link: "https://hh.ru/vacancy/12345",
    //     experience: 5,
    //     region: "Москва",
    //   },
    //   {
    //     name: "React Developer",
    //     salary: 180000,
    //     link: "https://hh.ru/vacancy/12346",
    //     experience: 3,
    //     region: "Санкт-Петербург",
    //   },
    //   {
    //     name: "Frontend Developer",
    //     salary: 150000,
    //     link: "https://habr.com/vacancy/98765",
    //     experience: 2,
    //     region: "Москва",
    //   },
    //   {
    //     name: "Vue.js Developer",
    //     salary: 175000,
    //     link: "https://hh.ru/vacancy/12347",
    //     experience: 4,
    //     region: "Новосибирск",
    //   },
    //   {
    //     name: "JavaScript Developer",
    //     salary: 140000,
    //     link: "https://habr.com/vacancy/98766",
    //     experience: 2,
    //     region: "Екатеринбург",
    //   },
    // ];

    // const response: Response = {
    //   success: true,
    //   error: "",
    //   pdf_data:
    //     "JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PAovTGVuZ3RoIDYgMCBSCi9GaWx0ZXIgL0ZsYXRlRGVjb2RlCj4+CnN0cmVhbQp4nDNUMFAwULA1UPBIzcnPS1VwzclMz0vlcv5H5xwvWuPnOjhzs7NzP/K+u/ffPnz6fO+KWr6svVN8Mx8L+fLp8mbl4vLFjEwMDAwTczO3Nrd2NDQ2dDo4ODhmpGcWFxUVFhYW5ifn5SUUFRQUF+Yb5OTk5OQWFhYXFxcXFhcWFxYXFBcW",
    //   images: mockImages,
    //   items: mockAnalysisItems,
    //   tables: mockTables,
    // };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const apiUrl: any = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(apiUrl + "/analysis", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(filters),
    });

    if (!response.ok) {
      throw new Error(`Ошибка при получении данных: ${response.statusText}`);
    }

    const data: Response = await response.json();

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error("Analytics API error:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Internal server error",
      },
      { status: 500 }
    );
  }
}
