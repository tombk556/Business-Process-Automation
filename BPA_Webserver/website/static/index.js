document.addEventListener('DOMContentLoaded', function() {
    const fetchButton = document.getElementById('fetch-data-button');
    fetchButton.addEventListener('click', fetchData);
});

function fetchData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            updateTable(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function updateTable(data) {
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = ''; // Clear existing table data

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${item.auto_id}</td>
                         <td>${item.ip}</td>
                         <td><a href="${item.href}" target="_blank" class="button is-link is-small">Access Link</a></td>
                         <td>${item.timestamp}</td>`;
        tableBody.appendChild(row);
    });
}
