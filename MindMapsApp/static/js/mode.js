document.addEventListener('DOMContentLoaded', function () {
    // Function to update the mode input value
    function setMode(mode) {
        document.getElementById('modeInput').value = mode;
    }

    // New function for setting the mode via button click.
    // This only applies the mode if the RAG checkbox is not checked.
    window.setModeFromButton = function(mode) {
        if (!document.getElementById('ragCheckbox').checked) {
            setMode(mode);
        }
    };

    // Update mode based on the checkbox state when it changes.
    document.getElementById('ragCheckbox').addEventListener('change', function() {
        if (this.checked) {
            // If the RAG checkbox is checked, force the mode to 'rag'
            setMode('rag');
        }
        // Optional: If unchecked, you can decide to revert to a default or leave the last button value intact.
    });

    // On form submission, make sure the mode is consistent with the checkbox state.
    const form = document.getElementById('userForm');
    form.addEventListener('submit', function () {
        if (document.getElementById('ragCheckbox').checked) {
            setMode('rag');
        }
        // If the checkbox is not checked, the mode remains as set by the last button click.
    });
});
