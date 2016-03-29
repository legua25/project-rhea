(function () {
	'use strict';

	define(function (require) {

		require('jquery');
		const angular = require('angular');

		// <paginator> directive - automatic pagination with pluggable data source
		return function paginator() {

			const template = `
				<div class="paginator">
					<div class="container-fluid">
						<table class="table table-responsive table-hover paginator-table"></table>
						<div class="col-xs-12 text-center">
							<ul class="pager paginator-control">
								<li class="previous" ng-class="{ false: 'disabled' }[$paginator.$previous === false]"><a href="#" ng-click="$paginator.previous()">&larr; Previous</a></li>
								<li class="next" ng-class="{ false: 'disabled' }[$paginator.$next === false]"><a href="#" ng-click="$paginator.next()">Next &rarr;</a></li>
							</ul>
						</div>
					</div>
				</div>
			`;

			function controller($scope, $element, $transclude) {

				const $size = ($scope.size || 15);
				const $table = $element.find('table.paginator-table');
				const $source = $scope.data;

				let $page_scope = null;

				this.page = false;
				this.$previous = false;
				this.$next = false;

				this.previous = function previous() { this.$retrieve(this.$previous || 1); };
				this.next = function next() { this.$retrieve(this.$next || this.$previous + 1); };
				this.$retrieve = function $retrieve(page) {

					// Reset the paginator - release resources and scopes
					this.page = false;
					$table.empty();
					if ($page_scope !== null) {

						$page_scope.$destroy();
						$page_scope = null;
					}

					// Call the data source function with the current state for this paginator
					// This directive expects the $source function to return a promise with the processed response
					// as a two-attribute object, namely "{ 'pagination': {}, 'entries': [] }"
					const request = $source({ 'page': page, 'size': $size });
					request.then(function (data) {

						const pagination = data.pagination;
						const entries = data.entries;

						// Update the paginator's data
						this.page = pagination.page;
						this.$previous = pagination.previous;
						this.$next = pagination.next;

						// Update the data table
						this.$update(entries);
					}.bind(this));
				};
				this.$update = function $update(entries) {

					// Transclude the table contents into the paginator table - add the reference to the
					// recently-loaded entries
					$transclude(function (element, scope) {

						$table.append(element);

						$page_scope = scope;
						$page_scope.entries = entries;
						$page_scope.$offset = (this.page * $size);
					}.bind(this));
				};

				// Get the first batch of items to populate the paginator table
				this.$retrieve(1);
			};
			function link($scope, element, attrs) {};

			return {
				'restrict': 'E',
				'transclude': true,
				'scope': { 'data': '&', 'size': '@' },
				'template': template,
				'controllerAs': '$paginator',
				'controller': [ '$scope', '$element', '$transclude', controller ],
				'link': link
			};
		};
	});

})();
