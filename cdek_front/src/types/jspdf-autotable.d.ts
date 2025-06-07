import { jsPDF } from 'jspdf';

declare module 'jspdf-autotable' {
  interface AutoTableOptions {
    startY?: number;
    margin?: number | { top?: number; right?: number; bottom?: number; left?: number };
    head?: (string | { content: string; styles?: Record<string, any> })[][];
    body?: (string | number | { content: string | number; styles?: Record<string, any> })[][];
    foot?: (string | number | { content: string | number; styles?: Record<string, any> })[][];
    styles?: Record<string, any>;
    headStyles?: Record<string, any>;
    bodyStyles?: Record<string, any>;
    alternateRowStyles?: Record<string, any>;
    columnStyles?: Record<string, any>;
    didParseCell?: (data: any) => void;
    willDrawCell?: (data: any) => void;
    didDrawCell?: (data: any) => void;
    didDrawPage?: (data: any) => void;
  }

  interface jsPDFWithPlugin extends jsPDF {
    lastAutoTable?: { finalY: number };
    autoTable: (options: AutoTableOptions) => jsPDFWithPlugin;
  }

  const autoTable: (doc: jsPDF, options: AutoTableOptions) => jsPDFWithPlugin;
  export default autoTable;
}
