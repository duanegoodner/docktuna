import subprocess
import pytest

@pytest.mark.parametrize("script", ["simple_tune.py", "gpu_tune.py"])
def test_tuning_scripts(script):
    """Runs tuning scripts and checks for successful execution."""
    result = subprocess.run(
        ["poetry", "run", "python", f"src/docktuna/{script}", "--n_trials", "1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"{script} failed with error:\n{result.stderr}"

def test_import_simple_tune():
    """Ensure simple_tune.py can be imported without running as a script."""
    import docktuna.simple_tune  


def test_import_gpu_tune():
    """Ensure gpu_tune.py can be imported without running as a script."""
    import docktuna.gpu_tune

