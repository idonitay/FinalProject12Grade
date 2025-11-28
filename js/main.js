

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

function drawLine(canvasOrId, p1, p2) {
    // Find the canvas element
    const canvas =
        typeof canvasOrId === "string"
            ? document.getElementById(canvasOrId)
            : canvasOrId;

    const ctx = canvas.getContext("2d");
    //stylethe brush
    ctx.lineWidth = 2;
    ctx.strokeStyle = "black";

    //draw the line
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
}


function playerDrawHandler() {
    let points = [];

    canvas.onclick = function (e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        points.push({ x, y });

        canvas.onmousemove = function (moveEvent) {
            const rect = canvas.getBoundingClientRect();
            const x = moveEvent.clientX - rect.left;
            const y = moveEvent.clientY - rect.top;

            points.push({ x, y });

            drawLine(
                "canvas",
                points[points.length - 2],
                points[points.length - 1]
            );

            canvas.mouseup = function () 
            {
                points = [];
                canvas.onmousemove = null;
            };
        };
    };

    canvas.mouseup = function () 
    {
        points = [];
        canvas.onmousemove = null;
    };

    
}


canvas_wrapper_div = createDiv("canvas-wrapper-div", body_div, ["canvas_wrapper_div"])
canvas = createCanvas("canvas", canvas_wrapper_div, []);
canvas.addEventListener('click', playerDrawHandler)

// drawLine(canvas=canvas, p1={x: 40, y: 80}, p2={x: 200, y: 200})
// drawLine(canvas=canvas, p1={x: 70, y: 68}, p2={x: 300, y: 100})

