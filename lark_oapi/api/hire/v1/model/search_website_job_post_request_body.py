# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class SearchWebsiteJobPostRequestBody(object):
    _types = {
        "job_type_id_list": List[str],
        "city_code_list": List[str],
        "job_function_id_list": List[str],
        "subject_id_list": List[str],
        "keyword": str,
        "update_start_time": str,
        "update_end_time": str,
        "create_start_time": str,
        "create_end_time": str,
    }

    def __init__(self, d=None):
        self.job_type_id_list: Optional[List[str]] = None
        self.city_code_list: Optional[List[str]] = None
        self.job_function_id_list: Optional[List[str]] = None
        self.subject_id_list: Optional[List[str]] = None
        self.keyword: Optional[str] = None
        self.update_start_time: Optional[str] = None
        self.update_end_time: Optional[str] = None
        self.create_start_time: Optional[str] = None
        self.create_end_time: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SearchWebsiteJobPostRequestBodyBuilder":
        return SearchWebsiteJobPostRequestBodyBuilder()


class SearchWebsiteJobPostRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._search_website_job_post_request_body = SearchWebsiteJobPostRequestBody()

    def job_type_id_list(self, job_type_id_list: List[str]) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.job_type_id_list = job_type_id_list
        return self

    def city_code_list(self, city_code_list: List[str]) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.city_code_list = city_code_list
        return self

    def job_function_id_list(self, job_function_id_list: List[str]) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.job_function_id_list = job_function_id_list
        return self

    def subject_id_list(self, subject_id_list: List[str]) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.subject_id_list = subject_id_list
        return self

    def keyword(self, keyword: str) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.keyword = keyword
        return self

    def update_start_time(self, update_start_time: str) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.update_start_time = update_start_time
        return self

    def update_end_time(self, update_end_time: str) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.update_end_time = update_end_time
        return self

    def create_start_time(self, create_start_time: str) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.create_start_time = create_start_time
        return self

    def create_end_time(self, create_end_time: str) -> "SearchWebsiteJobPostRequestBodyBuilder":
        self._search_website_job_post_request_body.create_end_time = create_end_time
        return self

    def build(self) -> "SearchWebsiteJobPostRequestBody":
        return self._search_website_job_post_request_body
