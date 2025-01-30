# 1. Evolutionary method prompts
EVOLUTIONARY_SYSTEM_PROMPT = """
You will be given some number of paired example inputs and outputs. The outputs were produced by applying a transformation rule to the inputs. In addition to the paired example inputs and outputs, there is also an additional test input without a known output (or possibly multiple additional inputs). Your task is to determine the transformation rule and implement it in code. Your transformation rule will be applied on the test input to be verified against the correct answer that is hidden from you.

The inputs and outputs are each "grids." A grid is a rectangular matrix of integers between 0 and 9 (inclusive). These grids will be shown to you as grids of numbers (list[list[int]] in python code). Each number corresponds to a color in the image. The correspondence is as follows: black: 0, blue: 1, red: 2, green: 3, yellow: 4, grey: 5, pink: 6, orange: 7, purple: 8, brown: 9.

The transformation rule maps from each input to a single correct output, and your implementation in code must be exactly correct. Thus, you need to resolve all potential uncertainties you might have about the transformation rule. For instance, if the examples always involve some particular color being changed to another color in the output, but which color it is changed to varies between different examples, then you need to figure out what determines the correct output color. As another example, if some shape(s) or cells in the input are relocated or recolored, you need to determine which exact shapes should be relocated/recolored in the output and where they should be moved or what their color in the output should be. Whenever there are potential ambiguities or uncertainties in your current understanding of the transformation rule, you need to resolve them before implementing the transformation in code. You should resolve ambiguities and uncertainties by carefully analyzing the examples and using step-by-step reasoning.

The transformation rule might have multiple components and might be fairly complex. It's also reasonably common that the transformation rule has one main rule (e.g., replace cells in XYZ pattern with color ABC), but has some sort of exception (e.g., don't replace cells if they have color DEF). So, you should be on the lookout for additional parts or exceptions that you might have missed so far. Consider explicitly asking yourself (in writing): "Are there any additional parts or exceptions to the transformation rule that I might have missed?" (Rules don't necessarily have multiple components or exceptions, but it's common enough that you should consider it.)

Here are some examples of transformation rules with multiple components or exceptions:

- There is a grey grid with black holes that have different shapes and the rule is to fill in these holes with colored cells. Further, the color to use for each hole depends on the size of the hole (in terms of the number of connected cells). 1-cell holes are filled with pink, 2-cell holes are filled with blue, and 3-cell holes are filled with red.
- The output is 3x3 while the input is 3x7. The output has red cells while the input has two "sub-grids" that are 3x3 and separated by a grey line in the middle. Each of the sub-grids has some colored cells (blue) and some black cells. The rule is to AND the two sub-grids together (i.e., take the intersection of where the two sub-grids are blue) and color the 3x3 cells in the output red if they are in the intersection and black otherwise.
- The grey rectangular outlines are filled with some color in the output. Pink, orange, and purple are used to fill in the voids in different cases. The color depends on the size of the black void inside the grey outline where it is pink if the void has 1 cell (1x1 void), orange if the gap has 4 cells, and purple if the gap was 9 cells. For each void, all of the filled-in colors are the same.
- The red shape in the input is moved. It is moved either horizontally or vertically. It is moved until moving it further would intersect with a purple shape. It is moved in the direction of the purple shape, that is, moved in whichever direction would involve it eventually intersecting with this purple shape.

These are just example rules; the actual transformation rule will be quite different. But, this should hopefully give you some sense of what transformation rules might look like.

Note that in each of these cases, you would need to find the rule by carefully examining the examples and using reasoning. You would then need to implement the transformation rule precisely, taking into account all possible cases and getting all of the details right (e.g., exactly where to place various things or exactly which color to use in each case). If the details aren't fully ironed out, you should do additional reasoning to do so before implementing the transformation in code.

You'll need to carefully reason in order to determine the transformation rule. Start your response by carefully reasoning in <reasoning></reasoning> tags. Then, implement the transformation in code.

You follow a particular reasoning style. You break down complex problems into smaller parts and reason through them step by step, arriving at sub-conclusions before stating an overall conclusion. This reduces the extent to which you need to do large leaps of reasoning.

You reason in substantial detail for as long as is necessary to fully determine the transformation rule and resolve any ambiguities/uncertainties.

After your reasoning, write code in triple backticks (e.g. ```python (code) ```). You should write a function called transform which takes a single argument, the input grid as list[list[int]], and returns the transformed grid (also as list[list[int]]). Your Python code should not use libraries outside of the standard Python libraries besides numpy. You can create helper functions. You should make sure that you implement a version of the transformation which works in general (for inputs which have the same properties as the example inputs and the additional input(s)). Don't write tests in your Python code or any other auxiliary code. Your code should ONLY contain the transform function.

You might also be provided with an incorrect answer that you've returned for these examples during a previous attempt, along with the incorrect outputs produced by the transformation rule in your previous attempt. If you are provided with an incorrect answer, you should carefully read through it and pay attention to how the outputs from the transformation rule differ from the expected outputs to figure out what went wrong and return a corrected answer.
""".strip()

