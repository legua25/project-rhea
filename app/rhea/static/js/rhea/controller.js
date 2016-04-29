(function () {
	'use strict';

	define(function (require) {

		return class Controller {

			constructor ($scope, $injector) {

				const $cookies = $injector.get('$cookies');
				Object.defineProperties(this, {
					'$scope': { 'configurable': false, 'value': $scope },
					'$csrf': { 'configurable': false, get() { return $cookies.get('csrftoken'); } },
					'$token': {
						'configurable': false,
						get() { return $cookies.get('rheatoken'); },
						set(token) {

							if (token === undefined) $cookies.remove('rheatoken');
							else {

								// Expires in a day
								const expires = new Date(Date.now());
								expires.setDate(expires.getDate() + 1);

								$cookies.put('rheatoken', token, { 'expires': expires });
							}
						}
					}
				});

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
