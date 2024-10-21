# ESMF Profiling tool
The **ESMF Profiling tool** is a Python-based tool designed to read and process performance profile data from ESMF profiling log files. It provides a structured way to extract hierachical timing and computational stats for various regions within ESMF log files, enabling detailed performance analysis.

## Directory structure
```
├── esmfFileParser.py
├── esmfRegion.py
└── README.md
```

### Components:
 1. `esmfFileParser.py`: 
    - handles the input ESMF profile files.
    - constructs the hierarchical data structure.
    - outputs runtimes for specific regions.
 2. `esmfRegion.py`: 
    - defines the ESMFRegion class.
    - represents individual ESMF regions, capturing performance metrics.

The tool supports two profiling data formats, where metrics are included in the brackets for indexing:
 1. `ESMF_Profile.xxxx`:    (0. count, 1. total, 2. self_time, 3. mean    , 4. min_time, 5. max_time           )
 2. `ESMF_Profile.summary`: (0. count, 1. PETs , 2. mean     , 3. min_time, 4. max_time, 5. min_PET, 6. max_PET)

## Usage
Before using the scripts, ensure that ESMF profiling log files are generated first. To enable profiling, simply set the `ESMF_RUNTIME_PROFILE` and `ESMF_RUNTIME_PROFILE_OUTPUT` options in the `config.yaml` file for the desired configuration:
```yaml
env:
  ESMF_RUNTIME_PROFILE: "ON"
  ESMF_RUNTIME_PROFILE_OUTPUT: "TEXT SUMMARY"
```
After running the configuration, specify the path to the profiling logs, along with any specific regions of interest.

One example for demonstration:
----------
```python
# Collect runtime info for specific regions
ESMF_path = ['/path/to/your/ESMF/output/files']
region_names = ['[ESMF]', '[ESMF]/[ensemble] RunPhase1/[ESM0001] RunPhase1/[OCN] RunPhase1']
profile_prefix = 'ESMF_Profile.'
esmf_summary = True  # Set to True for summary profiling
index = 2  # Choose the metric above to extract (e.g., mean time for summary profiling)
runtime_totals = collect_runtime_tot(ESMF_path, regionNames=region_names, profile_prefix=profile_prefix, esmf_summary=esmf_summary, index=index)
print(runtime_totals)
```
