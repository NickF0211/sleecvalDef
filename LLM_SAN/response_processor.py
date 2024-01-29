import copy
import json
import re

from inference_rules import parse_and_process, parse_and_refine, get_all_relations_str, get_all_relations, get_summary, \
    get_compare_result

pattern = r'\[.*\]'


def extract_substrings_with_special_chars(s):
    """
    Extract all substrings that are enclosed in square brackets, including the brackets,
    and allow special characters like newline.

    :param s: The input string.
    :return: A list of substrings enclosed in square brackets.
    """
    # Regular expression to find substrings within square brackets, including special characters
    pattern = r'\[.*?\]'
    return re.findall(pattern, s, re.DOTALL)


def parse_list(all_contents):
    results = []
    for content_list in all_contents:
        local_result = json.loads(content_list)
        results.extend(local_result)

    return results


def process_response(response_txt, case_study_title="example", output=""):
    all_content = extract_substrings_with_special_chars(response_txt)
    parsed_result = parse_list(all_content)
    if output:
        output_dict = {"name": case_study_title, "relations": parsed_result}
        with open(output, 'w') as out:
            json.dump(output_dict, out, indent=4)

    new_relations, test_cases = parse_and_process(parsed_result)
    for test_case in test_cases:
        print(test_case.prompt_questions())

    return parsed_result, new_relations, test_cases


def process_response_file(filename, case_study_title="example", output=""):
    with open(filename, 'r') as f:
        content = f.read()
        parsed_result, relations, test_cases = process_response(content, case_study_title=case_study_title,
                                                                output=output)
        return parsed_result, relations, test_cases

    return None


def print_stats(filename):
    with open(filename, 'r') as f:
        results = json.load(f)
        get_summary(results)

def compare_stats(raw, new):
    with open(raw, 'r') as raw_f:
        with open(new, 'r') as new_f:
            raw_results = json.load(raw_f)
            new_results = json.load(new_f)
            get_compare_result(raw_results, new_results)


def refine_relationship_file(relations, filename, case_study_title="example", output="", old_relation= None):
    with open(filename, 'r') as f:
        content = f.read()
        parsed_result, relations, test_cases = refine_relationship(relations, content,
                                                                   case_study_title=case_study_title,
                                                                   output=output, old_relation=old_relation)
        return parsed_result, relations, test_cases

    return None


def refine_relationship(old_relations, response_txt, case_study_title="example", output="", old_relation=None):
    all_content = extract_substrings_with_special_chars(response_txt)
    parsed_result = parse_list(all_content)

    new_relations, test_cases = parse_and_refine(old_relations, parsed_result)
    for test_case in test_cases:
        print(test_case.prompt_questions())

    if output:
        output_dict = {"name": case_study_title, "relations": get_all_relations(new_relations, old_relation)}
        with open(output, 'w') as out:
            json.dump(output_dict, out, indent=4)

    return parsed_result, new_relations, test_cases


if __name__ == "__main__":
    _, r, test_cases = process_response_file("Tabiat_group1/first_response.txt", "Tabiat",
                                             "Tabiat_group1/first_result.text")
    old_test = copy.deepcopy(test_cases)
    old_r = copy.deepcopy(r)
    _, r, test_cases = refine_relationship_file(r, "Tabiat_group1/second_response.txt", output="Tabiat_group1/second_result.text", old_relation=old_r)
    print("*" * 100)
    print(test_cases.intersection(old_test))
    assert (not test_cases.intersection(old_test))
    # _, r, test_cases = refine_relationship_file(r, "Tabiat_group2_mannual/third_response.text", output="Tabiat_group2_mannual/third_result.text", old_relation=old_r)

    print(get_all_relations_str(r))
    # with open("caseStudies/DressingAssist/first_response.txt", 'r') as fr:
    #     content = fr.read()
    #     _, relations, _ = process_response(content, "DressingAssist", "caseStudies/DressingAssist/relation.json")
    #     with open("caseStudies/DressingAssist/second_response.txt", 'r') as sr:
    #         content = sr.read()
    #         _, relations, _ = refine_relationship(relations, content, "DAISY", "caseStudies/DressingAssist/relation.json")

    #
    # caseStudies = ["ALMI", "ASPEN", "autoCar", "BSN", "CSI", "DAISY", "DressingAssist", "GDPR", "safecade"]
    # for case in caseStudies:
    #     _, r, test_cases = process_response_file("caseStudies/{}/response.txt".format(case), case,
    #                                              "caseStudies/{}/processed_results".format(case))
    #
    #     print("case study: {}".format(case))
    #     print("raw result")
    #     old_file = "caseStudies/{}/processed_results".format(case)
    #     new_file = "caseStudies/{}/relation.json".format(case)
    #     print_stats(old_file)
    #     print("san result")
    #     print_stats(new_file)
    #     compare_stats(old_file, new_file)
    #     print("*"*100)

