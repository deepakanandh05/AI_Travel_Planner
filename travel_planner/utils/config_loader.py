import yaml

def load_config(path="travel_planner/config/config.yaml"):
    """Read config.yaml and return dictionary."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

