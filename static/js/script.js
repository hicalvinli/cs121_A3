document.addEventListener('DOMContentLoaded', function() {
    // Select all the hidden result boxes
    const resultBoxes = document.querySelectorAll('.result-box');
    // Track how many results are currently visible
    let visibleCount = 5;

    // Show up to 'count' results, hide the rest
    function showResultsUpTo(count) {
        for (let i = 0; i < resultBoxes.length; i++) {
            if (i < count) {
                resultBoxes[i].style.display = 'block';
            } else {
                resultBoxes[i].style.display = 'none';
            }
        }
    }

    // Show the first 5 results on the first search
    showResultsUpTo(visibleCount);

    // If the query has more than 5 results
    const loadMoreBtn = document.getElementById('loadMoreButton');
    if (loadMoreBtn) {
        // Display more searches if the button is pressed
        loadMoreBtn.addEventListener('click', function() {
            // Display 5 more results
            visibleCount += 5;
            showResultsUpTo(visibleCount);

            // If shown all results, hide the button
            if (visibleCount >= resultBoxes.length) {
                loadMoreBtn.style.display = 'none';
            }
        });
    }
});
