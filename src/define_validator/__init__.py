"""
Define.xml Validator Package
FDA-compliant validation for CDISC define.xml files
"""

__version__ = "1.0.0"
__author__ = "Christian Baghai"

from .validator import DefineXMLValidator

__all__ = ['DefineXMLValidator']
