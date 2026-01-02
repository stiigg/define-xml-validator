#!/usr/bin/env python3
"""
Automatic schema download and management
"""
import hashlib
import urllib.request
from pathlib import Path
from typing import Optional


class SchemaManager:
    """Manages CDISC Define.xml schema downloads"""
    
    # Official CDISC schema URLs
    SCHEMA_URLS = {
        '2.0': 'https://www.cdisc.org/sites/default/files/schema/define-xml-2.0/define2-0-0.xsd',
        '2.1': 'https://www.cdisc.org/sites/default/files/schema/define-xml-2.1/define2-1-0.xsd'
    }
    
    # Known SHA-256 checksums for integrity verification
    SCHEMA_CHECKSUMS = {
        '2.0': 'placeholder_checksum_2_0',  # Update with actual checksum
        '2.1': 'placeholder_checksum_2_1'   # Update with actual checksum
    }
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize schema manager
        
        Args:
            cache_dir: Directory for caching schemas (default: ./schemas)
        """
        self.cache_dir = cache_dir or Path('./schemas')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_schema(self, version: str = '2.1') -> Path:
        """Get schema file, downloading if necessary
        
        Args:
            version: Schema version ('2.0' or '2.1')
            
        Returns:
            Path to schema file
        """
        schema_file = self.cache_dir / f'define-{version}.xsd'
        
        if schema_file.exists():
            # Verify checksum if available
            if self._verify_checksum(schema_file, version):
                return schema_file
            else:
                print(f"Warning: Cached schema checksum mismatch, re-downloading...")
        
        return self.download_schema(version, self.cache_dir)
    
    def download_schema(self, version: str, output_dir: Path) -> Path:
        """Download schema from CDISC website
        
        Args:
            version: Schema version ('2.0' or '2.1')
            output_dir: Directory to save schema
            
        Returns:
            Path to downloaded schema file
            
        Raises:
            ValueError: If version not supported
            RuntimeError: If download fails
        """
        if version not in self.SCHEMA_URLS:
            raise ValueError(f"Unsupported schema version: {version}. Use '2.0' or '2.1'")
        
        url = self.SCHEMA_URLS[version]
        output_file = output_dir / f'define-{version}.xsd'
        
        try:
            # Download with timeout
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
            
            # Save to file
            output_file.write_bytes(content)
            
            # Verify download
            if not output_file.exists():
                raise RuntimeError("Schema file not created after download")
            
            return output_file
            
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to download schema: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during schema download: {e}")
    
    def _verify_checksum(self, file_path: Path, version: str) -> bool:
        """Verify file checksum
        
        Args:
            file_path: Path to file
            version: Schema version
            
        Returns:
            True if checksum matches or no checksum available
        """
        expected = self.SCHEMA_CHECKSUMS.get(version)
        if not expected or expected.startswith('placeholder'):
            # No checksum available, skip verification
            return True
        
        actual = self._calculate_sha256(file_path)
        return actual == expected
    
    @staticmethod
    def _calculate_sha256(file_path: Path) -> str:
        """Calculate SHA-256 checksum of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of SHA-256 hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def list_cached_schemas(self) -> list[Path]:
        """List all cached schema files
        
        Returns:
            List of cached schema file paths
        """
        return list(self.cache_dir.glob('define-*.xsd'))
    
    def clear_cache(self) -> int:
        """Remove all cached schemas
        
        Returns:
            Number of files removed
        """
        count = 0
        for schema_file in self.list_cached_schemas():
            schema_file.unlink()
            count += 1
        return count
