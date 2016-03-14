
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
	rhea.directive('search', search)
		.directive('ngInitial', function ngInitial() {

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
	rhea.controller('Rhea', function RheaController($scope, $http, $cookies) {

		// Search function
		$scope.search_subjects = function search_subjects(query, timeout, max_results) {

			const request = $http.get(`/manage/subjects/`, {
				'params': { 'q': query, 'size': max_results },
				'headers': {
					'X-CSRFToken': $cookies.get('csrftoken'),
					'X-Requested-With': 'XMLHttpRequest'
				},
				'timeout': timeout
			});

			return request.then(function (response) {

				const data = response.data;
				return data['subjects']['entries'];
			}).catch(function () { return []; });
		};
		// Search result listener
		$scope.$on('result', function (e, data) {

			const entry = data.entry;

			// We only filter for ourselves to prevent creating recursive dependencies
			// This is so because a subject may be a dependency for another in different programs
			if (this.requirements.find(function (e) { return (e.code === $scope.data.code); }) === undefined)
				this.requirements.push(entry);
		}.bind(this));

		// Properties
		this.requirements = [];
		Object.defineProperty(this, '$count', {
			'configurable': false,
			get() { return this.requirements.length; }
		});

		// Methods
		this.preload = function preload(data) { this.requirements = JSON.parse(data); };
		this.remove = function remove(index) { this.requirements.splice(index, 1); };
	});


	$(document).ready(function () {
		angular.bootstrap($('body'), [ 'rhea' ]);
	});

	return rhea;
});
