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

# The following is keyed by group_id
metadata = {}
versioning = {}
versions = {}

#group_id = None
#last_group_id = None

for root, dir, files in os.walk("."):
	if '.git' in dir:
		# Don't enter the .git directory
		dir.remove('.git')
		continue

	for file in files:
		if file == 'maven-metadata.xml':
			e = ET.parse(os.path.join(root, file)).getroot()
			print(root)
		elif file.endswith('.jar'):
			version = os.path.basename(root)
			other = os.path.dirname(root)
			group_id, artifact_id = ids(other)

			if group_id not in metadata:
				mt = ET.Element("metadata")
				metadata[group_id] = mt
				ET.SubElement(mt,"groupId").text = group_id
				ET.SubElement(mt,"artifactId").text = artifact_id
				versioning[group_id] = ET.SubElement(mt,"versioning")
				versions[group_id] = ET.SubElement(versioning[group_id],"versions")
				ET.SubElement(versioning[group_id], "lastUpdated").text = utcnow().strftime("%Y%m%d%H%M%S")

			ET.SubElement(versions[group_id],"version").text = version

for group_id in metadata:
		# Now pretty print if we have populated metadata
		print(minidom.parseString(ET.tostring(metadata[group_id])).toprettyxml(indent="  "), end="")
