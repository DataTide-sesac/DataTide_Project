import sys
import os
import importlib.util

print("Current Working Directory:", os.getcwd())
print("sys.path:", sys.path)

try:
    # Try to find the spec for DataTide_back
    spec = importlib.util.find_spec("DataTide_back")
    if spec:
        print(f"Found DataTide_back spec: {spec.origin}")
        # Try to load the module
        module = importlib.util.module_from_spec(spec)
        sys.modules["DataTide_back"] = module
        spec.loader.exec_module(module)

        # Now try to import models from DataTide_back
        models_spec = importlib.util.find_spec("DataTide_back.models")
        if models_spec:
            print(f"Found DataTide_back.models spec: {models_spec.origin}")
            models_module = importlib.util.module_from_spec(models_spec)
            sys.modules["DataTide_back.models"] = models_module
            models_spec.loader.exec_module(models_module)
            print("Successfully imported DataTide_back.models")
        else:
            print("Could not find DataTide_back.models spec.")
    else:
        print("Could not find DataTide_back spec.")

except ModuleNotFoundError as e:
    print(f"ModuleNotFoundError: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
