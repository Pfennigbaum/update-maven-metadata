This is a simple Python script to update the ```maven-metadata.xml```
files in a local Maven repo.

Introduction
------------

This script updates the ```maven-metadata.xml``` files in a local Maven
repository in accordance to the contents. It starts at the current working
directory and recurses into every directory it can find from there. This
is useful, after artifacts haven been manually copied to the repository
without using Maven. Note that you should make a backup before using this
script. Also note that currently only a limitted set of features is
actually implemented.

Usage
-----

```
usage: update-maven-metadata.py [-h] [--do-it]

Updates the maven-metadata.xml file of Maven artifacts in accordance to the
contents. It starts at the current working directory. It is very simple and
thus may only work for very simple repostories like used by the Ontologizer.
Make sure to make a backup before using it.

optional arguments:
  -h, --help  show this help message and exit
  --do-it     Do the actual operation. Without specifying this option, no
              write file operation will actually happen.

```
