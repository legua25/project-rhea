
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
				$set($scope, value);
			};

			return {
				restrict: 'A',
				controller: [ '$scope', '$element', '$attrs', '$parse', controller ]
			};
		});

	// Controllers
	rhea.controller('Rhea', function RheaController($scope, $http, $cookies) {

		// Search function (required by <search> directive)
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

		// Event callbacks
		this.subjects = [];
		$scope.$on('entry-selected', function (e, data) {

			const entry = data.entry;

			if (!this.subjects.find(function (e) { return (e.code === entry.code); })) {

				entry.requirements = [];
				this.subjects.push(entry);
			}
		}.bind(this));

		// Properties
		this.$count = 0;

		// Methods
		this.remove = function remove(index) { this.subjects.splice(index, 1); };
		this.add_requirement = function add_requirement(entry) {

			entry.requirements.push({ 'requirement': false });
			this.$count++;
		};
		this.remove_requirement = function remove_requirement(entry, index) {

			entry.requirements.splice(index, 1);
			this.$count--;
		};
	});


	$(document).ready(function () {
		angular.bootstrap($('body'), [ 'rhea' ]);
	});

	return rhea;
});
