
# README

This is a simple command line utility for converting rhd files to axona files.

Clone this repository and go into the directory. Then use the following command format to convert the files.

```
python manage.py --output {output directory} --rhd {rhd path} --csv {csv path} --json {json path}
```

The RHD file should contain the raw electrophysiology data that needs to be down-sampled and converted.

The CSV file may contain concurrent position tracking data.

The JSON file may 
