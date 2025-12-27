

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


function changeBrushSize() 
{
    small_brush.onclick = function() {
        current_brush_size = 2;
    }

    big_brush.onclick = function() {
        current_brush_size = 7;
    }
}

function clearCanvas()
{
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
}

//canvas creation and event handler
canvas_wrapper_div = createDiv("canvas-wrapper-div", body_div, ["canvas_wrapper_div"])
canvas = createCanvas("canvas", canvas_wrapper_div, []);
canvas.addEventListener('mousedown', playerDrawHandler)

draw_tools_wrapper = createDiv("draw-tools-wrapper", body_div, ["draw_tools_wrapper"]);

//colors creation and event handlers
colors_wrapper = createDiv("colors-wrapper-div", draw_tools_wrapper, ["color_box_wrapper"]);

let draw_colors = [
    "#000000", // Black
    "#FF0000", // Red
    "rgb(6, 150, 51)", // green
    "rgb(31, 10, 188)", // blue
    "#FFFF00", // Yellow
    "rgb(255, 165, 0)", // Orange
    "rgba(217, 0, 255, 1)", // Magenta
    "rgba(0, 225, 255, 1)", // Teal
    "rgba(93, 102, 103, 1)", // gray
    "rgba(151, 159, 160, 1)", // light gray
    "rgba(124, 100, 197, 1)", // lilach
    "rgba(91, 13, 13, 1)", // Maroon
    "rgba(255, 255, 255, 1)", // white
    "rgba(10, 65, 2, 1)", // dark green
    "rgba(13, 2, 65, 1)", // dark blue
    "rgba(71, 51, 6, 1)", // brown
    "rgba(255, 0, 221, 1)", // pink
    "rgba(98, 205, 226, 1)", // sky

]

for (let draw_color of draw_colors)
{
    let box = createDiv("", colors_wrapper, ["color_box", "sw_button"]);
    box.style.backgroundColor = draw_color;
    box.addEventListener('click', function() {
        current_painting_color = draw_color;
    });
}

createDiv("", draw_tools_wrapper, ["row_break"]);

//brush size creation and event handlers
brushes_wrapper_div = createDiv("brushes-wrapper-div", draw_tools_wrapper, ["brushes_wrapper"]);
for (let brush_size = 1; brush_size <= 7; brush_size++)
{
    let brush = createDiv("", brushes_wrapper_div, ["circle", "sw_button"]);
    brush.style.width = brush_size * 5 + "px";
    brush.style.height = brush.style.width;
    brush.addEventListener("click", function() {
        current_brush_size = brush_size;
    });

}

createDiv("", draw_tools_wrapper, ["row_break"]);


//Board reset creation
reset_board_wrapper = createDiv("eraser-wrapper", draw_tools_wrapper, ["eraser_wrapper"]);
const trash_can = document.createElement('img');
trash_can.src = '../assets/trash_can.png'; // Replace with your image path or URL

reset_board_wrapper.appendChild(trash_can);
trash_can.classList.add("trash_can");
trash_can.classList.add("sw_button");

trash_can.addEventListener("click", clearCanvas)
// drawLine(canvas=canvas, p1={x: 40, y: 80}, p2={x: 200, y: 200})
// drawLine(canvas=canvas, p1={x: 70, y: 68}, p2={x: 300, y: 100})

