
var geojson,
            activeLayer;
    $(document).ready(function(){

        function generate_chart_titles(country, nuts_code, title){

             var plot_title_line = "Trend in Unemployment Rate By ".concat(title)
             var plot_title_bar = "Unemployment Rate By ".concat(title)

             $("#avg_chart_title").text("Average Rate Over The Categories ".concat(country).concat(" - ").concat(nuts_code))
             $("#line_chart_title").text(plot_title_line);
             $("#line_chart_subtitle").text(country.concat(" - ").concat(nuts_code));
             $("#bar_chart_title").text(plot_title_bar);
             $("#bar_chart_subtitle").text(country.concat(" - ").concat(nuts_code));
        }

        function compute_average(dt){

                var avg_data = []
                var max = 0
                var copy_obj = JSON.parse(JSON.stringify(dt));
                for (var key in dt){
                    if (dt[key].length > max){
                          max = dt[key].length
                    }
                }

                for (var key in dt){
                    if (dt[key].length < max){
                        var diff = max - dt[key].length;
                         for (var i=0; i < diff; i++){
                            copy_obj[key].push(0);
                         }
                    }
                }

                for (var x in copy_obj[Object.keys(dt)[0]]){
                    avg_data.push(0);
                }

                for (var key in dt){

                    avg_data = avg_data.map(function (num, idx) {
                                  return (num + parseFloat(String(copy_obj[key][idx]).trim()));
                                });
                }
                var len = Object.keys(dt).length;

                for (var i = 0; i < avg_data.length; i++) {
                      avg_data[i] = avg_data[i]/len;
                    }

            return avg_data

        }

        function plot_graphs(data){

            if (data.status === 'success'){
                    var trace_obj = data['results']
                    var year = trace_obj['years']
                    var country = trace_obj.country;
                    var nuts_code = trace_obj.nuts_code;
                    var legend = {'legend_title': trace_obj.legend_title, 'x': '', 'y': ''}
                    delete trace_obj.years;
                    delete trace_obj.country;
                    delete trace_obj.nuts_code;
                    delete trace_obj.legend_title;

                    plot_data = get_plot_data(trace_obj, year);

                    legend['y'] = plot_data.max;
                    legend['x'] = year.slice(-1)[0];
                    var layout = plot_layout(country, nuts_code, legend)

                    generate_chart_titles(country, nuts_code, legend.legend_title);

                    Plotly.newPlot('nuts_avg_plot', [{type:'bar', x: year, y: compute_average(trace_obj)}], layout);
                    Plotly.newPlot('nuts_line_plot', plot_data.line_data, layout);
                    Plotly.newPlot('nuts_bar_plot', plot_data.bar_data, layout);
                    }

        }

        var meta_data = {
                      "IE": {'color': "#8856a7", 'country': 'Ireland'},
                      "IT": {'color': "#e6550d", 'country': 'Italy'},
                      "BG": {'color': "#c51b8a", 'country': 'Bulgaria'},
                      "FR": {'color': "#31a354", 'country': 'France'}
                   };

        function getColor(country_code){
             return meta_data[country_code].color
        };

        var div = L.popup().setContent('<div id="popupcontainer">Loading...</div>');
        var map = new L.Map('map-holder', {
            center: new L.LatLng(46.8719, 7.5674),
            zoom: 4.5
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            minZoom: 1,
            maxZoom: 15,
            noWrap: true,
            attribution: 'Data: Central Statistics Office | Tiles courtesy of &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        $.getJSON('static/data/NutsRegions_v2.geojson', function(data){

            geojson = L.geoJSON(data, {

                 style: function(feature)
                 {
                     return{
                      color: '#fff',
                      weight: 1,
                     // fillColor: '#FED976',
                      fillOpacity: 1,
                      fillColor: getColor(feature.properties.NUTS_ID.split('').slice(0, 2).join(''))
                  }},

                 onEachFeature: onEachFeature
             }).addTo(map);
    });

     function highlightLayer(e)
     {
         var layer = e.target;
         activeLayer = layer;

         layer.setStyle({
             color: '#fff',
             fillColor: '#636363'
         });

         if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
             layer.bringToFront();
         }

     }

     function resetHighlight(e) {
         geojson.resetStyle(e.target);
     }

      function get_popup_data(nuts)
         {  var f;
            var popup_resp = $.ajax({
              type: "GET",
              contentType: "application/json",
              url: "/popupContent",
              async: false,
              data: {'nuts_region': nuts},
              success: function(data) {
                    f = data;
                    console.log(f);
                  }
            });
            return f
         }

      function plot_layout(country, nuts_code, legend){

            var layout = {
                          xaxis: {
                            title: {
                              text: 'Years',
                              font: {
                                family: 'Calibri',
                                size: 16,
                                color: '#7f7f7f'
                              }
                            },
                          },
                          yaxis: {
                            title: {
                              text: '(%) Unemployment Rate',
                              font: {
                                family: 'Calibri',
                                size: 16,
                                color: '#7f7f7f'
                              }
                            }
                          },
                          margin: {
                                l: 50,
                                r: 50,
                                b: 50,
                                t: 50,
                                pad: 4
                              },
                          barmode: 'stack'
                        };

            return layout
         }

     function get_plot_data(trace_obj, year){

            var line_data = []
            var bar_data = []
            var max = 0

            for (var key in trace_obj) {

                    if (max < Math.max.apply(Math, trace_obj[key]))
                    {
                        max = Math.max.apply(Math, trace_obj[key]);
                    }
                    line_data.push({x:year, y:trace_obj[key], type: 'scatter', name:String(key)})
                    bar_data.push({x:year, y:trace_obj[key], type: 'bar', name:String(key)})

                }
            return {'line_data':line_data, 'bar_data':bar_data, 'max': max}
         }

    function onEachFeature(feature, layer) {
             layer.on({
             mouseover: highlightLayer,
             mouseout: resetHighlight

         })


      //layer.bindPopup(div);

      layer.on('click', function (e) {

                var nuts_region = e['sourceTarget']['feature']['properties']['NUTS_ID']
                var data = get_popup_data(nuts_region);
                plot_graphs(data);
            });
        };

     //This creates a default graph on load - to avoid empty containers
     var data = get_popup_data('ITC3');
     plot_graphs(data);


    });




