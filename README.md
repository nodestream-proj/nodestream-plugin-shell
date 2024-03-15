# Nodestream Shell Plugin

This plugin provides a [Nodestream](https://github.com/nodestream-proj/nodestream) shell extractor. 

**NOTE: This plugin is currently in development and is not yet ready for production use.**

## Installation

```bash
pip install nodestream-plugin-shell
```

## For commands that return output in json format
```yaml
# pipeline.yaml
- implementation: nodestream_plugin_shell:Shell
  arguments:
    command: curl
    arguments:
      - https://example.com/api/data/json
    options: 
      X: GET
      header: "Accept: application/json"
    ignore_stdout: false #Provide json output from command to next step in pipeline.
```

This would be equivalent to running: 
```
curl https://example.com/api/data.json -X GET --header "Accept: application/json"
```

## For commands that create files that you would like to read into the pipeline

#### Terminal command


```yaml
# pipeline.yaml
- implementation: nodestream_plugin_shell:Shell
  arguments:
    command: curl
    arguments:
      - https://example.com/api/data.json
    options: 
      X: GET
      header: "Accept: application/json"
    flags: 
      - O
    ignore_stdout: true #Do not provide output from command to next step in pipeline.

- implementation: nodestream.pipeline.extractors:FileExtractor
  arguments:
    globs:
    - data.json
```

This would be equivalent to running: 
```
curl https://example.com/api/data.json -X GET --header "Accept: application/json" -O
cat data.json
```