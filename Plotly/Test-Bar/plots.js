let name = "Nathan's";

// Copy over the variables from the previous activity
let title = name + " Test Plotly Chart"; 

let url = "http://pi3.sytes.net:5015/api/v1.0/drg/1";

d3.json(url).then(function (stateData) {
    console.log(stateData)
    
	let xdata = [];
	let ydata = [];
       
    for (let k in stateData) {
    	item = stateData[k];
    	xdata.push(k);
    	ydata.push(item.avg_payments);
    }

	// Assign `x` and `y` values for the Plotly trace object
	let trace1 = {
  		x: xdata,
  		y: ydata,
  		type: 'bar'
	};

	// Leave the code below unchanged
	let data = [trace1];

	let layout = {
  		title: title
	};

	Plotly.newPlot("plot", data, layout);
});