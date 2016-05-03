(function () {
	'use strict';

	define(function (require) {

		const $ = require('jquery');
		const angular = require('angular');

		// <formset> directive - self-contained and managed formsets, compatible with Django's FormSet classes
		// NOTE: Passing initial data is achieved by serializing it and passing it through the "initial" attribute
		//       It's not pretty, but gets the job done.
		/* Example:

			<formset name="subjects" min="1">
				<item>
					<div class="col-xs-4">
						{{ form.empty_form.id }}
						<label>Name: {{ form.empty_form.name }}</label>
					</div>
				</item>
			</formset>

		*/
		return function formset() {

			const template = `
				<div class="formset container-fluid">
					<input type="hidden" name="{{ name }}-TOTAL_FORMS" value="{{ $forms.length }}" />
					<input type="hidden" name="{{ name }}-INITIAL_FORMS" value="0" />
					<input type="hidden" name="{{ name }}-MAX_NUM_FORMS" value="{{ max }}" />
					<input type="hidden" name="{{ name }}-MIN_NUM_FORMS" ng-if="min !== undefined" value="{{ min }}" />
					<div class="formset-header" ng-transclude="formset-header"></div>
					<ul class="formset-list list-unstyled"></ul>
					<div class="formset-footer" ng-transclude="formset-footer"></div>
				</div>
			`;

			function controller($scope, $element, $transclude, $compile) {

				$scope.max || ($scope.max = 1000);

				const $entries = [];  // This is a scope list - no miss on the indices this way
				const $container = $element.find('ul.formset-list');

				Object.defineProperty(this, 'length', { get() { return $entries.length; } });

				// Retrieve the template from the transclusion scope
				$transclude(function (element, scope) {

					scope.$destroy();
					this.$instantiate = function (scope) {

						const $template = element.html().trim().replace(/__prefix__/gi, '{{ $index }}');
						return $compile($template)(scope);
					};
				}.bind(this), null, 'formset-item');

				// Set the scopes for the attachable sections
				if ($transclude.isSlotFilled('formHead'))
					$transclude($scope.$parent, null, null, 'formHead');
				if ($transclude.isSlotFilled('formFooter'))
					$transclude($scope.$parent, null, null, 'formFooter');

				this.$onDestroy = function () {

					while ($entries.length) {

						let entry = $entries.pop();

						entry.scope.$destroy();
						entry.element.detach();
					}
				};
				this.add = function add(entry) {

					const scope = $scope.$new(true, $scope.$parent);
					scope.$forms = this;
					scope.$entry = entry;
					Object.defineProperty(scope, '$index', { get() { return $entries.findIndex((i) => i.scope === scope); } });

					const item = $('<li class="formset-item"></li>');
					item.append(this.$instantiate(scope));
					$container.append(item);

					$entries.push({ 'scope': scope, 'element': item });
				};
				this.remove = function remove(position) {

					if (position < 0 || position >= this.length)
						throw new RangeError('Attempted to remove form out of range');

					const item = $entries.splice(position, 1)[0];
					item.scope.$destroy();
					item.element.detach();
				};

				if ($scope.initial) {

					const $initial = JSON.parse($('<div/>').html($scope.initial).text());
					for (let i = 0; i < $initial.length; i++)
						this.add($initial[i]);
				}
			};
			function link($scope, $element, attrs) {};

			return {
				'restrict': 'E',
				'transclude': {
					'formset-item': 'item',
					'formset-header': '?formHead',
					'formset-footer': '?formFooter'
				},
				'scope': { 'name': '@', 'max': '@', 'min': '@', 'initial': '@' },
				'template': template,
				'controllerAs': '$forms',
				'controller': [ '$scope', '$element', '$transclude', '$compile', controller ],
				'link': link
			};
		};
	});

})();
