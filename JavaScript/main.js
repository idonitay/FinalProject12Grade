

let body_div = document.getElementById("body")

function createDiv(id, parent, styles)
{
    let newDiv = document.createElement('div');
    newDiv.id = id;
    for (const style in styles)
    {
        newDiv.classList.add(style);
    }

    parent.appendChild(newDiv);
    return newDiv;
}

