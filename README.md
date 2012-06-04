django-url-shortener
====================

This is URL shortening application written using the Django framework. It began
as a fork of https://github.com/nileshk/url-shortener, but with added
functionality for creating custom shortened URLs.

The project has been updated for Django 1.3 and now includes an extensive
tests.py.

Features
--------

* base62 values of the URL's id. base62 is `[a-zA-Z0-9]` (`26 + 26 + 10 = 62`).

* Ability to create custom short URLs.

* Keeps count of how many time each URL is followed.
