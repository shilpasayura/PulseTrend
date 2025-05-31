const loadingIndicator = 'Loading...';

new arc.nav('sales-prediction', q('#sales-prediction')[0], function(context, params) {
	let catalogue = {};
	arc.ajax('/data/catalogue', {
		callback: function(res) {
			catalogue = JSON.parse(res.responseText);
			const select = context.q('select')[0];
			select.innerHTML = '<option value="">All</option>';
			for (let item of catalogue)
				select.appendChild(arc.elem('option', item.title, {value: item.productId}));
			//
			select.onchange = function() {
				loadPredictions(this.value);
			};
		}
	});
	function loadPredictions(product) {
		arc.ajax('/data/sales-prediction'+(product ? '/'+product : ''), {
			callback: function(res) {
				const data = JSON.parse(res.responseText);
				google.charts.load('current', {'packages':['corechart']});
				google.charts.setOnLoadCallback(function drawSalesPredictionChart() {

					// Prepare the data array with headers
					const chartData = [['Date', 'Sales', 'Forecast']];
					for (let date in data.past) {
						chartData.push([date, data.past[date], null]);
					}
					for (let date in data.future) {
						chartData.push([date, null, data.future[date]]);
					}

					const cdata = google.visualization.arrayToDataTable(chartData);

					const options = {
						//title: false,//'Sales Prediction',
						curveType: 'function',
						legend: { position: 'bottom' },
						chartArea: {
							height: '70%'
						},
						hAxis: { 
							title: 'Date',
							slantedText: true,
							slantedTextAngle: 90
						},
						vAxis: {
							minValue: 0,
							title: 'Sales'
						}
					};

					const chart = new google.visualization.LineChart(context.q('.chart')[0]);
					chart.draw(cdata, options);
				});
			}
		});
	}
	loadPredictions(false);
});

new arc.nav('sentiment', q('#sentiment')[0], function(context, params) {
    arc.ajax('/data/sentiments', {
        callback: function(res) {
            const data = JSON.parse(res.responseText);

            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(function drawSentimentCharts() {

                // Column Chart: Sentiment Label Counts
                const countsData = [['Sentiment', 'Count']];
                data.counts.forEach(item => {
                    countsData.push([item.sentiment_label, item.count]);
                });

                const countsChartData = google.visualization.arrayToDataTable(countsData);

                const countsOptions = {
                    //title: false,//'Overall Sentiment Distribution',
                    legend: { position: 'none' },
                    vAxis: { title: 'Count' },
                    hAxis: { title: 'Sentiment Label' },
                    colors: ['#80A060', '#A08060', '#A0A050']
                };

                const countsChart = new google.visualization.ColumnChart(context.q('.chart.counts')[0]);
                countsChart.draw(countsChartData, countsOptions);

                // Scatter Plot: Sentiment vs. Total Sales per Product
                const correlationData = [['Average Sentiment', 'Total Sales', { role: 'tooltip' }]];
                data.correlation.forEach(item => {
                    const tooltip = `Product: ${item.productId}\nAvg Sentiment: ${item.avg_sentiment_score.toFixed(2)}\nTotal Sales: ${item.total_sales}`;
                    correlationData.push([item.avg_sentiment_score, item.total_sales, tooltip]);
                });

                const correlationChartData = google.visualization.arrayToDataTable(correlationData);

                const correlationOptions = {
                    //title: 'Sales vs. Average Sentiment per Product',
                    legend: { position: 'none' },
                    hAxis: { title: 'Average Sentiment', minValue: -1, maxValue: 1 },
                    vAxis: { title: 'Total Sales' },
                    tooltip: { isHtml: true },
                    colors: ['#8060A0']
                };

                const correlationChart = new google.visualization.ScatterChart(context.q('.chart.correlation')[0]);
                correlationChart.draw(correlationChartData, correlationOptions);
            });
        }
    });
});

new arc.nav('keywords', q('#keywords')[0], function(context, params) {
	arc.ajax('/data/keywords', {
		callback: function(res) {
			const data = JSON.parse(res.responseText);
			google.charts.load('current', {'packages':['corechart']});
			google.charts.setOnLoadCallback(function drawKeywords() {
				
				// Prepare the data array with headers
				const chartData = [['Keyword', 'Frequency']];
				for (let word of data) {
					chartData.push([word.Keyword, word.SearchCount]);
				}

				const cdata = google.visualization.arrayToDataTable(chartData);

				const options = {
					//title: false,//'Top Keywords',
					legend: { position: 'none' },
					vAxis: {
						title: 'Keyword'
					},
					hAxis: {
						title: 'Frequency',
						minValue: 0
					},
					//colors: ['#80A060']
				};

				const chart = new google.visualization.BarChart(context.q('.chart')[0]);
				chart.draw(cdata, options);
			});
		}
	});
});

new arc.nav('opportunities', q('#opportunities')[0], function(context, params) {
    arc.ajax('/data/opportunities', {
        callback: function(res) {
            const data = JSON.parse(res.responseText);
            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(function drawOpportunityChart() {
                
                // Prepare the data array with headers
                // Note: Bubble Chart expects: [ID, X, Y, Group, Size]
                const chartData = [['Category', 'Avg. Search Frequency', 'Avg. Quantity Sold', 'Category', 'Bubble Size']];
                data.forEach(item => {
                    chartData.push([
                        item.category, 
                        item.avg_frequency, 
                        item.avg_quantity_sold, 
                        item.category, 
                        item.avg_frequency // Using avg_frequency for size as in your Plotly example
                    ]);
                });

                const cdata = google.visualization.arrayToDataTable(chartData);

                const options = {
                    //title: false,//'Emerging Trends: High Search but Low Sales',
                    hAxis: { title: 'Avg. Search Frequency' },
                    vAxis: { title: 'Avg. Sales' },
                    bubble: { 
                        textStyle: { fontSize: 11, auraColor: 'none' },
                        opacity: 0.7
                    },
                    //colors: ['#8060A0']
                };

                const chart = new google.visualization.BubbleChart(context.q('.chart')[0]);
                chart.draw(cdata, options);
            });
        }
    });
});

window.onpopstate();