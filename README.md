# hcls-fhir-rdf
Sketching out an RDF representation for FHIR

## Directories
* data - the current stable FHIR specification
  * examples -- XML examples from specification
  * site -- FHIR definitions (we use the json format)
  * rdf -- RDF representation of examples
  * definitions.shex -- shex definitions of FHIR content
  * definitions.xml -- XML definitions used in xslt transformation
  * extract.log -- log of build for the data directory
* hcls_fhir_rdf -- python 3 modules for building data directory
* ontology -- (underway) work on modeling FHIR definitions in OWL
* tests -- python unit tests (not a lot at the moment)
* xsl -- XSLT 2.0 transform for converting FHIR instances from XML to RDF

## Requirements
* python3 (ideally >= 3.5, but any 3.x version will do).  You can determine whether you have python on your machine and its version by:
  * `python -v` -- if 3.x you are ready to go, otherwise...
  * `python3 -v` -- if this works you are also ready to go
* virtualenv -- if this isn't on your machine, see <http://pythoncentral.io/how-to-install-virtualenv-python/>
* java -- we need version 1.7 or greater


## Installation
1. Set up a python3 virtual environment:
```bash
> virtualenv hcls -p python3
> . hcls/bin/activate
(hcls) > pip install hcls-fhir-rdf
```

## Execution
To download the latest copy of the FHIR spec and unzip it:

```bash
(hcls) > download_fhir_spec
```

To generate the XML definitions for the XML to RDF transformation process:
```bash
(hcls) > generate_xml_definitions
```

To generate the ShEx definitions for the output RDF
```bash
(hcls) > generate_shex
```

To start the background XSLT transformer
```bash
(hcls) > nohup pyjxslt&
```

To transform the XML in the data/examples file into RDF:
```bash
(hcls) > generate_rdf
```


# Modules
## ```download_fhir_spec```
```download_fhir_spec``` has the following options:

```bash
usage: download_fhir_spec [-h] [-u URL] [-f FILE] [-d DIR] [-e EXAMPLEDIR]
                          [--force] [--unzip] [--logfile LOGFILE]
                          [--skipdownload]

Download and unzip the FHIR spec

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Base URL of the (default:
                        http://www.hl7.org/implement/standards/fhir/2015May/)
  -f FILE, --file FILE  Download zip file name (default: fhir-spec.zip)
  -d DIR, --dir DIR     target download directory (default: data)
  -e EXAMPLEDIR, --exampledir EXAMPLEDIR
                        Example directory (default: examples)
  --force               Force FHIR specification re-download 
  --unzip               Force re-unzip
  --logfile LOGFILE     Logging file. (default: extract.log in target directory)
  --skipdownload        Don't download zip file
```
### examples:

```bash
(hcls) > download_fhir_spec
```
1. If `fhir-spec.zip` is not present in the data directory, or it is present but its modification date is older than the one on the FHIR web site, download it.  Note that this can take a while
2. If the `fhir-spec.zip` was downloaded, unzip all of the files that end with ".profile.json" into the `site` directory
3. If the `fhir-spec.zip` file was downloaded, unzip all the files that end with ".example.xml" into the `examples` directory.

A log of the output can be found in `data/extract.log`

## ```generate_xml_definitions```
