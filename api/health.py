#!/usr/bin/env python3
"""
Health Check API Endpoint
========================

Simple health check endpoint for monitoring system status.
"""

import sys
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler
import json
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for health check"""
        try:
            # Check environment variables
            required_env_vars = [
                'GEMINI_API_KEY',
                'SUPABASE_URL',
                'SUPABASE_ANON_KEY'
            ]
            
            env_status = {}
            all_env_ok = True
            
            for var in required_env_vars:
                env_status[var] = bool(os.getenv(var))
                if not env_status[var]:
                    all_env_ok = False
            
            # System status
            status = "healthy" if all_env_ok else "degraded"
            
            # Send response
            self.send_response(200 if all_env_ok else 503)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            response = {
                'status': status,
                'timestamp': self.get_timestamp(),
                'environment': {
                    'variables_configured': env_status,
                    'all_required_present': all_env_ok
                },
                'services': {
                    'api': 'operational',
                    'database': 'unknown',  # Would need actual DB check
                    'llm': 'unknown'        # Would need actual LLM check
                },
                'version': '1.0.0'
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                'status': 'error',
                'timestamp': self.get_timestamp(),
                'error': str(e)
            }
            
            self.wfile.write(json.dumps(error_response).encode())
    
    def get_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

# For local testing
if __name__ == "__main__":
    import unittest.mock
    
    class MockRequest:
        def __init__(self):
            self.method = 'GET'
    
    mock_handler = handler(MockRequest(), ('127.0.0.1', 8000), None)
    mock_handler.do_GET() 