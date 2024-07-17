import subprocess
import os
import sys
import Quartz.CoreGraphics as CG
from AppKit import NSWorkspace

def run_applescript(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    try:
        result = subprocess.run(['osascript', script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script_name}: {e.stderr}")

def get_app_name_by_pid(pid):
    for app in NSWorkspace.sharedWorkspace().runningApplications():
        if app.processIdentifier() == pid:
            return app.localizedName()
    return None

def take_screenshot(window):
    app_name = get_app_name_by_pid(window['pid'])
    if not app_name:
        app_name = window['owner']
    title = window['title']
    if app_name == 'Code':
        app_name = 'Visual Studio Code'
    print(f"{window}")
    bounds = window['bounds']
    x, y, w, h = (bounds['X'],bounds['Y'], bounds['Width'],bounds['Height'],)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(script_dir, 'screenshot.png')
    applescript_content = f"""
    tell application "{app_name}" to activate

    set screenshot_path to POSIX path of "{screenshot_path}"

    do shell script "screencapture -R{x},{y},{w},{h} " & quoted form of screenshot_path
    """

    tmp_script_path = os.path.join(script_dir, "screenshot_temp.applescript")
    with open(tmp_script_path, "w") as script_file:
        script_file.write(applescript_content)
    print(applescript_content)
    try:
        print("Running AppleScript from file:", tmp_script_path)
        result = subprocess.run(['osascript', tmp_script_path], check=True, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print(f"Screenshot saved as screenshot.png")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while taking a screenshot: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("The screenshot command timed out.")
    finally:
        os.remove(tmp_script_path)
        print(f"Temporary AppleScript {tmp_script_path} cleaned up.")


def list_open_windows():
    window_list = CG.CGWindowListCopyWindowInfo(
        CG.kCGWindowListOptionOnScreenOnly | CG.kCGWindowListOptionIncludingWindow, 
        CG.kCGNullWindowID
    )

    open_windows = []
    for idx, window in enumerate(window_list):
        window_info = {
            'index': idx,
            'owner': window.get('kCGWindowOwnerName'),
            'title': window.get('kCGWindowName', 'Unnamed'),
            'layer': window.get('kCGWindowLayer'),
            'bounds': window.get('kCGWindowBounds'),
            'pid': window.get('kCGWindowOwnerPID')
        }
        open_windows.append(window_info)

    return open_windows

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--list-windows':
        windows = list_open_windows()
        for win in windows:
            print(f"[{win['index']}] Application: {win['owner']}, Window Title: {win['title']}, Layer: {win['layer']}")
    elif len(sys.argv) > 2 and sys.argv[1] == '--screenshot' and sys.argv[2].isdigit():
        index = int(sys.argv[2])
        windows = list_open_windows()
        if 0 <= index < len(windows):
            take_screenshot(windows[index])
        else:
            print("Invalid index number.")
    else:
        print("Usage:")
        print("  --list-windows: List all open windows with their index numbers.")
        print("  --screenshot <index>: Take a screenshot of the window with the specified index number.")

if __name__ == "__main__":
    main()

