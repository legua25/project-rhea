(function () {
	'use strict';

	require.config({
		'paths': {
			'jquery': 'vendor/jquery',
			'angular': 'vendor/angular',
			'angular-aria': 'vendor/angular-aria',
			'angular-cookies': 'vendor/angular-cookies',
			'angular-route': 'vendor/angular-route',
			'angular-sanitize': 'vendor/angular-sanitize',
			'bootstrap': 'vendor/bootstrap',
			'lodash': 'vendor/lodash',
			'select': 'vendor/select'
		},
		'shim': {
			'angular': { 'exports': 'angular', 'deps': [ 'jquery' ] },
			'angular-aria': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'angular-cookies': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'angular-route': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'angular-sanitize': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'bootstrap': { 'deps': [ 'jquery', 'angular' ] },
			'select': { 'deps': [ 'angular', 'angular-aria', 'angular-sanitize' ] }
		}
	});

})();
