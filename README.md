# Amalgamate
C++ source file amalgamation

## How to Use

```bash
python3 main.py config.json
```

## How to Configure

Complete your config file in json, see `test/sample.json`

`baseDirectory` The directory for all the relative paths. Can be a relative path (to current working directory) or an absolute path.

`sources` Source files to be amalgamated. Folder is supported. If folder is supplied, all the files in it with extension defined in `extension.source` and `extension.header` will be amalgamated.

`headers` Header files to be amalgamated. Only the files with extension defined in `extension.header` will be amalgamated.

`sourceDest` Output source file.

`headerDest` Output header file.

`prologue` Write your license here.

`includeDirectory` The include directories used when compile. Amalgamation will auto detect them to decide whether keep this include, replace with included file or just delete them.

`removeTwoSlashComments` Whether to remove the comments started with `//`.

`extension.source` and `extension.header` decide which file will be amalgamated.

