import os
# import sys
import json
import boto3
import logging
import pandas as pd


logging.basicConfig(level=logging.INFO)


class MTurkManager:
    """
    Manage MTurk operations.
    """

    def __init__(self, config):
        """
        MTurk Default Setting: Sandbox + reward = 0.00
        """
        self.mturk_env_config = config['mturk_env_config']
        self.worker_config = config['worker_config']
        self.hit_config = config['hit_config']
        self.save_hits = config['save_files']



    def set_environment(self):
        """
        Set environment with 'sandbox' as create_hits_in_live = False, and 'live' as True.
        """
        environments = {
                "live": {
                    "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
                    "preview": "https://www.mturk.com/mturk/preview",
                    "reward": self.mturk_env_config['reward']
                },
                "sandbox": {
                    "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
                    "preview": "https://workersandbox.mturk.com/mturk/preview",
                    "reward": self.mturk_env_config['reward']
                },
        }
        self.mturk_environment = environments["sandbox"] if self.mturk_env_config['sandbox_env'] else environments["live"]



    def setup_client(self, profile_name=None):
        """
        Setup a session and client for HITs.
        """
        session = boto3.Session(profile_name=profile_name,
                                aws_access_key_id = self.mturk_env_config['aws_access_key_id'],
                                aws_secret_access_key = self.mturk_env_config['aws_secret_access_key'],
                                )
        self.client = session.client(
            service_name='mturk',
            region_name='us-east-1',
            endpoint_url=self.mturk_environment['endpoint']
        )

        user_balance = self.client.get_account_balance()
        print(f"Your available balance is: ${user_balance['AvailableBalance']}")



    def create_per_hit(self, frontend_setting, QualificationRequirements):
        """
        Create HITs.
        """
        response = self.client.create_hit(Reward = 
                                            self.mturk_env_config['reward'], 
                                            QualificationRequirements = QualificationRequirements,
                                            Question = frontend_setting,
                                            **self.hit_config)

        hit_type_id = response['HIT']['HITTypeId']
        hit_id = response['HIT']['HITId'] 
        print_log("INFO", f" ====== Created HIT Successfully! ====== ")
        print_log("INFO", f" --- Created HIT_ID = {hit_id}")
        print_log("INFO", f" --- You can work HIT at: {self.mturk_environment['preview']}?groupId={hit_type_id}")
        return response 
        


    def save_per_hit_result(self, response, status=["Submitted", "Approved"], save_hit=True, approve_hit=True):
        """
        Save per created HIT result for retrieve to 'create_hits.csv'
        """

        hit_id = response['HIT']['HITId']
        assignments_response = self.client.list_assignments_for_hit(
            HITId=hit_id,
            AssignmentStatuses=[status] if type(status) == str else status
            )

        for r in assignments_response["Assignments"]:
            r["SubmitTime"] = str(r["SubmitTime"])
            r["AcceptTime"] = str(r["AcceptTime"])
            r["AutoApprovalTime"] = str(r["AutoApprovalTime"])
            if "ApprovalTime" in r:
                r["ApprovalTime"] = str(r["ApprovalTime"])

            # # This won't be saved but kept for potential use.
            # created_hit = {
            #     "HITId": response['HIT']['HITId'],
            #     'HIT_TYPE_ID': response['HIT']['HITTypeId'],
            #     'WORK_LINK': self.mturk_environment['preview'] + f"?groupId={response['HIT']['HITTypeId']}",
            #     'RESULT_LINK': self.mturk_environment['manage']
            # }

        if save_hit:

            if not os.path.exists(self.save_hits['save_dir']):
                os.makedirs(self.save_hits['save_dir']) 


            if self.save_hits['save_type'] == "csv":
                save_dir = os.path.join(self.save_hits['save_dir'], f'result_hit_{hit_id}.csv')
                df = pd.DataFrame(assignments_response["Assignments"], columns = ['HIT_ID', 'HIT_TYPE_ID', 'WORK_LINK', 'RESULT_LINK'])
                df.to_csv(save_dir, index=False)

            elif self.save_hits['save_type'] == "json":
                save_dir = os.path.join(self.save_hits['save_dir'], f'result_hit_{hit_id}.json')
                with open(save_dir, 'w', encoding='utf-8') as outfile:
                    json.dump(assignments_response["Assignments"], outfile, indent=4)




def print_log(loglevel, message, should_print=False):
    """
    Five Logging Levels:
        - 1-logging.DEBUG: Detailed information, typically of interest only when diagnosing problems.
        - 2-logging.INFO: Confirmation that things are working as expected.
        - 3-logging.WARNING: An indication that something unexpected happened, or some problem in the near future.
        - 4-logging.ERROR: Due to a more serious problem, the software has not been able to perform some function.
        - 5-logging.CRITICAL: A serious error, indicating that the program itself may be unable to continue running.

    When the code is specified Logging Level, all >= levels logging will be printed.
    """
    logging.log(getattr(logging, loglevel.upper()), message)
    if should_print:
        print(message)
