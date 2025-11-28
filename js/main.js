

let body_div = document.getElementById("body");

// let canvas_wrapper_div = createDiv("canvas-wrapper-div", body_div, ["canvas"]);

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

function createCanvas(id, parent, styles) {
    // Create a canvas element
    const canvas = document.createElement("canvas");
    canvas.id = id;

    // Apply styles if needed
    for (const style of styles) {
        canvas.classList.add(style);
    }

    // Append it to parent
    parent.appendChild(canvas);

    // Get context
    const ctx = canvas.getContext("2d");

    // Draw a rectangle
    ctx.fillStyle = "red";
    ctx.fillRect(20, 20, 150, 60);

    return canvas;
}

createCanvas("canvas-wrapper-div", body_div, []);