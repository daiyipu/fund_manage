"""
评分规则配置
根据《政府投资基金投向评价管理办法（试行）》定义
"""

SCORING_DIMENSIONS = {
    'POLICY': {
        'name': '政策符合性指标',
        'weight': 60.0,
        'max_score': 60.0,
        'indicators': [
            {
                'code': 'POLICY_01',
                'name': '支持新质生产力发展情况',
                'weight': 16.67,  # (10/60)*100
                'max_score': 10.0,
                'scoring_guide': {
                    '9-10': '突出成效，具有示范引领作用',
                    '7-8': '成效显著',
                    '5-6': '成效较好',
                    '3-4': '有一定成效',
                    '0-2': '成效不明显'
                }
            },
            {
                'code': 'POLICY_02',
                'name': '支持科技创新和促进成果转化情况',
                'weight': 16.67,
                'max_score': 10.0,
                'scoring_guide': {
                    '9-10': '关键技术突破或重大成果转化',
                    '7-8': '重要技术创新',
                    '5-6': '有明显技术创新',
                    '3-4': '有一定技术创新',
                    '0-2': '技术创新不足'
                }
            },
            {
                'code': 'POLICY_03',
                'name': '推进全国统一大市场建设情况',
                'weight': 16.67,
                'max_score': 10.0,
                'scoring_guide': {
                    '9-10': '对统一大市场建设有重大促进作用',
                    '7-8': '有显著促进作用',
                    '5-6': '有较好促进作用',
                    '3-4': '有一定促进作用',
                    '0-2': '促进作用有限'
                }
            },
            {
                'code': 'POLICY_04',
                'name': '支持绿色发展情况',
                'weight': 8.33,
                'max_score': 5.0,
                'scoring_guide': {
                    '5': '显著促进绿色发展，环保效益突出',
                    '4': '较好促进绿色发展',
                    '3': '有一定的绿色效益',
                    '2': '绿色效益一般',
                    '0-1': '绿色效益不明显'
                }
            },
            {
                'code': 'POLICY_05',
                'name': '支持民营经济发展和促进民间投资情况',
                'weight': 8.33,
                'max_score': 5.0,
                'scoring_guide': {
                    '5': '显著促进民营经济发展',
                    '4': '较好促进民营经济发展',
                    '3': '有一定促进作用',
                    '2': '促进作用一般',
                    '0-1': '促进作用有限'
                }
            },
            {
                'code': 'POLICY_06',
                'name': '壮大耐心资本情况',
                'weight': 8.33,
                'max_score': 5.0,
                'scoring_guide': {
                    '5': '显著壮大耐心资本',
                    '4': '较好壮大耐心资本',
                    '3': '一定壮大耐心资本',
                    '2': '壮大作用一般',
                    '0-1': '壮大作用有限'
                }
            },
            {
                'code': 'POLICY_07',
                'name': '带动社会资本情况',
                'weight': 8.33,
                'max_score': 5.0,
                'scoring_guide': {
                    '5': '杠杆效应显著（1:5以上）',
                    '4': '杠杆效应较好（1:3-1:5）',
                    '3': '有一定杠杆效应（1:2-1:3）',
                    '2': '杠杆效应一般（1:1-1:2）',
                    '0-1': '杠杆效应不明显（低于1:1）'
                }
            },
            {
                'code': 'POLICY_08',
                'name': '服务社会民生等其他重点领域情况',
                'weight': 16.67,
                'max_score': 10.0,
                'scoring_guide': {
                    '9-10': '在民生等重点领域有重大贡献',
                    '7-8': '有显著贡献',
                    '5-6': '有较好贡献',
                    '3-4': '有一定贡献',
                    '0-2': '贡献有限'
                }
            }
        ]
    },
    'LAYOUT': {
        'name': '优化生产力布局指标',
        'weight': 30.0,
        'max_score': 30.0,
        'indicators': [
            {
                'code': 'LAYOUT_01',
                'name': '落实国家区域战略情况',
                'weight': 33.33,
                'max_score': 10.0,
                'scoring_guide': {
                    '9-10': '完全符合且高质量落实区域战略',
                    '7-8': '较好落实区域战略',
                    '5-6': '基本落实区域战略',
                    '3-4': '部分落实区域战略',
                    '0-2': '未有效落实区域战略'
                }
            },
            {
                'code': 'LAYOUT_02',
                'name': '重点投向领域契合度',
                'weight': 33.33,
                'max_score': 10.0,
                'scoring_guide': {
                    '9-10': '完全契合国家重点投向领域',
                    '7-8': '较好契合重点投向领域',
                    '5-6': '基本契合重点投向领域',
                    '3-4': '部分契合重点投向领域',
                    '0-2': '契合度较低'
                }
            },
            {
                'code': 'LAYOUT_03',
                'name': '产能有效利用情况',
                'weight': 33.33,
                'max_score': 10.0,
                'scoring_guide': {
                    '9-10': '显著提升产能利用效率',
                    '7-8': '较好提升产能利用效率',
                    '5-6': '一定提升产能利用效率',
                    '3-4': '产能利用效率提升一般',
                    '0-2': '未有效提升产能利用效率'
                }
            }
        ]
    },
    'EXECUTION': {
        'name': '政策执行能力指标',
        'weight': 10.0,
        'max_score': 10.0,
        'indicators': [
            {
                'code': 'EXEC_01',
                'name': '资金效能情况',
                'weight': 40.0,
                'max_score': 4.0,
                'scoring_guide': {
                    '4': '资金使用效率极高，效益显著',
                    '3': '资金使用效率较高，效益较好',
                    '2': '资金使用效率一般',
                    '1': '资金使用效率较低',
                    '0': '资金使用效率低或存在问题'
                }
            },
            {
                'code': 'EXEC_02',
                'name': '基金管理人专业水平',
                'weight': 60.0,
                'max_score': 6.0,
                'scoring_guide': {
                    '6': '专业能力突出，经验丰富，业绩优秀',
                    '5': '专业能力强，经验较丰富',
                    '4': '专业能力较强，有一定经验',
                    '3': '专业能力一般，经验不足',
                    '1-2': '专业能力较弱或经验明显不足',
                    '0': '专业能力不足或存在违规记录'
                }
            }
        ]
    }
}

