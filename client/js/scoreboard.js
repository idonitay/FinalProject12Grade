class scoreboard
{
    constructor(parent)
    {
        this.parent = parent;
    }

    createScoreboardWrapper(classes)
    {
        return createDiv("scoreboard-wrapper", this.parent, classes);
    }

    createScoreLineForPlayer(index)
    {
        let scoreline = createDiv(`scoreboard-wrapper-${index}`, document.getElementById("scoreboard-table-body"), ["scoreboard_row"]);

        createDiv("", scoreline, ["scoreboard_cell", "scoreboard_rank"]).textContent = index + 1;
        createDiv("", scoreline, ["scoreboard_cell", "scoreboard_player_name"]);
        createDiv("", scoreline, ["scoreboard_cell", "scoreboard_points"]);
        
        return scoreline;
    }

    updateScoreLineByIndex(index, score, username)
    {
        let line = document.getElementById(`scoreboard-wrapper-${index}`);
        if (!line)
        {
            line = this.createScoreLineForPlayer(index);
        }

        line.querySelector(".scoreboard_rank").textContent = index + 1;
        line.querySelector(".scoreboard_player_name").textContent = username;
        line.querySelector(".scoreboard_points").textContent = score;

    }

    createScoreboard()
    {
        let scoreboard_wrapper = this.createScoreboardWrapper(["scoreboard_wrapper", "box"]);
        let scoreboard_header = createDiv("", scoreboard_wrapper, ["scoreboard_header"]);

        createDiv("", scoreboard_header, ["scoreboard_cell", "scoreboard_rank"]).textContent = "#";
        createDiv("", scoreboard_header, ["scoreboard_cell", "scoreboard_player_name"]).textContent = "שחקן";
        createDiv("", scoreboard_header, ["scoreboard_cell", "scoreboard_points"]).textContent = "נקודות";

        createDiv("scoreboard-table-body", scoreboard_wrapper, ["scoreboard_body"]);
    }

}
