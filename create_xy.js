const width = 600,
        height = 400,
        margin = {
            top: 10,
            bottom: 30,
            left: 30,
            right: 30
        };

var t = d3.transition()
        .duration(750);

var svg = d3.select("#container").append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("margin", "0 auto")
        .style("display", "block")
        .style("overflow", "visible");

// x-axis
svg.append("g")
        .attr("id", "xaxisticks")
        .attr("transform", `translate(${0}, ${height - margin.bottom})`);

svg.append("text")
    .attr("transform",
        `translate(${width / 2}, ${height})`)
    .text("Sentiment");

//    Draw y-axis
svg.append("g")
    .attr("id", "yaxisticks")
    .attr("transform", `translate(${margin.left}, ${0})`);

svg.append("text")
    .attr("transform",
        `translate(${margin.left / 2}, ${height / 2}) rotate(-90)`)
    .text("Price");

function changeDates() {
    var before = document.getElementById('daysBefore').value;
    var after = document.getElementById('daysAfter').value;

}

function showDropdown() {
    document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches(".dropbtn")) {

        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains("show")) {
                openDropdown.classList.remove("show");
            }
        }
    }
};

create_chart("NVDA");

function create_chart(ticker) {
    d3.json(ticker + "_info.json", draw_stock_chart);
}

function percent_increase(d) {
    return d["close"] / d["open"] * 100 - 100;
}

function draw_stock_chart(error, data) {
    if (error) throw error;

    var x_range = d3.extent(data, function(d) { return d["sentiment"]});
    var y_range = d3.extent(data, percent_increase);

    var x = d3.scaleLinear()
        .domain(x_range)
        .range([margin.left, width - margin.right]);

    var y = d3.scaleLinear()
        .domain(y_range)
        .range([height - margin.bottom, margin.top]);

    var circles = svg.selectAll("circle")
        .data(data, function (d) {return d["sentiment"] + " " + percent_increase(d)});

    circles
        .exit()
        .transition(t)
        .attr("cy", function(d) { return y(percent_increase(d)) + 100; })
        .attr("color", "blue")
        .style("fill-opacity", 1e-6)
        .remove();

    // If, for some statistically improbable reason, there is a circle in the update selection:
    circles
        .transition(t)
        .attr("cx", function(d) {
            return x(d["sentiment"]);
        })
        .attr("cy", function(d) {
            return y(percent_increase(d));
        });

    circles
        .enter()
        .append("circle")
        .attr("cx", function(d) {
            return x(d["sentiment"]);
        })
        .attr("cy", function(d) {
            return y(percent_increase(d));
        })
        .attr("r", 5)
        .on("mouseover", function(d) {
            svg.append("text")
                .attr("class", "data_point_text")
                .attr("transform",
                    `translate(${x(d["sentiment"]) + 5}, ${y(percent_increase(d)) - 5})`)
                .text("Sentiment: " + d["sentiment"]  + "\nOpen: " + d["open"] + "\nClose: " + d["close"]);
        })
        .on("mouseout", function(d) {
            svg.selectAll(".data_point_text")
                .remove();
        });

    svg.select("#yaxisticks")
        .transition()
        .duration(1000)
        .call(d3.axisLeft(y).ticks(5));

    svg.select("#xaxisticks")
        .transition()
        .duration(1000)
        .call(d3.axisBottom(x).ticks(5));
}