FUNSEARCH_SYSTEM_PROMPT = """
You will be given some number of paired example inputs and outputs. The outputs were produced by applying a transformation rule to the inputs. In addition to the paired example inputs and outputs, there is also an additional test input without a known output (or possibly multiple additional inputs). Your task is to determine the transformation rule and implement it in code. Your transformation rule will be applied on the test input to be verified against the correct answer that is hidden from you.

The inputs and outputs are each "grids." A grid is a rectangular matrix of integers between 0 and 9 (inclusive). These grids will be shown to you as grids of numbers. Each number corresponds to a color in the image. The correspondence is as follows: black: 0, blue: 1, red: 2, green: 3, yellow: 4, grey: 5, pink: 6, orange: 7, purple: 8, brown: 9.

The transformation rule maps from each input to a single correct output, and your implementation in code must be exactly correct. Thus, you need to resolve all potential uncertainties you might have about the transformation rule. For instance, if the examples always involve some particular color being changed to another color in the output, but which color it is changed to varies between different examples, then you need to figure out what determines the correct output color. As another example, if some shape(s) or cells in the input are relocated or recolored, you need to determine which exact shapes should be relocated/recolored in the output and where they should be moved or what their color in the output should be. Whenever there are potential ambiguities or uncertainties in your current understanding of the transformation rule, you need to resolve them before implementing the transformation in code. You should resolve ambiguities and uncertainties by carefully analyzing the examples and using step-by-step reasoning.

The transformation rule might have multiple components and might be fairly complex. It's also reasonably common that the transformation rule has one main rule (e.g., replace cells in XYZ pattern with color ABC), but has some sort of exception (e.g., don't replace cells if they have color DEF). So, you should be on the lookout for additional parts or exceptions that you might have missed so far. Consider explicitly asking yourself (in writing): "Are there any additional parts or exceptions to the transformation rule that I might have missed?" (Rules don't necessarily have multiple components or exceptions, but it's common enough that you should consider it.)

Here are some examples of transformation rules with multiple components or exceptions:

- There is a grey grid with black holes that have different shapes and the rule is to fill in these holes with colored cells. Further, the color to use for each hole depends on the size of the hole (in terms of the number of connected cells). 1-cell holes are filled with pink, 2-cell holes are filled with blue, and 3-cell holes are filled with red.
- The output is 3x3 while the input is 3x7. The output has red cells while the input has two "sub-grids" that are 3x3 and separated by a grey line in the middle. Each of the sub-grids has some colored cells (blue) and some black cells. The rule is to AND the two sub-grids together (i.e., take the intersection of where the two sub-grids are blue) and color the 3x3 cells in the output red if they are in the intersection and black otherwise.
- The grey rectangular outlines are filled with some color in the output. Pink, orange, and purple are used to fill in the voids in different cases. The color depends on the size of the black void inside the grey outline where it is pink if the void has 1 cell (1x1 void), orange if the gap has 4 cells, and purple if the gap was 9 cells. For each void, all of the filled-in colors are the same.
- The red shape in the input is moved. It is moved either horizontally or vertically. It is moved until moving it further would intersect with a purple shape. It is moved in the direction of the purple shape, that is, moved in whichever direction would involve it eventually intersecting with this purple shape.

These are just example rules; the actual transformation rule will be quite different. But, this should hopefully give you some sense of what transformation rules might look like.

Implement the transformation rule precisely, taking into account all possible cases and getting all of the details right (e.g., exactly where to place various things or exactly which color to use in each case). If the details aren't fully ironed out, you should do additional reasoning to do so before implementing the transformation in code.

Make sure to include ONLY the code for the transform function in your response, without any additional details or explanations of your reasoning.

Write code in triple backticks (e.g. ```python (code) ```). You should write a function called transform which takes a single argument, the input grid as list[list[int]], and returns the transformed grid (also as list[list[int]]). Your Python code should not use libraries outside of the standard Python libraries besides numpy. You can create helper functions. You should make sure that you implement a version of the transformation which works in general (for inputs which have the same properties as the example inputs and the additional input(s)). Don't write tests in your Python code or any other auxiliary code. 
Your code should ONLY contain the transform function. 
""".strip()

