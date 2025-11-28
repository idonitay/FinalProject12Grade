

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
    for (const style of styles) 
    {
        canvas.classList.add(style);
    }
    canvas.width = 400;
    canvas.height = 400;

    // Append it to parent
    parent.appendChild(canvas);

    // Get context
    const ctx = canvas.getContext("2d");

    // Draw a rectangle
    
    // Parameters: x-coordinate, y-coordinate, width, height
    ctx.fillRect(400, 50, 400, 400);

    return canvas;
}

function drawLine(canvas, p1, p2)
{
    //finding the canvas
    
    const ctx = canvas.getContext("2d");
    
    //styling the brush
    ctx.lineWidth = 2;
    ctx.strokeStyle = "black";
    
    //drawing the line
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
}

canvas_wrapper_div = createDiv("canvas-wrapper-div", body_div, ["canvas_wrapper_div"])
canvas = createCanvas("canvas", canvas_wrapper_div, []);

drawLine(canvas=canvas, p1={x: 4, y: 8}, p2={x: 200, y: 200})