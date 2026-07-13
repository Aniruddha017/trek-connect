const chartData = document.getElementById("chart-data").dataset;

const bookingHistory = [
    Number(chartData.booked),
    Number(chartData.completed),
    Number(chartData.cancelled)
];

const difficultyCounts = [
    Number(chartData.easy),
    Number(chartData.moderate),
    Number(chartData.hard)
];

new Chart(document.getElementById("historyChart"), {

    type: "pie",
    data: {
        labels: [
            "Booked",
            "Completed",
            "Cancelled"
        ],
        datasets: [{
            data: bookingHistory,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "bottom"
            }
        }
    }
});


new Chart(document.getElementById("difficultyChart"), {

    type: "bar",
    data: {
        labels: [
            "Easy",
            "Moderate",
            "Hard"
        ],
        datasets: [{
            label: "Bookings",
            data: difficultyCounts,
            borderRadius: 8
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0
                }
            }
        },
    }
});