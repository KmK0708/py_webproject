import React from 'react';
import ReactSpeedometer from 'react-d3-speedometer';

function FearGreedGauge({index}) {
  return (
    <div style={{ background: '#1e1e2f', borderRadius: '12px', padding: '20px', width: '280px' }}>
      <h3 style={{ color: '#fff', textAlign: 'center' }}>Fear & Greed Index</h3>
      <ReactSpeedometer
        value={index}
        minValue={0}
        maxValue={100}
        segments={5}
        needleColor="white"
        segmentColors={['#ff4d4d', '#ffa500', '#f9f871', '#9acd32', '#00cc66']}
        height={160}
        width={250}
        textColor="#fff"
        currentValueText={`오늘 지수: ${index}`}
      />
      </div>
  )
}

export default FearGreedGauge