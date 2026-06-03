# Pipeline: hello_pipeline

## Purpose

Prove that the Thin Runner can run a pipeline definition made of one or more
skill steps.

## Flow

```text
Input
|
v
hello_world skill
|
v
Pipeline output
|
v
Memory + logs
```

## Command

`thin-runner run-pipeline pipelines/hello_pipeline.yaml`
