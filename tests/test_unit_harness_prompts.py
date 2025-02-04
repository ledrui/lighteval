import json
import os

import pytest

import lighteval.tasks.tasks_prompt_formatting as tasks_prompt_formatting
from lighteval.tasks.requests import Doc


PATH_TO_HARNESS_PROMPTS = os.path.join(os.path.dirname(__file__), "reference_scores/harness_prompts.json")


def pytest_generate_tests(metafunc: pytest.Metafunc):
    """Initializes the main test setup. This function is automatically called by pytest and
    should not be called manually.

    Every function with "model_input" as arguments will be sent the "parameters".
    This function will be run only once, ensuring that each model is run only once on the selected tasks.
    (This is better than using fixtures as fixtures are re-run once for each test, which is not a behavior we want).
    """
    parameters = []

    # If model_input is a test function argument
    # (= the function requires a fixture)
    if "prompt_inputs" in metafunc.fixturenames:
        with open(PATH_TO_HARNESS_PROMPTS) as f:
            prompt_fn_to_examples = json.load(f)

            for prompt_fn_name, examples in prompt_fn_to_examples.items():
                formatter_fn = getattr(tasks_prompt_formatting, prompt_fn_name)

                cur_params = []

                for task_name, examples_list in examples.items():
                    for input_line, reference_line in examples_list:
                        cur_params.append((formatter_fn, input_line, reference_line, task_name))
                parameters.append((prompt_fn_name, cur_params))
        metafunc.parametrize("prompt_inputs", parameters, scope="session")


def test_model_prediction(prompt_inputs: tuple[str, list]):
    """Evaluates a model on a full task - is parametrized using pytest_generate_test"""
    prompt_fn_name, examples = prompt_inputs
    for prompt_fn, input_line, reference_line, task_name in examples:
        formatted_line = prompt_fn(input_line, "")  # task_name)
        reference_line = Doc(**reference_line)

        error_msg = (
            f"Prompt formatting function {prompt_fn_name} failed on input {input_line} from task {task_name}.\n"
        )
        error_msg += f"Reference: {reference_line}\n"
        error_msg += f"Returned : {formatted_line}"
        assert formatted_line == reference_line, error_msg
