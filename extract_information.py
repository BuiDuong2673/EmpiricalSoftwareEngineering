"""Extract partial information from LLM report to support experiment with human evaluators."""
import json


class HumanExperimentDataExtractor:
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
    
    def run_extraction(self) -> None:
        """Run the extraction process based on the type of experiment."""
        if self.is_accuracy:
            report_path = self.full_accuracy_report_path
            try:
                with open(report_path, 'r', encoding='utf-8') as file:
                    full_report = [json.loads(line) for line in file]
            except FileNotFoundError:
                print(f"File not found: {report_path}")
                return
            first_round_data = self.first_round_experiment(full_report)
            second_round_data = self.second_round_experiment(full_report)
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


if __name__ == "__main__":
    extractor = HumanExperimentDataExtractor(is_accuracy=False)
    extractor.run_extraction()
            