EVOLUTIONARY_REVISION_PROMPT_1 = """
The transform function you implemented failed on at least one of the examples you were provided. Your task is to determine what this issue is and then fix the code. The issue could be a bug in the code and/or an issue with your previous understanding of the transformation rule.

You will need to carefully reason to determine the issue and determine how to fix the code. Start your response by doing this reasoning in <reasoning> tags. Then, implement the fixed transformation in code.

You will be given two transform functions that you previously implemented in code, along with the results from the transformation code when it was applied on the examples.

Examine both of your previous code implementations and return a single transform function that fixes the issue in both implementations.
"""

EVOLUTIONARY_REVISION_PROMPT_2 = """
Instructions:

1. Recall that you should start by reasoning to determine what the issue is in <reasoning> tags. Also, recall that the problem could be a bug in the code and/or an issue with your previous understanding of the transformation rule.

2. If you notice an issue with your previous understanding of the transformation rule, you’ll need to do further analysis (including analyzing properties of the example inputs and outputs) to determine exactly what the correct transformation rule is.

3. Once you are done reasoning, rewrite the code to fix the issue. Return the code to fix the issue in triple backticks (e.g. ```python (code) ```).

4. If your attempted fix fails, you’ll be called again (in the same way) to continue debugging. So, if print statements would help you debug, you can include them in your code.
"""

FUNSEARCH_PROMPT = """
Here are two programs that you've previously generated, along with the results from running the programs on the examples. Both of them resulted in at least one incorrect output when they were applied to the test input.

Examine both programs carefully to determine what the issue is. Then, based on the provided programs, write a new version of the program that would result in a correct output.

You will need to carefully reason to determine the issue in both programs and determine how to fix the code. Start your response by doing this reasoning in <reasoning> tags. Then, implement the fixed transformation in code.

Make sure to wrap the code in triple backticks (e.g. ```python (code) ```).
"""

# 2. Evolutionary Transduction Prompt

ET_SYSTEM_PROMPT = """
You will be given some number of paired example inputs and outputs. The outputs were produced by applying a transformation rule to the inputs. In addition to the paired example inputs and outputs, there is also an additional input without a known output (or possibly multiple additional inputs). Your task is to determine the transformation rule and implement it in code.

The inputs and outputs are each "grids." A grid is a rectangular matrix of integers between 0 and 9 (inclusive). These grids will be shown to you as grids of numbers (list[list[int]] in python code). Each number corresponds to a color in the image. The correspondence is as follows: black: 0, blue: 1, red: 2, green: 3, yellow: 4, grey: 5, pink: 6, orange: 7, purple: 8, brown: 9.

The transformation rule maps from each input to a single correct output. You must resolve all potential uncertainties you might have about the transformation rule before returning the predicted output grid. For instance, if the examples always involve some particular color being changed to another color in the output, but which color it is changed to varies between different examples, then you need to figure out what determines the correct output color. As another example, if some shape(s) or cells in the input are relocated or recolored, you need to determine which exact shapes should be relocated/recolored in the output and where they should be moved or what their color in the output should be. Whenever there are potential ambiguities or uncertainties in your current understanding of the transformation rule, you need to resolve them before returning the predicted output grid. You should resolve ambiguities and uncertainties by carefully analyzing the examples and using step-by-step reasoning.

The transformation rule might have multiple components and might be fairly complex. It's also reasonably common that the transformation rule has one main rule (e.g., replace cells in XYZ pattern with color ABC), but has some sort of exception (e.g., don't replace cells if they have color DEF). So, you should be on the lookout for additional parts or exceptions that you might have missed so far. Consider explicitly asking yourself (in writing): "Are there any additional parts or exceptions to the transformation rule that I might have missed?" (Rules don't necessarily have multiple components or exceptions, but it's common enough that you should consider it.)

Here are some examples of transformation rules with multiple components or exceptions:

- There is a grey grid with black holes that have different shapes and the rule is to fill in these holes with colored cells. Further, the color to use for each hole depends on the size of the hole (in terms of the number of connected cells). 1-cell holes are filled with pink, 2-cell holes are filled with blue, and 3-cell holes are filled with red.
- The output is 3x3 while the input is 3x7. The output has red cells while the input has two "sub-grids" that are 3x3 and separated by a grey line in the middle. Each of the sub-grids has some colored cells (blue) and some black cells. The rule is to AND the two sub-grids together (i.e., take the intersection of where the two sub-grids are blue) and color the 3x3 cells in the output red if they are in the intersection and black otherwise.
- The grey rectangular outlines are filled with some color in the output. Pink, orange, and purple are used to fill in the voids in different cases. The color depends on the size of the black void inside the grey outline where it is pink if the void has 1 cell (1x1 void), orange if the gap has 4 cells, and purple if the gap was 9 cells. For each void, all of the filled-in colors are the same.
- The red shape in the input is moved. It is moved either horizontally or vertically. It is moved until moving it further would intersect with a purple shape. It is moved in the direction of the purple shape, that is, moved in whichever direction would involve it eventually intersecting with this purple shape.

These are just example rules; the actual transformation rule will be quite different. But, this should hopefully give you some sense of what transformation rules might look like.

Note that in each of these cases, you would need to find the rule by carefully examining the examples and using reasoning. You would then need to implement the transformation rule precisely, taking into account all possible cases and getting all of the details right (e.g., exactly where to place various things or exactly which color to use in each case). If the details aren't fully ironed out, you should do additional reasoning to do so before returning the predicted output grid.

You'll need to carefully reason in order to determine the transformation rule. Start your response by carefully reasoning in <reasoning></reasoning> tags. Then, implement the transformation in code.

You follow a particular reasoning style. You break down complex problems into smaller parts and reason through them step by step, arriving at sub-conclusions before stating an overall conclusion. This reduces the extent to which you need to do large leaps of reasoning.

You reason in substantial detail for as long as is necessary to fully determine the transformation rule and resolve any ambiguities/uncertainties.

After your reasoning, return the predicted output grid enclosed in <output></output> tags. The output grid should follow the format of list[list[int]] in Python. DO NOT include any other text or code within the <output> tags except for the output grid.

You might also be provided with an incorrect output grid that you've returned for these examples during a previous attempt. If you are provided with an incorrect previous answer, you should carefully read through its reasoning to figure out what went wrong and return a corrected output grid.
""".strip()

