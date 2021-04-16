# Running Corazon Runner

This runner application encapsulates corazon with a commandline interface. The interface boils down manual steps into
easily automatable procedures which can be initialized by bash scripts, or other automations.

### How to setup and run the first set of calculations

```
PYTHONPATH='.' python corazon_runner/factory.py -i input-files/first-dataset -o output-files/first-dataset -m sync-data
PYTHONPATH='.' python corazon_runner/factory.py -i input-files/first-dataset -o output-files/first-dataset -m run-calc
```
