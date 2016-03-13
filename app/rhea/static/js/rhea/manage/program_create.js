
// "rhea.programs" module
const requirements = [
	System.import('vendor/angular-cookies')
];

Promise.all(requirements).then(function (modules) {
	'use strict';

	// "rhea" Angular module
	const rhea = angular.module('rhea', [ 'ngCookies' ]);
	rhea.controller('Rhea', function RheaController($scope, $http, $cookies) {

		this.subjects = [];
	});

	$(document).ready(function () {
		angular.bootstrap($('body'), [ 'rhea' ]);
	});

	return rhea;
});
