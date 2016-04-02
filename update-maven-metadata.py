#! /usr/bin/python
# For the details of the maven-metadata.xml model
# https://maven.apache.org/ref/3.2.1/maven-repository-metadata/repository-metadata.html.
#
# (c) 2016 by Sebastian Bauer

from __future__ import print_function

import argparse
import datetime
import glob
import os
import os.path
import re
import sys
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

def ids(path):
	"""Extract the group id and artifact id from the path."""
	group_id, artifact_id = os.path.split(path)
	if group_id.startswith('./'): group_id = group_id[2:]
	group_id = group_id.replace('/','.')
	return group_id, artifact_id

parser = argparse.ArgumentParser(description="""
	Updates the maven-metadata.xml file of Maven artifacts in accordance to the
	contents. It starts at the current working directory. It is very simple and
	thus may only work for very simple repostories like used by the Ontologizer.
	Make sure to make a backup before using it.
	""")
args = parser.parse_args()


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
			groups[group_id][artifact_id][version] = {}
			groups[group_id][artifact_id][version]["files"] = []
			groups[group_id][artifact_id][version]["path"] = root

		groups[group_id][artifact_id][version]["files"].append(file)

# Build maven-metadata.xml for each artifact
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

# Build maven-metadata.xml for each individual version of each artifactId
for group_id, artifacts in groups.iteritems():
	for artifact_id, artifact_versions in artifacts.iteritems():
		for version in artifact_versions:
			files = artifact_versions[version]["files"]
			path = artifact_versions[version]["path"]

			# Basically sorts according to the timestamp as the prefix
			# of the file is all the same
			files = sorted(files)

			snapshot_ext = '-SNAPSHOT'
			is_snapshot = version.endswith(snapshot_ext)
			mt = ET.Element("metadata")
			ET.SubElement(mt,"groupId").text = group_id
			ET.SubElement(mt,"artifactId").text = artifact_id
			ET.SubElement(mt,"version").text = version
			versioning = ET.SubElement(mt,"versioning")

			if is_snapshot:
				# Version without -SNAPHOT suffix
				plain_version = version.replace(snapshot_ext,"")

				# Regexp for extracting the timestamp
				regexp = "{0}-{1}-(\d+.\d+)-.*".format(artifact_id,plain_version)
				pat = re.compile(regexp)

				def stamp_of(f):
					"""
					Return the time stamp of the given filename or the empty
					string if no time stamp could be found
					"""
					m = pat.match(f)
					if m: return m.group(1)
					return ""

				stamps = [stamp_of(s) for s in files]
				new_stem = []
				build_number = 1
				for s in stamps:
					new_stem.append("{0}-{1}-{2}-{3}".format(artifact_id, plain_version, s, build_number))
					build_number = build_number + 1

				# Old names
				old_stem = [os.path.splitext(f)[0] for f in files]

				# Rename all files beginning with the stem
				for old, new in zip(old_stem,new_stem):
					p = os.path.join(path,old)

					# The old names of all files sharing the stem
					old_files = glob.glob(p + "*")

					# The new (final) names of all files sharing the stem
					new_files = [os.path.join(path,new + f[len(p):]) for f in old_files]

					# Temporary names
					tmp_path = os.path.join(path, "tmp")
					tmp_files = [os.path.join(tmp_path,new + f[len(p):]) for f in old_files]

					# Finanlly, rename the files but move them into a temporary
					# folder first to avoid clashes that could happen on certain
					# sorting orders

					os.mkdir(tmp_path)

					for old_f, tmp_f in zip(old_files, tmp_files):
						os.rename(old_f, tmp_f)

					for tmp_f, new_f in zip(tmp_files, new_files):
						os.rename(tmp_f, new_f)

					os.rmdir(tmp_path)
				snapshot = ET.SubElement(versioning,"snapshot")
				ET.SubElement(snapshot,"timestamp").text = str(stamps[-1])
				ET.SubElement(snapshot,"buildNumber").text = str(build_number)
			else: pass
			print(minidom.parseString(ET.tostring(mt)).toprettyxml(indent="  "), end="")
