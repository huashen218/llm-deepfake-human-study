import os
import json
import argparse
import xmltodict
import numpy as np
from mturk_cores import MTurkManager, print_log


def main(args):

    # ===============================
    # step1: Parsing Configurations
    # ===============================
    current_dir = os.path.dirname(os.path.realpath(__file__))
    html_file_dir = os.path.join(current_dir, "recruit_template.html")

    """
    To test HIT in sandbox, set args.test_hit = True (default);
    If post HIT for production, please set args.test_hit = False.
    """
    config_dir = os.path.join(current_dir, "config.json")

    with open(config_dir, "r") as read_file:
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
    # step3: Retrieve Results and Save
    # ===============================
    result_id = "12_05_2022_23_56"   # This result_id should be identical to the date_time in `main_create_hit.py`
    save_results_dir = os.path.join(current_dir, f"recruit_participants_production_{result_id}.json")
    with open(save_results_dir, "r") as read_file:
        result_ids = json.load(read_file)
    result_json_file_dir = os.path.join(current_dir, f"MTurk_results_{result_id}.json")



    item = result_ids['worker_recruiting'][0]

    hit = client.get_hit(HITId=item['hit_id'])
    assignmentsList = client.list_assignments_for_hit(
        HITId=item['hit_id'],
        AssignmentStatuses=['Submitted', 'Approved'],  # 
        MaxResults=100
    )

    ### If recruit more than 100 workers, uncomment below.
    assignmentsList_over100 = client.list_assignments_for_hit(
        HITId=item['hit_id'],
        NextToken = assignmentsList['NextToken'],
        AssignmentStatuses=['Submitted', 'Approved'],  # 
        MaxResults=100
    )
    
    ### If recruit more than 100 workers, uncomment below.
    assignmentsList_over200 = client.list_assignments_for_hit(
        HITId=item['hit_id'],
        NextToken = assignmentsList_over100['NextToken'],
        AssignmentStatuses=['Submitted', 'Approved'],  # 
        MaxResults=100
    )
    
    assignments = assignmentsList['Assignments'] + assignmentsList_over100['Assignments'] + assignmentsList_over200['Assignments']



    # assignments = assignmentsList['Assignments']
    item['assignments_submitted_count'] = len(assignments)
    print(f" ### No.0: HIT={hit['HIT']['HITId']}; Submitted Assignments Number = {item['assignments_submitted_count']} ### ")
    

    ground_label = "Negative"
    all_results = {}
    all_results[hit['HIT']['HITId']] = {}

    answers = []   # All Answer for 1 HIT.
    correct_workers = []
    for assignment in assignments:
        each_answer = {}
        each_answer["WorkerID"] = assignment['WorkerId']
        each_answer["AssignmentId"] = assignment['AssignmentId']

        answer_dict = xmltodict.parse(assignment['Answer'])
        answer = answer_dict['QuestionFormAnswers']['Answer']

        ### Worker get correct results.
        # if answer[-2]['FreeText'] == ground_label:
        #     correct_workers.append(assignment['WorkerId'])
        correct_workers.append(assignment['WorkerId'])

        for ans in answer:
            each_answer[ans['QuestionIdentifier']] = ans['FreeText']
        answers.append(each_answer)

        # Approve the Assignment (if it hasn't been already)
        if assignment['AssignmentStatus'] == 'Submitted':
            client.approve_assignment(
                AssignmentId=assignment['AssignmentId'],
                OverrideRejection=False
            )


    all_results[hit['HIT']['HITId']]["Answers"] = answers
    all_results[hit['HIT']['HITId']]["Correct_Workers"] = correct_workers
    with open(result_json_file_dir, 'w') as json_file:
        json.dump(all_results, json_file, indent = 2)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_hit', action='store_true', dest='test_hit', default=True)
    args = parser.parse_args()
    main(args)



