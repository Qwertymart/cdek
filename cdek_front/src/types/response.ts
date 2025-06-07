export interface Response {
  success: boolean;
  error: string;
  pdf_data: string;
  images: ImageResp[];
  items: AnalysisItemResponse;
  tables: TableResponse[];
}

export interface ImageResp {
  name: string;
  type: number;
  data: string;
  size: number;
}

export interface AnalysisItemResponse {
  total_number: number;
  average: number; // float
  median: number;
}

export interface TableResponse {
  name: string;
  salary: number;
  link: string;
  experience: number;
  region: string;
}
