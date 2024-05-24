<?php
/*
|--------------------------------------------------------------------------
| LtiController
|--------------------------------------------------------------------------
*/
Route::get('/lti/redirect', [
    'uses' => 'Member\LtiLoginController@redirect'
])->name('lti.redirect');
Route::post('/lti/redirect', [
    'uses' => 'Member\LtiLoginController@redirect'
])->name('lti.redirect');
Route::get('/lti/login', [
    'uses' => 'Member\LtiLoginController@login'
])->name('lti.login');
Route::post('/lti/login', [
    'uses' => 'Member\LtiLoginController@login'
])->name('lti.login');