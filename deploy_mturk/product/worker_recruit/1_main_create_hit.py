import os
import json
import random
import argparse
import numpy as np
from mturk_cores import MTurkManager, print_log
from datetime import datetime



def load_frontend_setting(html_url):
    html_layout = open(html_url, 'r').read()
    QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
            <HTMLContent><![CDATA[{}]]></HTMLContent>
            <FrameHeight>800</FrameHeight>
            </HTMLQuestion>"""
    question_xml = QUESTION_XML.format(html_layout)
    return question_xml




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
    # step3: MTurk Tasks  --- Create HIT & Save Info
    # ===============================
    frontend_setting = load_frontend_setting(html_file_dir)
    QualificationRequirement = config['worker_config']['worker_requirements']
    print_log("INFO", f" ====== Display Worker Requirements ====== \n{QualificationRequirement}")
    response = mturk_manager.create_per_hit(frontend_setting, QualificationRequirement)
    

    results = {}
    results['worker_recruiting'] = []
    results['worker_recruiting'].append({
        'hit_id': response['HIT']['HITId'],
        'config': config
    })

    now = datetime.now()
    date_time = now.strftime("%d_%m_%Y_%H_%M")
    save_results_dir = os.path.join(current_dir, f"recruit_participants_production_{date_time}.json")
    with open(save_results_dir, 'w') as json_file:
        json.dump(results, json_file, indent = 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_hit', action='store_true', dest='test_hit', default=True)
    args = parser.parse_args()
    main(args)


