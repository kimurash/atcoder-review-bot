import os
import logging
from random import choice

from dotenv import find_dotenv
from dotenv import load_dotenv
from notion_client import Client

# パッケージ内では暗黙的相対インポートが行われない
from api.routers.config import *


load_dotenv(find_dotenv())

class TaskSelector:
    FEEL_GOOD = '得意'
    FEEL_BAD  = '苦手'

    TOTAL_PRIORITY = 7

    def __init__(self, debug=False) -> None:
        self.client = Client(
            auth=os.getenv('NOTION_TOKEN'),
            log_level=(logging.DEBUG if debug
                       else logging.WARNING)
        )

    def get_prime_task(self):
        """
        出題する問題を取得する
        """
        cand_tasks = self.get_cand_tasks()
        task_group = self.prioritize_task(cand_tasks)
        prime_task = self.decide_task(task_group)

        return prime_task

    def get_cand_tasks(self):
        """
        全ての候補をNotionのDBから取得する
        """
        response = self.client.databases.query(
            # 辞書をキーワード引数として渡す
            **{
                'database_id': os.getenv('NOTION_DB_ID'),
                'filter': {
                    'and': [
                        {
                            'property': 'contest',
                            'select': {
                                'equals': 'ABC'
                            }
                        },
                        {
                            'or': [
                                {
                                    'property': 'diff',
                                    'select': {
                                        'equals': '灰'
                                    }
                                },
                                {
                                    'property': 'diff',
                                    'select': {
                                        'equals': '茶'
                                    }
                                },
                                {
                                    'property': 'diff',
                                    'select': {
                                        'equals': '緑'
                                    }
                                },
                            ]
                        }
                    ]
                }
            }
        )

        return response['results']
    
    def prioritize_task(self, cand_tasks: list[dict]):
        """
        問題を優先度別に分類する
        """
        task_group = [[] for _ in range(7)]
        for task in cand_tasks:
            task_group[self.get_priority(task)]\
            .append(task)
        
        return task_group

    def get_priority(self, page: dict):
        props = page['properties']
        feeling = props['feeling']['select']['name']
        result = props['result']['select']['name']

        if feeling == self.FEEL_GOOD:
            if result == AC:
                return 5
            elif result == ALMOST_AC:
                return 0
            elif result == CANNOT_AC:
                return 2
        elif feeling == self.FEEL_BAD:
            if result == AC:
                return 4
            elif result == ALMOST_AC:
                return 1
            elif result == CANNOT_AC:
                return 3
        else:
            return 6

    def decide_task(self, task_group: list[list]):
        """
        出題する問題を決定する
        """
        for group in task_group:
            if len(group) <= 0:
                continue
            
            return choice(group)
        else:
            return None