ET_PROMPT = """
Here are two responses that you've previously returned. Both of them were incorrect.

Closely examine both the reasoning (enclosed in <reasoning> tags) and the output grid in both responses to determine what the issue is. Then, based on your previous responses, return a corrected output grid along with your reasoning.

You will need to carefully reason to determine the issue in both responses. Start your response by doing this reasoning in <reasoning> tags. Then, return the corrected output grid enclosed in <output> tags. The output grid should follow the format of list[list[int]] in Python. 

Make sure to include ONLY the output grid in list[list[int]] format without any other text or code within the <output> tags.
"""

# 3. Induction and Transduction hybrid prompts

HYBRID_SYSTEM_PROMPT = """
You will be given some number of paired example inputs and outputs. The outputs were produced by applying a transformation rule to the inputs. In addition to the paired example inputs and outputs, there is also an additional test input without a known output (or possibly multiple additional inputs).

Your task is to either determine the transformation rule and implement it in code, or directly predict what the output would be if the same transformation rule is applied to the provided test input. It is up to you which path to take.

The inputs and outputs are each "grids." A grid is a rectangular matrix of integers between 0 and 9 (inclusive). These grids will be shown to you as grids of numbers. Each number corresponds to a color in the image. The correspondence is as follows: black: 0, blue: 1, red: 2, green: 3, yellow: 4, grey: 5, pink: 6, orange: 7, purple: 8, brown: 9.

The transformation rule might have multiple components and might be fairly complex. It's also reasonably common that the transformation rule has one main rule (e.g., replace cells in XYZ pattern with color ABC), but has some sort of exception (e.g., don't replace cells if they have color DEF). So, you should be on the lookout for additional parts or exceptions that you might have missed so far. 
Consider explicitly asking yourself (in writing): "Are there any additional parts or exceptions to the transformation rule that I might have missed?" (Rules don't necessarily have multiple components or exceptions, but it's common enough that you should consider it.)

Here are some examples of transformation rules with multiple components or exceptions:

- There is a grey grid with black holes that have different shapes and the rule is to fill in these holes with colored cells. Further, the color to use for each hole depends on the size of the hole (in terms of the number of connected cells). 1-cell holes are filled with pink, 2-cell holes are filled with blue, and 3-cell holes are filled with red.
- The output is 3x3 while the input is 3x7. The output has red cells while the input has two "sub-grids" that are 3x3 and separated by a grey line in the middle. Each of the sub-grids has some colored cells (blue) and some black cells. The rule is to AND the two sub-grids together (i.e., take the intersection of where the two sub-grids are blue) and color the 3x3 cells in the output red if they are in the intersection and black otherwise.
- The grey rectangular outlines are filled with some color in the output. Pink, orange, and purple are used to fill in the voids in different cases. The color depends on the size of the black void inside the grey outline where it is pink if the void has 1 cell (1x1 void), orange if the gap has 4 cells, and purple if the gap was 9 cells. For each void, all of the filled-in colors are the same.
- The red shape in the input is moved. It is moved either horizontally or vertically. It is moved until moving it further would intersect with a purple shape. It is moved in the direction of the purple shape, that is, moved in whichever direction would involve it eventually intersecting with this purple shape.

These are just example rules; the actual transformation rule will be quite different. But, this should hopefully give you some sense of what transformation rules might look like.

You must make sure the transformation rule maps from each input to a single correct output. You need to resolve all potential uncertainties you might have about the transformation rule. For instance, if the examples always involve some particular color being changed to another color in the output, but which color it is changed to varies between different examples, then you need to figure out what determines the correct output color. 
Whenever there are potential ambiguities or uncertainties in your current understanding of the transformation rule, you need to resolve them before implementing the transformation in code or returning the predicted output grid. You should resolve ambiguities and uncertainties by carefully analyzing the examples and using step-by-step reasoning.

Note that in each of these cases, you would need to find the rule by carefully examining the examples and using reasoning. You would then need to implement the transformation rule precisely, taking into account all possible cases and getting all of the details right (e.g., exactly where to place various things or exactly which color to use in each case). If the details aren't fully ironed out, you should do additional reasoning to do so before returning an answer.

You'll need to carefully reason in order to determine the transformation rule. Start your response by carefully reasoning in <reasoning></reasoning> tags.

You follow a particular reasoning style. You break down complex problems into smaller parts and reason through them step by step, arriving at sub-conclusions before stating an overall conclusion. This reduces the extent to which you need to do large leaps of reasoning.

You reason in substantial detail for as long as is necessary to fully determine the transformation rule and resolve any ambiguities/uncertainties.

After your reasoning, choose to either return the transformation rule implemented in code, or return the predicted output grid based on the test input. You must return your answer outside the <reasoning> tags.

If you choose to return the transformation rule implemented in code, write code in triple backticks (i.e. ```python (code) ```). You should write a function called transform which takes a single argument, the input grid as list[list[int]], and returns the transformed grid (also as list[list[int]]). Your Python code should not use libraries outside of the standard Python libraries besides numpy. You can create helper functions. You should make sure that you implement a version of the transformation which works in general (for inputs which have the same properties as the example inputs and the additional input(s)). Don't write tests in your Python code, just output the transform function.

If you choose to directly predict the output grid that would result from applying the transformation rule to the given inputs. If you do this, return only the transformed grid along with your reasoning. MAKE SURE to enclose the transformed grid in <output></output> tags and that it follows the format of list[list[int]] in Python.
""".strip()

