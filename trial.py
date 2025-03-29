import random

# Function to generate short names
def generate_code_name(name):
    parts = name.split()
    if len(parts) >= 3:
        return parts[0][:3] + parts[1][:2]  # First 3 letters of first + first 2 of second
    elif len(name) > 3:
        return name[:3]  # First 3 letters for names longer than 3 characters
    return name  # Keep names of length 3 or less unchanged

# Function to schedule matches
def schedule_tt_tournament(players):
    while True:
        random.shuffle(players)
        matches = set()
        
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                match = tuple(sorted([players[i], players[j]]))  # Ensure unique pairing
                matches.add(match)

        match_list = list(matches)
        random.shuffle(match_list)

        # Track match counts
        player_match_count = {player: 0 for player in players}
        final_matches = []
        
        for match in match_list:
            p1, p2 = match
            if player_match_count[p1] < 2 and player_match_count[p2] < 2:
                final_matches.append(match)
                player_match_count[p1] += 1
                player_match_count[p2] += 1

        # Handle odd number of players
        unmatched_players = [p for p, count in player_match_count.items() if count < 2]
        while len(unmatched_players) >= 2:
            p1, p2 = unmatched_players[:2]
            final_matches.append((p1, p2))
            player_match_count[p1] += 1
            player_match_count[p2] += 1
            unmatched_players = [p for p, count in player_match_count.items() if count < 2]

        if all(count == 2 for count in player_match_count.values()):
            return final_matches

# User input for player names
player_names = input("Enter player names separated by commas: ").split(',')
player_names = [name.strip() for name in player_names]  # Remove extra spaces

# Generate short names
short_name_map = {name: generate_code_name(name) for name in player_names}
short_names = list(short_name_map.values())

# Schedule matches using short names
matches = schedule_tt_tournament(short_names)

# Reverse name mapping for display
reverse_name_map = {v: k for k, v in short_name_map.items()}

print("\nPlayer Codes (Used Internally):")
for full_name, code in short_name_map.items():
    print(f"{full_name} → {code}")

print("\nScheduled Matches:")
full_matches = []
match_scores = {}  # To store individual match scores

for i, match in enumerate(matches, start=1):
    full_match = (reverse_name_map[match[0]], reverse_name_map[match[1]])
    full_matches.append(full_match)
    print(f"Match {i}: {full_match[0]} vs {full_match[1]}")

# Scoreboard dictionary
scoreboard = {player: {"MP": 0, "W": 0, "L": 0, "D": 0, "Pts": 0, "TotalScored": 0} for player in player_names}

# Enter Scores
print("\nEnter Scores for Each Match:")
for i, match in enumerate(full_matches, start=1):
    p1, p2 = match
    print(f"\nMatch {i}: {p1} vs {p2}")
    score1 = int(input(f"Enter score for {p1}: "))
    score2 = int(input(f"Enter score for {p2}: "))

    # Store match scores for tie-breaker
    match_scores[(p1, p2)] = (score1, score2)
    match_scores[(p2, p1)] = (score2, score1)

    # Update scoreboard
    scoreboard[p1]["MP"] += 1
    scoreboard[p2]["MP"] += 1
    scoreboard[p1]["TotalScored"] += score1
    scoreboard[p2]["TotalScored"] += score2

    if score1 > score2:
        scoreboard[p1]["W"] += 1
        scoreboard[p2]["L"] += 1
        scoreboard[p1]["Pts"] += 3
    elif score2 > score1:
        scoreboard[p2]["W"] += 1
        scoreboard[p1]["L"] += 1
        scoreboard[p2]["Pts"] += 3
    else:
        scoreboard[p1]["D"] += 1
        scoreboard[p2]["D"] += 1
        scoreboard[p1]["Pts"] += 1
        scoreboard[p2]["Pts"] += 1

# Sorting function with tie-breaker
def tie_breaker(player1, player2):
    """ Breaks ties based on head-to-head results, then total points scored. """
    p1_pts = scoreboard[player1]["Pts"]
    p2_pts = scoreboard[player2]["Pts"]

    if p1_pts != p2_pts:
        return p2_pts - p1_pts  # Higher points rank higher

    # Head-to-head result
    if (player1, player2) in match_scores:
        score1, score2 = match_scores[(player1, player2)]
        if score1 > score2:
            return -1  # player1 won, ranks higher
        elif score2 > score1:
            return 1  # player2 won, ranks higher

    # Total points scored as a secondary tie-breaker
    p1_total = scoreboard[player1]["TotalScored"]
    p2_total = scoreboard[player2]["TotalScored"]

    if p1_total != p2_total:
        return p2_total - p1_total  # Higher total points rank higher

    # Random choice if everything is still tied
    return random.choice([-1, 1])

# Display Final Standings
sorted_scores = sorted(scoreboard.items(), key=lambda x: x[1]["Pts"], reverse=True)
sorted_scores.sort(key=lambda x: (x[1]["Pts"], x[1]["TotalScored"]), reverse=True)

print("\n🏆 Final Standings (Point Table with Tie-Breaker) 🏆")
print(f"{'Rank':<5} {'Player':<20} {'MP':<5} {'W':<5} {'L':<5} {'D':<5} {'Pts':<5} {'TotalPts':<10}")
ranked_players = sorted_scores.copy()

for i in range(len(ranked_players) - 1):
    if ranked_players[i][1]["Pts"] == ranked_players[i + 1][1]["Pts"]:
        if tie_breaker(ranked_players[i][0], ranked_players[i + 1][0]) > 0:
            ranked_players[i], ranked_players[i + 1] = ranked_players[i + 1], ranked_players[i]

for rank, (player, stats) in enumerate(ranked_players, 1):
    print(f"{rank:<5} {player:<20} {stats['MP']:<5} {stats['W']:<5} {stats['L']:<5} {stats['D']:<5} {stats['Pts']:<5} {stats['TotalScored']:<10}")
