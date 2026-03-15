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




    createScoreboard()
    {
        let scoreboard_wrapper = this.createScoreboardWrapper(["chat_box_wrapper"]);
    }

}