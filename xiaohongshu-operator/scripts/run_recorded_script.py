#!/usr/bin/env python3
import json
import time
import urllib.request
import urllib.error
import sys
import argparse

def send_executor_request(endpoint, payload=None, method="POST"):
    url = f"http://127.0.0.1:9222/api/v1/executor/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    data = None
    if payload:
        data = json.dumps(payload).encode("utf-8")
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Error calling {url}: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

def run_script(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read script JSON: {e}")
        sys.exit(1)
        
    scripts = data.get("scripts", [])
    if not scripts:
        print("No scripts found in JSON.")
        sys.exit(1)
        
    script = scripts[0]
    print(f"Running script: {script.get('name', 'Unnamed script')}")
    
    # 1. Navigate to URL if specified
    start_url = script.get("url")
    if start_url:
        print(f"Navigating to {start_url}...")
        res = send_executor_request("navigate", {"url": start_url})
        time.sleep(3) # Wait for initial load
        
    actions = script.get("actions", [])
    
    for i, action in enumerate(actions):
        a_type = action.get("type")
        print(f"[{i+1}/{len(actions)}] Executing: {a_type}")
        
        if a_type == "sleep":
            duration_ms = action.get("duration", 1000)
            print(f"   Sleeping for {duration_ms} ms...")
            time.sleep(duration_ms / 1000.0)
            
        elif a_type == "click":
            # Prefer xpath if available, then selector
            xpath = action.get("xpath")
            selector = action.get("selector")
            text = action.get("text")
            
            # BrowserWing APIs for click identifier string
            if text and not xpath and not selector:
                # Need to use evaluate to click by text
                script_code = f'() => {{ Array.from(document.querySelectorAll("*")).find(el => el.textContent === "{text}" || (el.innerText && el.innerText.includes("{text}")))?.click(); return true; }}'
                res = send_executor_request("evaluate", {"script": script_code})
                print(f"   Click via evaluate (text={text}): {res.get('success', False)}")
            else:
                identifier = xpath if xpath else selector
                if not identifier:
                    print("   Warning: click action missing identifier")
                    continue
                
                res = send_executor_request("click", {"identifier": identifier})
                if not res.get("success"):
                    print(f"   Warning: native click failed for {identifier}, trying JS eval fallback...")
                    # Fallback
                    script_code = f'() => {{ const el = document.evaluate(`{xpath}`, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue || document.querySelector(`{selector}`); if (el) el.click(); return true; }}'
                    send_executor_request("evaluate", {"script": script_code})
                    
        elif a_type == "input":
            xpath = action.get("xpath")
            selector = action.get("selector")
            value = action.get("value", "")
            identifier = xpath if xpath else selector
            if identifier:
                res = send_executor_request("type", {"identifier": identifier, "text": value})
                print(f"   Type: {res.get('success', False)}")
            else:
                print("   Warning: input action missing identifier")
                
        elif a_type == "keyboard":
            key = action.get("key", "")
            if key.lower() == "backspace":
                res = send_executor_request("press-key", {"key": "Backspace"})
            elif key.lower() == "tab":
                res = send_executor_request("press-key", {"key": "Tab"})
            elif key.lower() == "enter":
                res = send_executor_request("press-key", {"key": "Enter"})
            else:
                res = send_executor_request("press-key", {"key": key})
            print(f"   Keyboard {key}: {res.get('success', False)}")

    print("Script execution completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run BrowserWing JSON script exports")
    parser.add_argument("script_file", help="Path to the exported JSON file")
    args = parser.parse_args()
    run_script(args.script_file)
