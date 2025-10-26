import React from 'react'
import {Line} from 'react-chartjs-2'

import{
    Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);


function FearGreedChart({ data }) {
  if (!data || data.length === 0) {
    return <div style={{ textAlign: 'center', color: '#999' }}>지수 데이터를 불러오는 중...</div>;
  }

  const datasetColors = data.map(d =>
  d.value < 25 ? 'red' : d.value < 50 ? 'orange' : d.value < 75 ? 'yellow' : 'green'
);

  const chartData = {
    labels: data.map(d => new Date(d.timestamp * 1000).toLocaleDateString('ko-KR')),
    datasets: [
      {
        label: 'Fear & Greed Index',
        data: data.map(d => Number(d.value)),
        fill: false,
        pointBackgroundColor: datasetColors,
        borderColor: 'rgba(75,192,192,1)',
        backgroundColor: 'rgba(75,192,192,0.4)',
        tension: 0.2,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '최근 30일 공포·탐욕지수' },
    },
    scales: {
      y: { min: 0, max: 100, title: { display: true, text: '지수(0~100)' } },
    },
  };

  return (
    <div style={{ background: '#1e1e1e', padding: '20px', borderRadius: '10px', marginTop: '30px' }}>
      <Line data={chartData} options={options} />
    </div>
  );
}

export default FearGreedChart;