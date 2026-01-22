"""Extract partial information from LLM report to support experiment with human evaluators."""
import json


class HumanExperiment:
    """Extract data from LLM report to support 2 experiments with human evaluators."""
    def __init__(self, is_accuracy: bool=True) -> None:
        """Initialize the class."""
        self.is_accuracy = is_accuracy
        self.full_accuracy_report_path = "accuracy_test_reports.jsonl"
        self.full_attack_report_path = "attack_test_reports.jsonl"
    
    def accuracy_first_experiment(self, full_report: list[dict]) -> list[dict]:
        """Extract only the question from each json in full_report."""
        extracted_data = []
        for entry in full_report:
            extracted_entry = {
                "question": entry["question"],
                "correct answer": "",
                "source": ""
            }
            extracted_data.append(extracted_entry)
        return extracted_data
    
    def accuracy_second_experiment(self, full_report: list[dict]) -> list[dict]:
        """Extract question, answer, and source from each json in full_report."""
        extracted_data = []
        for entry in full_report:
            extracted_entry = {
                "question": entry["question"],
                "llm answer": entry["llm answer"],
                "assessment": ""
            }
            extracted_data.append(extracted_entry)
        return extracted_data
    
    def attack_experiment(self, full_report: list[dict]) -> list[dict]:
        """Extract question, llm answer, and attack prompt from each json in full_report."""
        extracted_data = []
        for entry in full_report:
            extracted_entry = {
                "type of attack": entry["type of attack"],
                "attack prompt": entry["attack prompt"],
                "chatbot response": entry["chatbot response"],
                "assessment": ""
            }
            extracted_data.append(extracted_entry)
        return extracted_data
    
    def data_extraction(self) -> None:
        """Run the extraction process based on the type of experiment."""
        if self.is_accuracy:
            report_path = self.full_accuracy_report_path
            try:
                with open(report_path, 'r', encoding='utf-8') as file:
                    full_report = [json.loads(line) for line in file]
            except FileNotFoundError:
                print(f"File not found: {report_path}")
                return
            first_round_data = self.accuracy_first_experiment(full_report)
            second_round_data = self.accuracy_second_experiment(full_report)
            first_round_output_path = "human_experiment_first_round.jsonl"
            second_round_output_path = "human_experiment_second_round.jsonl"
            with open(first_round_output_path, 'w', encoding='utf-8') as file:
                for entry in first_round_data:
                    file.write(json.dumps(entry, ensure_ascii=False) + "\n")
            with open(second_round_output_path, 'w', encoding='utf-8') as file:
                for entry in second_round_data:
                    file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        else:
            report_path = self.full_attack_report_path
            try:
                with open(report_path, 'r', encoding='utf-8') as file:
                    full_report = [json.loads(line) for line in file]
            except FileNotFoundError:
                print(f"File not found: {report_path}")
                return
            attack_data = self.attack_experiment(full_report)
            attack_output_path = "human_experiment_attack.jsonl"
            with open(attack_output_path, 'w', encoding='utf-8') as file:
                for entry in attack_data:
                    file.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def find_empty_answers(self, file_path: str) -> None:
        """Find empty answers in a file.
        
        Args:
            file_path (str): The path to the file to be checked.
        """
        # Read the jsonl file
        with open(file_path, 'r', encoding='utf-8') as file:
            question_list = [json.loads(line) for line in file]
        empty_answer_list = []
        for question_answer in question_list:
            if file_path.endswith("human_experiment_first_round.jsonl"):
                if question_answer.get("correct answer", "") == "" or question_answer.get("source", "") == "":
                    empty_answer_list.append(question_answer)
            if file_path.startswith("human_vs_chatbot_comparison"):
                if question_answer.get("assessment") == None:
                    empty_answer_list.append(question_answer)
        # Save empty answers to a new file
        output_path = file_path.replace(".jsonl", "_empty_answers.jsonl")
        with open(output_path, 'w', encoding='utf-8') as file:
            for entry in empty_answer_list:
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        # Print there are how many empty answers
        print(f"Found {len(empty_answer_list)} empty answers. Saved to {output_path}.")
    
    def compare_answers(self, file_path_1: str, file_path_2: str) -> None:
        """Compare the correct answer and source in 2 files.
        
        Args:
            file_path_1 (str): the path to the first file.
            file_path_2 (str): the path to the second file.
        """
        # Read 2 files
        with open(file_path_1, 'r', encoding='utf-8') as file:
            answer_list_1 = [json.loads(line) for line in file]
        with open(file_path_2, 'r', encoding='utf-8') as file:
            answer_list_2 = [json.loads(line) for line in file]

        # Initialize a list to store discrepancies
        discrepancies = []

        # Compare answers
        for answer_dict_1 in answer_list_1:
            question = answer_dict_1["question"]
            for answer_dict_2 in answer_list_2:
                if answer_dict_2["question"] == question:
                    if (answer_dict_1["correct answer"].strip() != answer_dict_2["correct answer"].strip() or
                        answer_dict_1["source"] != answer_dict_2["source"]):
                        discrepancies.append({
                            "question": question,
                            "file_1_answer": answer_dict_1["correct answer"],
                            "file_2_answer": answer_dict_2["correct answer"],
                            "file_1_source": answer_dict_1["source"],
                            "file_2_source": answer_dict_2["source"]
                        })
                    break
        # Print the number of discrepancies found
        print(f"Found {len(discrepancies)} discrepancies between the two files.")
        # Save all discrepancies to a new file
        output_path = "human_evaluators_round_1_discrepancies.jsonl"
        with open(output_path, 'w', encoding='utf-8') as file:
            for entry in discrepancies:
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def compare_human_with_chatbot(self, file_path_1: str, file_path_2: str) -> None:
        """Print the answer in the first round of human with the chatbot answer to check if they are the same or different."""
        with open(file_path_1, 'r', encoding='utf-8') as file:
            human_reports = [json.loads(line) for line in file]
        with open(file_path_2, 'r', encoding='utf-8') as file:
            chatbot_reports = [json.loads(line) for line in file]
        # Initialize a list to store the comparison reports
        comparison_reports = []
        for human_report in human_reports:
            question = human_report["question"]
            human_answer = human_report["correct answer"]
            # Initialize the variable storing the two answers and questions
            report = {
                "question": question,
                "human answer": human_answer,
                "chatbot answer": "",
                "assessment": None
            }
            for chatbot_report in chatbot_reports:
                if chatbot_report["question"] == question:
                    chatbot_answer = chatbot_report["llm answer"]
                    report["chatbot answer"] = chatbot_answer
                    break
            comparison_reports.append(report)
        # Save the comparison reports to a new file
        # Get the last letter before .jsonl in file_path_1
        last_letter = file_path_1[-7]
        output_path = f"human_vs_chatbot_comparison_{last_letter}.jsonl"
        with open(output_path, 'w', encoding='utf-8') as file:
            for entry in comparison_reports:
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")        

    def visualize_jsonl(self, file_path: str):
        """Make a jsonl file in better visualization.
        
        Args:
            file_path (str): The path to the jsonl file.
        """
        # Make each item in one line
        with open(file_path, 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
        with open(file_path, 'w', encoding='utf-8') as file:
            for entry in data:
                file.write(json.dumps(entry, ensure_ascii=False, indent=4) + "\n")


if __name__ == "__main__":
    experiment = HumanExperiment(is_accuracy=True)
    # experiment.compare_answers(
    #     "human_experiment_first_round_1.jsonl",
    #     "human_experiment_first_round_2.jsonl"
    # )

    # experiment.compare_human_with_chatbot(
    #     "human_experiment_first_round_1.jsonl",
    #     "human_experiment_second_round.jsonl"
    # )

    # experiment.visualize_jsonl("human_vs_chatbot_comparison_1.jsonl")

    experiment.find_empty_answers("human_vs_chatbot_comparison_1.jsonl")
            