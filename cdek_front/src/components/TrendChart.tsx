'use client';

import * as d3 from 'd3';
import { useEffect, useRef } from 'react';
import { SalaryData } from '@/types';

interface Props {
    data: SalaryData[];
}

export default function TrendChart({ data }: Props) {
    const ref = useRef<SVGSVGElement | null>(null);

    useEffect(() => {
        const svg = d3.select(ref.current);
        svg.selectAll("*").remove();

        if (data.length === 0) return;

        const grouped = d3.groups(data, d => d.date).map(([date, items]) => ({
            date,
            median: d3.median(items, d => d.salary) || 0,
            avg: d3.mean(items, d => d.salary) || 0,
        }));

        const width = 500;
        const height = 300;
        const margin = { top: 20, right: 30, bottom: 30, left: 50 };

        const x = d3.scalePoint()
            .domain(grouped.map(d => d.date))
            .range([margin.left, width - margin.right]);

        const y = d3.scaleLinear()
            .domain([
                d3.min(grouped, d => Math.min(d.median, d.avg))! * 0.9,
                d3.max(grouped, d => Math.max(d.median, d.avg))! * 1.1,
            ])
            .nice()
            .range([height - margin.bottom, margin.top]);

        const lineMedian = d3.line<any>()
            .x(d => x(d.date)!)
            .y(d => y(d.median));

        const lineAvg = d3.line<any>()
            .x(d => x(d.date)!)
            .y(d => y(d.avg));

        svg.attr('width', width).attr('height', height);

        svg.append('g')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x));

        svg.append('g')
            .attr('transform', `translate(${margin.left},0)`)
            .call(d3.axisLeft(y));

        svg.append('path')
            .datum(grouped)
            .attr('fill', 'none')
            .attr('stroke', '#36a2eb')
            .attr('stroke-width', 2)
            .attr('d', lineMedian);

        svg.append('path')
            .datum(grouped)
            .attr('fill', 'none')
            .attr('stroke', '#ff6384')
            .attr('stroke-width', 2)
            .attr('d', lineAvg);
    }, [data]);

    return <svg id="trend-chart" ref={ref}></svg>;
}
