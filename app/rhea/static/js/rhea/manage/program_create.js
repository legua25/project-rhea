
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
		$scope.search_dependencies = function search_dependencies(subject) {
			return function $search_dependencies(query, timeout, max_results) {

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
					return data['subjects']['entries'].map(function (entry) {

						entry.subject = subject;
						return entry;
					});
				}).catch(function () { return []; });
			};
		};

		// Event callbacks
		this.subjects = [];
		$scope.$on('result', function (e, data) {

			const entry = data.entry;
			const name = data.name;

			switch (name) {
				case 'dependencies':

					const subject = entry.subject;
					if (subject.requirements.find(function (e) { return (e.code === entry.code && e.code !== subject.code); }) === undefined)
						subject.requirements.push(entry);

					break;
				case 'subjects':

					if (this.subjects.find(function (e) { return (e.code === entry.code); }) === undefined) {

						entry.requirements = [];
						this.subjects.push(entry);

						this.$count++;
					}

					break;
			}
		}.bind(this));

		// Properties
		this.$count = 0;

		// Methods
		this.remove = function remove(index) {

			this.subjects.splice(index, 1);
			this.$count--;
		};
		this.remove_requirement = function remove_requirement(entry, index) { entry.requirements.splice(index, 1); };
	});


	$(document).ready(function () {
		angular.bootstrap($('body'), [ 'rhea' ]);
	});

	return rhea;
});
