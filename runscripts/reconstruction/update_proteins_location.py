import csv
import os
import yaml
import json
import numpy as np
from reconstruction.spreadsheets import JsonReader

CSV_DIALECT = csv.excel_tab

EXISTING_MONOMER_FILE = os.path.join("reconstruction", "ecoli", "flat", "proteins.tsv")
NEW_MONOMER_FILE = os.path.join("reconstruction", "ecoli", "flat", "proteins_new.tsv")
MONOMER_COMPARISON_FILE = os.path.join("reconstruction", "ecoli", "flat", "proteins_location_comparison.tsv")

ECOCYC_DUMP = os.path.join("reconstruction", "ecoli", "flat", "eco_wc_test_fun.json")

def getMonomerLocationsFromOurData():
	reader = JsonReader(open(EXISTING_MONOMER_FILE, "r"), dialect = CSV_DIALECT)
	data = [row for row in reader]
	D = dict([(x["id"].encode("utf-8"), (x["location"][0].encode("utf-8"), x["comments"].encode("utf-8"))) for x in data])
	return D

def getMonomerLocationsFromEcocyc(reactionData):
	D = {}
	for reaction in reactionData:
		for element in reaction["elements"]:
			if element["type"] == "proteinmonomer":
				D[element["molecule"]] = element["location"]
	return D

def getLocationDifferences(ourLocations, ecocycLocations):
	"""
	Outputs monomers that have a different location in ourLocations as compared to ecocycLocations.
	Exception: ecocyc compartments "x" and "z" are ignored (and become "c")
	"""
	locationDifferences = {}
	notFoundInEcocyc = []
	for monomer in ourLocations:
		if monomer in ecocycLocations:
			if ourLocations[monomer][0] != ecocycLocations[monomer]:
				if ecocycLocations[monomer] == "x" or ecocycLocations[monomer] == "z":
					locationDifferences[monomer] = "c"
				else:
					locationDifferences[monomer] = ecocycLocations[monomer]
		else:
			notFoundInEcocyc.append(monomer)
	return locationDifferences, notFoundInEcocyc



jsonData = yaml.safe_load(open(ECOCYC_DUMP, "r"))

ourLocations = getMonomerLocationsFromOurData()
ecocycLocations = getMonomerLocationsFromEcocyc(jsonData["complexations"])
locationDifferences, notFoundInEcocyc = getLocationDifferences(ourLocations, ecocycLocations)


h = open(MONOMER_COMPARISON_FILE, "w")
h.write('"id"\t"ourLocation"\t"comments"\t"ecocycLocations"\n')

for monomer in locationDifferences:
	h.write('"%s"\t["%s"]\t"%s"\t["%s"]\n' % (
		monomer,
		ourLocations[monomer][0],
		ourLocations[monomer][1],
		ecocycLocations[monomer],
		)
	)
h.close()

h = open(NEW_MONOMER_FILE, "w")
h.write('"aaCount"\t"name"\t"seq"\t"comments"\t"codingRnaSeq"\t"mw"\t"location"\t"rnaId"\t"id"\t"geneId"\n')

reader = JsonReader(open(EXISTING_MONOMER_FILE, "r"), dialect = CSV_DIALECT)
data = [row for row in reader]

for monomer in data:
	h.write('%s\t%s\t"%s"\t"%s"\t"%s"\t%s\t["%s"]\t"%s"\t"%s"\t"%s"\n' % (
		monomer["aaCount"],
		json.dumps(monomer["name"]),
		monomer["seq"],
		"Location information from Ecocyc dump." if monomer["id"] in locationDifferences else monomer["comments"],
		monomer["codingRnaSeq"],
		monomer["mw"],
		locationDifferences[monomer["id"]] if monomer["id"] in locationDifferences else monomer["location"][0].encode("utf-8"),
		monomer["rnaId"],
		monomer["id"],
		monomer["geneId"],
		)
	)
h.close()