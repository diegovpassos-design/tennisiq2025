#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ Services
================
Serviços do sistema
"""

from .dashboard_web import app as dashboard_app
from .dashboard_logger import dashboard_logger
from .integrador_resultados import integrador_resultados

__all__ = ['dashboard_app', 'dashboard_logger', 'integrador_resultados']
