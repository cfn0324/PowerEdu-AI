#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库应用URL配置
"""

from ninja import Router
from .views import router as knowledge_router

# 创建应用级路由器
router = Router()

# 包含知识库相关路由
router.add_router("", knowledge_router, tags=["知识库"])
