import os
import json
import xmltodict
import numpy as np
from mturk_cores import MTurkManager, print_log
from datetime import datetime


def main():

    # ===============================
    # step1: Parsing Configurations
    # ===============================
    group = "group1"
    article_numbers, n = 50, 5  

    # version="v_select"
    # result_id = "13_05_2022_17_26"  # v_select

    version="v_write"
    result_id = "13_05_2022_17_32"   # v_write


    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

    current_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_path, "config.json"), "r") as read_file:
        config = json.load(read_file)
    print_log("INFO", f" ====== Display Your Configuration ====== \n{config}")

    ### Set bonus ###

    bonus = True
 
    bonus_path = os.path.join(current_path, f"{version}_{result_id}_bonus_record.json")
    if not os.path.exists(bonus_path):
        bonus_record = {}
    else:
        with open(bonus_path, "r") as read_file:
            bonus_record = json.load(read_file)



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

            ### hit_id
            # all_results[item['hit_id']] = {}

            ### hit_no.
            all_results[f'hit{i}'] = {}


            assignmentsList = client.list_assignments_for_hit(
                HITId=item['hit_id'],
                AssignmentStatuses=['Submitted', 'Approved'],
                MaxResults=100
            )

            # ## update_expiration_for_hit 
            # response = client.update_expiration_for_hit(
            #     HITId=item['hit_id'],
            #     ExpireAt= datetime(2022, 6, 20)
            # )


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

                print("assignment['AssignmentStatus']:", assignment['AssignmentStatus'])
                if assignment['AssignmentStatus'] == 'Submitted':

                    client.approve_assignment(
                        AssignmentId=assignment['AssignmentId'],
                        OverrideRejection=False
                    )

                if assignment['AssignmentStatus'] == 'Approved':
                    if bonus:
                        key = f"WorkerId={assignment['WorkerId']}-AssignmentId={assignment['AssignmentId']}"
                        if not key in bonus_record.keys():
                            response = client.send_bonus(
                                WorkerId=assignment['WorkerId'],
                                BonusAmount='0.2',
                                AssignmentId=assignment['AssignmentId'],
                                Reason='Bonus for joining and being approved in our HIT. Thanks!',
                                # UniqueRequestToken='hit-bonus'
                            )
                            bonus_record[f"WorkerId={assignment['WorkerId']}-AssignmentId={assignment['AssignmentId']}"] = "YES"
                            print(f"===Give bonus to WorkerId={assignment['WorkerId']} with AssignmentId={assignment['AssignmentId']}")
                        else:
                            print("===Already Exists!")
                            # exit()
            ### hit_id
            # all_results[item['hit_id']]["Answers"] = answers

            ### hit_no.
            all_results[f'hit{i}']["Answers"] = answers

    with open(result_json_file_dir, 'w') as json_file:
        json.dump(all_results, json_file, indent = 2)

    with open(bonus_path, 'w') as json_file:
        json.dump(bonus_record, json_file, indent = 2)

if __name__ == '__main__':
    main()

