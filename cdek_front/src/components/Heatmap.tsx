// import React, { useEffect, useRef } from 'react';
// import * as d3 from 'd3';
// import { RegionData } from '@/types';

// interface HeatmapProps {
//     data: RegionData[];
// }

// const Heatmap: React.FC<HeatmapProps> = ({ data }) => {
//     const svgRef = useRef<SVGSVGElement | null>(null);

//     useEffect(() => {
//         if (!svgRef.current || data.length === 0) return;

//         const svg = d3.select(svgRef.current);
//         svg.selectAll('*').remove(); // Очистка предыдущих рендеров

//         const width = 1000;
//         const cellSize = 150;
//         const cols = Math.floor(width / cellSize);
//         const rows = Math.ceil(data.length / cols);
//         const height = rows * cellSize;

//         svg.attr('width', width).attr('height', height);

//         const maxSalary = d3.max(data, d => d.avgSalary) || 1;

//         const group = svg.append('g');

//         data.forEach((region, i) => {
//             const x = (i % cols) * cellSize;
//             const y = Math.floor(i / cols) * cellSize;
//             const ratio = region.avgSalary / maxSalary;
//             const red = Math.round(255 * ratio);
//             const green = Math.round(255 * (1 - ratio));
//             const color = `rgb(${red}, ${green}, 50)`;

//             const cell = group.append('g').attr('transform', `translate(${x},${y})`);

//             cell.append('rect')
//                 .attr('width', cellSize - 10)
//                 .attr('height', cellSize - 10)
//                 .attr('fill', color)
//                 .attr('rx', 10)
//                 .attr('ry', 10);

//             cell.append('text')
//                 .attr('x', (cellSize - 10) / 2)
//                 .attr('y', 20)
//                 .attr('text-anchor', 'middle')
//                 .attr('fill', 'white')
//                 .style('font-size', '12px')
//                 .style('font-weight', 'bold')
//                 .text(region.region);

//             cell.append('text')
//                 .attr('x', (cellSize - 10) / 2)
//                 .attr('y', 40)
//                 .attr('text-anchor', 'middle')
//                 .attr('fill', 'white')
//                 .style('font-size', '12px')
//                 .text(`${region.avgSalary.toLocaleString()} ₽`);

//             cell.append('text')
//                 .attr('x', (cellSize - 10) / 2)
//                 .attr('y', 58)
//                 .attr('text-anchor', 'middle')
//                 .attr('fill', 'white')
//                 .style('font-size', '10px')
//                 .text(`Медиана: ${region.median.toLocaleString()} ₽`);

//             cell.append('text')
//                 .attr('x', (cellSize - 10) / 2)
//                 .attr('y', 74)
//                 .attr('text-anchor', 'middle')
//                 .attr('fill', 'white')
//                 .style('font-size', '10px')
//                 .text(`(${region.count} позиций)`);
//         });
//     }, [data]);

//     return (
//         <div className="overflow-x-auto">
//             <svg id="heatmap-chart" ref={svgRef} />
//         </div>
//     );
// };

// export default Heatmap;

// // import React from 'react';
// // import { RegionData } from '@/types';

// // interface HeatmapProps {
// //     data: RegionData[];
// // }

// // const Heatmap: React.FC<HeatmapProps> = ({ data }) => {
// //     const maxSalary = Math.max(...data.map(item => item.avgSalary), 1);

// //     return (
// //         <div className="overflow-x-auto">
// //             <div className="min-w-full inline-block align-middle">
// //                 <div className="grid grid-cols-[repeat(auto-fill,minmax(120px,1fr))] gap-4">
// //                     {data.map(region => {
// //                         const ratio = region.avgSalary / maxSalary;
// //                         const red = Math.round(255 * ratio);
// //                         const green = Math.round(255 * (1 - ratio));
// //                         const color = `rgb(${red}, ${green}, 50)`;


// //                         return (
// //                             <div
// //                                 key={region.region}
// //                                 className="text-center p-4 rounded-lg"
// //                                 style={{ backgroundColor: color }}
// //                             >
// //                                 <div className="font-semibold">{region.region}</div>
// //                                 <div className="text-lg font-bold">{region.avgSalary.toLocaleString()} ₽</div>
// //                                 <div className="text-sm">Медиана: {region.median.toLocaleString()} ₽</div>
// //                                 <div className="text-sm">({region.count} позиций)</div>
// //                             </div>
// //                         );
// //                     })}
// //                 </div>
// //             </div>
// //         </div>
// //     );
// // };

// // export default Heatmap;
