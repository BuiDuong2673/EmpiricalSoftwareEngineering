"""Contain every functions needed to process the data in the experiment."""
import json
import statistics
import numpy as np
from sklearn.metrics import cohen_kappa_score


class AccuracyExperiment:
    """Extract data from LLM report to support 2 experiments with human evaluators."""
    def __init__(self) -> None:
        """Initialize the class."""
        self.full_accuracy_report_path = "llm_report/accuracy_test_reports.jsonl"

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

    def measure_cohen_kappa(self, human_path_1: str, human_path_2: str) -> None:
        """Calculate the inter-rater accuracy between human vs human, human vs llm.
        
        Args:
            human_path_1 (str): path to human evaluator 1 assessment file.
            human_path_2 (str): path to human evaluator 2 assessment file.
        """          
        # Read human evaluators assessments
        with open(human_path_1, "r", encoding="utf-8") as file_1:
            human_assessment_1 = json.load(file_1)
        with open(human_path_2, "r", encoding="utf-8") as file_2:
            human_assessment_2 = json.load(file_2)
        # Read LLM evaluator assessment
        try:
            with open(self.full_accuracy_report_path, 'r', encoding='utf-8') as file:
                llm_report = [json.loads(line) for line in file]
        except FileNotFoundError:
            print(f"File not found: {self.full_accuracy_report_path}")
            return
        # Collect list of human assessment
        human_assessment_list_1 = []
        human_assessment_list_2 = []
        for hi_1, _ in human_assessment_1.items():
            human_assessment_list_1.append(human_assessment_1[hi_1].get("assessment"))
            human_assessment_list_2.append(human_assessment_2[hi_1].get("assessment"))
        print(f"len(human_assessment_list_1) = {len(human_assessment_list_1)}")
        print(f"len(human_assessment_list_2) = {len(human_assessment_list_2)}")
        
        # Collect list of LLM assessment
        llm_assessment_list = []
        for index, human_report in human_assessment_1.items():
            question = human_report.get("question")
            for l_report in llm_report:
                if l_report.get("question") == question:
                    llm_assessment_list.append(str(l_report.get("assessment")).lower())
                    break
        print(f"len(llm_assessment_list) = {len(llm_assessment_list)}")

        # Calculate human vs human inter-rater
        human_human_kappa = cohen_kappa_score(human_assessment_list_1, human_assessment_list_2)
        print(f"Human vs Human inter-rater consistency - Cohen Kappa: {human_human_kappa:.4f}")

        # Calculate human 1 vs llm inter-rater
        human_llm_kappa_1 = cohen_kappa_score(human_assessment_list_1, llm_assessment_list)
        print(f"Human 1 vs LLM inter-rater consistency - Cohen Kappa: {human_llm_kappa_1:.4f}")

        # Calculate human 2 vs llm inter-rater
        human_llm_kappa_2 = cohen_kappa_score(human_assessment_list_2, llm_assessment_list)
        print(f"Human 2 vs LLM inter-rater consistency - Cohen Kappa: {human_llm_kappa_2:.4f}")

    def compare_human_llm_assessment(self, human_path_1: str, human_path_2: str) -> None:
        """Compare the assessments made by LLM with the assessments made by human evaluators.
        
        Args:
            human_path_1 (str): path to human evaluator 1 assessment.
            human_path_2 (str): path to human evaluator 2 assessment.
        """
        # Read human evaluators assessments
        with open(human_path_1, "r", encoding="utf-8") as file_1:
            human_assessment_1 = json.load(file_1)
        with open(human_path_2, "r", encoding="utf-8") as file_2:
            human_assessment_2 = json.load(file_2)
        # Read LLM evaluator assessment
        try:
            with open(self.full_accuracy_report_path, 'r', encoding='utf-8') as file:
                llm_report = [json.loads(line) for line in file]
        except FileNotFoundError:
            print(f"File not found: {self.full_accuracy_report_path}")
            return
        
        # Variables to count the number of time they have the same and different assessment
        same_1 = 0
        different_1= 0
        same_2 = 0
        different_2= 0

        # Variable to store the discrepancies cases
        discrepancy_1 = {}
        discrepancy_2 = {}

        # Compare human evaluator 1 assessment with LLM
        for idx, assess_1 in human_assessment_1.items():
            question = assess_1.get("question")
            # Compare if same index have same question
            if question == llm_report[int(idx)].get("question"):
                # Check if they have the same assessment
                if assess_1.get("assessment") == str(llm_report[int(idx)].get("assessment")).lower():
                    same_1 += 1
                else:
                    different_1 += 1
                    discrepancy_1[idx] = {
                        "question": question,
                        "human assessment": assess_1.get("assessment"),
                        "llm assessment": llm_report[int(idx)].get("assessment")
                    }
            else:
                print(f"WARNING: there is something wrong with the order. Questions in {idx} are different.")
        
        # Compare human evaluator 2 assessment with LLM
        for idx, assess_2 in human_assessment_2.items():
            question = assess_2.get("question")
            # Compare if same index have same question
            if question == llm_report[int(idx)].get("question"):
                # Check if they have the same assessment
                if assess_2.get("assessment") == str(llm_report[int(idx)].get("assessment")).lower():
                    same_2 += 1
                else:
                    different_2 += 1
                    discrepancy_2[idx] = {
                        "question": question,
                        "human assessment": assess_2.get("assessment"),
                        "llm assessment": llm_report[int(idx)].get("assessment")
                    }
            else:
                print(f"WARNING: there is something wrong with the order. Questions in {idx} are different.")

        # Visualize the data
        print(f"Evaluator 1 vs LLM:\nSame: {same_1}\nDifferent: {different_1}")
        print(f"Evaluator 2 vs LLM:\nSame: {same_2}\nDifferent: {different_2}")

        # Save the discrepancies cases to a file
        with open("accuracy_human_llm_discrepancies_1.json", "w", encoding="utf-8") as file:
            json.dump(discrepancy_1, file, ensure_ascii=False, indent=4)
        print("Saved discrepancies to file: accuracy_human_llm_discrepancies_1.json")

        with open("accuracy_human_llm_discrepancies_2.json", "w", encoding="utf-8") as file:
            json.dump(discrepancy_2, file, ensure_ascii=False, indent=4)
        print("Saved discrepancies to file: accuracy_human_llm_discrepancies_2.json")


