(function () {
	'use strict';

	define(function (require) {

		return class Controller {

			constructor ($scope, $injector) {

				Object.defineProperty(this, '$scope', { 'configurable': false, 'value': $scope });
				return new Proxy(this, {

					get(target, key, receiver) {

						if ($injector.has(key.toString())) return $injector.get(key, receiver);
						return target[key];
					},
					has(target, key) { return ($injector.has(key) || Object.hasOwnProperty(target, key)); }

				});
			}

		}
	});

})();
