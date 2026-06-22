
//GLOBAL INITIALIZATION

const currentTeam = document.body.getAttribute('data-team');
const container = document.getElementById('overlay-container');

// RENDER METHOD WITH GEAR EXCLUSION

//  Dynamically renders the 3v3 layout rows using the supplied team data frame.

function renderOverlay(teamData) {
    if (!teamData) return;

    // Clear out any previous layout elements
    container.innerHTML = '';

    // Enforce exactly 3 rows for the 3v3 structure
    teamData.forEach(player => {
        const hasCharacter = player.character && player.character !== "No character assigned" && player.character !== "";
        const hasPlayerName = player.player && player.player.trim() !== "";

        // Skip rendering this entire row if the player name or character is missing
        if (!hasPlayerName || !hasCharacter) {
            return;
        }

        const rawTrainings = player.trainings || [];

        // Extract the first item as the Gear asset name if it exists
        const gearAssetName = rawTrainings.length > 0 ? rawTrainings[0] : null;

        // Standard trainings are everything AFTER the first item (index 1 onwards)
        const standardTrainings = rawTrainings.slice(1);
        const standardCount = standardTrainings.length;

        // Calculate dynamic row size (Size 1 to 5) based ONLY on standard training items
        let rowSize = 1;
        if (standardCount >= 5) {
            rowSize = 5;
        } else if (standardCount >= 2) {
            rowSize = standardCount; // 2, 3, or 4 items map to Sizes 2, 3, or 4
        } else {
            rowSize = 1; // 0 or 1 items map to Size 1
        }

        // Create the primary absolute row canvas
        const rowDiv = document.createElement('div');
        rowDiv.className = 'player-row';

        // 1. PRE-FLIP LOGIC FOR RED TEAM:
        // We define a class to pre-flip specific assets BEFORE the main row mirror happens.
        const preFlipClass = (currentTeam === 'red') ? 'pre-flip-asset' : '';

        // 2. MAIN ROW MIRROR:
        // Apply the layout mirror to the entire container after the internal elements are set.
        if (currentTeam === 'red') {
            rowDiv.classList.add('mirror-entire-row');
        }

        const teamSuffix = currentTeam; // 'blue' or 'red'

        // Frame asset links matching your specific naming convention
        const bgAsset = `assets/${rowSize}bg${teamSuffix}.png`;
        const borderAsset = `assets/${rowSize}${teamSuffix}.png`;
        const gearBgAsset = `assets/gearbg${teamSuffix}.png`;
        const gearFullAsset = `assets/gear3${teamSuffix}.png`;
        const pfpBorderAsset = `assets/pfp${teamSuffix}.png`;

        const charImgSrc = `assets/${player.character}.png`;
        const gearImgSrc = gearAssetName ? `assets/${gearAssetName}.png` : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
        //that string represents a 1x1 transparent png

        // Generate the layered inner HTML payload structure
        rowDiv.innerHTML = `
            <div class="row-sheet layer-bg" style="background-image: url('${bgAsset}');"></div>

            <div class="inline-content-track layer-under-gear">
                <div class="portrait-wrapper">
                    <img class="char-portrait" src="${charImgSrc}" alt="${player.character || 'Empty'}">

                    <img class="char-border ${preFlipClass}" src="${pfpBorderAsset}" alt="Portrait Border">
                </div>

                <div class="trainings-track">
                    ${standardTrainings.map(item => `
                        <img class="training-icon ${preFlipClass}" src="assets/${item}.png" title="${item}" alt="${item}">
                    `).join('')}
                </div>
            </div>

            <div class="row-sheet layer-gear-bg" style="background-image: url('${gearBgAsset}');"></div>

            <div class="inline-content-track layer-gear-icon-track">
                <div class="gear-wrapper">
                    <img class="gear-icon ${preFlipClass}" src="${gearImgSrc}" alt="Gear Icon" title="${gearAssetName || 'No Gear'}">
                </div>
            </div>

            <div class="row-sheet layer-gear-full" style="background-image: url('${gearFullAsset}');"></div>

            <div class="row-sheet layer-border" style="background-image: url('${borderAsset}');"></div>
        `;

        container.appendChild(rowDiv);
    });
}


// WEBSOCKET REAL-TIME CLIENT

function connectToWebSocket() {
    const socket = new WebSocket('ws://localhost:8765');

    socket.onopen = () => {
        console.log('Successfully connected to Python WebSocket stream server.');
    };

    socket.onmessage = (event) => {
        console.log('--- WEBSOCKET PACKET RECEIVED ---');
        console.log('Raw string payload:', event.data);

        try {
            const data = JSON.parse(event.data);
            console.log('Parsed JavaScript object structure:', data);

            // Check if the payload is wrapped in a team object, otherwise fall back to the raw array
            let teamData = null;
            if (data && data[currentTeam]) {
                teamData = data[currentTeam];
            } else if (Array.isArray(data)) {
                teamData = data; // Fallback if the backend updates just the array directly
            }

            if (teamData) {
                console.log(`Rendering overlay with ${teamData.length} players for context: ${currentTeam}`);
                renderOverlay(teamData);
            } else {
                console.warn(`Received packet but found no matching dataset for team: ${currentTeam}`);
            }

        } catch (error) {
            console.error('Error interpreting the incoming data frame string:', error);
        }
    };

    socket.onclose = () => {
        console.log('WebSocket server disconnected. Retrying connection in 3 seconds...');
        setTimeout(connectToWebSocket, 3000);
    };

    socket.onerror = (error) => {
        console.error('WebSocket communication glitch encountered:', error);
    };
}

connectToWebSocket();
