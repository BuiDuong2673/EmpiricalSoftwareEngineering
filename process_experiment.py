"""Contain every functions needed to process the data in the experiment."""
import json


class HumanExperiment:
    """Extract data from LLM report to support 2 experiments with human evaluators."""
    def __init__(self, is_accuracy: bool=True) -> None:
        """Initialize the class."""
        self.is_accuracy = is_accuracy
        self.full_accuracy_report_path = "llm_report/accuracy_test_reports.jsonl"
        self.full_attack_report_path = "llm_report/attack_test_reports.jsonl"

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
    
    def create_experiment_form_round_1(self) -> None:
        """Retrieved informations needed and provide the blank space for evaluator to fill in for round 1."""
        if self.is_accuracy:
            report_path = self.full_accuracy_report_path
            try:
                with open(report_path, 'r', encoding='utf-8') as file:
                    full_report = [json.loads(line) for line in file]
            except FileNotFoundError:
                print(f"File not found: {report_path}")
                return
            
            # Extract first and second round form
            first_round_data_list = self.accuracy_first_experiment(full_report)
            first_round_data_dict = {}
            for i, data_dict in enumerate(first_round_data_list):
                first_round_data_dict[i] = data_dict

            # Define the paths where these forms will be stored.
            first_round_output_paths = []
            for i in range(2):
                first_round_output_paths.append(f"human_experiment_first_round_{i + 1}.json")

            # Save the form into the file paths
            for frp in first_round_output_paths:
                with open(frp, 'w', encoding='utf-8') as file:
                    json.dump(first_round_data_dict, file, ensure_ascii=False, indent=4)
        else:
            report_path = self.full_attack_report_path
            try:
                with open(report_path, 'r', encoding='utf-8') as file:
                    full_report = [json.loads(line) for line in file]
            except FileNotFoundError:
                print(f"File not found: {report_path}")
                return
            attack_data_list = self.attack_experiment(full_report)
            attack_data_dict = {}
            for i, data_dict in enumerate(attack_data_list):
                attack_data_dict[i] = data_dict

            output_paths = []
            for i in range(2):
                output_paths.append(f"human_experiment_attack_{i + 1}.json")
            
            for op in output_paths:
                with open(op, 'w', encoding='utf-8') as file:
                    json.dump(attack_data_dict, file, ensure_ascii=False, indent=4)
        
    def create_experiment_form_round_2(self) -> None:
        """Create the form for round 2."""
        # Read LLM report
        try:
            with open(self.full_accuracy_report_path, 'r', encoding='utf-8') as file:
                full_report = [json.loads(line) for line in file]
        except FileNotFoundError:
            print(f"File not found: {self.full_accuracy_report_path}")
            return
        # Read human report
        human_report_paths = ["human_experiment_first_round_1.json", "human_experiment_first_round_2.json"]
        for path in human_report_paths:
            # Read the file
            with open(path, 'r', encoding='utf-8') as file:
                human_report = json.load(file)
            second_round_dict = {}
            for i, h_r in human_report.items():
                for llm_r in full_report:
                    if h_r.get("question").strip() == llm_r.get("question"):
                        second_round_dict[i] = {
                            "question": h_r.get("question"),
                            "human answer": h_r.get("correct answer"),
                            "chatbot answer": llm_r.get("llm answer"),
                            "assessment": ""
                        }
                        break
            # Write the form to a json file
            output_path = path.replace("first", "second")
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(second_round_dict, file, ensure_ascii=False, indent=4)
        return second_round_dict

    def find_empty_answers(self, file_path: str) -> None:
        """Find empty answers in a file.
        
        Args:
            file_path (str): The path to the file to be checked.
        """
        # Read the json file
        with open(file_path, 'r', encoding='utf-8') as file:
            finished_form = json.load(file)
        
        empty_answer_list = []
        for _, answer in finished_form.items():
            if file_path.startswith("human_experiment_first_round"):
                if answer.get("correct answer", "") == "" or answer.get("source", "") == "":
                    empty_answer_list.append(answer)
            if file_path.startswith("human_vs_chatbot_comparison"):
                if answer.get("assessment") == None:
                    empty_answer_list.append(answer)
        
        # Change empty_answer_list to dict
        empty_answer_dict = {}
        for i, answer in enumerate(empty_answer_list):
            empty_answer_dict[i] = answer

        # Save empty answers to a new file
        if len(empty_answer_list) > 0:
            output_path = file_path.replace(".json", "_empty_answers.json")
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(empty_answer_dict, file, ensure_ascii=False, indent=4)

        # Print there are how many empty answers
        print(f"Found {len(empty_answer_list)} empty answers.")
    
    def compare_human_answers(self, file_path_1: str, file_path_2: str) -> None:
        """Compare the correct answer and source in 2 files.
        
        Args:
            file_path_1 (str): the path to the first file.
            file_path_2 (str): the path to the second file.
        """
        # Read 2 files
        with open(file_path_1, 'r', encoding='utf-8') as file:
            answer_dict_1 = json.load(file)
        with open(file_path_2, 'r', encoding='utf-8') as file:
            answer_dict_2 = json.load(file)

        # Initialize a list to store discrepancies
        discrepancies = []

        # Compare answers
        for _, answer_1 in answer_dict_1.items():
            question_1 = answer_1.get("question")
            for _, answer_2 in answer_dict_2.items():
                if answer_2.get("question") == question_1:
                    if (answer_1["correct answer"].strip() != answer_2["correct answer"].strip() or
                        answer_1["source"] != answer_2["source"]):
                        discrepancies.append({
                            "question": question_1,
                            "file_1_answer": answer_1["correct answer"],
                            "file_2_answer": answer_2["correct answer"],
                            "file_1_source": answer_1["source"],
                            "file_2_source": answer_2["source"]
                        })
                    break

        # Print the number of discrepancies found
        print(f"Found {len(discrepancies)} discrepancies between the two files.")

        # Save all discrepancies to a new file
        output_path = "human_evaluators_round_1_discrepancies.json"
        with open(output_path, 'w', encoding='utf-8') as file:
            for entry in discrepancies:
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def change_jsonl_to_json(self, file_path):
        result = {}
        buffer = ""
        index = 0

        with open(file_path, encoding="utf-8") as file:
            for line in file:
                buffer += line

                try:
                    obj = json.loads(buffer)
                    result[index] = obj
                    index += 1
                    buffer = ""  # reset after successful parse
                except json.JSONDecodeError:
                    # not a complete JSON object yet
                    continue
        
        # Save the json to a file
        with open(file_path.replace(".jsonl" , ".json"), "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)

        if buffer.strip():
            raise ValueError("File ended with incomplete JSON object")

        return result
    
    def compare_human_assessment(self, file_path_1: str, file_path_2: str) -> None:
        # Read assessments
        with open(file_path_1, "r", encoding="utf-8") as file_1:
            human_assessment_1 = json.load(file_1)
        with open(file_path_2, "r", encoding="utf-8") as file_2:
            human_assessment_2 = json.load(file_2)

        # Initilialize variables to store the accuracy
        accurate_num = 0
        wrong_report_list = []
        for i_1, assessment_1 in human_assessment_1.items():
            if assessment_1.get("question").strip() == human_assessment_2[i_1].get("question").strip():
                if assessment_1.get("assessment").strip() == human_assessment_2[i_1].get("assessment").strip():
                    accurate_num += 1
                else:
                    wrong_report = {
                        "question": assessment_1.get("question"),
                        "chatbot answer": assessment_1.get("chatbot answer"),
                        "evaluator 1 assessment": assessment_1.get("assessment"),
                        "evaluator 2 assessment": human_assessment_2[i_1].get("assessment"),
                        "which correct": ""
                    }
                    # Add the report into list
                    wrong_report_list.append(wrong_report)
            else:
                print(f"WARNING: there is something wrong with the order. Question in {i_1} is different.")
        # Change the wrong report list to dict
        wrong_report_dict = {}
        for i, item in enumerate(wrong_report_list):
            wrong_report_dict[i] = item
        
        # Print the number of discrepancies
        print(f"The number of discrepancies between evaluators assessments are: {len(wrong_report_list)}")
        
        # Save wrong report into file
        with open("second_round_discrepancies.json", "w", encoding="utf-8") as file:
            json.dump(wrong_report_dict, file, ensure_ascii=False, indent=4)
        print("Saved the discrepancies to file: second_round_discrepancies.json")
    
    def create_accurate_assessment(self, evaluator_path_1: str, evaluator_path_2: str, discrepancy_path: str) -> None:
        # Read human evaluators assessments
        with open(evaluator_path_1, "r", encoding="utf-8") as file_1:
            human_assessment_1 = json.load(file_1)
        with open(evaluator_path_2, "r", encoding="utf-8") as file_2:
            human_assessment_2 = json.load(file_2)
        
        # Read the discrepancies
        with open(discrepancy_path, "r", encoding="utf-8") as file_3:
            discrepancies = json.load(file_3)
        
        # Initilialize variables to store the accuracy
        accurate_1 = 0  # Track the number of time evaluator 1 is correct
        accurate_2 = 0  # Track the number of time evaluator 2 is correct

        # Initialize the variable to store the correct assessment
        correct_assessment_dict = {}

        for i_1, assessment_1 in human_assessment_1.items():
            correct_assessment_dict[i_1] = {}
            if assessment_1.get("question").strip() == human_assessment_2[i_1].get("question").strip():
                if assessment_1.get("assessment").strip() == human_assessment_2[i_1].get("assessment").strip():
                    accurate_1 += 1
                    accurate_2 += 1
                    correct_assessment_dict[i_1] = {
                        "question": assessment_1.get("question"),
                        "correct assessment": assessment_1.get("assessment")
                    }
                else:
                    for i_d, discrepancy in discrepancies.items():
                        if discrepancy.get("question").strip() == assessment_1.get("question"):
                            if discrepancy.get("which correct").strip() == "1":
                                accurate_1 += 1
                                correct_assessment_dict[i_1] = {
                                    "question": assessment_1.get("question"),
                                    "correct assessment": assessment_1.get("assessment")
                                }
                            else:
                                accurate_2 += 1
                                correct_assessment_dict[i_1] = {
                                    "question": human_assessment_2.get("question"),
                                    "correct assessment": human_assessment_2.get("assessment")
                                }
            else:
                print(f"WARNING: there is something wrong with the order. Questions in {i_1} are different.")
    
        # Print the human evaluators accuracy
        accurate_rate_1 = accurate_1/len(human_assessment_1.values())
        print(f"Evaluator 1 accuracy rate: {accurate_1} / {len(human_assessment_1.values())} = {accurate_rate_1:.4f}")
        
        accurate_rate_2 = accurate_2/len(human_assessment_2.values())
        print(f"Evaluator 2 accuracy rate: {accurate_2} / {len(human_assessment_2.values())} = {accurate_rate_2:.4f}")

        # Save the correct answer into a file
        with open("correct_assessment.json", "w", encoding="utf-8") as file:
            json.dump(correct_assessment_dict, file, ensure_ascii=False, indent=4)
        print("Saved the correct assessment to file: correct_assessment.json")
    
    def calculate_llm_accuracy(self, correct_assessment_path: str) -> None:
        """Compare the human assessment with LLM assessment.
        
        Args:
            human_file_path (str): path to the file storing human assessment.
        """
        # Read correct assessment
        with open(correct_assessment_path, "r", encoding="utf-8") as human_file:
            correct_assessment_dict = json.load(human_file)
        # Read llm assessment
        try:
            with open(self.full_accuracy_report_path, 'r', encoding='utf-8') as file:
                llm_report = [json.loads(line) for line in file]
            # Change full report into a dict
            llm_report_dict = {}
            for i, report in enumerate(llm_report):
                if len(report) == 0:
                    continue
                llm_report_dict[i] = report
        except FileNotFoundError:
            print(f"File not found: {self.full_accuracy_report_path}")
            return
        
        print(f"Len llm_report_dict = {len(llm_report_dict.values())}")

        # Variable storing which cases LLM give wrong assessment.
        wrong_assessment_dict = {}

        for i, llm_assessment in llm_report_dict.items():
            question = llm_assessment.get("question")
            # Search for the correct assessment for the question in the dict
            for c_i, correct_assessment in correct_assessment_dict.items():
                if question.strip() == correct_assessment.get("question"):
                    # Compare LLM assessment with human assessment
                    if str(llm_assessment.get("assessment")).lower() != correct_assessment.get("correct assessment"):
                        wrong_assessment_dict[i] = {
                            "question": llm_assessment.get("question"),
                            "llm assessment": llm_assessment.get("assessment"),
                            "correct assessment": correct_assessment.get("correct assessment")
                        }
        
        # Visualize the accuracy rate of 
        accuracy_time = len(llm_report_dict.values()) - len(wrong_assessment_dict.values())
        accuracy_rate = accuracy_time / len(llm_report_dict.values())
        print(f"Accuracy of LLM: {accuracy_time} / {len(llm_report_dict.values())} = {accuracy_rate:.4f}")

        # Store the wrong cases in a file
        with open("llm_wrong_assessment.json", "w", encoding="utf-8") as file:
            json.dump(wrong_assessment_dict, file, ensure_ascii=False, indent=4)
        print("Saved LLM wrong assessment to file: llm_wrong_assessment.json")            

    
if __name__ == "__main__":
    human_experiment = HumanExperiment(True)
    # human_experiment.create_experiment_form_round_1()

    # human_experiment.change_jsonl_to_json("old_experiment/human_vs_chatbot_comparison_1.jsonl")

    # human_experiment.find_empty_answers("filled_form/human_experiment_second_round_2.json")

    # human_experiment.create_experiment_form_round_2()

    # human_experiment.compare_human_assessment(
    #     "filled_form/human_experiment_second_round_1.json",
    #     "filled_form/human_experiment_second_round_2.json"
    # )

    human_experiment.create_accurate_assessment(
        "filled_form/human_experiment_second_round_1.json",
        "filled_form/human_experiment_second_round_2.json",
        "filled_form/second_round_discrepancies.json"
    )

    # human_experiment.calculate_llm_accuracy(
    #     "filled_form/correct_assessment.json"
    # )
