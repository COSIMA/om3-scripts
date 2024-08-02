This directory contains Payu setup and archive userscripts for ACCESS-OM3.

To use, add these to config.yaml:

```yaml
userscripts:
    setup: /usr/bin/bash /g/data/vk83/apps/om3-scripts/payu_config/setup.sh
    archive: /usr/bin/bash /g/data/vk83/apps/om3-scripts/payu_config/archive.sh

modules:
    use: 
        - /g/data/hh5/public/modules
    load: 
        - conda/analysis
```
