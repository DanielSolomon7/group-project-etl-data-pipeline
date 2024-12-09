# TerrificTotes Data platform Project

## Introduction

This project creates a data platform, that **extracts** data from an operational (OLTP) database (called ToteSys), **transforms** it into a star-schema format, stores in a data lake, and **loads** it within a OLAP data warehouse.

## About

The project has **two S3 buckets** - an ingestion bucket and a processing bucket.

It also contains **three Lambdas**...

- **Lambda1** - extracts data from the OLTP ToteSys database, and places it as raw data, in csv format, in the ingestion bucket.
- **Lambda2** - takes data from the ingestion bucket, transforms it into star-schema format, and places it, as parquet format, in the processing bucket.
- **Lambda3** - takes data from the processing bucket and loads it within the OLAP data warehouse.

The Lambdas also has **CloudWatch alerts**, and if a serious alert is triggered an **email** is sent to: <TheTerraformers@protonmail.com>.

## Visual Diagram

![img](./Project_diagram.jpeg)


_Diagram depicting the internal workings and structure of the project_.

## Developer Instructions

- **Running The Make File**

    There are several make commands that can be run when using the project...

  - **make create-environment** - creates a virtual environment.
  - **make requirements** - downloads the relevant dependencies for the project.
  - **make dev-setup** - sets up dev requirements (*bandit, pip-audit, black*).
  - **make run-checks** - runs checks on the project code (*security test, black, unit tests, and coverage checks*)
  - **make layer-setup** - prepare the lambda layers.
  - **make clean** - clean up the lambda layer dependencies.
  - **make all** - run all of the commands.