class AttackExperiment:
    """This is the program to analyze the prompt attack experiment data."""
    
    def __init__(self) -> None:
        self.llm_attack_report_path = "llm_report/attack_test_reports.jsonl"
    
    def create_human_experiment_form(self):
        """Hide LLM assessment and ask human to assess chatbot whether it is vulnerable to prompt attacks."""
        try:
            with open(self.llm_attack_report_path, 'r', encoding='utf-8') as file:
                full_report = [json.loads(line) for line in file]
        except FileNotFoundError:
            print(f"File not found: {self.llm_attack_report_path}")
            return
        
        attack_data_dict = {}
        for i, data_dict in enumerate(full_report):
            attack_data_dict[i] = {
                "type of attack": data_dict.get("type of attack"),
                "attack prompt": data_dict.get("attack prompt"),
                "chatbot response": data_dict.get("chatbot response"),
                "is success": ""
            }

        output_paths = []
        for i in range(2):
            output_paths.append(f"human_experiment_attack_{i + 1}.json")
        
        for op in output_paths:
            with open(op, 'w', encoding='utf-8') as file:
                json.dump(attack_data_dict, file, ensure_ascii=False, indent=4)
    
    def find_empty_answer(self, file_path: str) -> None:
        """Check if there are any cases that human evaluator skipped.
        
        Args:
            file_path (str): path to human evaluator file.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            human_assessment = json.load(file)
        
        miss_num = 0
        for idx, assessment in human_assessment.items():
            if assessment.get("is success").strip() == "":
                print(f"The Evalutor missed this case: {assessment.get("attack prompt")}")
                miss_num += 1
        
        print(f"The number of assessment missed: {miss_num}")
    
    def compare_human_assessment(self, file_path_1: str, file_path_2: str) -> None:
        """Compare the human evaluator assessments and write the discrepancy case into a file.
        
        Args:
            file_path_1 (str): the path to evaluator 1 assessment report.
            file_path_2 (str): the path to evaluator 2 assessment report.
        """
        # Read the evaluators' assessment reports
        with open(file_path_1, "r", encoding="utf-8") as file_1:
            human_assessment_1 = json.load(file_1)
        with open(file_path_2, "r", encoding="utf-8") as file_2:
            human_assessment_2 = json.load(file_2)
        
        # Search for the discrepancies
        discrepancy_dict = {}
        for idx, assess_1 in human_assessment_1.items():
            attack_prompt = assess_1.get("attack prompt")
            if attack_prompt == human_assessment_2[idx].get("attack prompt"):
                # Check if the assessment is the same
                if assess_1.get("is success").strip() != human_assessment_2[idx].get("is success").strip():
                    discrepancy_dict[idx] = {
                        "attack prompt": attack_prompt,
                        "chatbot response": assess_1.get("chatbot response"),
                        "evaluator 1 assessment": assess_1.get("is success"),
                        "evaluator 2 assessment": human_assessment_2[idx].get("is success"),
                        "which correct": ""
                    }
            else:
                print(f"WARNING: something with the attack order. Why attack {idx} are different between evaluators?")
        
        # Visualize the difference
        print(f"The number of discrepancies: {len(discrepancy_dict.values())}")

        # Save the discrepancies into a file
        if len(discrepancy_dict.values()) > 0:
            output_path = "attack_evaluators_discrepancies.json"
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(discrepancy_dict, file, ensure_ascii=False, indent=4)
            print(f"Saved the discrepancies into: {output_path}")
    
    def create_correct_assessment(self, file_path_1: str, file_path_2: str, discrepancy_path: str) -> None:
        """Create a correct assessment as the one that both human evaluators agree.
        
        Args:
            file_path_1 (str): the path to human 1 assessment report.
            file_path_2 (str): the path to human 2 assessment report.
            discrepancy_path (str): the path to the file storing cases that 2 evaluators give different assessment.
        """
        # Read the evaluators' assessment reports
        with open(file_path_1, "r", encoding="utf-8") as file_1:
            human_assessment_1 = json.load(file_1)
        with open(file_path_2, "r", encoding="utf-8") as file_2:
            human_assessment_2 = json.load(file_2)
        # Read the discrepancies report
        with open(discrepancy_path, "r", encoding="utf-8") as file_3:
            discrepancy_dict = json.load(file_3)
        
        # Track the accuracy of human evaluators
        accuracy_1 = 0
        accuracy_2 = 0

        # Store the correct assessment for each case
        correct_assessment_dict = {}
        # Loop through each attack case
        for idx, assess_1 in human_assessment_1.items():
            correct_assessment_dict[idx] = {
                "attack prompt": human_assessment_2[idx].get("attack prompt"),
                "chatbot response": human_assessment_2[idx].get("chatbot response"),
            }
            if assess_1.get("attack prompt") == human_assessment_2[idx].get("attack prompt"):
                if assess_1.get("is success").strip() == human_assessment_2[idx].get("is success").strip():
                    accuracy_1 += 1
                    accuracy_2 += 1
                    # Store the correct assessment in the dict
                    correct_assessment_dict[idx]["is success"] = assess_1.get("is success")
                else:
                    # Read the final result of discussion for discrepancies cases
                    which_correct = discrepancy_dict[idx].get("which correct")
                    if which_correct == "1":
                        accuracy_1 += 1
                        correct_assessment_dict[idx]["is success"] = assess_1.get("is success")
                    else:
                        accuracy_2 += 1
                        correct_assessment_dict[idx]["is success"] = human_assessment_2[idx].get("is success")
            else:
                print(f"WARNING: something with the attack order. Why attack {idx} are different between evaluators?")
        
        # Print the human accuracy
        accuracy_rate_1 = accuracy_1 / len(human_assessment_1.items())
        print(f"Evaluator 1 accuracy: {accuracy_1} / {len(human_assessment_1.items())} = {accuracy_rate_1:.4f}")

        accuracy_rate_2 = accuracy_2 / len(human_assessment_2.items())
        print(f"Evaluator 2 accuracy: {accuracy_2} / {len(human_assessment_2.items())} = {accuracy_rate_2:.4f}")

        # Save the correct answer to a file
        output_path = "attack_correct_assessment.json"
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(correct_assessment_dict, file, ensure_ascii=False, indent=4)       
        print(f"Saved the correct assessment into a file: {output_path}")
    
    def calculate_llm_accuracy(self, correct_assessment_path: str) -> None:
        """Calculate llm accuracy overall and over each attack classes.
        
        Args:
            correct_assessment_path (str): the path to the file storing correct assessment
        """
        # Read the correct assessment
        with open(correct_assessment_path, "r", encoding="utf-8") as file_1:
            correct_assessment = json.load(file_1)
        # Read LLM report
        try:
            with open(self.llm_attack_report_path, 'r', encoding='utf-8') as file:
                llm_report = [json.loads(line) for line in file]
        except FileNotFoundError:
            print(f"File not found: {self.llm_attack_report_path}")
            return
        
        # Count the time llm give correct answer
        accurate = 0
        prompt_injection_accuracy = 0
        prompt_leaking_accuracy = 0
        jailbreaking_accuracy = 0

        prompt_injection_attack = 0
        prompt_leaking_attack = 0
        jailbreaking_attack = 0

        # Variable to store llm wrong assessment cases
        wrong_case_dict = {}

        # Loop through each attack case
        for idx, llm_r in enumerate(llm_report):
            # Check if the same index corresponds to the same attack prompts
            if llm_r.get("attack prompt").strip() == correct_assessment[f"{idx}"].get("attack prompt").strip():
                # Check if it is prompt injection, prompt leaking, or jailbreaking attack
                attack_type = llm_r.get("type of attack")
                if attack_type == "prompt injection":
                    prompt_injection_attack += 1
                elif attack_type == "prompt leaking":
                    prompt_leaking_attack += 1
                elif attack_type == "jailbreaking":
                    jailbreaking_attack += 1
                else:
                    print(f"Strang attack type: {attack_type}")

                # Check if llm give correct assessment
                if str(llm_r.get("is success")).lower() == correct_assessment[f"{idx}"].get("is success"):
                    accurate += 1
                    # Update each class accuracy
                    if attack_type == "prompt injection":
                        prompt_injection_accuracy += 1
                    elif attack_type == "prompt leaking":
                        prompt_leaking_accuracy += 1
                    elif attack_type == "jailbreaking":
                        jailbreaking_accuracy += 1
                    else:
                        print(f"Strang attack type: {attack_type}")
                else:
                    # Store wrong case:
                    wrong_case_dict[idx] = {
                        "attack prompt": llm_r.get("attack prompt"),
                        "chatbot response": llm_r.get("chatbot response"),
                        "llm assessment": llm_r.get("is success"),
                        "correct assessment": correct_assessment[f"{idx}"].get("is success")
                    }
            else:
                print(f"WARNING: something with the attack order. Why attack {idx} are different?")
        
        # Visualize the result
        accuracy_rate = accurate / len(llm_report)
        print(f"LLM attack assessment accuracy: {accurate} / {len(llm_report)} = {accuracy_rate:.4f}")

        # Print each class accuracy
        # Prompt injection
        prompt_injection_accuracy_rate = prompt_injection_accuracy / prompt_injection_attack
        print(f"LLM prompt injection attack assessment accuracy: {prompt_injection_accuracy} / {prompt_injection_attack} = {prompt_injection_accuracy_rate:.4f}")
        # Prompt leaking
        prompt_leaking_accuracy_rate = prompt_leaking_accuracy / prompt_leaking_attack
        print(f"LLM prompt leaking attack assessment accuracy: {prompt_leaking_accuracy} / {prompt_leaking_attack} = {prompt_leaking_accuracy_rate:.4f}")
        # Jailbreaking
        jailbreaking_accuracy_rate = jailbreaking_accuracy / jailbreaking_attack
        print(f"LLM jailbreaking attack assessment accuracy: {jailbreaking_accuracy} / {jailbreaking_attack} = {jailbreaking_accuracy_rate:.4f}")
        # Add all the classes accuracy into a list
        class_accuracies = [
            prompt_injection_accuracy_rate, prompt_leaking_accuracy_rate, jailbreaking_accuracy_rate
        ]

        # Save the wrong cases into a file
        output_path = "llm_attack_wrong_cases.json"
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(wrong_case_dict, file, ensure_ascii=False, indent=4)       
        print(f"Saved LLM wrong cases into a file: {output_path}")
        return class_accuracies

    
    def calculate_llm_per_class_variance(self, class_accuracies: list[float]) -> None:
        """Calculate the variance in accuracy between classes.
        
        Args:
            class_accuracies (list[float]): a list stores the accuracy rate of each class.
        """
        # Calculate standard deviation
        sd = np.std(class_accuracies)

        # Calculate interquartile range
        q75, q25 = np.percentile(class_accuracies, [75 ,25])
        iqr = q75 - q25

        # Calculate the mean
        mean = np.mean(class_accuracies)

        # Calculate median
        median = statistics.median(class_accuracies)   

        # Visualize the calculated statistics
        print(f"Standard deviation: {sd:.4f}")
        print(f"Interquartile range: {iqr:.4f}")
        print(f"Mean: {mean:.4f}")
        print(f"Median: {median:.4f}")
    
    def measure_cohen_kappa(self, human_path_1: str, human_path_2: str) -> None:
        """Calculate the inter-rater accuracy between human vs human, human vs llm.
        
        Args:
            human_path_1 (str): path to human evaluator 1 assessment file.
            human_path_2 (str): path to human evaluator 2 assessment file.
        """          
        # Read human evaluators assessments
        with open(human_path_1, "r", encoding="utf-8") as file_1:
            human_assessment_1 = json.load(file_1)
        with open(human_path_2, "r", encoding="utf-8") as file_2:
            human_assessment_2 = json.load(file_2)
        # Read LLM evaluator assessment
        try:
            with open(self.llm_attack_report_path, 'r', encoding='utf-8') as file:
                llm_report = [json.loads(line) for line in file]
        except FileNotFoundError:
            print(f"File not found: {self.llm_attack_report_path}")
            return
        # Collect list of human assessment
        human_assessment_list_1 = []
        human_assessment_list_2 = []
        for hi_1, _ in human_assessment_1.items():
            human_assessment_list_1.append(human_assessment_1[hi_1].get("is success"))
            human_assessment_list_2.append(human_assessment_2[hi_1].get("is success"))
        print(f"len(human_assessment_list_1) = {len(human_assessment_list_1)}")
        print(f"len(human_assessment_list_2) = {len(human_assessment_list_2)}")
        
        # Collect list of LLM assessment
        llm_assessment_list = []
        for index, human_report in human_assessment_1.items():
            attack_prompt = human_report.get("attack prompt")
            for l_report in llm_report:
                if l_report.get("attack prompt") == attack_prompt:
                    llm_assessment_list.append(str(l_report.get("is success")).lower())
                    break
        print(f"len(llm_assessment_list) = {len(llm_assessment_list)}")

        # Calculate human vs human inter-rater
        human_human_kappa = cohen_kappa_score(human_assessment_list_1, human_assessment_list_2)
        print(f"Human vs Human inter-rater consistency - Cohen Kappa: {human_human_kappa:.4f}")

        # Calculate human 1 vs llm inter-rater
        human_llm_kappa_1 = cohen_kappa_score(human_assessment_list_1, llm_assessment_list)
        print(f"Human 1 vs LLM inter-rater consistency - Cohen Kappa: {human_llm_kappa_1:.4f}")

        # Calculate human 2 vs llm inter-rater
        human_llm_kappa_2 = cohen_kappa_score(human_assessment_list_2, llm_assessment_list)
        print(f"Human 2 vs LLM inter-rater consistency - Cohen Kappa: {human_llm_kappa_2:.4f}")



if __name__ == "__main__":
    accuracy_experiment = AccuracyExperiment()
    # accuracy_experiment.create_experiment_form_round_1(is_accuracy=False)

    # accuracy_experiment.change_jsonl_to_json("old_experiment/human_vs_chatbot_comparison_1.jsonl")

    # accuracy_experiment.find_empty_answers("filled_form/human_experiment_second_round_2.json")

    # accuracy_experiment.create_experiment_form_round_2()

    # accuracy_experiment.compare_human_assessment(
    #     "filled_form/human_experiment_second_round_1.json",
    #     "filled_form/human_experiment_second_round_2.json"
    # )

    # accuracy_experiment.create_accurate_assessment(
    #     "filled_form/human_experiment_second_round_1.json",
    #     "filled_form/human_experiment_second_round_2.json",
    #     "filled_form/second_round_discrepancies.json"
    # )

    # accuracy_experiment.calculate_llm_accuracy(
    #     "filled_form/correct_assessment.json"
    # )

    # accuracy_experiment.measure_cohen_kappa(
    #     "filled_form/human_experiment_second_round_1.json",
    #     "filled_form/human_experiment_second_round_2.json",       
    # )

    accuracy_experiment.compare_human_llm_assessment(
        "filled_form/human_experiment_second_round_1.json",
        "filled_form/human_experiment_second_round_2.json"
    )

    attack_experiment = AttackExperiment()

    # attack_experiment.create_human_experiment_form()

    # attack_experiment.find_empty_answer(
    #     "filled_form/human_experiment_attack_2.json"
    # )

    # attack_experiment.compare_human_assessment(
    #     "filled_form/human_experiment_attack_1.json",
    #     "filled_form/human_experiment_attack_2.json"
    # )

    # attack_experiment.create_correct_assessment(
    #     "filled_form/human_experiment_attack_1.json",
    #     "filled_form/human_experiment_attack_2.json",
    #     "filled_form/attack_evaluators_discrepancies.json"
    # )

    # class_accuracies = attack_experiment.calculate_llm_accuracy(
    #     "filled_form/attack_correct_assessment.json"
    # )

    # attack_experiment.calculate_llm_per_class_variance(class_accuracies)

    # attack_experiment.measure_cohen_kappa(
    #     "filled_form/human_experiment_attack_1.json",
    #     "filled_form/human_experiment_attack_2.json"
    # )
