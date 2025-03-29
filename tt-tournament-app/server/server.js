const express = require("express");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

let players = [];
let matches = [];
let matchScores = {}; // Store scores for tie-breakers
let scoreboard = {}; // Player stats

// Generate short names
function generateCodeName(name) {
    let parts = name.split(" ");
    if (parts.length >= 3) {
        return parts[0].slice(0, 3) + parts[1].slice(0, 2);
    } else if (name.length > 3) {
        return name.slice(0, 3);
    }
    return name;
}

// Generate round-robin matches
app.post("/generate-matches", (req, res) => {
    const { players: playerList } = req.body;

    if (!playerList || playerList.length < 2) {
        return res.status(400).json({ error: "At least 2 players are required" });
    }

    players = playerList.map(name => name.trim());
    matches = [];
    matchScores = {};
    scoreboard = {};

    // Generate short names for internal use
    let shortNameMap = {};
    players.forEach(player => {
        shortNameMap[player] = generateCodeName(player);
    });

    let shortNames = Object.values(shortNameMap);

    // Generate unique matchups
    for (let i = 0; i < shortNames.length; i++) {
        for (let j = i + 1; j < shortNames.length; j++) {
            matches.push({
                player1: shortNames[i],
                player2: shortNames[j],
            });
        }
    }

    // Shuffle matches randomly
    matches.sort(() => Math.random() - 0.5);

    // Track how many matches each player has played
    let playerMatchCount = {};
    shortNames.forEach(name => (playerMatchCount[name] = 0));
    let finalMatches = [];

    for (let match of matches) {
        let { player1, player2 } = match;
        if (playerMatchCount[player1] < 2 && playerMatchCount[player2] < 2) {
            finalMatches.push(match);
            playerMatchCount[player1]++;
            playerMatchCount[player2]++;
        }
    }

    // Handle odd player cases
    let unmatched = shortNames.filter(p => playerMatchCount[p] < 2);
    while (unmatched.length >= 2) {
        let [p1, p2] = unmatched.splice(0, 2);
        finalMatches.push({ player1: p1, player2: p2 });
        playerMatchCount[p1]++;
        playerMatchCount[p2]++;
    }

    // Create scoreboard
    players.forEach(player => {
        scoreboard[player] = {
            MP: 0,
            W: 0,
            L: 0,
            D: 0,
            Pts: 0,
            TotalScored: 0,
        };
    });

    res.json({ matches: finalMatches, shortNameMap });
});

// Submit match scores
app.post("/submit-scores", (req, res) => {
    const { results } = req.body;

    if (!results || results.length === 0) {
        return res.status(400).json({ error: "No match results provided" });
    }

    results.forEach(match => {
        const { player1, player2, score1, score2 } = match;

        if (!scoreboard[player1] || !scoreboard[player2]) return;

        scoreboard[player1].MP += 1;
        scoreboard[player2].MP += 1;
        scoreboard[player1].TotalScored += score1;
        scoreboard[player2].TotalScored += score2;

        // Store scores for tie-breakers
        matchScores[`${player1}-${player2}`] = { score1, score2 };
        matchScores[`${player2}-${player1}`] = { score1: score2, score2: score1 };

        // Determine winner
        if (score1 > score2) {
            scoreboard[player1].W += 1;
            scoreboard[player2].L += 1;
            scoreboard[player1].Pts += score1 - score2; // Only difference is added
            scoreboard[player2].Pts -= score1 - score2; // Only difference is subtracted
        } else if (score2 > score1) {
            scoreboard[player2].W += 1;
            scoreboard[player1].L += 1;
            scoreboard[player2].Pts += score2 - score1;
            scoreboard[player1].Pts -= score2 - score1;
        }
    });

    // Sorting logic based on points difference
    let sortedPlayers = Object.entries(scoreboard)
        .map(([player, stats]) => ({ player, ...stats }))
        .sort((a, b) => b.Pts - a.Pts || b.TotalScored - a.TotalScored);

    res.json({ rankings: sortedPlayers });
});

// Start Server
const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
