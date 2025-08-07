#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TennisIQ Core
============
Módulos principais do sistema
"""

from .bot import TennisIQBot
from .detector_vantagem_mental import DetectorVantagemMental

__all__ = ['TennisIQBot', 'DetectorVantagemMental']
