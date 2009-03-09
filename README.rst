Introduction
============

django-valhalla is a RESTful API used to log IRC channels.

Although I'm using this application for IRC logging purposes, there's nothing
that couples the application to IRC.  I figure this project could be used
anywhere you want a web service to record a tidbit of data and associate it
with a person and a timestamp.


Goals
=====

* GET Deeds
* POST Deeds
* DELETE Deeds
* HTTP Basic Authentication


Requirements
============

* Built on Django 1.0.2
* django-rest-interface - http://code.google.com/p/django-rest-interface/
