let name = "Nathan's";

// Copy over the variables from the previous activity
let title = name + " Test Plotly Chart"; 

let url = "http://pi3.sytes.net:5015/api/v1.0/categories";

d3.json(url).then(function (stateData) {
    console.log(stateData)
    
	let values = [];
	let labels = [];
       
    stateData.forEach(item => {
    	console.log("Key:", Object.keys(item)[0])
    	console.log("Values:", Object.values(item)[0])
    	values.push(Object.values(item)[0]);
    	labels.push(Object.keys(item)[0]);
    });

	// Assign `x` and `y` values for the Plotly trace object
	let trace1 = {
  		values: values,
  		labels: labels,
  		type: 'pie'
	};

	// Leave the code below unchanged
	let data = [trace1];

	let layout = {
  		title: title
	};

	Plotly.newPlot("plot", data, layout);
});