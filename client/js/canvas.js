//create a class that is the canvas - where you can draw - it is a matrix, that when a player draws, the matrix changes and the screen canvas updates acoordingly
class Canvas {
    constructor(width, height, x0, y0)
    {
        this.width = width;
        this.height = height;
        this.x0 = x0;
        this.y0 = y0;
        this.mat = this.createMatrix(this.width, this.height, "#FFFFFF")
    }

    //create a matrix with a given value
    createMatrix(rows, cols, defaultValue = 0) 
    {
        return Array(rows).fill().map(() => Array(cols).fill(defaultValue));
    }

    //change the value of a color of a single cell
    changeCellColor(row, col, color)
    {
        if (row < this.x0 + this.width && col < this.y0 + this.height && rox > this.x0 && col > this.y0)
        {
            this.mat[row][col] = color
        }
    }
}
