django-url-shortener
--------------------

This is URL shortening application written using the Django framework. It began
as a fork of https://github.com/nileshk/url-shortener, but now includes
functionality for creating custom shortened URLs.

The project has also been updated for Django 1.4 and now includes an extensive
tests.py.

Features
--------

* base62 values of the URL's database id. base62 is: `[a-zA-Z0-9]`. `(26 + 26 +
  10 = 62)`

* Ability to create custom short URLs. Ex: http://you.rs/KimK ->
  http://www.kimkardashian.com

* Keeps count of how many time each URL is followed.
