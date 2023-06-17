import os
import json
import random
import numpy as np

from mturk_cores import *
from datetime import date
from datetime import datetime
import copy

# Process of custom html: https://blog.mturk.com/tutorial-mturk-using-python-in-jupyter-notebook-17ba0745a97f

# Tutorial: https://requester.mturk.com/developer?openid.pape.max_auth_age=43200&openid.identity=https%3A%2F%2Fwww.amazon.com%2Fap%2Fid%2Famzn1.account.AHE7YVOU4VMHEEDRA334DG323MUQ&stashKey=8b7e1ece-1e99-4399-8523-81cc292d63c5&openid.claimed_id=https%3A%2F%2Fwww.amazon.com%2Fap%2Fid%2Famzn1.account.AHE7YVOU4VMHEEDRA334DG323MUQ
# MTurk Developer: https://requester.mturk.com/developer
# Config Parameters: https://docs.aws.amazon.com/en_us/AWSJavaScriptSDK/v3/latest/clients/client-mturk/interfaces/createhitcommandinput.html#maxassignments
# MTurk API References: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/Welcome.html

# API Reference - QualificationRequirement: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html
# Developer Guide - Managing Workers: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/ManagingWorkers.html
# Tutorial: Creating a qualification requirement that requires workers be in a group: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/CustomQualTutorialGroup.html
# Tutorial: Creating a qualification type to exclude workers from selected tasks:     https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/CustomQualTutorialExclude.html
# CreateWorkerBlock: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_CreateWorkerBlockOperation.html;     https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#MTurk.Client.create_worker_block
# 



def load_frontend_setting(html_url):
    html_layout = open(html_url, 'r').read()
    QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
            <HTMLContent><![CDATA[{}]]></HTMLContent>
            <FrameHeight>800</FrameHeight>
            </HTMLQuestion>"""
    question_xml = QUESTION_XML.format(html_layout)
    return question_xml



def main():

    # ===============================
    # step1: Parsing Configurations
    # ===============================
    group = "group3"

    article_numbers, n = 50, 5

    # version="v_select"
    version="v_write"

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    html_folder = os.path.join(root_dir, "generate_hit_htmls", "htmls", group, version)
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
    # step3: MTurk Tasks  --- Create HIT
    # ===============================

    # """
    # Block Workers Who Have Seen the HITs
    # """
    # block_worker_lists = config['block_workers']
    # for worker in block_worker_lists:
    #     response = client.create_worker_block(
    #         WorkerId=worker["WorkerId"],
    #         Reason=worker["Reason"],
    #     )

    """
    Create HIT with Qualified Workers
    """

    hit_records = {}

    for i in range(0, article_numbers, n):

        QualificationRequirement = []
        QualificationRequirement = copy.deepcopy(config['worker_config']['worker_requirements'])
        QualificationRequirement.append(
                                {
                                "QualificationTypeId": "3P1HXW38ULCEVI3NPSSINSERGCRK55",
                                "Comparator": 'Exists',
                                "ActionsGuarded": 'DiscoverPreviewAndAccept'}
                                )

        hit_records[f'HITNumber{i}'] = []
        html_file_path = os.path.join(html_folder, f"{group}_hit{i}.html")
        print(f"=== HIT file path: {html_file_path}")
        frontend_setting = load_frontend_setting(html_file_path)
        response = mturk_manager.create_per_hit(frontend_setting, QualificationRequirement)

        hit_records[f'HITNumber{i}'].append({
            "hit_id": response['HIT']['HITId']
        })

    now = datetime.now()
    date_time = now.strftime("%d_%m_%Y_%H_%M")

    save_results_dir = os.path.join(current_path, f"MTurk_create_{date_time}_{version}.json")
    with open(save_results_dir, 'w') as json_file:
        json.dump(hit_records, json_file, indent = 2)


if __name__ == '__main__':
    main()
