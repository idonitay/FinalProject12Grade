

let body_div = document.getElementById("body");
current_painting_color = "#000000";

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

function drawLine(canvasOrId, p1, p2, able2draw, color) {
    if (able2draw)
    {
        // Find the canvas element
        const canvas =
            typeof canvasOrId === "string"
                ? document.getElementById(canvasOrId)
                : canvasOrId;

        const ctx = canvas.getContext("2d");
        //stylethe brush
        ctx.lineWidth = 2;
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

            drawLine("canvas", pointa, pointb, canDraw, current_painting_color);

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

function changebrushcolor()
{
    red_color_box.onclick = function() {
        current_painting_color = "#FF0000"
    }

    black_color_box.onclick = function() {
        current_painting_color = "#000000"
    }
}

//canvas creation and event handler
canvas_wrapper_div = createDiv("canvas-wrapper-div", body_div, ["canvas_wrapper_div"])
canvas = createCanvas("canvas", canvas_wrapper_div, []);
canvas.addEventListener('mousedown', playerDrawHandler)

//colors creation and event handlers
colors_wrapper = createDiv("colors-wrapper-div", body_div, ["color_box_wrapper"]);
red_color_box = createDiv("red-color-box", colors_wrapper, ["color_box", "red_bg"]);
black_color_box = createDiv("black-color-box", colors_wrapper, ["color_box", "black_bg"]);

red_color_box.addEventListener('click', changebrushcolor)
black_color_box.addEventListener('click', changebrushcolor)
// drawLine(canvas=canvas, p1={x: 40, y: 80}, p2={x: 200, y: 200})
// drawLine(canvas=canvas, p1={x: 70, y: 68}, p2={x: 300, y: 100})

