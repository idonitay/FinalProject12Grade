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

function createTextInput(id, parent, styles)
{
    return createInput(id, parent, styles, "text");
}

function createInput(id, parent, styles, input_type)
{
    let new_text_input = document.createElement('input');
    new_text_input.type = input_type;
    
    new_text_input.id = id;

    for (const style of styles)
    {
        new_text_input.classList.add(style);
    }

    parent.appendChild(new_text_input);
    return new_text_input;
}