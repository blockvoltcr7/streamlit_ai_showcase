import os
from crewai import Crew, Agent, Task
from crewai_tools import BaseTool

class FileWriterTool(BaseTool):
    name: str = "File Writer"
    description: str = "Writes the agent's output to a file"

    def _run(self, output: str, filename: str) -> str:
        directory = "file_output"
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as f:
            f.write(output)
        return f"Output written to {filepath}"

class AverageCalculatorTool(BaseTool):
    name: str = "Average Calculator"
    description: str = "Calculates the average of a list of numbers"

    def _run(self, numbers: str) -> str:
        num_list = [float(num) for num in numbers.split(',')]
        average = sum(num_list) / len(num_list)
        return f"The average is {average:.2f}"

# Create an agent with the custom tools
analysis_agent = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="You are an experienced data analyst skilled in calculating averages.",
    tools=[FileWriterTool(), AverageCalculatorTool()]
)

# Create a task for data analysis
data_analysis_task = Task(
    description="Calculate the average age of participants and write the result to a file. Ages: {ages}",
    agent=analysis_agent,
    expected_output="A string containing the average age calculated from the given list of ages, and confirmation of file writing."
)

# Create a crew and add the task
analysis_crew = Crew(
    agents=[analysis_agent],
    tasks=[data_analysis_task]
)

# Define multiple datasets to analyze
datasets = [
    {"ages": "25, 30, 35, 40, 45"},
    {"ages": "20, 25, 30, 35, 40"},
    {"ages": "30, 35, 40, 45, 50"}
]

# Execute the crew for each dataset
results = analysis_crew.kickoff_for_each(inputs=datasets)

# Print the results and write them to files
for i, result in enumerate(results, 1):
    print(f"Dataset {i} Result:")
    print(result)
    
    # Convert CrewOutput to string
    result_str = str(result)
    
    # Write the result to a file
    filename = f"dataset_{i}_result.txt"
    file_writer = FileWriterTool()
    file_output = file_writer.run(result_str, filename)
    print(file_output)
    print()

print("All results have been written to the file_output directory.")