-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/JlhV1B
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- DB schema diagram for Project 3

CREATE TABLE "DRG" (
    "DRG Id" INT   NOT NULL,
    "DRG Definition" VARCHAR   NOT NULL,
    "Category" VARCHAR   NOT NULL,
    CONSTRAINT "pk_DRG" PRIMARY KEY (
        "DRG Id"
     )
);

CREATE TABLE "DRG_RECORDS" (
    "Id" INT   NOT NULL,
    "DRG Id" INT   NOT NULL,
    "Provider Id" INT   NOT NULL,
    "Total Discharges" INT   NOT NULL,
    "Average Total Payments" NUMERIC   NOT NULL,
    "Average Medicare Payments" NUMERIC   NOT NULL,
    "Average Covered Charges" NUMERIC   NOT NULL,
    CONSTRAINT "pk_DRG_RECORDS" PRIMARY KEY (
        "Id"
     )
);

CREATE TABLE "PROVIDERS" (
    "Provider Id" INT   NOT NULL,
    "Provider Name" VARCHAR   NOT NULL,
    "Provider Street Address" VARCHAR   NOT NULL,
    "Provider City" VARCHAR   NOT NULL,
    "Provider State" VARCHAR   NOT NULL,
    "zip code" INT   NOT NULL,
    "latitude" FLOAT   NOT NULL,
    "longitude" FLOAT   NOT NULL,
    CONSTRAINT "pk_PROVIDERS" PRIMARY KEY (
        "Provider Id"
     )
);

ALTER TABLE "DRG_RECORDS" ADD CONSTRAINT "fk_DRG_RECORDS_DRG Id" FOREIGN KEY("DRG Id")
REFERENCES "DRG" ("DRG Id");

ALTER TABLE "DRG_RECORDS" ADD CONSTRAINT "fk_DRG_RECORDS_Provider Id" FOREIGN KEY("Provider Id")
REFERENCES "PROVIDERS" ("Provider Id");