# 等级划分标准
GRADING_STANDARDS = {
    'excellent': {'min': 90.0, 'name': '优秀', 'color': '#52c41a'},
    'good': {'min': 80.0, 'name': '良好', 'color': '#1890ff'},
    'qualified': {'min': 60.0, 'name': '合格', 'color': '#faad14'},
    'unqualified': {'min': 0.0, 'name': '不合格', 'color': '#f5222d'}
}

# 角色权限定义
ROLE_PERMISSIONS = {
    'admin': {
        'can_create_project': True,
        'can_edit_project': True,
        'can_delete_project': True,
        'can_score': True,
        'can_approve': True,
        'can_view_all': True,
        'can_export': True,
        'can_manage_users': True,
        'can_view_statistics': True
    },
    'manager': {
        'can_create_project': True,
        'can_edit_project': True,
        'can_delete_project': False,
        'can_score': True,
        'can_approve': True,
        'can_view_all': True,
        'can_export': True,
        'can_manage_users': False,
        'can_view_statistics': True
    },
    'scorer': {
        'can_create_project': False,
        'can_edit_project': False,
        'can_delete_project': False,
        'can_score': True,
        'can_approve': False,
        'can_view_all': False,  # 只能查看分配给自己的项目
        'can_export': False,
        'can_manage_users': False,
        'can_view_statistics': False
    },
    'viewer': {
        'can_create_project': False,
        'can_edit_project': False,
        'can_delete_project': False,
        'can_score': False,
        'can_approve': False,
        'can_view_all': True,
        'can_export': True,
        'can_manage_users': False,
        'can_view_statistics': True
    }
}

# 角色名称映射
ROLE_NAMES = {
    'admin': '系统管理员',
    'manager': '部门负责人',
    'scorer': '评分专家',
    'viewer': '查看人员'
}
