# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from .i18n import I18n
from .i18n import I18n
from .interview_assessment_dimension_args import InterviewAssessmentDimensionArgs


class InterviewAssessmentDimension(object):
    _types = {
        "id": str,
        "name": I18n,
        "description": I18n,
        "enabled": bool,
        "seq": int,
        "required": bool,
        "dimension_type": int,
        "args": InterviewAssessmentDimensionArgs,
    }

    def __init__(self, d):
        self.id: Optional[str] = None
        self.name: Optional[I18n] = None
        self.description: Optional[I18n] = None
        self.enabled: Optional[bool] = None
        self.seq: Optional[int] = None
        self.required: Optional[bool] = None
        self.dimension_type: Optional[int] = None
        self.args: Optional[InterviewAssessmentDimensionArgs] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "InterviewAssessmentDimensionBuilder":
        return InterviewAssessmentDimensionBuilder()


class InterviewAssessmentDimensionBuilder(object):
    def __init__(self, interview_assessment_dimension: InterviewAssessmentDimension = InterviewAssessmentDimension({})) -> None:
        self._interview_assessment_dimension: InterviewAssessmentDimension = interview_assessment_dimension
    
    def id(self, id: str) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.id = id
        return self
    
    def name(self, name: I18n) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.name = name
        return self
    
    def description(self, description: I18n) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.description = description
        return self
    
    def enabled(self, enabled: bool) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.enabled = enabled
        return self
    
    def seq(self, seq: int) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.seq = seq
        return self
    
    def required(self, required: bool) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.required = required
        return self
    
    def dimension_type(self, dimension_type: int) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.dimension_type = dimension_type
        return self
    
    def args(self, args: InterviewAssessmentDimensionArgs) -> "InterviewAssessmentDimensionBuilder":
        self._interview_assessment_dimension.args = args
        return self
    
    def build(self) -> "InterviewAssessmentDimension":
        return self._interview_assessment_dimension