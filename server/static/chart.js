function createChart(ctx, label, color) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [label, 'Remaining'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [color, '#444'],
                hoverBackgroundColor: [color, '#444'],
                borderWidth: 0
            }]
        },
        options: {
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false }
            },
            cutout: '70%'
        }
    });
}

const cpuChart = createChart(document.getElementById('cpuChart').getContext('2d'), 'CPU', 'rgba(255, 99, 132, 1)');
const ramChart = createChart(document.getElementById('ramChart').getContext('2d'), 'RAM', 'rgba(54, 162, 235, 1)');
const diskChart = createChart(document.getElementById('diskChart').getContext('2d'), 'Disk', 'rgba(75, 192, 192, 1)');


function updateChart(chart, value) {
    chart.data.datasets[0].data[0] = value;
    chart.data.datasets[0].data[1] = 100 - value;
    chart.update();
}


async function fetchMetrics(server_id) {
    try {
        const response = await fetch(`${window.location.origin}/metrics`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "server_id": cid })
        });

        const data = await response.json();

        
        updateChart(cpuChart, data.cpu);
        updateChart(ramChart, data.ram);
        updateChart(diskChart, data.disk);

        document.getElementById('cpuInfo').innerHTML = `<p class = "text-show">${data.cpu}% Usage</p>`;
        document.getElementById('ramInfo').innerHTML = `<p class = "text-show">${data.ram}% Usage</p>`;
        document.getElementById('diskInfo').innerHTML = `<p class = "text-show">${data.disk}% Usage</p>`;
    } catch (error) {
        console.error('Error fetching metrics:', error);
    }
}

setInterval(() => fetchMetrics(cid), 5000);
fetchMetrics(cid);