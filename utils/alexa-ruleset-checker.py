#! /usr/bin/env python3.3

# Copyright 2014 Claudio Moretti
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

#
# You NEED: 'top-1m.csv' and 'newRules.diff' in the same directory as merger.py
# git diff --name-status master..remotes/origin/stable src/chrome/content/rules >> newRules.diff
#

import csv
import xml.etree.ElementTree as etree
import subprocess
import random

# Variables and constants
sitesList = []
tmpRulesFileName = "/tmp/rulesDiff-" + format(random.randrange(1,65535)) # Feel free to enlarge if needed

# Functions
def ruleLookup(target):
    try: # list.index(value) throus an exception for a "not found", so if it throws it, it's not found
        sitesList.index(target)
        return 1
    except:
        return 0

# Fetch the Alexa Top 1M


# Handles reading the Alexa Top 1M and pushing all sites in a list
sitesReader = csv.reader(open('top-1m.csv'), delimiter=',', quotechar='"')
for row in sitesReader:
    try:
        # Since some Alexa sites are not FQDNs, split where there's a "/" and keep ony the first part
        siteFQDN = sitesList.append(row[1].split("/",1)[0])

    except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

# `git diff` the master revision against stable, rules folder only
try:
    tmpRulesFile = open(tmpRulesFileName,"w")
    subprocess.call(['git', 'diff', '--name-status', 'master..remotes/origin/stable', '../src/chrome/content/rules'], stdout=tmpRulesFile)
    tmpRulesFile.close()
except OSError as e:
    sys.exit('An OSError exception was raised: %s' % (e))

rulesList = open(tmpRulesFileName, 'r')
for line in rulesList:
    try:
        # Split into "file mode in commit + file path"
        ruleFile = line.split()
        found = 0
        # If file mode is "A" (add)
        if ruleFile[0] == "A": # If file was "added", parse
            ruleText = etree.parse(ruleFile[1])
            for target in ruleText.findall('target'):
                FQDN = target.get('host') # URL of the website
                if ruleLookup(FQDN) == 1: # Look it up in the sitesList
                    found = 1
                    break
        # If found, print it
        if found == 1:
            print("FOUND: ", ruleFile[1])
        # else ignore
        # There are some problems with file name encoding. So, for now, just print an error and pass
    except FileNotFoundError: # Won't happen before line.split() is invoked
        print("File not found:", ruleFile[1])
        pass

# Close the rules file
rulesList.close()
