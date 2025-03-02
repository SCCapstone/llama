const canvas = document.getElementById('metrics_graph');
const ctx = canvas.getContext('2d');

// Securely grab data of student's ratings
const rating_data = JSON.parse(document.getElementById('rating_data').textContent);

const c_width = canvas.width;
const c_height = canvas.height;
const padding = c_height * 0.1;
const g_width = c_width - (padding * 2);
const g_height = c_height - (padding * 2);

const min_score = 0;
const max_score = 5;

function init_graph() {
    // draw bounding lines
    ctx.strokeStyle = "black"
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, g_height + padding);
    ctx.lineTo(g_width + padding, g_height + padding);
    ctx.stroke();

    // draw horizontal lines
    ctx.strokeStyle = "gray"
    for(let i = min_score; i <= max_score; i++) {
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
        let  point = rating_data[i];
        ctx.fillStyle = 'green';
        if(!point.attendance) {
            ctx.fillStyle = 'red';
            point.score = 0;
        }
        if(!point.prepared) {
            ctx.fillStyle = 'orange';
        }
        ctx.arc(padding + ((i+1) * g_width)/rating_data.length+1, g_height + padding - ((point.score * g_height) / max_score), padding*.5, 0, 2*Math.PI);
        ctx.fill();

        // don't update weighted average on absent
        if(point.prepared) {
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

function draw_all() {
    init_graph();
    draw_points();
}

draw_all();