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
                'weight': 16.67,
                'max_score': 10.0,
                'type': 'leaf',
                'scoring_guide': {
                    '10': '投向新质生产力领域比例≥90%',
                    '9': '投向新质生产力领域比例80%-90%（含80%）',
                    '8': '投向新质生产力领域比例70%-80%（含70%）',
                    '7': '投向新质生产力领域比例60%-70%（含60%）',
                    '6': '投向新质生产力领域比例50%-60%（含50%）',
                    '5': '投向新质生产力领域比例40%-50%（含40%）',
                    '4': '投向新质生产力领域比例30%-40%（含30%）',
                    '3': '投向新质生产力领域比例20%-30%（含20%）',
                    '2': '投向新质生产力领域比例10%-20%（含10%）',
                    '1': '投向新质生产力领域比例<10%',
                    '0': '未投向新质生产力领域'
                }
            },
            {
                'code': 'POLICY_02',
                'name': '支持科技创新和促进成果转化情况',
                'weight': 16.67,
                'max_score': 10.0,
                'type': 'parent',
                'scoring_guide': {},
                'sub_indicators': [
                    {
                        'code': 'POLICY_02_01',
                        'name': '新增发明专利或技术成果',
                        'weight': 30.0,
                        'max_score': 3.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '3': '新增6项及以上成果',
                            '2.5': '新增5项成果',
                            '2': '新增4项成果',
                            '1.5': '新增3项成果',
                            '1': '新增2项成果',
                            '0.5': '新增1项成果',
                            '0': '无新增成果'
                        }
                    },
                    {
                        'code': 'POLICY_02_02',
                        'name': '支持科技成果转化',
                        'weight': 20.0,
                        'max_score': 2.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '2': '支持科技成果转化',
                            '0': '无科技成果转化'
                        }
                    },
                    {
                        'code': 'POLICY_02_03',
                        'name': '支持解决"卡脖子"难题',
                        'weight': 50.0,
                        'max_score': 5.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '5': '支持多个"卡脖子"领域',
                            '3': '支持一个"卡脖子"领域',
                            '0': '不涉及"卡脖子"技术'
                        }
                    }
                ]
            },
            {
                'code': 'POLICY_03',
                'name': '推进全国统一大市场建设情况',
                'weight': 16.67,
                'max_score': 10.0,
                'type': 'parent',
                'scoring_guide': {},
                'sub_indicators': [
                    {
                        'code': 'POLICY_03_01',
                        'name': '返投比例情况',
                        'weight': 30.0,
                        'max_score': 3.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '3': '未设置返投要求或返投比例<50%',
                            '2': '返投比例50%-100%（含50%）',
                            '1': '返投比例100%-150%（含100%）',
                            '0': '返投比例≥150%'
                        }
                    },
                    {
                        'code': 'POLICY_03_02',
                        'name': '注册地迁移条件',
                        'weight': 30.0,
                        'max_score': 3.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '3': '未设置注册地迁移条件',
                            '0': '设置了注册地迁移条件'
                        }
                    },
                    {
                        'code': 'POLICY_03_03',
                        'name': '违规行为情况',
                        'weight': 40.0,
                        'max_score': 4.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '4': '不存在违规行为',
                            '0': '存在违规行为'
                        }
                    }
                ]
            },
            {
                'code': 'POLICY_04',
                'name': '支持绿色发展情况',
                'weight': 8.33,
                'max_score': 5.0,
                'type': 'parent',
                'scoring_guide': {},
                'sub_indicators': [
                    {
                        'code': 'POLICY_04_01',
                        'name': '碳减排比例',
                        'weight': 60.0,
                        'max_score': 3.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '3': '碳减排比例≥5%',
                            '2': '碳减排比例3%-5%（含3%）',
                            '1': '碳减排比例1%-3%（含1%）',
                            '0': '碳减排比例<1%或为负或不涉及绿色发展领域'
                        }
                    },
                    {
                        'code': 'POLICY_04_02',
                        'name': '绿色发展投向比例',
                        'weight': 40.0,
                        'max_score': 2.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '2': '投向比例>20%',
                            '1': '投向比例≤20%',
                            '0': '不涉及绿色发展领域'
                        }
                    }
                ]
            },
            {
                'code': 'POLICY_05',
                'name': '支持民营经济发展和促进民间投资情况',
                'weight': 8.33,
                'max_score': 5.0,
                'type': 'leaf',
                'scoring_guide': {
                    '5': '民营企业占比≥50%',
                    '4': '民营企业占比40%-50%（含40%）',
                    '3': '民营企业占比30%-40%（含30%）',
                    '2': '民营企业占比20%-30%（含20%）',
                    '1': '民营企业占比10%-20%（含10%）',
                    '0': '民营企业占比<10%'
                }
            },
            {
                'code': 'POLICY_06',
                'name': '壮大耐心资本情况',
                'weight': 8.33,
                'max_score': 5.0,
                'type': 'leaf',
                'scoring_guide': {
                    '5': '投早投小占比≥70%或平均投资期≥5年',
                    '3': '投早投小占比50%-70%（含50%）或平均投资期3-5年（含3年）',
                    '2': '投早投小占比20%-50%（含20%）或平均投资期2-3年（含2年）',
                    '0': '投早投小占比<20%且平均投资期<2年'
                }
            },
            {
                'code': 'POLICY_07',
                'name': '带动社会资本情况',
                'weight': 8.33,
                'max_score': 5.0,
                'type': 'leaf',
                'scoring_guide': {
                    '5': '社会资本占比≥50%',
                    '4': '社会资本占比40%-50%（含40%）',
                    '3': '社会资本占比30%-40%（含30%）',
                    '2': '社会资本占比20%-30%（含20%）',
                    '1': '社会资本占比10%-20%（含10%）',
                    '0': '社会资本占比<10%'
                }
            },
            {
                'code': 'POLICY_08',
                'name': '服务社会民生等其他重点领域情况',
                'weight': 16.67,
                'max_score': 10.0,
                'type': 'parent',
                'scoring_guide': {},
                'sub_indicators': [
                    {
                        'code': 'POLICY_08_01',
                        'name': '就业/税收/营收排名',
                        'weight': 50.0,
                        'max_score': 5.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '5': '排名前10%',
                            '4': '排名前10%-30%',
                            '3': '排名30%-50%',
                            '2': '排名50%-70%',
                            '1': '排名70%-90%',
                            '0': '排名90%以后'
                        }
                    },
                    {
                        'code': 'POLICY_08_02',
                        'name': '重点领域贡献情况',
                        'weight': 50.0,
                        'max_score': 5.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '5': '涉及两个及以上重点领域',
                            '3': '涉及一个重点领域',
                            '0': '不涉及重点领域'
                        }
                    }
                ]
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
                'type': 'leaf',
                'scoring_guide': {
                    '10': '投向符合国家区域战略要求',
                    '0': '投向不符合国家区域战略要求'
                }
            },
            {
                'code': 'LAYOUT_02',
                'name': '重点投向领域契合度',
                'weight': 33.33,
                'max_score': 10.0,
                'type': 'leaf',
                'scoring_guide': {
                    '10': '重点投向领域比例≥90%',
                    '8': '重点投向领域比例70%-90%（含70%）',
                    '6': '重点投向领域比例50%-70%（含50%）',
                    '4': '重点投向领域比例30%-50%（含30%）',
                    '0': '重点投向领域比例<30%'
                }
            },
            {
                'code': 'LAYOUT_03',
                'name': '产能有效利用情况',
                'weight': 33.33,
                'max_score': 10.0,
                'type': 'parent',
                'scoring_guide': {},
                'sub_indicators': [
                    {
                        'code': 'LAYOUT_03_01',
                        'name': '产能利用率',
                        'weight': 50.0,
                        'max_score': 5.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '5': '产能利用率高于行业平均水平',
                            '3': '产能利用率接近行业平均水平±5%以内',
                            '0': '产能利用率低于行业平均水平'
                        }
                    },
                    {
                        'code': 'LAYOUT_03_02',
                        'name': '资产周转率',
                        'weight': 50.0,
                        'max_score': 5.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '5': '资产周转率≥100%',
                            '4': '资产周转率80%-100%（含80%）',
                            '3': '资产周转率60%-80%（含60%）',
                            '0': '资产周转率<60%'
                        }
                    }
                ]
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
                'type': 'parent',
                'scoring_guide': {},
                'sub_indicators': [
                    {
                        'code': 'EXEC_01_01',
                        'name': '出资完成比例',
                        'weight': 25.0,
                        'max_score': 1.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '1': '出资完成比例≥50%',
                            '0.5': '出资完成比例30%-50%（含30%）',
                            '0': '出资完成比例<30%'
                        }
                    },
                    {
                        'code': 'EXEC_01_02',
                        'name': '闲置资金情况',
                        'weight': 25.0,
                        'max_score': 1.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '1': '闲置资金占比<30%',
                            '0': '闲置资金占比≥30%'
                        }
                    },
                    {
                        'code': 'EXEC_01_03',
                        'name': '内部收益率',
                        'weight': 25.0,
                        'max_score': 1.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '1': '内部收益率≥3%',
                            '0': '内部收益率<3%'
                        }
                    },
                    {
                        'code': 'EXEC_01_04',
                        'name': '资产增值率',
                        'weight': 25.0,
                        'max_score': 1.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '1': '资产增值率≥5%',
                            '0': '资产增值率<5%'
                        }
                    }
                ]
            },
            {
                'code': 'EXEC_02',
                'name': '基金管理人专业水平',
                'weight': 60.0,
                'max_score': 6.0,
                'type': 'parent',
                'scoring_guide': {},
                'sub_indicators': [
                    {
                        'code': 'EXEC_02_01',
                        'name': '高级管理人员从业年限',
                        'weight': 16.67,
                        'max_score': 1.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '1': '从业年限>10年',
                            '0': '从业年限≤10年'
                        }
                    },
                    {
                        'code': 'EXEC_02_02',
                        'name': '风险防控有效性',
                        'weight': 16.67,
                        'max_score': 1.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '1': '有制度且无风险损失',
                            '0': '无制度或发生风险损失/爆雷'
                        }
                    },
                    {
                        'code': 'EXEC_02_03',
                        'name': '信用建设情况',
                        'weight': 33.33,
                        'max_score': 2.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '2': '信用情况较好',
                            '0': '信用情况较差'
                        }
                    },
                    {
                        'code': 'EXEC_02_04',
                        'name': '信息报送及披露',
                        'weight': 33.33,
                        'max_score': 2.0,
                        'type': 'leaf',
                        'scoring_guide': {
                            '2': '信息登记较好且披露透明度高',
                            '1': '信息登记较好或披露透明度高',
                            '0': '信息登记较差且披露透明度不足'
                        }
                    }
                ]
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
