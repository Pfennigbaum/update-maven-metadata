#! /usr/bin/python
"""
Updates the maven-metadata.xml file of Maven artifacts in accordance to the
contents. It is very simple and thus may only work for very simple repostories.

For the details of the model see
https://maven.apache.org/ref/3.2.1/maven-repository-metadata/repository-metadata.html.

"""

from __future__ import print_function

import datetime
import os
import os.path
import sys
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

def ids(path):
	"""Extract the group id and artifact id from the path."""
	group_id, artifact_id = os.path.split(path)
	if group_id.startswith('./'): group_id = group_id[2:]
	group_id = group_id.replace('/','.')
	return group_id, artifact_id

utcnow = datetime.datetime.utcnow

# Groups contain artifacts that contain version that contains released jars
groups = {}

# Scan directory and extract jars and where they belong to
for root, dir, files in os.walk("."):
	if '.git' in dir:
		# Don't enter the .git directory
		dir.remove('.git')
		continue

	for file in [f for f in files if f.endswith('.jar')]:
		version = os.path.basename(root)
		other = os.path.dirname(root)
		group_id, artifact_id = ids(other)

		if group_id not in groups:
			groups[group_id] = {}

		if artifact_id not in groups[group_id]:
			groups[group_id][artifact_id] = {}

		if version not in groups[group_id][artifact_id]:
			groups[group_id][artifact_id][version] = []

		groups[group_id][artifact_id][version].append(file)

# Build XML
for group_id, artifacts in groups.iteritems():
	for artifact_id, artifact_versions in artifacts.iteritems():
		mt = ET.Element("metadata")
		ET.SubElement(mt,"groupId").text = group_id
		ET.SubElement(mt,"artifactId").text = artifact_id
		versioning = ET.SubElement(mt,"versioning")
		versions = ET.SubElement(versioning,"versions")
		for version in artifact_versions:
			ET.SubElement(versions,"version").text = version
		ET.SubElement(versioning, "lastUpdated").text = utcnow().strftime("%Y%m%d%H%M%S")

		print(minidom.parseString(ET.tostring(mt)).toprettyxml(indent="  "), end="")
