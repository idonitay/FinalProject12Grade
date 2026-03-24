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

function createButton(id, parent, text, styles)
{
    let new_button = document.createElement('button');
    new_button.id = id;
    new_button.innerText = text;

    for (const style of styles)
    {
        new_button.classList.add(style);
    }

    parent.appendChild(new_button);
    return new_button;
}

function turn_canvas_to_dict(canvas_obj)
{
   return {
        width: canvas_obj.width,
        height: canvas_obj.height,
        data: canvas_obj.toDataURL("image/png") // base64 string
    };
}

function draw_dict_on_canvas(canvas, dict) {
    const ctx = canvas.getContext("2d");

    const img = new Image();
    img.src = dict.data;

    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
    };
}

function turn_brushstroke_to_dict(pointa, pointb, color, size)
{
    return {
        "pointA": pointa,
        "pointB": pointb,
        "color": color,
        "size": size
    }
}