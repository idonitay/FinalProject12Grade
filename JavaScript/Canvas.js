class Canvas {
    constructor(width, height, x0, y0)
    {
        this.width = width;
        this.height = height;
        this.x0 = x0;
        this.y0 = y0;
        this.mat = this.createMatrix(this.width, this.height, "#FFFFFF")
    }

    createMatrix(rows, cols, defaultValue = 0) 
    {
        return Array(rows).fill().map(() => Array(cols).fill(defaultValue));
    }

    changeCellColor(row, col, color)
    {
        if (row < this.x0 + this.width && col < this.y0 + this.height && rox > this.x0 && col > this.y0)
        {
            this.mat[row][col] = color
        }
    }
}