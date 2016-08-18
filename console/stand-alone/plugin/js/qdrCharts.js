/*
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
*/
/**
 * @module QDR
 */
/**
 * @module QDR
 */
var QDR = (function (QDR) {

  /**
   * @method ChartsController
   * @param $scope
   * @param QDRServer
   * @param QDRChartServer
   *
   * Controller that handles the QDR charts page
   */
  QDR.module.controller("QDR.ChartsController", ['$scope', 'QDRService', 'QDRChartService', '$uibModal', '$location',
  function($scope, QDRService, QDRChartService, $uibModal, $location) {
    var updateTimer = null;

    QDR.log.debug("started Charts controller");
    if (!angular.isDefined(QDRService.schema))
        return;

    $scope.svgCharts = [];
    // create an svg object for each chart
    QDRChartService.charts.filter(function (chart) {return chart.dashboard}).forEach(function (chart) {
        var svgChart = new QDRChartService.AreaChart(chart, $location.$$path)
        svgChart.zoomed = false;
        $scope.svgCharts.push(svgChart);
    })

    // redraw the charts every second
    var updateCharts = function () {
        $scope.svgCharts.forEach(function (svgChart) {
            svgChart.tick(svgChart.chart.id()); // on this page we are using the chart.id() as the div id in which to render the chart
        })
        updateHandle = setTimeout(updateCharts, 1100);
    }
	$scope.chartsLoaded = function () {
		setTimeout(updateCharts, 0);
	}

	$scope.zoomChart = function (chart) {
		chart.zoomed = !chart.zoomed;
		chart.zoom(chart.chart.id(), chart.zoomed);
	}
    $scope.showListPage = function () {
        $location.path("/list");
    };

    $scope.hasCharts = function () {
        return QDRChartService.numCharts() > 0;
    };

    $scope.editChart = function (chart) {
        doDialog("chart-config-template.html", chart.chart);
    };

    $scope.delChart = function (chart) {
        QDRChartService.unRegisterChart(chart.chart);
        // remove from svgCharts
        $scope.svgCharts.forEach(function (svgChart, i) {
            if (svgChart === chart) {
                delete $scope.svgCharts.splice(i, 1);
            }
        })
    };

    // called from dialog when we want to clone the dialog chart
    // the chart argument here is a QDRChartService chart
    $scope.addChart = function (chart) {
        $scope.svgCharts.push(new QDRChartService.AreaChart(chart, $location.$$path));
    };

    $scope.$on("$destroy", function( event ) {
        if (updateTimer) {
            cancelTimer(updateTimer);
            updateTimer = null;
        }
        for (var i=$scope.svgCharts.length-1; i>=0; --i) {
            delete $scope.svgCharts.splice(i, 1);
        }
    });

    function doDialog(template, chart) {

	    var modalInstance = $uibModal.open({
	      animation: true,
	      templateUrl: template,
	      controller: 'QDR.ChartDialogController',
	      resolve: {
	        chart: function () {
	          return chart;
	        },
	        dashboard: function () {
	            return $scope;
	        }
	      }
	    });
    };

  }]);

  QDR.module.controller("QDR.ChartDialogController", function($scope, QDRChartService, $location, $uibModalInstance, $rootScope, chart, dashboard) {
        var dialogSvgChart = null;
        $scope.svgDivId = "dialogChart";    // the div id for the svg chart

		$scope.updateTimer = null;
        $scope.chart = chart;  // the underlying chart object from the dashboard
        $scope.dialogChart = $scope.chart.copy(); // the chart object for this dialog
        $scope.userTitle = $scope.chart.title();

        $scope.$watch('userTitle', function(newValue, oldValue) {
            if (newValue !== oldValue) {
                $scope.dialogChart.title(newValue);
            }
        })
        // the stored rateWindow is in milliseconds, but the slider is in seconds
        $scope.rateWindow = $scope.chart.rateWindow / 1000;

		var cleanup = function () {
			if ($scope.updateTimer) {
				clearTimeout($scope.updateTimer);
				$scope.updateTimer = null;
			}
			QDRChartService.unRegisterChart($scope.dialogChart);     // remove the chart
		}
		$scope.okClick = function () {
			cleanup();
	        $uibModalInstance.close();
	    };

        // initialize the rateWindow slider
        $scope.slider = {
            'options': {
                min: 1,
                max: 10,
                step: 1,
                tick: true,
                stop: function (event, ui) {
                    $scope.dialogChart.rateWindow = ui.value * 1000;
                    if (dialogSvgChart)
                        dialogSvgChart.tick($scope.svgDivId);
                }
            }
		};

        $scope.visibleDuration =
        $scope.duration = {
            'options': {
                min: 1,
                max: 10,
                step: 1,
                tick: true,
                stop: function (event, ui) {
                    if (dialogSvgChart)
                        dialogSvgChart.tick($scope.svgDivId);
                }
            }
		};

        // handle the Apply button click
        // update the dashboard chart's properties
        $scope.apply = function () {
            $scope.chart.areaColor = $scope.dialogChart.areaColor;
            $scope.chart.lineColor = $scope.dialogChart.lineColor;
            $scope.chart.type = $scope.dialogChart.type;
            $scope.chart.rateWindow = $scope.dialogChart.rateWindow;
            $scope.chart.title($scope.dialogChart.title());
            $scope.chart.visibleDuration = $scope.dialogChart.visibleDuration;
            QDRChartService.saveCharts();
        }

        // add a new chart to the dashboard based on the current dialog settings
        $scope.copyToDashboard = function () {
            var chart = $scope.dialogChart.copy();
            // set the new chart's dashboard state
            QDRChartService.addDashboard(chart);
            // notify the chart controller that it needs to display a new chart
            dashboard.addChart(chart);
        }

        // update the chart on the popup dialog
        var updateDialogChart = function () {
            // draw the chart using the current data
            if (dialogSvgChart)
                dialogSvgChart.tick($scope.svgDivId);

            // draw the chart again in 1 second
            $scope.updateTimer = setTimeout(updateDialogChart, 1000);
        }

        var showChart = function () {
            // ensure the div for our chart is loaded in the dom
            var div = angular.element("#dialogChart");
            if (!div.width()) {
                setTimeout(showChart, 100);
                return;
            }
            dialogSvgChart = new QDRChartService.AreaChart($scope.dialogChart, $location.$$path);
            updateDialogChart();
        }
        showChart();


  });

  return QDR;

}(QDR || {}));

