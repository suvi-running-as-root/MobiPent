# backend/main.py
# pyright: reportMissingImports=false

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import subprocess
import xml.etree.ElementTree as ET
import json
import re
import zipfile
import hashlib
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

from auth import router as auth_router
from analyzer import router as analyzer_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MobiPent Security Scanner", description="OWASP MASVS/MASTG Compliant Mobile Security Testing")
app.include_router(auth_router)

UPLOAD_DIR = "uploads"
APKTOOL_BAT_PATH = r"C:\Users\Vishwanath BK\Tools\apktool\apktool.bat"
SCAN_REPORTS_DIR = "scan_reports"

# CORS for Expo Dev App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create required directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SCAN_REPORTS_DIR, exist_ok=True)

# Register routers
app.include_router(auth_router, prefix="/auth")
app.include_router(analyzer_router, prefix="/analyzer")

class OWASPMobileScanner:
    """
    OWASP MASVS/MASTG/MASWE compliant mobile security scanner
    """
    
    def __init__(self, apk_path: str):
        self.apk_path = apk_path
        self.output_dir = apk_path + "_analysis"
        self.manifest_path = os.path.join(self.output_dir, "AndroidManifest.xml")
        self.findings = {
            "MASVS-STORAGE": [],
            "MASVS-CRYPTO": [],
            "MASVS-AUTH": [],
            "MASVS-NETWORK": [],
            "MASVS-PLATFORM": [],
            "MASVS-CODE": [],
            "MASVS-RESILIENCE": [],
            "MASVS-PRIVACY": []
        }
        self.risk_score = 0
        self.total_tests = 0
        self.passed_tests = 0
        
    def extract_apk(self) -> bool:
        """Extract APK using apktool"""
        try:
            subprocess.run([
                APKTOOL_BAT_PATH, "d", self.apk_path, 
                "-o", self.output_dir, "-f"
            ], check=True, capture_output=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            logger.error(f"APK extraction failed: {e}")
            return False
    
    def analyze_manifest(self) -> Dict:
        """MASVS-PLATFORM: Analyze AndroidManifest.xml for security issues"""
        findings = []
        
        if not os.path.exists(self.manifest_path):
            findings.append({"severity": "HIGH", "issue": "AndroidManifest.xml not found"})
            return {"findings": findings}
        
        try:
            tree = ET.parse(self.manifest_path)
            root = tree.getroot()
            
            # MASWE-0001: Debug mode detection
            app_element = root.find('.//application')
            if app_element is not None:
                debuggable = app_element.get('{http://schemas.android.com/apk/res/android}debuggable')
                if debuggable == "true":
                    findings.append({
                        "severity": "HIGH",
                        "issue": "MASWE-0001: Debug mode enabled",
                        "description": "Application is debuggable in production",
                        "masvs_control": "MASVS-CODE-8"
                    })
                    self.risk_score += 25
                
                # MASWE-0002: Backup allowed
                allow_backup = app_element.get('{http://schemas.android.com/apk/res/android}allowBackup')
                if allow_backup != "false":
                    findings.append({
                        "severity": "MEDIUM",
                        "issue": "MASWE-0002: Backup allowed",
                        "description": "App data can be backed up via ADB",
                        "masvs_control": "MASVS-STORAGE-1"
                    })
                    self.risk_score += 15
                
                # MASWE-0003: Clear text traffic
                clear_text = app_element.get('{http://schemas.android.com/apk/res/android}usesCleartextTraffic')
                if clear_text == "true":
                    findings.append({
                        "severity": "HIGH",
                        "issue": "MASWE-0003: Clear text traffic allowed",
                        "description": "App allows HTTP traffic",
                        "masvs_control": "MASVS-NETWORK-1"
                    })
                    self.risk_score += 30
            
            # MASWE-0004: Exported components analysis
            exported_components = []
            for component in root.iter():
                if component.tag in ['activity', 'service', 'receiver', 'provider']:
                    exported = component.get('{http://schemas.android.com/apk/res/android}exported')
                    if exported == "true":
                        name = component.get('{http://schemas.android.com/apk/res/android}name')
                        exported_components.append(f"{component.tag}: {name}")
            
            if exported_components:
                findings.append({
                    "severity": "MEDIUM",
                    "issue": "MASWE-0004: Exported components found",
                    "description": f"Components: {', '.join(exported_components)}",
                    "masvs_control": "MASVS-PLATFORM-1"
                })
                self.risk_score += 10
            
            # MASWE-0005: Dangerous permissions
            dangerous_perms = [
                'READ_EXTERNAL_STORAGE', 'WRITE_EXTERNAL_STORAGE',
                'READ_CONTACTS', 'WRITE_CONTACTS', 'ACCESS_FINE_LOCATION',
                'ACCESS_COARSE_LOCATION', 'CAMERA', 'RECORD_AUDIO',
                'READ_SMS', 'SEND_SMS', 'CALL_PHONE'
            ]
            
            found_dangerous = []
            for perm in root.findall('.//uses-permission'):
                perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
                if perm_name and any(dangerous in perm_name for dangerous in dangerous_perms):
                    found_dangerous.append(perm_name.split('.')[-1])
            
            if found_dangerous:
                findings.append({
                    "severity": "MEDIUM",
                    "issue": "MASWE-0005: Dangerous permissions",
                    "description": f"Permissions: {', '.join(found_dangerous)}",
                    "masvs_control": "MASVS-PLATFORM-1"
                })
                self.risk_score += 5
            
            self.findings["MASVS-PLATFORM"] = findings
            return {"findings": findings}
            
        except Exception as e:
            logger.error(f"Manifest analysis failed: {e}")
            return {"findings": [{"severity": "ERROR", "issue": f"Analysis failed: {e}"}]}
    
    def analyze_storage_security(self) -> Dict:
        """MASVS-STORAGE: Analyze data storage security"""
        findings = []
        
        # Check for hardcoded sensitive data
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'private_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        # Search in resources and code
        for root_dir, _, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith(('.xml', '.properties', '.json', '.smali')):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in sensitive_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    findings.append({
                                        "severity": "HIGH",
                                        "issue": "MASWE-0006: Hardcoded sensitive data",
                                        "description": f"Found in {file}",
                                        "masvs_control": "MASVS-STORAGE-1"
                                    })
                                    self.risk_score += 20
                                    break
                    except Exception:
                        continue
        
        # Check for database files
        db_files = []
        for root_dir, _, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_files.append(file)
        
        if db_files:
            findings.append({
                "severity": "MEDIUM",
                "issue": "MASWE-0007: Database files found",
                "description": f"Files: {', '.join(db_files)}",
                "masvs_control": "MASVS-STORAGE-1"
            })
            self.risk_score += 10
        
        self.findings["MASVS-STORAGE"] = findings
        return {"findings": findings}
    
    def analyze_crypto_security(self) -> Dict:
        """MASVS-CRYPTO: Analyze cryptographic implementations"""
        findings = []
        
        # Check for weak crypto algorithms
        weak_crypto = [
            'MD5', 'SHA1', 'DES', 'RC4', 'ECB'
        ]
        
        # Check for hardcoded keys/IVs
        crypto_patterns = [
            r'AES.*KEY.*=.*["\'][^"\']{16,}["\']',
            r'IV.*=.*["\'][^"\']{16,}["\']',
            r'SALT.*=.*["\'][^"\']{8,}["\']'
        ]
        
        for root_dir, _, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Check for weak algorithms
                            for weak in weak_crypto:
                                if weak in content:
                                    findings.append({
                                        "severity": "HIGH",
                                        "issue": f"MASWE-0008: Weak crypto algorithm {weak}",
                                        "description": f"Found in {file}",
                                        "masvs_control": "MASVS-CRYPTO-1"
                                    })
                                    self.risk_score += 25
                                    break
                            
                            # Check for hardcoded crypto keys
                            for pattern in crypto_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    findings.append({
                                        "severity": "HIGH",
                                        "issue": "MASWE-0009: Hardcoded crypto key",
                                        "description": f"Found in {file}",
                                        "masvs_control": "MASVS-CRYPTO-2"
                                    })
                                    self.risk_score += 30
                                    break
                    except Exception:
                        continue
        
        self.findings["MASVS-CRYPTO"] = findings
        return {"findings": findings}
    
    def analyze_network_security(self) -> Dict:
        """MASVS-NETWORK: Analyze network security"""
        findings = []
        
        # Check network security config
        nsc_path = os.path.join(self.output_dir, "res", "xml", "network_security_config.xml")
        if os.path.exists(nsc_path):
            try:
                tree = ET.parse(nsc_path)
                root = tree.getroot()
                
                # Check for trust-user-certs
                if root.find('.//trust-user-certs') is not None:
                    findings.append({
                        "severity": "MEDIUM",
                        "issue": "MASWE-0010: User certificates trusted",
                        "description": "App trusts user-added certificates",
                        "masvs_control": "MASVS-NETWORK-3"
                    })
                    self.risk_score += 15
                
                # Check for cleartext permitted
                if root.find('.//base-config[@cleartextTrafficPermitted="true"]') is not None:
                    findings.append({
                        "severity": "HIGH",
                        "issue": "MASWE-0011: Clear text traffic permitted",
                        "description": "Network security config allows HTTP",
                        "masvs_control": "MASVS-NETWORK-1"
                    })
                    self.risk_score += 25
                    
            except Exception:
                pass
        
        # Check for URL patterns in code
        url_patterns = [
            r'http://[^\s"\']+',
            r'https://[^\s"\']+',
        ]
        
        http_urls = []
        for root_dir, _, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in url_patterns:
                                matches = re.findall(pattern, content)
                                for match in matches:
                                    if match.startswith('http://'):
                                        http_urls.append(match)
                    except Exception:
                        continue
        
        if http_urls:
            findings.append({
                "severity": "MEDIUM",
                "issue": "MASWE-0012: HTTP URLs found",
                "description": f"Insecure URLs: {len(http_urls)} found",
                "masvs_control": "MASVS-NETWORK-1"
            })
            self.risk_score += 10
        
        self.findings["MASVS-NETWORK"] = findings
        return {"findings": findings}
    
    def analyze_code_quality(self) -> Dict:
        """MASVS-CODE: Analyze code quality and obfuscation"""
        findings = []
        
        # Analyze code obfuscation
        smali_dir = os.path.join(self.output_dir, "smali")
        if os.path.exists(smali_dir):
            short_names = 0
            long_names = 0
            total_classes = 0
            
            for root_dir, _, files in os.walk(smali_dir):
                for file in files:
                    if file.endswith(".smali"):
                        total_classes += 1
                        name = file.replace(".smali", "")
                        if len(name) <= 2 or re.match(r'^[a-z]{1,3}$', name):
                            short_names += 1
                        else:
                            long_names += 1
            
            if total_classes > 0:
                obfuscation_ratio = short_names / total_classes
                if obfuscation_ratio < 0.3:
                    findings.append({
                        "severity": "MEDIUM",
                        "issue": "MASWE-0013: Code not obfuscated",
                        "description": f"Only {obfuscation_ratio:.1%} of classes appear obfuscated",
                        "masvs_control": "MASVS-CODE-6"
                    })
                    self.risk_score += 15
                else:
                    findings.append({
                        "severity": "INFO",
                        "issue": "Code appears obfuscated",
                        "description": f"{obfuscation_ratio:.1%} of classes appear obfuscated",
                        "masvs_control": "MASVS-CODE-6"
                    })
        
        # Check for logging statements
        log_patterns = [
            r'Log\.[vdiwea]\(',
            r'System\.out\.print',
            r'printStackTrace\(',
        ]
        
        log_statements = 0
        for root_dir, _, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in log_patterns:
                                log_statements += len(re.findall(pattern, content))
                    except Exception:
                        continue
        
        if log_statements > 10:
            findings.append({
                "severity": "MEDIUM",
                "issue": "MASWE-0014: Excessive logging",
                "description": f"Found {log_statements} logging statements",
                "masvs_control": "MASVS-CODE-8"
            })
            self.risk_score += 10
        
        self.findings["MASVS-CODE"] = findings
        return {"findings": findings}
    
    def analyze_resilience(self) -> Dict:
        """MASVS-RESILIENCE: Analyze anti-tampering and runtime protection"""
        findings = []
        
        # Check for anti-debugging measures
        anti_debug_patterns = [
            r'Debug.*detect',
            r'isDebuggerConnected',
            r'JDWP',
            r'TracerPid'
        ]
        
        # Check for root detection
        root_detection_patterns = [
            r'su\b',
            r'/system/bin/su',
            r'/system/xbin/su',
            r'busybox',
            r'Superuser\.apk'
        ]
        
        protection_found = False
        for root_dir, _, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Check for anti-debug
                            for pattern in anti_debug_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    findings.append({
                                        "severity": "INFO",
                                        "issue": "Anti-debugging measures found",
                                        "description": f"Found in {file}",
                                        "masvs_control": "MASVS-RESILIENCE-2"
                                    })
                                    protection_found = True
                                    break
                            
                            # Check for root detection
                            for pattern in root_detection_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    findings.append({
                                        "severity": "INFO",
                                        "issue": "Root detection found",
                                        "description": f"Found in {file}",
                                        "masvs_control": "MASVS-RESILIENCE-1"
                                    })
                                    protection_found = True
                                    break
                    except Exception:
                        continue
        
        if not protection_found:
            findings.append({
                "severity": "MEDIUM",
                "issue": "MASWE-0015: No runtime protection",
                "description": "No anti-tampering measures detected",
                "masvs_control": "MASVS-RESILIENCE-1"
            })
            self.risk_score += 15
        
        self.findings["MASVS-RESILIENCE"] = findings
        return {"findings": findings}
    
    def analyze_privacy(self) -> Dict:
        """MASVS-PRIVACY: Analyze privacy and data protection"""
        findings = []
        
        # Check for sensitive data collection
        privacy_patterns = [
            r'IMEI',
            r'IMSI',
            r'getDeviceId',
            r'getSubscriberId',
            r'getSimSerialNumber',
            r'getNetworkOperator',
            r'getLastKnownLocation',
            r'getContactList'
        ]
        
        privacy_issues = []
        for root_dir, _, files in os.walk(self.output_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in privacy_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    privacy_issues.append(pattern)
                    except Exception:
                        continue
        
        if privacy_issues:
            findings.append({
                "severity": "MEDIUM",
                "issue": "MASWE-0016: Sensitive data access",
                "description": f"Accesses: {', '.join(set(privacy_issues))}",
                "masvs_control": "MASVS-PRIVACY-1"
            })
            self.risk_score += 10
        
        self.findings["MASVS-PRIVACY"] = findings
        return {"findings": findings}
    
    def generate_report(self) -> Dict:
        """Generate comprehensive OWASP compliance report"""
        # Calculate statistics
        total_findings = sum(len(findings) for findings in self.findings.values())
        high_severity = sum(1 for findings in self.findings.values() 
                          for finding in findings if finding.get("severity") == "HIGH")
        medium_severity = sum(1 for findings in self.findings.values() 
                            for finding in findings if finding.get("severity") == "MEDIUM")
        
        # Risk assessment
        if self.risk_score >= 100:
            risk_level = "CRITICAL"
        elif self.risk_score >= 70:
            risk_level = "HIGH"
        elif self.risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Generate summary
        summary = []
        for category, findings in self.findings.items():
            if findings:
                summary.append(f"🔍 {category}: {len(findings)} issues found")
            else:
                summary.append(f"✅ {category}: No issues found")
        
        report = {
            "scan_info": {
                "timestamp": datetime.now().isoformat(),
                "apk_file": os.path.basename(self.apk_path),
                "scanner_version": "1.0.0",
                "owasp_version": "MASVS 2.1.0"
            },
            "risk_assessment": {
                "risk_level": risk_level,
                "risk_score": self.risk_score,
                "total_findings": total_findings,
                "high_severity": high_severity,
                "medium_severity": medium_severity
            },
            "summary": summary,
            "detailed_findings": self.findings,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        if any("Debug mode" in str(finding) for findings in self.findings.values() for finding in findings):
            recommendations.append("🔧 Disable debug mode in production builds")
        
        if any("Backup" in str(finding) for findings in self.findings.values() for finding in findings):
            recommendations.append("🔧 Set android:allowBackup=\"false\" in AndroidManifest.xml")
        
        if any("Clear text" in str(finding) for findings in self.findings.values() for finding in findings):
            recommendations.append("🔧 Implement proper TLS/SSL and disable clear text traffic")
        
        if any("Hardcoded" in str(finding) for findings in self.findings.values() for finding in findings):
            recommendations.append("🔧 Remove hardcoded secrets and use secure key management")
        
        if any("obfuscated" in str(finding) for findings in self.findings.values() for finding in findings):
            recommendations.append("🔧 Implement code obfuscation and minification")
        
        if any("runtime protection" in str(finding) for findings in self.findings.values() for finding in findings):
            recommendations.append("🔧 Implement anti-tampering and runtime protection")
        
        return recommendations

@app.get("/")
async def root():
    return {"message": "📡 OWASP MASVS/MASTG Compliant MobiPent Backend Running!"}

@app.post("/analyze/comprehensive")
async def analyze_comprehensive(file: UploadFile = File(...)):
    """Comprehensive OWASP MASVS/MASTG analysis"""
    print(f"\n=== 📥 OWASP Comprehensive Analysis ===")
    print(f"➡️ File: {file.filename}")

    # Save uploaded file
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Initialize scanner
    scanner = OWASPMobileScanner(file_location)
    
    # Extract APK
    if not scanner.extract_apk():
        raise HTTPException(status_code=500, detail="Failed to extract APK")
    
    # Run all OWASP analyses
    try:
        print("🔍 Running OWASP MASVS compliance tests...")
        
        # Execute all security analyses
        scanner.analyze_manifest()
        scanner.analyze_storage_security()
        scanner.analyze_crypto_security()
        scanner.analyze_network_security()
        scanner.analyze_code_quality()
        scanner.analyze_resilience()
        scanner.analyze_privacy()
        
        # Generate comprehensive report
        report = scanner.generate_report()
        
        # Save report
        report_file = os.path.join(SCAN_REPORTS_DIR, f"{file.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Analysis complete. Risk Level: {report['risk_assessment']['risk_level']}")
        
        return {
            "analysis_type": "OWASP MASVS/MASTG Comprehensive",
            "file": file.filename,
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/tool")
async def analyze_tool(
    tool_name: str = Form(...),
    file: UploadFile = File(...)
):
    """Individual tool analysis with OWASP compliance"""
    print(f"\n=== 📥 OWASP Tool Analysis ===")
    print(f"➡️ Tool: {tool_name}")
    print(f"➡️ File: {file.filename}")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    scanner = OWASPMobileScanner(file_location)
    
    if not scanner.extract_apk():
        return {"tool_used": tool_name, "file": file.filename, "result": {"summary": ["❌ APK extraction failed"]}}
    
    # Map tools to OWASP analyses
    if tool_name == "Static Analysis":
        scanner.analyze_manifest()
        scanner.analyze_storage_security()
        scanner.analyze_code_quality()
        result = {"summary": scanner.findings}
    elif tool_name == "Manifest Check":
        scanner.analyze_manifest()
        result = {"summary": scanner.findings["MASVS-PLATFORM"]}
    elif tool_name == "Reverse Engineering":
        scanner.analyze_code_quality()
        result = {"summary": scanner.findings["MASVS-CODE"]}
    elif tool_name == "Root Detection Test":
        scanner.analyze_resilience()
        result = {"summary": scanner.findings["MASVS-RESILIENCE"]}
    elif tool_name == "Code Obfuscation Check":
        scanner.analyze_code_quality()
        result = {"summary": scanner.findings["MASVS-CODE"]}
    elif tool_name == "Network Traffic Inspection":
        scanner.analyze_network_security()
        result = {"summary": scanner.findings["MASVS-NETWORK"]}
    elif tool_name == "Crypto Analysis":
        scanner.analyze_crypto_security()
        result = {"summary": scanner.findings["MASVS-CRYPTO"]}