try:
    from ruamel.yaml import YAML

    ryaml = YAML()
    ryaml.preserve_quotes = True
except ImportError:
    print("\nFatal error: ruamel.yaml is not available.")
    print("On NCI, do the following and try again:")
    print("   module use /g/data/vk83/modules && module load payu/1.1.5\n")
    raise


def read_yaml(yaml_path):
    with open(yaml_path, "r") as f:
        return ryaml.load(f)


def write_yaml(data, yaml_path):
    with open(yaml_path, "w") as f:
        ryaml.dump(data, f)


class LiteralString(str):
    pass


def represent_literal_str(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


ryaml.representer.add_representer(LiteralString, represent_literal_str)
