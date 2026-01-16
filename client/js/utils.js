function createDiv(id, parent, styles)
{
    let newDiv = document.createElement('div');
    newDiv.id = id;

    for (const style of styles)
    {
        newDiv.classList.add(style);
    }

    parent.appendChild(newDiv);
    return newDiv;
}