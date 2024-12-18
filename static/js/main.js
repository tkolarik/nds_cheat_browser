// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const resultDiv = document.getElementById('result');
    const gameSearchInput = document.getElementById('game-search');
    const cheatSearchInput = document.getElementById('cheat-search');

    let currentGameID = '';

    // Handle ROM Upload
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous results and searches
        resultDiv.innerHTML = '';
        gameSearchInput.value = '';
        cheatSearchInput.value = '';
        cheatSearchInput.disabled = true;
        currentGameID = '';

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
                displayError(errorData.error);
                return;
            }

            const data = await response.json();
            currentGameID = data.gameid.split(' ')[0];
            displayCheats(data);
            cheatSearchInput.disabled = false;
        } catch (error) {
            console.error('Error:', error);
            displayError('An unexpected error occurred.');
        }
    });

    // Handle Game Search
    gameSearchInput.addEventListener('input', async () => {
        const query = gameSearchInput.value.trim();
        if (query === '') {
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
        if (query === '' || !currentGameID) {
            return;
        }

        try {
            const response = await fetch(`/search_cheats?game_id=${encodeURIComponent(currentGameID)}&q=${encodeURIComponent(query)}`);
            const data = await response.json();
            displayCheats({
                gameid: `${currentGameID} <JAMCRC>`,  // JAMCRC not displayed here
                game_name: data.name,
                folders: data.folders
            });
        } catch (error) {
            console.error('Error:', error);
        }
    });

    function displayError(message) {
        resultDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                ${message}
            </div>
        `;
    }

    function displayCheats(data) {
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
                    <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${folder.folder_name.replace(/\s+/g, '_')}" aria-expanded="false" aria-controls="${folder.folder_name.replace(/\s+/g, '_')}">
                        ${folder.folder_name}
                    </button>
                </h5>
            `;
            folderCard.appendChild(folderHeader);

            const folderBody = document.createElement('div');
            folderBody.id = folder.folder_name.replace(/\s+/g, '_');
            folderBody.className = 'collapse';
            folderBody.innerHTML = '<div class="card-body"></div>';
            folderCard.appendChild(folderBody);

            // Populate Cheats within Folder
            folder.cheats.forEach(cheat => {
                const cheatCard = document.createElement('div');
                cheatCard.className = 'card mb-2';

                const cheatHeader = document.createElement('div');
                cheatHeader.className = 'card-header';
                cheatHeader.innerHTML = `
                    <h6 class="mb-0">
                        <button class="btn btn-sm btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${cheat.name.replace(/\s+/g, '_')}_${Math.random().toString(36).substr(2, 9)}" aria-expanded="false" aria-controls="${cheat.name.replace(/\s+/g, '_')}">
                            ${cheat.name}
                        </button>
                    </h6>
                `;
                cheatCard.appendChild(cheatHeader);

                const cheatBody = document.createElement('div');
                const uniqueId = `${cheat.name.replace(/\s+/g, '_')}_${Math.random().toString(36).substr(2, 9)}`;
                cheatBody.id = uniqueId;
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

        // Implement Copy to Clipboard Functionality
        const copyButtons = resultDiv.querySelectorAll('.copy-btn');
        copyButtons.forEach(button => {
            button.addEventListener('click', () => {
                const codes = button.previousElementSibling.textContent;
                navigator.clipboard.writeText(codes).then(() => {
                    // Show a Bootstrap toast or alert for feedback
                    alert('Cheat codes copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                });
            });
        });
    }

    function displaySearchResults(data) {
        // Clear previous results
        resultDiv.innerHTML = '';

        // Display Search Results
        if (Object.keys(data).length === 0) {
            resultDiv.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    No games found matching your search.
                </div>
            `;
            return;
        }

        // Iterate over filtered games and display
        for (const [game_id, game_info] of Object.entries(data)) {
            const gameInfo = document.createElement('div');
            gameInfo.className = 'mb-4';
            gameInfo.innerHTML = `
                <h2>${game_info.name} (${game_id})</h2>
            `;
            resultDiv.appendChild(gameInfo);

            const foldersContainer = document.createElement('div');
            foldersContainer.id = `folders-container-${game_id}`;
            resultDiv.appendChild(foldersContainer);

            // Populate Folders and Cheats
            game_info.folders.forEach(folder => {
                const folderCard = document.createElement('div');
                folderCard.className = 'card mb-3';

                const folderHeader = document.createElement('div');
                folderHeader.className = 'card-header';
                folderHeader.innerHTML = `
                    <h5 class="mb-0">
                        <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${folder.folder_name.replace(/\s+/g, '_')}_${game_id}" aria-expanded="false" aria-controls="${folder.folder_name.replace(/\s+/g, '_')}">
                            ${folder.folder_name}
                        </button>
                    </h5>
                `;
                folderCard.appendChild(folderHeader);

                const folderBody = document.createElement('div');
                folderBody.id = `${folder.folder_name.replace(/\s+/g, '_')}_${game_id}`;
                folderBody.className = 'collapse';
                folderBody.innerHTML = '<div class="card-body"></div>';
                folderCard.appendChild(folderBody);

                // Populate Cheats within Folder
                folder.cheats.forEach(cheat => {
                    const cheatCard = document.createElement('div');
                    cheatCard.className = 'card mb-2';

                    const cheatHeader = document.createElement('div');
                    cheatHeader.className = 'card-header';
                    cheatHeader.innerHTML = `
                        <h6 class="mb-0">
                            <button class="btn btn-sm btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${cheat.name.replace(/\s+/g, '_')}_${Math.random().toString(36).substr(2, 9)}_${game_id}" aria-expanded="false" aria-controls="${cheat.name.replace(/\s+/g, '_')}">
                                ${cheat.name}
                            </button>
                        </h6>
                    `;
                    cheatCard.appendChild(cheatHeader);

                    const cheatBody = document.createElement('div');
                    const uniqueId = `${cheat.name.replace(/\s+/g, '_')}_${Math.random().toString(36).substr(2, 9)}_${game_id}`;
                    cheatBody.id = uniqueId;
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
            });
        }

        // Implement Copy to Clipboard Functionality
        const copyButtons = resultDiv.querySelectorAll('.copy-btn');
        copyButtons.forEach(button => {
            button.addEventListener('click', () => {
                const codes = button.previousElementSibling.textContent;
                navigator.clipboard.writeText(codes).then(() => {
                    // Show a Bootstrap toast or alert for feedback
                    alert('Cheat codes copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                });
            });
        });
    }
});
