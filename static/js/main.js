// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const resultDiv = document.getElementById('result');
    const gameSearchInput = document.getElementById('game-search');
    const cheatSearchInput = document.getElementById('cheat-search');

    const parsedGameIDDiv = document.getElementById('parsed-gameid');
    const currentGameSearchDiv = document.getElementById('current-game-search');
    const currentCheatSearchDiv = document.getElementById('current-cheat-search');

    let currentGameID = '';

    // Initialize Bootstrap Toasts
    const toastEl = document.getElementById('feedback-toast');
    const toast = new bootstrap.Toast(toastEl);

    const copyNameToastEl = document.getElementById('copy-name-toast');
    const copyNameToast = new bootstrap.Toast(copyNameToastEl);

    function showCopyNameToast() {
        copyNameToast.show();
    }

    // Handle ROM Upload
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous results and searches
        resultDiv.innerHTML = '';
        gameSearchInput.value = '';
        cheatSearchInput.value = '';
        cheatSearchInput.disabled = true;
        currentGameID = '';

        // Hide previous GameID and search term displays
        parsedGameIDDiv.classList.add('d-none');
        currentGameSearchDiv.classList.add('d-none');
        currentCheatSearchDiv.classList.add('d-none');
        currentGameSearchDiv.textContent = '';
        currentCheatSearchDiv.textContent = '';

        const fileInput = document.getElementById('rom');
        const files = fileInput.files;

        if (files.length === 0) {
            alert('Please select a .nds file to upload.');
            return;
        }

        const file = files[0];

        // Prepare form data
        const formData = new FormData();
        formData.append('rom', file);

        // Show loading indicator
        const loading = document.createElement('div');
        loading.className = 'text-center my-4';
        loading.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Processing...</p>
        `;
        resultDiv.appendChild(loading);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            // Remove loading indicator
            resultDiv.removeChild(loading);

            if (!response.ok) {
                const errorData = await response.json();
                displayError(errorData.error, errorData.gameid);
                return;
            }

            const data = await response.json();
            currentGameID = data.gameid;  // Use full GameID
            displayCheats(data);

            // Display Parsed GameID
            parsedGameIDDiv.innerHTML = `<strong>Parsed GameID:</strong> ${data.gameid}`;
            parsedGameIDDiv.classList.remove('d-none');

            cheatSearchInput.disabled = false;
        } catch (error) {
            console.error('Error:', error);
            displayError('An unexpected error occurred.');
        }
    });

    // Handle Game Search
    gameSearchInput.addEventListener('input', async () => {
        const query = gameSearchInput.value.trim();

        // Update Current Game Search Term Display
        if (query !== '') {
            currentGameSearchDiv.innerHTML = `<strong>Current Game Search:</strong> "${query}"`;
            currentGameSearchDiv.classList.remove('d-none');
        } else {
            currentGameSearchDiv.classList.add('d-none');
            currentGameSearchDiv.textContent = '';
        }

        if (query === '') {
            // Optionally, display all games or clear results
            return;
        }

        try {
            const response = await fetch(`/search_games?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            displaySearchResults(data);
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Handle Cheat Search
    cheatSearchInput.addEventListener('input', async () => {
        const query = cheatSearchInput.value.trim();

        // Update Current Cheat Search Term Display
        if (query !== '') {
            currentCheatSearchDiv.innerHTML = `<strong>Current Cheat Search:</strong> "${query}"`;
            currentCheatSearchDiv.classList.remove('d-none');
        } else {
            currentCheatSearchDiv.classList.add('d-none');
            currentCheatSearchDiv.textContent = '';
        }

        if (query === '' || !currentGameID) {
            return;
        }

        try {
            const response = await fetch(`/search_cheats?game_id=${encodeURIComponent(currentGameID)}&q=${encodeURIComponent(query)}`);
            const data = await response.json();
            displayCheats({
                gameid: currentGameID,  // Use full GameID
                game_name: data.name,
                folders: data.folders
            });
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Improved copy function with iOS support
    function handleCopy(text, successCallback) {
        // For iOS Safari compatibility
        if (navigator.userAgent.match(/ipad|iphone/i)) {
            // Create input element
            const textArea = document.createElement("input");
            textArea.value = text;
            textArea.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 2em;
                height: 2em;
                padding: 0;
                border: none;
                outline: none;
                box-shadow: none;
                background: transparent;
                opacity: 0;
                -webkit-user-select: text;
                user-select: text;
            `;

            document.body.appendChild(textArea);

            // Handle iOS specific quirks
            textArea.contentEditable = true;
            textArea.readOnly = false;
            
            const range = document.createRange();
            range.selectNodeContents(textArea);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            textArea.setSelectionRange(0, text.length);

            try {
                // Attempt to copy
                document.execCommand('copy');
                successCallback();
            } catch (err) {
                console.error('iOS Copy failed:', err);
                // Try modern clipboard API as fallback
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text)
                        .then(successCallback)
                        .catch(err => console.error('Clipboard API failed:', err));
                }
            } finally {
                // Clean up
                document.body.removeChild(textArea);
                selection.removeAllRanges();
            }
        } else {
            // For non-iOS devices, use the modern Clipboard API with fallback
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text)
                    .then(successCallback)
                    .catch(err => {
                        console.error('Clipboard API Error:', err);
                        fallbackCopyText(text, successCallback);
                    });
            } else {
                fallbackCopyText(text, successCallback);
            }
        }
    }

    function fallbackCopyText(text, successCallback) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.cssText = 'position: fixed; top: 0; left: 0; opacity: 0;';
        document.body.appendChild(textarea);
        
        try {
            textarea.focus();
            textarea.select();
            const successful = document.execCommand('copy');
            if (successful) {
                successCallback();
            }
        } catch (err) {
            console.error('Fallback: Unable to copy', err);
        } finally {
            document.body.removeChild(textarea);
        }
    }

    function displayError(message, gameid = '') {
        let errorMessage = `
            <div class="alert alert-danger" role="alert">
                ${message}
        `;
        if (gameid) {
            errorMessage += `<br><strong>Parsed GameID:</strong> ${gameid}`;
        }
        errorMessage += `</div>`;
        resultDiv.innerHTML = errorMessage;
    }

    function sanitizeId(str) {
        return str.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    }

    function generateUniqueID() {
        return '_' + Math.random().toString(36).substr(2, 9);
    }

    function displayCheats(data) {
        // Clear previous results
        resultDiv.innerHTML = '';

        // Display Game Information
        const gameInfo = document.createElement('div');
        gameInfo.className = 'mb-4';
        gameInfo.innerHTML = `
            <h2>${data.game_name} (${data.gameid})</h2>
        `;
        resultDiv.appendChild(gameInfo);

        // Container for Folders and Cheats
        const foldersContainer = document.createElement('div');
        foldersContainer.id = 'folders-container';
        resultDiv.appendChild(foldersContainer);

        // Populate Folders and Cheats
        data.folders.forEach(folder => {
            const folderCard = document.createElement('div');
            folderCard.className = 'card mb-3';

            const folderHeader = document.createElement('div');
            folderHeader.className = 'card-header';
            folderHeader.innerHTML = `
                <h5 class="mb-0">
                    <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${sanitizeId(folder.folder_name)}" aria-expanded="false" aria-controls="${sanitizeId(folder.folder_name)}">
                        ${folder.folder_name}
                    </button>
                </h5>
            `;
            folderCard.appendChild(folderHeader);

            const folderBody = document.createElement('div');
            folderBody.id = sanitizeId(folder.folder_name);
            folderBody.className = 'collapse';
            folderBody.innerHTML = '<div class="card-body"></div>';
            folderCard.appendChild(folderBody);

            // Populate Cheats within Folder
            folder.cheats.forEach(cheat => {
                const cheatCard = document.createElement('div');
                cheatCard.className = 'card mb-2';

                const cheatHeader = document.createElement('div');
                cheatHeader.className = 'card-header d-flex justify-content-between align-items-center';
                const uniqueCheatId = `${sanitizeId(cheat.name)}_${generateUniqueID()}`;
                cheatHeader.innerHTML = `
                    <h6 class="mb-0">
                        <button class="btn btn-sm btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${uniqueCheatId}" aria-expanded="false" aria-controls="${uniqueCheatId}">
                            ${cheat.name}
                        </button>
                    </h6>
                    <button class="btn btn-sm btn-outline-secondary copy-name-btn" data-cheat-name="${cheat.name}" title="Copy Cheat Name" aria-label="Copy Cheat Name">
                        <img src="/static/icons/copy-icon.svg" alt="Copy" width="16" height="16" class="copy-icon">
                    </button>
                `;
                cheatCard.appendChild(cheatHeader);

                const cheatBody = document.createElement('div');
                cheatBody.id = uniqueCheatId;
                cheatBody.className = 'collapse';
                cheatBody.innerHTML = `
                    <div class="card-body">
                        <p><strong>Notes:</strong> ${cheat.notes || 'N/A'}</p>
                        <p><strong>Codes:</strong></p>
                        <pre class="bg-light p-2 rounded">${cheat.codes || 'N/A'}</pre>
                        <button class="btn btn-secondary btn-sm copy-btn">Copy Codes</button>
                    </div>
                `;
                cheatCard.appendChild(cheatBody);

                folderBody.querySelector('.card-body').appendChild(cheatCard);
            });

            foldersContainer.appendChild(folderCard);
        });

        // Implement Copy Codes Functionality
        const copyCodeButtons = resultDiv.querySelectorAll('.copy-btn');
        copyCodeButtons.forEach(button => {
            button.addEventListener('click', () => {
                const codes = button.previousElementSibling.textContent;
                handleCopy(codes, () => toast.show());
            });
        });

        // Implement Copy Name Functionality
        const copyNameButtons = resultDiv.querySelectorAll('.copy-name-btn');
        copyNameButtons.forEach(button => {
            button.addEventListener('click', () => {
                const cheatName = button.getAttribute('data-cheat-name');
                handleCopy(cheatName, () => showCopyNameToast());
            });
        });
    }
});