// Wait for HTML document to load
document.addEventListener('DOMContentLoaded', function() {
    // Select all the hidden result boxes
    const resultBoxes = document.querySelectorAll('.result-box');
    // Set the initial number of results to display
    let visibleCount = 5;

    // Function to show only the first count
    function showResultsUpTo(count) {
        for (let i = 0; i < resultBoxes.length; i++) {
            if (i < count) {
                // Make visible
                resultBoxes[i].style.display = 'block';
            } else {
                // Hide
                resultBoxes[i].style.display = 'none';
            }
        }
    }

    // Show the first 5 results on page load
    showResultsUpTo(visibleCount);

    // Check if the "Load More" exists on the page
    const loadMoreBtn = document.getElementById('loadMoreButton');
    if (loadMoreBtn) {
        // Show 5 more additional results when pressed
        loadMoreBtn.addEventListener('click', function() {
            visibleCount += 5;
            // Update display
            showResultsUpTo(visibleCount);

            // If we've shown all results, hide the button
            if (visibleCount >= resultBoxes.length) {
                loadMoreBtn.style.display = 'none';
            }
        });
    }

    //Show Summary
    const summaryButtons = document.querySelectorAll('.show-summary-btn');

    // Loop through each summary
    summaryButtons.forEach((btn) => {
    btn.addEventListener('click', async function() {
        // Retrieve URL and query from the button's data attributes
        const url = btn.dataset.url;
        const query = btn.dataset.query;

        // Find the summary div
        const summaryDiv = btn.parentNode.querySelector('.result-summary');
        console.log("Summary div before update:", summaryDiv);

        // Check if summary div
        if (summaryDiv.style.display === 'none') {
            // Indicate summary is loading
            summaryDiv.textContent = 'Loading summary...';
            // Make summary div visible
            summaryDiv.style.display = 'block';
            try {
                // Send POST request to server
                const response = await fetch('/summarize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url, query })
                });
                // Throw error if response is not 200
                if (!response.ok) {
                    throw new Error('Network response was not OK');
                }

                // Parse JSON response from server
                const data = await response.json();
                console.log("Fetched summary:", data.summary);

                // Update summary with fetched summary text from AI
                summaryDiv.textContent = data.summary;

                // Debugging
            } catch (error) {
                // Display error message
                summaryDiv.textContent = 'Error loading summary.';
                console.error('Summary error:', error);
            }
            // ERM NEED TO FIX THIS
        } else {
            // Hide if summary div is visible
            summaryDiv.style.display = 'none';
        }
    });
});

});
