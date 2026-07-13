const chartData = document.getElementById("chart-data").dataset;

const trekNames = chartData.trekNames.split(",");

const participantCounts = chartData.participantCounts.split(",").map(Number);

new Chart(document.getElementById("participantChart"), {

    type: "bar",
    data: {
        labels: trekNames,
        datasets: [{
            label: "Participants",
            data: participantCounts,
            backgroundColor: "#5c8773",
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
        }
    }
});