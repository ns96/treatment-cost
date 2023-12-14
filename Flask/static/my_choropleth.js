// funtion to create intervals from a min max range
// https://stackoverflow.com/questions/68803346/split-a-range-of-min-and-max-in-n-intervals
function getIntervals(min, max, nbIntervalls) {
    max -= min;  // --------------------------> subtract min
    var size = Math.round((max-1) / nbIntervalls);
    var result = [];

    for (let i = 0; i < nbIntervalls; i++) {
        var inf = i + i * size;
        var sup = inf + size < max ? inf + size: max;

        result.push([inf + min, sup + min]);  // --------------------> add again min
        if(inf >= max || sup >= max) break;
    }
    return result;
}

// create the default map
function createDefaultMap() {
  // remove any old maps: https://stackoverflow.com/questions/19186428/refresh-leaflet-map-map-container-is-already-initialized
  document.getElementById('usmap').innerHTML = "<div class='col-md-12' id='map'></div>";
  
  var map = L.map('map').setView([37.8, -96], 4);

  var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  // control that shows state info on hover
  var info = L.control();

  info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info');
    this.update();
    return this._div;
  };

  info.update = function (props) {
    const contents = props ? `<b>${props.name}</b><br />${props.density} people / mi<sup>2</sup>` : 'Hover over a state';
    this._div.innerHTML = `<h4>Population Density</h4>${contents}`;
  };

  info.addTo(map);

  // get color depending on population density value
  function getColor(d) {
    return d > 1000 ? '#800026' :
      d > 500  ? '#BD0026' :
      d > 200  ? '#E31A1C' :
      d > 100  ? '#FC4E2A' :
      d > 50   ? '#FD8D3C' :
      d > 20   ? '#FEB24C' :
      d > 10   ? '#FED976' : '#FFEDA0';
  }

  function style(feature) {
    return {
      weight: 2,
      opacity: 1,
      color: 'white',
      dashArray: '3',
      fillOpacity: 0.7,
      fillColor: getColor(feature.properties.density)
    };
  }

  function highlightFeature(e) {
    const layer = e.target;

    layer.setStyle({
      weight: 5,
      color: '#666',
      dashArray: '',
      fillOpacity: 0.7
    });

    layer.bringToFront();

    info.update(layer.feature.properties);
  }

  /* global statesData */
  var geojson = L.geoJson(statesData, {
    style,
    onEachFeature
  }).addTo(map);

  function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
  }

  function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
  }

  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
      click: zoomToFeature
    });
  }

  map.attributionControl.addAttribution('Population data &copy; <a href="http://census.gov/">US Census Bureau</a>');


  var legend = L.control({position: 'bottomright'});

  legend.onAdd = function (map) {

    const div = L.DomUtil.create('div', 'info legend');
    const grades = [0, 10, 20, 50, 100, 200, 500, 1000];
    const labels = [];
    let from, to;

    for (let i = 0; i < grades.length; i++) {
      from = grades[i];
      to = grades[i + 1];

      labels.push(`<i style="background:${getColor(from + 1)}"></i> ${from}${to ? `&ndash;${to}` : '+'}`);
    }

    div.innerHTML = labels.join('<br>');
    return div;
  };

  legend.addTo(map);
}

// function to do map with medical procedure cost information
function createMapWithCost(costData, min, max) {
  let costInt = getIntervals(min, max, 8);
  
  // remove any old maps: https://stackoverflow.com/questions/19186428/refresh-leaflet-map-map-container-is-already-initialized
  document.getElementById('usmap').innerHTML = "<div id='map'></div>";
  
  var map = L.map('map').setView([37.8, -96], 4);

  var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  // control that shows state info on hover
  var info = L.control();

  info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info');
    this.update();
    return this._div;
  };

  info.update = function (props) {
    var contents = "Hover over US State";
    
    if(props) {
      let cost = costData[props.abr];
      
      if(cost) {
        contents = `<b>${props.name}</b><br/>Average Cost: $${cost.avg_payments.toLocaleString()}`;
        contents += `<br/>Average Medicare: $${cost.avg_medicare.toLocaleString()}`
        contents += `<br/>Difference: $${cost.avg_difference.toLocaleString()}`
        contents += `<br/>Percent Medicare: ${cost.pct_medicare.toLocaleString()}%`
        contents += `<br>Total Providers: ${cost.count}<br>Total Patients: ${cost.discharges}`;
      } else {
        contents = `<b>${props.name}</b><br/>No Data`;
      }
    }
    
    this._div.innerHTML = `<h4>Procedure Cost</h4>${contents}`;
  };

  info.addTo(map);

  // get color depending on cost value
  function getColor(c) {
    return c > costInt[7][0]  ? '#800026' :
      c > costInt[6][0]       ? '#BD0026' :
      c > costInt[5][0]       ? '#E31A1C' :
      c > costInt[4][0]       ? '#FC4E2A' :
      c > costInt[3][0]       ? '#FD8D3C' :
      c > costInt[2][0]       ? '#FEB24C' :
      c > costInt[1][0]       ? '#FED976' : '#FFEDA0';
  }

  function style(feature) {
    let color = "#FFFFFF"; // white background
    let cost = costData[feature.properties.abr];
    
    if(cost) {
      color = getColor(cost.avg_payments);
    }
    
    return {
      weight: 2,
      opacity: 1,
      color: 'white',
      dashArray: '3',
      fillOpacity: 0.7,
      fillColor: color
    };
  }

  function highlightFeature(e) {
    const layer = e.target;

    layer.setStyle({
      weight: 5,
      color: '#666',
      dashArray: '',
      fillOpacity: 0.7
    });

    layer.bringToFront();

    info.update(layer.feature.properties);
  }

  /* global statesData */
  var geojson = L.geoJson(statesData, {
    style,
    onEachFeature
  }).addTo(map);

  function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
  }

  function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
    
    // get the state and load provider data
    let state = e.target.feature.properties.abr;
    let url = root + "/api/v1.0/providers/" + state + "/" + drgId;
    
    d3.json(url).then(function (data) {
      // add marker for each provider
      data.forEach(provider => {
        let marker = L.marker([provider.latitude, provider.longitude]).addTo(map);
        marker.bindPopup("<b>" + provider.name + "</b>");
      });
      
      // show the providers in a table
      showProviders(data);
    });
  }

  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
      click: zoomToFeature
    });
  }

  map.attributionControl.addAttribution('Population data &copy; <a href="http://census.gov/">US Census Bureau</a>');


  var legend = L.control({position: 'bottomright'});

  legend.onAdd = function (map) {

    const div = L.DomUtil.create('div', 'info legend');
    const grades = [costInt[0][0], costInt[1][0], costInt[2][0], costInt[3][0],
                    costInt[4][0], costInt[5][0], costInt[6][0], costInt[7][0]];
    const labels = [];
    let from, to;

    for (let i = 0; i < grades.length; i++) {
      from = grades[i];
      to = grades[i + 1];

      labels.push(`<i style="background:${getColor(from + 1)}"></i> $${from.toLocaleString()}${to ? ` &ndash; $${to.toLocaleString()}` : '+'}`);
    }

    div.innerHTML = labels.join('<br>');
    return div;
  };

  legend.addTo(map);
}

// load the default map with population density
createDefaultMap();