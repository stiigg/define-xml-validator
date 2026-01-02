#!/usr/bin/env python3
"""
Validation report generation in multiple formats
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class ReportGenerator:
    """Generate validation reports in various formats"""
    
    def __init__(self, validation_results: Dict[str, Any]):
        """Initialize report generator
        
        Args:
            validation_results: Validation results dictionary
        """
        self.results = validation_results
    
    def generate_text(self) -> str:
        """Generate text format report
        
        Returns:
            Formatted text report
        """
        lines = []
        lines.append("\n" + "="*70)
        lines.append("  DEFINE.XML VALIDATION REPORT")
        lines.append("="*70)
        
        # Summary
        meta = self.results.get('metadata', {})
        lines.append(f"\nFile: {meta.get('file_path', 'N/A')}")
        lines.append(f"SHA-256: {meta.get('sha256', 'N/A')}")
        lines.append(f"Timestamp: {meta.get('timestamp', 'N/A')}")
        
        # Overall status
        summary = self.results.get('summary', {})
        lines.append(f"\nStatus: {summary.get('status', 'UNKNOWN')}")
        lines.append(f"Errors: {summary.get('total_errors', 0)}")
        lines.append(f"Warnings: {summary.get('total_warnings', 0)}")
        
        # Layer-by-layer results
        layers = self.results.get('layers', {})
        for layer_num in sorted(layers.keys(), key=lambda x: int(x.split('_')[1])):
            layer_data = layers[layer_num]
            lines.append(f"\n{'─'*70}")
            lines.append(f"Layer {layer_num.split('_')[1]}: {layer_data.get('name', 'Unknown')}")
            lines.append(f"{'─'*70}")
            
            # Errors
            errors = layer_data.get('errors', [])
            if errors:
                lines.append(f"\n  ❌ ERRORS ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    lines.append(f"    {i}. {error}")
            
            # Warnings
            warnings = layer_data.get('warnings', [])
            if warnings:
                lines.append(f"\n  ⚠️  WARNINGS ({len(warnings)}):")
                for i, warning in enumerate(warnings, 1):
                    lines.append(f"    {i}. {warning}")
            
            if not errors and not warnings:
                lines.append("  ✓ No issues found")
        
        lines.append("\n" + "="*70)
        return "\n".join(lines)
    
    def generate_json(self, output_file: Path) -> None:
        """Generate JSON format report
        
        Args:
            output_file: Path to output JSON file
        """
        output_file.write_text(
            json.dumps(self.results, indent=2, default=str)
        )
    
    def generate_html(self, output_file: Path) -> None:
        """Generate HTML format report
        
        Args:
            output_file: Path to output HTML file
        """
        meta = self.results.get('metadata', {})
        summary = self.results.get('summary', {})
        layers = self.results.get('layers', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Define.xml Validation Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .metadata {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card.success {{ border-left: 4px solid #10b981; }}
        .stat-card.error {{ border-left: 4px solid #ef4444; }}
        .stat-card.warning {{ border-left: 4px solid #f59e0b; }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .layer {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .layer-header {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}
        .issue {{
            padding: 12px;
            margin: 10px 0;
            border-radius: 5px;
            background: #f9fafb;
        }}
        .issue.error {{
            border-left: 4px solid #ef4444;
            background: #fef2f2;
        }}
        .issue.warning {{
            border-left: 4px solid #f59e0b;
            background: #fffbeb;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }}
        .badge.success {{
            background: #d1fae5;
            color: #065f46;
        }}
        .badge.error {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .badge.warning {{
            background: #fef3c7;
            color: #92400e;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Define.xml Validation Report</h1>
        <p>FDA-Compliant 7-Layer Validation</p>
    </div>
    
    <div class="metadata">
        <p><strong>File:</strong> {meta.get('file_path', 'N/A')}</p>
        <p><strong>SHA-256:</strong> <code>{meta.get('sha256', 'N/A')}</code></p>
        <p><strong>Timestamp:</strong> {meta.get('timestamp', 'N/A')}</p>
    </div>
    
    <div class="summary">
        <div class="stat-card {summary.get('status', '').lower()}">
            <div class="stat-label">Status</div>
            <div class="stat-value">{summary.get('status', 'UNKNOWN')}</div>
        </div>
        <div class="stat-card error">
            <div class="stat-label">Errors</div>
            <div class="stat-value">{summary.get('total_errors', 0)}</div>
        </div>
        <div class="stat-card warning">
            <div class="stat-label">Warnings</div>
            <div class="stat-value">{summary.get('total_warnings', 0)}</div>
        </div>
    </div>
    
    <h2>Layer-by-Layer Results</h2>
"""
        
        # Add each layer
        for layer_num in sorted(layers.keys(), key=lambda x: int(x.split('_')[1])):
            layer_data = layers[layer_num]
            layer_name = layer_data.get('name', 'Unknown')
            errors = layer_data.get('errors', [])
            warnings = layer_data.get('warnings', [])
            
            status_badge = "success" if not errors and not warnings else ("error" if errors else "warning")
            status_text = "PASSED" if not errors and not warnings else ("FAILED" if errors else "WARNINGS")
            
            html += f"""
    <div class="layer">
        <div class="layer-header">
            Layer {layer_num.split('_')[1]}: {layer_name}
            <span class="badge {status_badge}">{status_text}</span>
        </div>
"""
            
            if errors:
                html += f"        <h4 style='color: #ef4444;'>❌ Errors ({len(errors)})</h4>\n"
                for error in errors:
                    html += f"        <div class='issue error'>{error}</div>\n"
            
            if warnings:
                html += f"        <h4 style='color: #f59e0b;'>⚠️ Warnings ({len(warnings)})</h4>\n"
                for warning in warnings:
                    html += f"        <div class='issue warning'>{warning}</div>\n"
            
            if not errors and not warnings:
                html += "        <p style='color: #10b981;'>✓ No issues found</p>\n"
            
            html += "    </div>\n"
        
        html += """
</body>
</html>
"""
        
        output_file.write_text(html)
