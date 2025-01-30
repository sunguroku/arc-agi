import os
import sys
import json
import datetime
import random
import openai
from dotenv import load_dotenv

from execute import evaluate_response
from prompts import (
    EVOLUTIONARY_SYSTEM_PROMPT,
    FUNSEARCH_SYSTEM_PROMPT,
    EVOLUTIONARY_REVISION_PROMPT_1,
    EVOLUTIONARY_REVISION_PROMPT_2,
    FUNSEARCH_PROMPT,
    ET_SYSTEM_PROMPT,
    ET_PROMPT,
    HYBRID_SYSTEM_PROMPT,
    HYBRID_PROMPT,
)

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

azure_client = openai.AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE_URL"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

deepseek_client = openai.OpenAI(api_key="ollama", base_url="http://localhost:11434/v1/")


def query_gpt4o_azure(prompt: str) -> str:
    """
    Send a prompt to GPT4o hosted on Azure and get the response.

    Args:
        prompt (str): the input prompt

    Returns:
        str: response from the model
    """

    try:
        response = azure_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": EVOLUTIONARY_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=3000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying GPT-4: {e}")
        return ""


def query_gpt4o(messages: list) -> str:
    """
    Send messages to GPT-4 and get the response

    Args:
        messages (list): The list of message dictionaries to send to GPT-4

    Returns:
        str: The model's response text
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=10000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying GPT-4: {e}")
        return ""


def query_r1(prompt: str) -> str:
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-r1:8b",
            messages=[
                {"role": "system", "content": HYBRID_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=10000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying R1: {e}")
        return ""


def construct_initial_prompt(task):
    # Format the task data into the prompt
    examples = []
    i = 1
    for item in task["train"]:
        input_rows = ",\n".join(str(row) for row in item["input"])
        output_rows = ",\n".join(str(row) for row in item["output"])
        examples.append(
            f"Example {i}\n\nInput:\n\n[{input_rows}]\n\nOutput:\n\n[{output_rows}]"
        )
        i += 1

    prompt = "Here are the paired example inputs and outputs.\n\n" + "\n\n".join(
        examples
    )

    test_input_rows = ",\n".join(str(row) for row in task["test"][0]["input"])
    prompt += (
        "\n\n"
        + f"Here is the additional test input without a known output:\n\n[{test_input_rows}]"
    )
    return prompt


def construct_revision_prompt(responses):
    prompt = EVOLUTIONARY_REVISION_PROMPT_1 + "\n\n"
    for i, r in enumerate(responses):
        prompt += f"Here are the code and results from transform function {i + 1}.\n\n"
        prompt += "Code: \n\n" + r["code"] + "\n\nResults:\n\n" + r["results"]
    prompt += EVOLUTIONARY_REVISION_PROMPT_2 + "\n\n"
    return prompt


def construct_hybrid_revision_prompt(task, previous_response, previous_results):
    prompt = HYBRID_PROMPT + "\n\n"

    prompt += "A. Examples\n\n"

    prompt += construct_initial_prompt(task)

    # Attach previous answer if there is one
    if previous_response:
        prompt += "\n\nB. Incorrect Previous Answer\n\n"
        start = previous_response.find("<reasoning>")
        prompt += previous_response[start:]

    if "NOT_APPLICABLE_FOR_TRANSDUCTION" not in previous_results:
        prompt += "\n\nC. Outputs produced by the previous answer\n\n"
        prompt += previous_results

    return prompt


def construct_funsearch_prompt(responses):
    prompt = FUNSEARCH_PROMPT + "\n\n"
    for i, r in enumerate(responses):
        prompt += f"Program {i + 1}\n"
        prompt += (
            "Code: \n\n"
            + r["code"]
            + "\n\nResults from running the code:\n\n"
            + r["results"]
            + "\n\n"
        )
    return prompt


def construct_et_prompt(responses):
    """Makes prompt for the evolutionary transduction method"""
    prompt = ET_PROMPT + "\n\n"
    for i, r in enumerate(responses):
        prompt += f"Response {i + 1}\n\n"
        prompt += r["response"] + "\n\n"
    return prompt


def evolutionary_method(task, logfile):
    i = 0
    max_tries = 5
    programs_per_gen = 5
    top_responses = []
    task_solved = False
    print(
        f"========== SYSTEM PROMPT ==========\n\n" + EVOLUTIONARY_SYSTEM_PROMPT,
        file=logfile,
    )
    while not task_solved and i < max_tries:
        print(f"========== Iteration {i + 1} ==========", file=logfile)
        if i == 0:
            prompt = construct_initial_prompt(task)
        else:
            prompt = construct_initial_prompt(task) + "\n\n"
            prompt += construct_funsearch_prompt(top_responses)
        print(f"Prompt: {prompt}", file=logfile)

        messages = [
            {"role": "system", "content": EVOLUTIONARY_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # Generate 10 programs
        responses = []
        for _ in range(programs_per_gen):
            r = query_gpt4o(messages)
            print(f"Response: {r}", file=logfile)
            responses.append(r)

        # Evaluate the programs and track scores
        evals = []

        for r in responses:
            solved, code, results, correctness, avg_pixel_correctness = (
                evaluate_response(r, task)
            )

            score = correctness + avg_pixel_correctness
            print(f"Results: {results}", file=logfile)
            print(f"Score: {score}", file=logfile)
            evals.append(
                {
                    "response": r,
                    "code": code,
                    "score": score,
                    "results": results,
                }
            )

            print("SOLVED?", solved)

            if solved:
                task_solved = True
                break

        if task_solved:
            print(f"========== Task solved! ==========", file=logfile)
            return True

        # Sort by score and take top 2
        evals.sort(key=lambda x: x["score"], reverse=True)
        top_responses = evals[:2]
        for r in top_responses:
            print(f'Top response scores: {r["score"]}\n', file=logfile)

        avg_score_per_gen = sum(e["score"] for e in evals) / len(evals)
        print(
            f"======Average score per generation: {avg_score_per_gen}=======",
            file=logfile,
        )
        i += 1

    print(f"Failed to solve task in {i} attempts", file=logfile)
    return False


def hybrid_method(task, logfile):
    max_tries = 25
    previous_response = ""
    previous_results = ""
    i = 0
    print(
        f"========== SYSTEM PROMPT ==========\n\n" + HYBRID_SYSTEM_PROMPT,
        file=logfile,
    )
    for i in range(max_tries):
        if i == 0:
            prompt = construct_initial_prompt(task)
        else:
            prompt = construct_hybrid_revision_prompt(
                task, previous_response, previous_results
            )

        messages = [
            {"role": "system", "content": HYBRID_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        response = query_gpt4o(messages)

        print(f"\n========== Iteration {i+1} ==========", file=logfile)
        print(f"\n========== PROMPT ==========\n\n{prompt}\n\n", file=logfile)
        print(f"\n========== RESPONSE ==========\n\n{response}\n\n", file=logfile)

        if "<output>" not in response and "```python" not in response:
            # if LLM for some reason fails to respond with either option, skip and try again.
            print(f"\nSkipping iteration {i+1} due to invalid response\n", file=logfile)
            continue

        # Execute the response and check if correct
        try:
            solved, _, results, _, pixel_correctness = evaluate_response(response, task)
        except Exception as e:
            if "<output>" in response:
                print("Internal error handling transduction case:" + str(e))
                break
            results = "The code failed to run with the following error:\n" + str(e)

        # Log evaluation results
        print(
            f"========== Evaluation Results ==========\n\n{results}\n\nPixel Correctness: {pixel_correctness}",
            file=logfile,
        )

        if solved:
            print(f"========== Solved task! ==========", file=logfile)
            return True

        previous_response = response
        previous_results = results
        i += 1

    print(
        f"========== Couldn't solve task in {max_tries} tries ==========",
        file=logfile,
    )
    return False


def evolutionary_transduction_method(task, logfile):
    i = 0
    max_tries = 5
    programs_per_gen = 5
    top_responses = []
    task_solved = False
    print(
        f"========== SYSTEM PROMPT ==========\n\n" + ET_SYSTEM_PROMPT,
        file=logfile,
    )
    while not task_solved and i < max_tries:
        print(f"========== Iteration {i + 1} ==========", file=logfile)
        if i == 0:
            prompt = construct_initial_prompt(task)
        else:
            prompt = construct_initial_prompt(task) + "\n\n"
            prompt += construct_et_prompt(top_responses)
        print(f"Prompt: {prompt}", file=logfile)

        messages = [
            {"role": "system", "content": ET_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # Generate 10 programs
        responses = []
        for _ in range(programs_per_gen):
            r = query_gpt4o(messages)
            print(f"Response: {r}", file=logfile)
            responses.append(r)

        # Evaluate the programs and track scores
        evals = []

        for r in responses:
            solved, code, results, correctness, avg_pixel_correctness = (
                evaluate_response(r, task)
            )

            score = correctness + avg_pixel_correctness
            print(f"Results: {results}", file=logfile)
            print(f"Score: {score}", file=logfile)
            evals.append(
                {
                    "response": r,
                    "code": code,
                    "score": score,
                    "results": results,
                }
            )

            if solved:
                task_solved = True
                break

        if task_solved:
            print(f"========== Task solved! ==========", file=logfile)
            return True

        # Sort by score and take top 2
        evals.sort(key=lambda x: x["score"], reverse=True)
        top_responses = evals[:2]
        for r in top_responses:
            print(f'Top response scores: {r["score"]}\n', file=logfile)

        avg_score_per_gen = sum(e["score"] for e in evals) / len(evals)
        print(
            f"======Average score per generation: {avg_score_per_gen}=======",
            file=logfile,
        )
        i += 1

    print(f"Failed to solve task in {i} attempts", file=logfile)
    return False


def main():
    # Create random folder name for organization
    random_num = random.randint(1, 1000000)
    folder_name = str(random_num)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print(f"Conducting evaluations in {folder_name}")

    total_ct = 0
    correct_ct = 0
    # Loop through all json files in evaluation directory
    eval_dir = "./sample_data"
    for filename in os.listdir(eval_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(eval_dir, filename)
            print(f"\nProcessing {filename}")

            logfilepath = os.path.join(folder_name, filename[:-5] + ".txt")
            logfile = open(logfilepath, "w")

            # Load the task data
            with open(filepath, "r") as f:
                task = json.load(f)

            method = sys.argv[1] if len(sys.argv) > 1 else "evolutionary"
            if method == "hybrid":
                correct = hybrid_method(task, logfile)
            elif method == "et":
                correct = evolutionary_transduction_method(task, logfile)
            else:
                correct = evolutionary_method(task, logfile)

            if correct:
                correct_ct += 1
            total_ct += 1

    print(f"Solved {correct_ct} out of {total_ct} tasks")


if __name__ == "__main__":
    main()
