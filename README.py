
# README

This is a simple command line utility for converting rhd files to axona files.

Clone this repository and go into the directory. Then use the following command format to convert the files.

```
python manage.py --output {output directory} --rhd {rhd path} --csv {csv path} --json {json path}
```

The RHD file should contain the raw electrophysiology data that needs to be down-sampled and converted.

If you have additional position data, you must include a CSV and JSON file formatted like the ones shown in the test data directory.

The JSON file contains the header information to be written into the axona POS file. The CSV file should contain the tracker data.
