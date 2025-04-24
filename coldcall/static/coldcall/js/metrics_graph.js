const canvas = document.getElementById('metrics_graph');

let c_width, c_height, padding, g_width, g_height = 0;
// initialize proper canvas size, 
function resize_canvas() {
    const container = canvas.parentElement;

    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    
    c_width = canvas.width;
    c_height = canvas.height;
    padding = c_height * 0.1;
    g_width = c_width - (padding * 2);
    g_height = c_height - (padding * 2);
    
}

window.addEventListener('load', resize_canvas());
window.addEventListener('resize', resize_canvas());

const ctx = canvas.getContext('2d');

// Securely grab data of student's ratings
const rating_data = JSON.parse(document.getElementById('rating_data').textContent);


const min_score = 0;
const max_score = 5;

const points = []; //populated in draw_points, store locations for tooltips

function init_graph() {
    ctx.reset();
    // draw bounding lines
    ctx.strokeStyle = "black"
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, g_height + padding);
    ctx.lineTo(g_width + padding, g_height + padding);
    ctx.stroke();

    // draw horizontal lines and text
    ctx.strokeStyle = "gray"
    for(let i = min_score; i <= max_score; i++) {
        ctx.font = "12px Arial";
        ctx.fillText(5-i, padding-10, (i * g_height) / max_score + padding);

        ctx.beginPath();
        
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, (i * g_height) / max_score + padding);
        ctx.lineTo(g_width + padding, (i * g_height) / max_score + padding)
        ctx.stroke();
    }
}

function draw_points() {
    let sum = 0, non_absent = 0;
    let last_x = padding, last_y = g_height + padding;

    for(let i = 0; i < rating_data.length; ++i) {
        // read data and draw point with color based on status, absent always appears as 0
        ctx.beginPath();
        ctx.setLineDash([]); // reset stroke for future loops
        let point = rating_data[i];
        ctx.fillStyle = 'green';
        if(!point.attendance) {
            ctx.fillStyle = 'red';
            point.score = 0;
        }
        if(!point.prepared) {
            ctx.fillStyle = 'orange';
            point.score = 0;
        }

        let x = padding + ((i+1) * g_width)/rating_data.length+1;
        let y = g_height + padding - ((point.score * g_height) / max_score);

        points.push({x,y, data: point}); // create obj with point data and position

        ctx.arc(x, y, padding*.5, 0, 2*Math.PI);
        ctx.fill();

        // don't update weighted average on absent or unprpared
        if(point.attendance && point.prepared) {
            // draw running average line 
            ctx.beginPath();
            ctx.setLineDash([4,4]) //4 pixels on, 4 pixels off
            ctx.strokeStyle = "black"
            ctx.moveTo(last_x, last_y);
            ++non_absent;
            sum += point.score;
            last_x = padding + ((i+1) * g_width)/rating_data.length+1;
            last_y = g_height + padding - ((sum/non_absent * g_height) / max_score);
            ctx.lineTo(last_x, last_y);
            ctx.stroke();
        }
    }
}

function calculate_linear_regression(data) {
    let n = data.length;
    if (n == 0) return null;

    let sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;

    for (let i = 0; i < n; i++) {
        let x = i+1;
        let y = data[i].score;

        sum_x += x;
        sum_y += y;
        sum_xy += x*y;
        sum_x2 += x*x;
    }
    // line of best fit formula
    let slope = ((n * sum_xy) - (sum_x * sum_y)) / ((n * sum_x2) - (sum_x * sum_x));
    let intercept = (sum_y - (slope * sum_x)) / n;

    return { slope, intercept };
}

function draw_best_fit() {
    let data = rating_data.filter(p => p.attendance && p.prepared)
        .map((p, i) => ({score: p.score, index: i+1}));

    if(data.length < 2) return;

    let { slope, intercept } = calculate_linear_regression(data);

    let x1 = padding;
    let y1 = g_height + padding - (((slope * 1 + intercept) * g_height) / max_score);

    let x2 = padding + (rating_data.length * g_width) / rating_data.length;
    let y2 = g_height + padding - (((slope * rating_data.length + intercept) * g_height) / max_score);

    ctx.beginPath();
    ctx.setLineDash([2, 2]);
    ctx.strokeStyle = "blue";
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
}


function draw_all() {
    ctx.clearRect(0, 0, c_width, c_height); // clears canvas on each draw
    init_graph();
    draw_points();
    draw_best_fit();
}

function show_hover(x, y, txt) {
    ctx.fillStyle = "white";
    ctx.strokeStyle = "black";
    ctx.lineWidth = 2;
    ctx.font = "12px Arial"; //TODO: replace this with better font once decided
    ctx.setLineDash([]);

    //TODO: change this to scale with canvas size instead of magic numbers
    let tooltip_width = ctx.measureText(txt).width + 10;
    let tooltip_height = 20;

    // render tooltip to the center to prevent it from rendering out of bounds
    if(x < g_width / 2) {
        ctx.fillRect(x + 10, y - 15, tooltip_width, tooltip_height);
        ctx.strokeRect(x + 10, y - 15, tooltip_width, tooltip_height);
        ctx.fillStyle = "black";
        ctx.fillText(txt, x + 15, y);
    } else {
        ctx.fillRect(x - 10 - tooltip_width, y - 15, tooltip_width, tooltip_height);
        ctx.strokeRect(x - 10 - tooltip_width, y - 15, tooltip_width, tooltip_height);
        ctx.fillStyle = "black";
        ctx.fillText(txt, x - 5 - tooltip_width, y);
    }
}

canvas.addEventListener("click", (event) => {
    draw_all();

    let rect = canvas.getBoundingClientRect();
    x = event.clientX - rect.left;
    y = event.clientY - rect.top;

    points.forEach(point => {
        const dx = x - point.x;
        const dy = y - point.y;
        let distance = Math.sqrt(dx ** 2 + dy ** 2);

        if(distance < padding * 1.2) { // dots have a radius of padding, give slightly more leniance on render
            let date = new Date(point.data.date);
            let txt = `${date.toLocaleString()}`;
            show_hover(point.x, point.y, txt);
        }
    });
});

canvas.addEventListener("mouseleave", (event) => {
    draw_all();
})

draw_all();