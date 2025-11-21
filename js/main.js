

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

  // Get the canvas element
  const canvas = document.getElementById("canvas-wrapper-div");

  // Get the 2D rendering context
  const ctx = canvas.getContext("2d");

  // Set the fill color for the rectangle
  ctx.fillStyle = "blue";

  // Draw a filled rectangle
  // Parameters: x-coordinate, y-coordinate, width, height
  ctx.fillRect(20, 20, 150, 60);
  ctx.fill