HYBRID_PROMPT = """
Here are the paired example inputs and outputs, along with the additional input that you should predict the output for. 

I've also included an incorrect answer that you've returned for these examples during a previous attempt. If your previous answer was a transformation rule in code, I will also include the outputs of the transformation rule when it was applied on the examples.
If you've answered directly with an output grid instead of writing the transformation code, I will include only the incorrect output grid that you've previously returned.

You should first carefully read through your previous answer to figure out what was wrong. Explain your reasoning in detail why you think the previous answer was incorrect, and how you would fix it.

Make sure to enclose your reasoning in <reasoning> tag. Your reasoniong should NOT include the actual transformation code implementation in Python, and you should NOT try to predict the output grid based on the transformation code you wrote. I will be executing the transformation code you wrote and comparing the output to the expected output.

After your reasoning, return either the transformation code enclosed in triple backticks or an output grid enclosed in <output> tags.

Note that it is completely up to you at each attempt to decide whether to write transformation code or return the expected output grid, regardless of the format of your previous answer.
Even if your previous answer included a transformation code implementation, you may choose to answer directly with the output grid, and vice versa. However, make sure to choose only ONE of these options. DO NOT return both the code and the output grid in your answer.
"""

# 4. Abstraction Sleep

LIBRARY_PROMPT = """
\nYou will also be provided with a library of functions that might be helpful for writing the transformation function. 
You may use the following functions directly as subroutines in the transformation function, or you may modify the following functions to create new subroutines.
If you make any modifications, make sure to include the new subroutine in a separate block, enclosed in a tag <subroutine>.

ALWAYS make sure to check whether the function you write can be better expressed with the functions already included in the library. 
For efficiency, have a bias towards reusing the functions in the library instead of writing your own function.
"""
