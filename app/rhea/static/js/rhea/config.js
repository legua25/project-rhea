(function () {
	'use strict';

	require.config({
		'baseUrl': '/static/js/',
		'paths': {
			'jquery': 'vendor/jquery',
			'angular': 'vendor/angular',
			'angular-aria': 'vendor/angular-aria',
			'angular-cookies': 'vendor/angular-cookies',
			'bootstrap': 'vendor/bootstrap',
			'lodash': 'vendor/lodash'
		},
		'shim': {
			'angular': { 'exports': 'angular', 'deps': [ 'jquery' ] },
			'angular-aria': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'angular-cookies': { 'exports': 'angular', 'deps': [ 'angular' ] },
			'bootstrap': { 'deps': [ 'jquery', 'angular' ] },
			'lodash': { 'exports': '_' }
		}
	});

})();
