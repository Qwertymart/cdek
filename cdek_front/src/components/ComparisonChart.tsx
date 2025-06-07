'use client';

import * as d3 from 'd3';
import { useEffect, useRef } from 'react';
import { SalaryData } from '@/types';

interface Props {
    data: SalaryData[];
}

export default function ComparisonChart({ data }: Props) {
    const ref = useRef<SVGSVGElement | null>(null);

    useEffect(() => {
        const svg = d3.select(ref.current);
        svg.selectAll("*").remove();

        if (data.length === 0) return;

        const grouped = d3.groups(data, d => d.position).map(([position, items]) => ({
            label: position,
            avgSalary: d3.mean(items, d => d.salary) || 0,
        }));

        const width = 500;
        const height = 300;
        const margin = { top: 20, right: 20, bottom: 50, left: 60 };

        const x = d3.scaleBand()
            .domain(grouped.map(d => d.label))
            .range([margin.left, width - margin.right])
            .padding(0.2);

        const y = d3.scaleLinear()
            .domain([0, d3.max(grouped, d => d.avgSalary)!])
            .nice()
            .range([height - margin.bottom, margin.top]);

        svg.attr('width', width).attr('height', height);

        svg.append('g')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "rotate(15)")
            .style("text-anchor", "start")
            .attr("dx", "0.5em")
            .attr("dy", "0.1em");

        svg.append('g')
            .attr('transform', `translate(${margin.left},0)`)
            .call(d3.axisLeft(y));

        svg.selectAll('.bar')
            .data(grouped)
            .enter()
            .append('rect')
            .attr('x', d => x(d.label)!)
            .attr('y', d => y(d.avgSalary))
            .attr('width', x.bandwidth())
            .attr('height', d => y(0) - y(d.avgSalary))
            .attr('fill', 'rgba(75,192,192,0.6)');
    }, [data]);

    return <svg id="comparison-chart" ref={ref}></svg>;
}
