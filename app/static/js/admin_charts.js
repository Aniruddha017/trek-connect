const chartData = document.getElementById("chart-data").dataset;

const overviewData = [
    Number(chartData.totalUsers),
    Number(chartData.totalStaff),
    Number(chartData.totalTreks),
    Number(chartData.totalBookings)
];

const userData = [
    Number(chartData.activeUsers),
    Number(chartData.blacklistedUsers)
];

const trekStatusData = [
    Number(chartData.pendingTreks),
    Number(chartData.openTreks),
    Number(chartData.closedTreks),
    Number(chartData.ongoingTreks),
    Number(chartData.completedTreks)
];

new Chart(document.getElementById("overviewChart"), {

    type: "bar",
    data: {
        labels: [
            "Users",
            "Staff",
            "Treks",
            "Bookings"
        ],
        datasets: [{
            label: "Count",
            data: overviewData,
            borderRadius: 8,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});


new Chart(document.getElementById("userChart"), {

    type: "pie",
    data: {
        labels: [
            "Active Users",
            "Blacklisted Users"
        ],
        datasets: [{
            data: userData,
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


new Chart(document.getElementById("trekChart"), {

    type: "doughnut",
    data: {
        labels: [
            "Pending",
            "Open",
            "Closed",
            "Ongoing",
            "Completed"
        ],
        datasets: [{
            data: trekStatusData,
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