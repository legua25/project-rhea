(function () {
	'use strict';

	// Academic programs management
	const requirements = [
		'angular.min.js',
		'utils/paginator.js',
		'angular-cookies.min.js'
	];

	define(requirements, function (angular, Paginator) {

		const rhea = angular.module('rhea', [ 'ngCookies' ]);
		rhea.controller('RheaController', class RheaController {

			constructor($scope, $http, $cookies) {

				this.programs = new Paginator(function (page, size) {

					// Retrieve the list of academic programs from the backend
					const request = $http.get(`/manage/programs/`, {
						'params': { 'page': page, 'size': size },
						'headers': { 'X-CSRFToken': $cookies.get('csrftoken') }
					});

					return request.then(function (response) {

						// We must select the data to leave only the metadata AND the entries
						return response.data['programs'];
					}).catch(function (response) {});
				});
			}

		});
	});

})();
