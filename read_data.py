# Standard library imports
import json
import pickle

if __name__ == "__main__":
    data_name = "reg"

    # Load existing answers
    try:
        results = pickle.load(
            open(f"collected_data/{data_name}_generated.pickle", "rb")
        )
    except:
        results = {}

    print(json.dumps(results, indent=2))
