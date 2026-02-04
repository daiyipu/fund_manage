"""
数据模型定义
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class User:
    """用户模型"""
    id: int
    username: str
    password_hash: str
    real_name: str
    email: Optional[str] = None
    role: str = 'viewer'
    department: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Project:
    """项目模型"""
    id: int
    project_code: str
    project_name: str
    fund_name: Optional[str] = None
    fund_manager: Optional[str] = None
    investment_amount: Optional[Decimal] = None
    investment_date: Optional[datetime] = None
    region: Optional[str] = None
    industry: Optional[str] = None
    project_stage: str = 'early'
    description: Optional[str] = None
    status: str = 'draft'
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ScoringDimension:
    """评分维度模型"""
    id: int
    dimension_code: str
    dimension_name: str
    weight: Decimal
    max_score: Decimal
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass
class ScoringIndicator:
    """评分指标模型"""
    id: int
    indicator_code: str
    dimension_id: int
    indicator_name: str
    weight: Decimal
    max_score: Decimal
    scoring_criteria: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass
class ProjectScore:
    """项目评分记录模型"""
    id: int
    project_id: int
    dimension_id: int
    indicator_id: int
    score: Decimal
    weighted_score: Decimal
    scorer_id: int
    scorer_comment: Optional[str] = None
    scored_at: Optional[datetime] = None


@dataclass
class ScoringSummary:
    """评分汇总模型"""
    id: int
    project_id: int
    dimension_id: int
    total_score: Decimal
    weighted_total: Decimal
    calculated_at: Optional[datetime] = None


@dataclass
class ProjectTotalScore:
    """项目总分模型"""
    id: int
    project_id: int
    total_score: Decimal
    policy_score: Decimal
    layout_score: Decimal
    execution_score: Decimal
    rank_in_period: Optional[int] = None
    grade: Optional[str] = None
    reviewed_by: Optional[int] = None
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class ApprovalRecord:
    """审批记录模型"""
    id: int
    project_id: int
    action: str
    actor_id: int
    actor_role: str
    comment: Optional[str] = None
    action_at: Optional[datetime] = None


@dataclass
class ScoringResult:
    """评分结果详情"""
    project: Project
    total_score: Decimal
    grade: str
    dimension_scores: dict  # {dimension_code: {score, weighted_score, indicators: [...]}}
    scores_by_indicator: dict  # {indicator_code: {score, weighted_score, scorer_comment}}
    rank: Optional[int] = None
