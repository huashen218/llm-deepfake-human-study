import os
import json
import xmltodict
import numpy as np
from mturk_cores import MTurkManager, print_log



def main():

    # ===============================
    # step1: Parsing Configurations
    # ===============================
    group = "group2_new"

    article_numbers, n = 50, 3 

    version="v_select"
    # version="v_write"

    result_id = "14_05_2022_21_49"    # "v_select"
    # result_id = "24_04_2022_21_41"    # "v_write"

    

    current_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_path, "config.json"), "r") as read_file:
        config = json.load(read_file)
    print_log("INFO", f" ====== Display Your Configuration ====== \n{config}")


    # ===============================
    # step2: MTurkManager Client Setup
    # ===============================
    """
    client functions to view:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#MTurk.Client.create_worker_block
    """
    mturk_manager = MTurkManager(config)
    mturk_manager.set_environment()
    mturk_manager.setup_client()
    client = mturk_manager.client
    print(client.get_account_balance()['AvailableBalance'])



    # ===============================
    # step3: Retrieve and Approve MTurk Results
    # ===============================
    """
    Create HIT with Qualified Workers
    """
    ### The result_id is identical to the json file generated from 'create_hit_sandbox.py'

    with open(os.path.join(current_path, f"MTurk_create_{result_id}_{version}.json"), "r") as read_file:
        results = json.load(read_file)
    result_json_file_dir = os.path.join(current_path, f"MTurk_result_{result_id}_{version}.json")


    all_results = {}
    count = 0

    for i in range(0, article_numbers, n):
        batches = results[f'HITNumber{i}']
        for item in batches:

            count += 1
            hit = client.get_hit(HITId=item['hit_id'])
            all_results[item['hit_id']] = {}

            assignmentsList = client.list_assignments_for_hit(
                HITId=item['hit_id'],
                AssignmentStatuses=['Submitted', 'Approved'],
                MaxResults=100
            )

            assignments = assignmentsList['Assignments']
            item['assignments_submitted_count'] = len(assignments)
            print(f" ### No.{count}: HIT={item['hit_id']}; Submitted Assignments Number = {item['assignments_submitted_count']} ### ")
            

            answers = []
            for assignment in assignments:

                answer_dict = xmltodict.parse(assignment['Answer'])
                answer = answer_dict['QuestionFormAnswers']['Answer']
                each_answer = {}
                each_answer["WorkerID"] = assignment['WorkerId']
                for ans in answer:
                    each_answer[ans['QuestionIdentifier']] = ans['FreeText']
                answers.append(each_answer)

                if assignment['AssignmentStatus'] == 'Submitted':
                    client.approve_assignment(
                        AssignmentId=assignment['AssignmentId'],
                        OverrideRejection=False
                    )

            all_results[item['hit_id']]["Answers"] = answers

    with open(result_json_file_dir, 'w') as json_file:
        json.dump(all_results, json_file, indent = 2)


if __name__ == '__main__':
    main()

