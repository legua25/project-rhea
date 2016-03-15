
// "rhea.programs" module
const requirements = [
	System.import('vendor/angular-cookies'),
	System.import('rhea/utils/search')
];

Promise.all(requirements).then(function (modules) {
	'use strict';

	const search = modules[1];

	// "rhea" Angular module
	const rhea = angular.module('rhea', [ 'ngCookies' ]);
	rhea.directive('ngInitial', function ngInitial() {

			function controller($scope, $element, $attrs, $parse) {
				// https://stackoverflow.com/questions/13769732/angular-js-init-ng-model-from-default-values

				const value = ($attrs.ngInitial || $attrs.value);
				const $set = $parse($attrs.ngModel).assign;

				if (typeof $set === 'function')
					$set($scope, value);
			};

			return {
				restrict: 'A',
				controller: [ '$scope', '$element', '$attrs', '$parse', controller ]
			};
		});

	// Controllers
	rhea.controller('Rhea', function RheaController($scope, $http, $cookies) {});


	$(document).ready(function () {
		angular.bootstrap($('body'), [ 'rhea' ]);
	});

	return rhea;
});
