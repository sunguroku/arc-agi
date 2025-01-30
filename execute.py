# Load test input from training.json
import json
import os
import ast


def pixel_correctness(output_grid, ground_truth):
    """measures pixel correctness of the output_grid"""
    # Check if grids have same dimensions. If not, penalize with 0.
    if len(output_grid) != len(ground_truth) or len(output_grid[0]) != len(
        ground_truth[0]
    ):
        print("GRID DIMENSIONS MISMATCH WHILE MEASURING PIXEL CORRECTNESS")
        return 0

    # Count matching pixels
    matches = 0
    total_pixels = len(output_grid) * len(output_grid[0])

    for i in range(len(output_grid)):
        for j in range(len(output_grid[0])):
            if output_grid[i][j] == ground_truth[i][j]:
                matches += 1

    return matches / total_pixels


def extract_program(response: str):
    """Extract the Python code between triple backticks"""
    # use rfind it to start from the end, because sometimes the file will include the previous answer the model has returned.
    start = response.rfind("```python")
    end = response.find("```", start + 8)

    if start == -1 or end == -1:
        raise ("Could not find Python code between triple backticks")

    return response[start + 9 : end].strip()


def load_transform_function(code: str):
    """Load the transform function from a text file"""

    # Create a new namespace to execute the code
    namespace = {}
    exec(code, namespace)
    try:
        exec(code, namespace)
    except Exception as e:
        raise ValueError(f"Failed to execute code with error: {str(e)}")

    # Return the transform function
    if "transform" not in namespace:
        raise ValueError("No transform function found in the code")
    return namespace["transform"]


def evaluate_response(response: str, task: dict):
    """Evaluate both induction and transduction responses and returns a boolean indicating if the response is correct, the code,
    the results, and the correctness and pixel correctness"""

    results = ""

    # Get test input grid
    test_input = task["test"][0]["input"]
    test_output = task["test"][0]["output"]

    # handle transduction case
    if "<output>" in response:
        extracted_array = extract_array(response)
        solved = extracted_array == test_output
        results = "NOT_APPLICABLE_FOR_TRANSDUCTION"
        return (
            solved,
            "",
            results,
            solved,
            pixel_correctness(extracted_array, test_output),
        )

    try:
        code = extract_program(response)
    except Exception as e:
        results += f"\nError: Could not find Python code between triple backticks with error: {str(e)}"
        return False, "", results, -1, -1

    # Load the transform function from the file
    transform = load_transform_function(code)

    correct_count = 0
    pixel_correctness_sum = 0
    # Apply transformation to all training pairs
    for i, pair in enumerate(task["train"], 1):
        train_input = pair["input"]
        train_output = pair["output"]

        try:
            train_result = transform(train_input)
        except Exception as e:
            results = f"\nError: Transform function failed to run with error: {str(e)}"
            return False, code, results, -1, -1

        results += f"Result for example {i}:\n"

        # Compare result to training output
        if train_result == train_output:
            results += "✓ Transformation matches expected output!\n"
            correct_count += 1
        else:
            results += "✗ Transformation does not match expected output.\n"

            train_input_rows = ",\n".join(str(row) for row in train_input)
            results += f"\nInput Grid:\n[{train_input_rows}]\n"

            train_output_rows = ",\n".join(str(row) for row in train_output)
            results += f"\nExpected Output Grid:\n[{train_output_rows}]\n"

            train_result_rows = ",\n".join(str(row) for row in train_result)
            results += f"\nIncorrect Resulting Output Grid:\n[{train_result_rows}]\n"

        # add pixel correctness
        pixel_correctness_sum += pixel_correctness(train_result, train_output)
        results += "\n"

    correctness = correct_count / len(task["train"])
    avg_pixel_correctness = pixel_correctness_sum / len(task["train"])

    # Handle case where transform function fails to execute
    try:
        output = transform(test_input)
    except Exception as e:
        results += f"\nError: Transform function failed to run on the test input with error: {str(e)}"
        return False, code, results, correctness, avg_pixel_correctness

    return output == test_output, code, results, correctness, avg_pixel_correctness


def extract_array(content: str):

    # Find content between triple backticks (only the last occurrence)
    start = content.find("<output>")
    if start == -1:
        raise ValueError("No opening <output> tag found in file")

    end = content.find("</output>")
    if end == -1:
        raise ValueError("No closing </output> tag found in file")

    # Extract the array string between backticks
    array_str = content[start + 8 : end].strip()
    try:
        output = ast.literal_eval(array_str)
    except Exception as e:
        print(f"Error: Could not parse array string with error: {str(e)}")
        return None

    return output


def main():
    print("hello")


if __name__ == "__main__":
    main()
