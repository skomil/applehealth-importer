# applehealth-importer
Convert and load Apple Health data to InfluxDB

This package will convert data exported from the IOS Health app to a InfluxDB database. To run the script:

```importer.py IMPORT_PATH INFLUX_HOST INFLUX_USER INFLUX_PASS```

To use prebuilt docker image:
```docker pull skomil/applehealth-importer```

Properties:

* IMPORT_PATH: Directory where export.zip file is located.
* INFLUX_HOST: Influx DB Host address
* INFLUX_USER: Influx DB Username
* INFLUX_PASS: Influx DB Password

## Script DB Import Workflow

* Currently this script is setup to write to an influxdb named `apple_health`
* Since export.zip contains all data, it will wipe out all data in the database before it adds new data

