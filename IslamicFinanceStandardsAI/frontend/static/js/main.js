/**
 * Islamic Finance Standards Enhancement Platform
 * Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    if (copyButtons.length > 0) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-copy-target');
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    // Select the text
                    const range = document.createRange();
                    range.selectNode(targetElement);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                    
                    // Copy the text
                    try {
                        document.execCommand('copy');
                        
                        // Visual feedback
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        
                        setTimeout(() => {
                            this.innerHTML = originalText;
                        }, 2000);
                    } catch (err) {
                        console.error('Failed to copy text: ', err);
                    }
                    
                    // Clear selection
                    window.getSelection().removeAllRanges();
                }
            });
        });
    }

    // Proposal voting functionality
    const voteButtons = document.querySelectorAll('.vote-btn');
    if (voteButtons.length > 0) {
        voteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (this.disabled) {
                    e.preventDefault();
                    return;
                }
                
                const voteType = this.getAttribute('data-vote-type');
                const proposalId = this.getAttribute('data-proposal-id');
                const voteForm = document.getElementById(`vote-form-${voteType}`);
                
                if (voteForm) {
                    voteForm.submit();
                }
            });
        });
    }

    // Comment form validation
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            const commentText = document.getElementById('comment').value.trim();
            
            if (commentText.length < 5) {
                e.preventDefault();
                alert('Comment must be at least 5 characters long.');
                return false;
            }
            
            return true;
        });
    }

    // Suggestion form validation
    const suggestionForm = document.getElementById('suggestion-form');
    if (suggestionForm) {
        suggestionForm.addEventListener('submit', function(e) {
            const suggestionText = document.getElementById('suggestion').value.trim();
            
            if (suggestionText.length < 10) {
                e.preventDefault();
                alert('Suggestion must be at least 10 characters long.');
                return false;
            }
            
            return true;
        });
    }

    // Search functionality
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('search-input');
            
            if (searchInput.value.trim().length < 3) {
                e.preventDefault();
                alert('Search query must be at least 3 characters long.');
                return false;
            }
            
            return true;
        });
    }

    // Profile form validation
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            const nameInput = document.getElementById('name');
            const currentPasswordInput = document.getElementById('current-password');
            
            if (nameInput.value.trim().length < 3) {
                e.preventDefault();
                alert('Name must be at least 3 characters long.');
                return false;
            }
            
            if (currentPasswordInput.value.trim().length === 0) {
                e.preventDefault();
                alert('Current password is required to save changes.');
                return false;
            }
            
            return true;
        });
    }

    // Diff view toggle
    const diffToggle = document.getElementById('diff-toggle');
    if (diffToggle) {
        diffToggle.addEventListener('change', function() {
            const currentText = document.getElementById('current-text');
            const proposedText = document.getElementById('proposed-text');
            const diffView = document.getElementById('diff-view');
            
            if (this.checked) {
                currentText.style.display = 'none';
                proposedText.style.display = 'none';
                diffView.style.display = 'block';
            } else {
                currentText.style.display = 'block';
                proposedText.style.display = 'block';
                diffView.style.display = 'none';
            }
        });
    }

    // Filter proposals by status
    const statusFilters = document.querySelectorAll('.status-filter');
    if (statusFilters.length > 0) {
        statusFilters.forEach(filter => {
            filter.addEventListener('click', function(e) {
                e.preventDefault();
                
                const status = this.getAttribute('data-status');
                const proposalItems = document.querySelectorAll('.proposal-item');
                
                // Update active filter
                statusFilters.forEach(f => f.classList.remove('active'));
                this.classList.add('active');
                
                // Filter proposals
                if (status === 'all') {
                    proposalItems.forEach(item => item.style.display = 'block');
                } else {
                    proposalItems.forEach(item => {
                        if (item.getAttribute('data-status') === status) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                }
            });
        });
    }

    // Sort proposals
    const sortOptions = document.querySelectorAll('.sort-option');
    if (sortOptions.length > 0) {
        sortOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                
                const sortBy = this.getAttribute('data-sort');
                const proposalContainer = document.querySelector('.proposal-container');
                const proposalItems = Array.from(document.querySelectorAll('.proposal-item'));
                
                // Update active sort option
                sortOptions.forEach(o => o.classList.remove('active'));
                this.classList.add('active');
                
                // Sort proposals
                proposalItems.sort((a, b) => {
                    if (sortBy === 'newest') {
                        return new Date(b.getAttribute('data-timestamp')) - new Date(a.getAttribute('data-timestamp'));
                    } else if (sortBy === 'votes') {
                        return parseInt(b.getAttribute('data-votes')) - parseInt(a.getAttribute('data-votes'));
                    } else if (sortBy === 'comments') {
                        return parseInt(b.getAttribute('data-comments')) - parseInt(a.getAttribute('data-comments'));
                    }
                    return 0;
                });
                
                // Re-append sorted items
                proposalItems.forEach(item => {
                    proposalContainer.appendChild(item);
                });
            });
        });
    }

    // Handle semantic search
    const semanticSearchForm = document.getElementById('semantic-search-form');
    if (semanticSearchForm) {
        semanticSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const searchInput = document.getElementById('semantic-search-input');
            const searchQuery = searchInput.value.trim();
            const useWeb = document.getElementById('use-web-search').checked;
            const resultsContainer = document.getElementById('search-results');
            
            if (searchQuery.length < 3) {
                alert('Search query must be at least 3 characters long.');
                return false;
            }
            
            // Show loading indicator
            resultsContainer.innerHTML = '<div class="text-center my-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">Searching...</p></div>';
            
            // Perform semantic search
            fetch(`/api/search?q=${encodeURIComponent(searchQuery)}&web=${useWeb}`)
                .then(response => response.json())
                .then(data => {
                    // Display results
                    if (data.length === 0) {
                        resultsContainer.innerHTML = '<div class="alert alert-info">No results found.</div>';
                    } else {
                        let resultsHtml = '<div class="list-group">';
                        
                        data.forEach(result => {
                            const source = result.metadata.source || 'Unknown';
                            const title = result.metadata.title || 'Untitled';
                            const url = result.metadata.url || '#';
                            const isWeb = result.metadata.retrieved_from_web || false;
                            
                            resultsHtml += `
                                <div class="list-group-item">
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <h5 class="mb-0">${title}</h5>
                                        <span class="badge ${isWeb ? 'bg-info' : 'bg-secondary'}">${source}</span>
                                    </div>
                                    <p>${result.content.substring(0, 200)}...</p>
                                    ${url !== '#' ? `<a href="${url}" target="_blank" class="btn btn-sm btn-outline-primary">View Source</a>` : ''}
                                </div>
                            `;
                        });
                        
                        resultsHtml += '</div>';
                        resultsContainer.innerHTML = resultsHtml;
                    }
                })
                .catch(error => {
                    console.error('Error performing search:', error);
                    resultsContainer.innerHTML = '<div class="alert alert-danger">An error occurred while searching. Please try again.</div>';
                });
            
            return false;
        });
    }
});
