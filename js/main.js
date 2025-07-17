async function loadData() {
  const res = await fetch('data/top100.json');
  const stocks = await res.json();
  const container = document.getElementById('stocks-table');
  container.innerHTML = '';

  stocks.forEach(stock => {
    const div = document.createElement('div');
    div.className = 'stock';
    div.innerHTML = `
      <h2>${stock.symbol} (${stock.change > 0 ? '+' : ''}${stock.change}%)</h2>
      <p>총 거래량: ${stock.volume.toLocaleString()}</p>
      <canvas id="chart-${stock.symbol}"></canvas>
    `;
    container.appendChild(div);

    const ctx = document.getElementById(`chart-${stock.symbol}`).getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: stock.timestamps,
        datasets: [{
          label: '가격',
          data: stock.data,
          borderColor: 'blue',
          backgroundColor: 'rgba(0, 0, 255, 0.1)',
          tension: 0.3,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero: false },
          x: { display: true }
        }
      }
    });
  });
}

// 30초마다 자동 갱신
loadData();
setInterval(loadData, 30000);
