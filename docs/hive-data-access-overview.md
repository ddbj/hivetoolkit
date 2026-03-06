# Hive Data Access API – Overview for hivetoolkit Users

This document provides a simplified overview of the data model exposed by the
Hive Data Access API for Python (`hive-data-access`), as relevant to users of `hivetoolkit`. This document is **not** a complete or authoritative specification of the
Hive Data Access API. The official and up-to-date API documentation is provided
by Reifycs Inc.

hive-data-access provides a structured interface for accessing mass spectrometry data
stored in Hive-formatted files. The data model is hierarchical and read-only.

## HiveFile

`HiveFile` represents a single Hive-format data file.

Responsibilities:

-   Opening and closing a file
-   Providing access to contained measurements

Typical operations:

-   Retrieve the number of measurements
-   Access a specific measurement by index

## Measurement

A `Measurement` represents one acquired sample within a file.

Responsibilities:

-   Providing metadata for the sample
-   Providing access to analysis objects

A file may contain one or multiple measurements, depending on the acquisition setup.

## QualAnalysis

`QualAnalysis` represents scan-mode (qualitative) mass spectrometry data.

Characteristics:

-   Spectra are stored in the order of acquisition
-   Multiple acquisition conditions may be present

Typical access patterns:

-   Retrieve spectra by index
-   Find spectra near a given retention time
-   Generate TIC, BPC, or XIC chromatograms

## QuanAnalysis

`QuanAnalysis` represents quantitative data such as SIM or SRM channels.

Characteristics:

-   Each analysis corresponds to one channel or transition
-   Chromatogram data are directly accessible

Typical access patterns:

-   Retrieve chromatogram points
-   Use the analysis object directly for visualization

## Indexing Convention

All indices used in hive-data-access APIs are **zero-based** unless otherwise noted.

## Notes

-   hive-data-access provides read-only access to data.
-   Data traversal is explicit and index-based.
-   Visualization and further analysis are expected to be performed by external tools.
