#Puck



### 0.1.3 / 2016-05-14
==================

  * Add examples
  * Enhance: Support class sytle to build apis
  * Feature: support restful style to bulid apis.
  * Fix: when content_type is multipart/form-data, the request.form[xx] should be a string.
  * Fix session bug when expire=None


### 0.1.2 / 2016-05-10
==================

  * Fix: The match url bug when the dynamic part in url is string or int.
  * Add setup
  * Enhance: Convert the sessions expire time into utc
  * Fix: Cookies dict in request.
  * Enhance: Support using hash type in redis to store session.
  * Feature: Support session, which use redis to store.


### 0.1.1 / 2016-05-07
==================

  * Enhance: the proxy support operate the real object behind it.
  * Fix: the cookie dict bug in request.
  * Fix upload file bug.
  * Update Header class to support be used in request._file and request._form
  * Fix form and file in request.
  * Update notations.
