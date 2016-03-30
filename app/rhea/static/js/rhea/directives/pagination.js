(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');

		// <paginator> directive - automatic pagination with pluggable data source and configurable representation
		/* Example:

		    <paginator data="subjects(page, size)" size="15">
				<table class="table table-bordered table-hover">
					<thead>
						<tr><th>#</th> <th>Name</th> <th>Code</th> <th>Hours per Week</th></tr>
					</thead>
					<tbody>
						<tr ng-repeat="entry in entries">
							<td>{% ng entry.id %}</td> <td>{% ng entry.name %}</td> <td>{% ng entry.code %}</td> <td>{% ng entry.hours %}</td>
						</tr>
					</tbody>
				</table>
			</paginator>

		*/
		return function paginator() {

			const template = `
				<div class="paginator">
					<section class="container-fluid">
						<div class="paginator-content"></div>
						<div class="col-xs-12 text-center">
							<ul class="pager paginator-control">
								<li class="previous" ng-class="{ false: 'disabled' }[$paginator.$previous !== false]"><a href="#" ng-click="$paginator.previous()">&larr; Previous</a></li>
								<li class="next" ng-class="{ false: 'disabled' }[$paginator.$next !== false]"><a href="#" ng-click="$paginator.next()">Next &rarr;</a></li>
							</ul>
						</div>
					</section>
				</div>
			`;

			function controller($scope, $element, $transclude) {

				const $size = ($scope.size || 15);
				const $panel = $element.find('.paginator-content');
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

						$page_scope = scope;
						$page_scope.entries = entries;
						$page_scope.$offset = (this.page * $size);

						$panel.empty();
						$panel.prepend(element);
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
