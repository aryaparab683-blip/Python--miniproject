const subjectChartEl = document.getElementById('subjectChart');
if (subjectChartEl) {
    const labels = JSON.parse(subjectChartEl.dataset.labels || '[]');
    const values = JSON.parse(subjectChartEl.dataset.values || '[]');
    const colors = JSON.parse(subjectChartEl.dataset.colors || '[]');
    new Chart(subjectChartEl, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#999' },
                },
            },
        },
    });
}
