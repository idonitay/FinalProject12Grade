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
        console.log("create score line")
        let scoreline = createDiv(`scoreboard-wrapper-${index}`, document.getElementById("scoreboard-wrapper"), []);
        
        return scoreline;
    }

    updateScoreLineByIndex(index, score, username)
    {
        let line = document.getElementById(`scoreboard-wrapper-${index}`);
        if (!line)
        {
            line = this.createScoreLineForPlayer(index);
        }
        
        line.innerHTML = `${username}: ${score} points`;

    }

    createScoreboard()
    {
        let scoreboard_wrapper = this.createScoreboardWrapper(["chat_box_wrapper", "box"]);
    }

}