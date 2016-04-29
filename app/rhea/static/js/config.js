(function () {
	'use strict';

	require.config({
		'paths': {
			'jquery': 'vendor/jquery',
			'angular': 'vendor/angular',
			'angular-aria': 'vendor/angular-aria',
			'angular-cookies': 'vendor/angular-cookies',
			'angular-route': 'vendor/angular-route',
			'bootstrap': 'vendor/bootstrap',
			'lodash': 'vendor/lodash'
		},
		'shim': {
			'angular': { 'exports': 'angular', 'deps': [ 'jquery' ] },
			'angular-aria': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'angular-cookies': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'angular-route': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'bootstrap': { 'deps': [ 'jquery', 'angular' ] }
		}
	});

})();
