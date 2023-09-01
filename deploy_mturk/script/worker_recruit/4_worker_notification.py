import os
import json
import random
import numpy as np
from mturk_cores import MTurkManager, print_log
from datetime import date
from datetime import datetime


def worker_filtering(worker_group_ids, results):
    all_worker_ids = np.hstack(worker_group_ids)

    submit_worker_ids = []
    for hit in results.values():
        for ans in hit['Answers']:
            submit_worker_ids.append(ans['WorkerID'])

    missed_workers = list(set(all_worker_ids).difference(set(submit_worker_ids)))
    return missed_workers



def main():


    # ===============================
    # step1: Parsing Configurations
    # ===============================
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "config.json"), "r") as read_file:
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
    # step3: Set WorkerIDs and Notification
    # ===============================
    """Recruited Workers
    """
    worker_group_file = "MTurk_WorkerGroup_Track.json"
    current_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_path, worker_group_file), "r") as read_file:
        recruited_worker_json_file = json.load(read_file)

    ### Select the worker group to notify ###
    worker_group_ids = [list(recruited_worker_json_file["3"]["WorkerIDs"])]        # Format - worker_group_ids = [["A26HDYGF38K5SG", "A26HDYGF38K5SG"]]

    ### Set the notifications
    Notification_subject = "Qualified HITs Ready for You (Increased Reweard) - [Title: Select the Paragraph Generated AI Machines?]"
    Notification_message =  """Thank you for taking our Qualification HIT! 
    We have doubled our rewards for both approved and ongoing HITs (by adding a post-hoc $0.2 bonus for each finished assignment).
    Please search the HIT title -- 'Select the Paragraph Generated AI Machines?' to find the HITs. 
    We're pleased to have you in our project evaluation and look foward to your more participation :).  Thank you!
    """


    # ===============================
    # step4: Notifying the Workers
    # ===============================
    response = client.notify_workers(
        Subject= Notification_subject,
        MessageText=Notification_message,
        WorkerIds=["A26HDYGF38K5SG"]
    )

    for worker_group in worker_group_ids:
        response = client.notify_workers(
            Subject= Notification_subject,
            MessageText=Notification_message,
            WorkerIds=worker_group
        )



if __name__ == '__main__':
    main()
