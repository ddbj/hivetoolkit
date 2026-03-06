# README

This directory contains documentation for the Python visualization toolkit
**hivetoolkit** and its related components.

The documents are organized by purpose.  
Please refer to the descriptions below to decide which document to read.

## Where to Start

If you are new to hivetoolkit, start with the overview documents listed below.
They explain the roles of each component and how they fit together.

## Documents

### hive-data-access-overview.md

**Overview of data access and analysis objects**

This document explains how analysis and data objects are obtained from Hive-format
mass spectrometry files using the Hive Data Access API for Python.

Read this document if you want to understand:

-   how Hive-format data is accessed
-   what analysis objects (e.g. QualAnalysis, QuanAnalysis) represent
-   how data objects are prepared before visualization

### hivetoolkit-overview.md

**Overview of visualization capabilities provided by hivetoolkit**

This document provides a conceptual overview of the visualization functions
offered by hivetoolkit.

Read this document if you want to understand:

-   what types of visualizations are available
-   how chromatograms, spectra, and multi-panel plots are conceptually used
-   which visualization functions are relevant for your task

This document focuses on _what can be visualized_ rather than on implementation
details.

### hivetoolkit-api-reference.md

**Detailed API reference for hivetoolkit**

This document provides detailed definitions of hivetoolkit visualization functions,
including function arguments, supported options, and behavior.

Read this document if you need:

-   exact function signatures
-   descriptions of optional arguments
-   detailed behavior of visualization functions

## Executable Examples

Executable examples demonstrating typical visualization workflows are provided
in the `notebooks/` directory at the top level of this repository.

The notebooks are recommended if you prefer to learn by running code and
experimenting interactively.
