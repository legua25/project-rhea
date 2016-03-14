
module.exports = function search() {
	'use strict';

	const template = `
		<div class="search-bar dropdown">
			<span class="input-group {{ size ? 'input-group-' + size : '' }}">
				<input type="search" class="form-control {{ size ? 'input-' + size : '' }}" placeholder="{{ placeholder || 'Search&hellip;' }}" ng-model="search.$query" ng-change="search.resolve()" />
				<span class="input-group-addon"><i class="glyphicon glyphicon-search"></i></span>
			</span>
			<ul class="dropdown-menu" style="width: 100%"></ul>
			<template ng-transclude></template>
		</div>
	`;

	function link($scope, element, attrs, search, $transclude) {

		// Connect the result list to the data
		search.$$handle = element.find('.dropdown');
		search.$$target = element.find('ul.dropdown-menu');
		search.$$template = $transclude;

		const input = element.find('input[type=search]');
		input.blur(function () {

			setTimeout(function () {

				search.$$handle.removeClass('open');
				search.$$target.empty();
				search.$results.splice(0, search.$results.length);
			}, 150);
		});
		input.focus(function () {

			if (search.$results.length > 0)
				search.$$handle.addClass('open');
			else if (search.$query.length > 1)
				search.resolve(search.$query);
		});
	};
	function controller($scope, $compile) {

		this.$query = '';
		this.$results = [];

		// Controls for query resolution
		const timeout = ($scope.timeout || 500);
		const max_results = ($scope.maxResults || 15);
		let $lock = false;

		this.resolve = function resolve() {

			const query = this.$query;

			// Clear the result list
			this.$$target.empty();
			this.$$handle.removeClass('open');
			this.$results.splice(0, this.$results.length);

			if (query.length > 1) {

				// If there's a search underway, we must wait
				if ($lock === true) setTimeout(resolve.bind(this), timeout);
				else {

					// Mark the search as in-progress and resolve
					$lock = true;
					setTimeout(function process() {

						// Request the new content from the query function
						$scope.query()(query, timeout, max_results).then(function (data) {

							if (data.length > 0) {

								// Add these to the dropdown list and show them
								for (let i = (data.length - 1); i >= 0; i--) {

									this.$results.unshift(data[i]);

									// Compile a new, unique scope for the new element
									const scope = $scope.$new();
									scope.entry = data[i];
									scope.index = i;

									this.$$template(scope, function (element) {

										const item = $compile($(`<li><a ng-click="search.select(${i})" style="cursor: pointer"></a></li>`))($scope);
										item.find('a').append(element);

										this.$$target.prepend(item);
									}.bind(this));

								}

								if (!this.$$handle.hasClass('open')) this.$$handle.addClass('open');
							}
						}.bind(this));

						$lock = false;
					}.bind(this), 0);
				}
			}
		};
		this.select = function select(index) {

			const entry = this.$results[index];
			$scope.$emit('result', {
				'index': index,
				'entry': entry,
				'name': $scope.name
			});

			this.$$handle.removeClass('open');
			this.$query = '';
		};
	};

	return {
		'restrict': 'E',
		'transclude': true,
		'scope': {
			'placeholder': '@',
			'timeout': '@',
			'query': '&',
			'maxResults': '@',
			'size': '@',
			'name': '@'
		},
		'controllerAs': 'search',
		'template': template,
		'link': link,
		'controller': [ '$scope', '$compile', controller ]
	};
};
