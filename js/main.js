

let body_div = document.getElementById("body");
current_painting_color = "#000000";
current_brush_size = 2;

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

function drawLine(canvasOrId, p1, p2, able2draw, color, brush_size) {
    if (able2draw)
    {
        // Find the canvas element
        const canvas =
            typeof canvasOrId === "string"
                ? document.getElementById(canvasOrId)
                : canvasOrId;

        const ctx = canvas.getContext("2d");
        //stylethe brush
        ctx.lineWidth = brush_size;
        ctx.strokeStyle = color;

        //draw the line
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
    }
}


function playerDrawHandler() {
    
    let canDraw = false;
    canvas.onmousedown = function (e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        canDraw = true;
        let pointa = {x, y};

        canvas.onmousemove = function (moveEvent) {
            const rect = canvas.getBoundingClientRect();
            const x = moveEvent.clientX - rect.left;
            const y = moveEvent.clientY - rect.top;

            let pointb = pointa;
            pointa = {x, y};

            drawLine("canvas", pointa, pointb, canDraw, current_painting_color, current_brush_size);

            canvas.mouseleave = function () 
            {
                canvas.onmousemove = null;
                canDraw = false
            };

            canvas.onmouseup = function () 
            {
                canvas.onmousemove = null;
                canDraw = false
            };
        };
    };

    canvas.onmouseleave = function () 
    {
        canvas.onmousemove = null;
        canDraw = false;
    };

    
}

function changeBrushColor()
{
    red_color_box.onclick = function() {
        current_painting_color = "#FF0000"
    }

    black_color_box.onclick = function() {
        current_painting_color = "#000000"
    }

    green_color_box.onclick = function() {
        current_painting_color = "rgb(6, 150, 51)"
    }
}

function changeBrushSize() 
{
    small_brush.onclick = function() {
        current_brush_size = 2;
    }

    big_brush.onclick = function() {
        current_brush_size = 7;
    }
}

//canvas creation and event handler
canvas_wrapper_div = createDiv("canvas-wrapper-div", body_div, ["canvas_wrapper_div"])
canvas = createCanvas("canvas", canvas_wrapper_div, []);
canvas.addEventListener('mousedown', playerDrawHandler)

//colors creation and event handlers
colors_wrapper = createDiv("colors-wrapper-div", body_div, ["color_box_wrapper"]);
black_color_box = createDiv("black-color-box", colors_wrapper, ["color_box", "black_bg"]);
red_color_box = createDiv("red-color-box", colors_wrapper, ["color_box", "red_bg"]);
green_color_box = createDiv("green-color-box", colors_wrapper, ["color_box", "green_bg"]);


red_color_box.addEventListener('click', changeBrushColor)
black_color_box.addEventListener('click', changeBrushColor)
green_color_box.addEventListener('click', changeBrushColor)

//brush size creation and event handlers
small_brush = createDiv("small-brush", body_div, ["circle", "small_circle"]);
big_brush = createDiv("big-brush", body_div, ["circle", "big_circle"]);

small_brush.addEventListener("click", changeBrushSize)
big_brush.addEventListener("click", changeBrushSize)
// drawLine(canvas=canvas, p1={x: 40, y: 80}, p2={x: 200, y: 200})
// drawLine(canvas=canvas, p1={x: 70, y: 68}, p2={x: 300, y: 100})

