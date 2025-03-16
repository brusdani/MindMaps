document.addEventListener('DOMContentLoaded', function () {
    const nodeSelector = document.getElementById('nodeSelector');

    // Fetch data from the 'data.json' file
    fetch("../static/data.json")
        .then(response => response.json())
        .then(data => {
            // Populate the drop-down menu with nodes
            data.nodes.forEach(function (node) {
                const option = document.createElement('option');
                option.value = node.id;  // Use the node's id as the value
                option.innerText = node.id;  // Use the node's id as the text
                nodeSelector.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Error loading data.json:", error);
        });
});
