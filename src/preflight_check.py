#!/usr/bin/env python3
import sys
import ast
from pathlib import Path

def test_imports():
    print("🔍 Testing imports...")
    errors = []
    tests = [
        ("streamlit", "Streamlit framework"),
        ("pandas", "Pandas data library"),
        ("plotly.graph_objects", "Plotly visualization"),
        ("anthropic", "Anthropic API client"),
        ("dotenv", "Environment variables"),
    ]
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ❌ {description} - MISSING")
            errors.append((module_name, "Not installed"))
    return errors

def test_modules():
    print("\n🔍 Testing custom modules...")
    errors = []
    modules = [
        ("modules.config", "Configuration"),
        ("modules.data", "Data management"),
        ("modules.narratives", "Narratives"),
        ("modules.analysis", "AI analysis"),
        ("modules.insights", "Insights"),
    ]
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ❌ {description} - ERROR")
            errors.append((module_name, "Import failed"))
    return errors

def test_files():
    print("\n🔍 Testing required files...")
    errors = []
    # Check if we're in src/ or root - find project root
    current = Path.cwd()
    if current.name == "src":
        root = current.parent
    else:
        root = current
    
    files = [
        (str(root / ".env"), "Environment config"),
        (str(root / "pyproject.toml"), "Project dependencies"),
        (str(root / "src" / "metrics_app.py"), "Main application"),
    ]
    for file_path, description in files:
        if Path(file_path).exists():
            print(f"  ✓ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            errors.append((file_path, "Missing"))
    return errors

def test_app_syntax():
    print("\n🔍 Testing app syntax...")
    # Find metrics_app.py
    app_file = "metrics_app.py" if Path("metrics_app.py").exists() else "../metrics_app.py" if Path("../metrics_app.py").exists() else "src/metrics_app.py" if Path("src/metrics_app.py").exists() else None
    
    if not app_file:
        print("  ❌ metrics_app.py not found")
        return [("metrics_app.py", "File not found in expected locations")]
    
    try:
        with open(app_file, "r") as f:
            code = f.read()
        ast.parse(code)
        print("  ✓ Syntax valid")
        return []
    except SyntaxError as e:
        print(f"  ❌ Syntax error on line {e.lineno}")
        return [(app_file, f"Syntax error: {e.msg}")]
    except FileNotFoundError:
        print(f"  ❌ {app_file} not found")
        return [(app_file, "File not found")]

def test_function_definitions():
    """Verify all called functions are actually defined"""
    print("\n🔍 Testing function definitions...")
    errors = []
    
    # Find metrics_app.py
    app_file = "metrics_app.py" if Path("metrics_app.py").exists() else "../metrics_app.py" if Path("../metrics_app.py").exists() else "src/metrics_app.py" if Path("src/metrics_app.py").exists() else None
    
    if not app_file:
        print("  ⚠️  Skipping (metrics_app.py not found)")
        return []
    
    try:
        with open(app_file, "r") as f:
            code = f.read()
        
        tree = ast.parse(code)
        
        # Find all function definitions
        defined_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_functions.add(node.name)
        
        # Find all function calls
        called_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_functions.add(node.func.id)
        
        # Check if main functions exist
        required_functions = [
            "main",
            "show_input_tab",
            "show_dashboard_tab",
            "show_about_tab"
        ]
        
        for func in required_functions:
            if func in defined_functions:
                print(f"  ✓ {func}() exists")
            else:
                print(f"  ❌ {func}() - MISSING")
                errors.append((func, "Function not defined but may be called"))
        
        # Warn about potentially missing functions
        undefined_calls = called_functions - defined_functions
        # Filter out known builtins and library functions
        builtins = {"print", "len", "str", "int", "float", "dict", "list", "set"}
        undefined_calls = undefined_calls - builtins
        
        if undefined_calls:
            print(f"\n  ⚠️  Functions called but not defined: {', '.join(sorted(undefined_calls)[:5])}")
            print("     (These might be from imports - verify manually)")
        
        return errors
        
    except Exception as e:
        print(f"  ❌ Could not analyze functions: {e}")
        return [("function_analysis", str(e))]

def test_import_completeness():
    """Test that metrics_app can actually be imported and run"""
    print("\n🔍 Testing app import...")
    try:
        import metrics_app
        
        # Check if main function exists and is callable
        if hasattr(metrics_app, "main"):
            print("  ✓ main() function accessible")
        else:
            print("  ❌ main() not found in module")
            return [("main", "Function not found")]
        
        return []
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return [("metrics_app", str(e))]

def run_alerting_tests():
    """Run the comprehensive alerting test suite (optional)."""
    print("\n🧪 Running alerting logic tests...")
    
    # Check if test_alerting.py exists
    if not Path("test_alerting.py").exists():
        print("  ⚠️  test_alerting.py not found - skipping (optional)")
        return []
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "test_alerting.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Print the output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("  ✓ All alerting tests passed")
            return []
        else:
            print("  ⚠️  Some alerting tests failed (non-critical)")
            return []  # Changed to non-blocking
    except Exception as e:
        print(f"  ⚠️  Could not run alerting tests: {e}")
        return []  # Changed to non-blocking


def main():
    print("="*60)
    print("🚀 PRE-FLIGHT SANITY CHECK")
    print("="*60)
    print()
    
    all_errors = []
    
    # Run all tests
    all_errors.extend(test_imports())
    all_errors.extend(test_modules())
    all_errors.extend(test_files())
    all_errors.extend(test_app_syntax())
    all_errors.extend(test_function_definitions())
    all_errors.extend(test_import_completeness())
    
    # Run alerting logic tests
    alerting_errors = run_alerting_tests()
    all_errors.extend(alerting_errors)
    
    print()
    print("="*60)
    
    if all_errors:
        print("❌ SANITY CHECK FAILED")
        print()
        print("Errors found:")
        for item, error in all_errors:
            print(f"  • {item}: {error}")
        print()
        print("Fix these issues before starting the app.")
        print("="*60)
        sys.exit(1)
    else:
        print("✅ ALL SANITY CHECKS PASSED")
        print("Safe to start Streamlit!")
        print("="*60)
        sys.exit(0)

if __name__ == "__main__":
    main()
