
// "rhea.programs" module
const requirements = [
	System.import('rhea/utils/paginator'),
	System.import('vendor/angular-cookies')
];

Promise.all(requirements).then(function (modules) {
	'use strict';

	const Paginator = modules[0];

	// "rhea" Angular module
	const rhea = angular.module('rhea', [ 'ngCookies' ]);
	rhea.controller('Rhea', function RheaController($scope, $http, $cookies) {

		this.programs = new Paginator(function (page, size) {

			// Django (per our security settings) requires all views to be identified as AJAX and given the CSRF token
			const request = $http.get(`/manage/programs/`, {
				'params': { 'page': (page || 1), 'size': (size || 10) },
				'headers': {
					'X-CSRFToken': $cookies.get('csrftoken'),
					'X-Requested-With': 'XMLHttpRequest'
				}
			});

			return request.then(function (response) {

				// Extract the response payload for the paginator to handle
				return response.data['programs'];
			});
		});
		this.subjects = new Paginator(function (page, size) {

			// Django (per our security settings) requires all views to be identified as AJAX and given the CSRF token
			const request = $http.get(`/manage/subjects/`, {
				'params': { 'page': (page || 1), 'size': (size || 10) },
				'headers': {
					'X-CSRFToken': $cookies.get('csrftoken'),
					'X-Requested-With': 'XMLHttpRequest'
				}
			});

			return request.then(function (response) {

				// Extract the response payload for the paginator to handle
				return response.data['subjects'];
			});
		});
	});

	$(document).ready(function () {
		angular.bootstrap($('body'), [ 'rhea' ]);
	});

	return rhea;
});
