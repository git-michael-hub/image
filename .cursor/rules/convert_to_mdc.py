#!/usr/bin/env python3
import json
import sys
import os

def convert_to_mdc(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    
    name = data.get("name", "Unnamed Rule")
    description = data.get("description", "")
    rules = data.get("rules", [])
    
    mdc_content = f"# {name}\n\n_{description}_\n\n"
    
    for rule in rules:
        rule_id = rule.get("id", "")
        rule_name = rule.get("name", "")
        rule_desc = rule.get("description", "")
        rule_severity = rule.get("severity", "")
        
        mdc_content += f"## {rule_name}\n\n"
        if rule_id:
            mdc_content += f"**ID**: {rule_id}  \n"
        if rule_severity:
            mdc_content += f"**Severity**: {rule_severity}  \n"
        mdc_content += f"\n{rule_desc}\n\n"
        
        # Handle guidelines if they exist
        if "guidelines" in rule:
            for guideline in rule["guidelines"]:
                mdc_content += f"- {guideline}\n"
            mdc_content += "\n"
        
        # Handle reference if it exists
        if "reference" in rule:
            mdc_content += f"**Reference**: {rule['reference']}\n\n"
        
        # Handle pattern if it exists
        if "pattern" in rule:
            pattern_type = rule["pattern"].get("type", "")
            pattern_query = rule["pattern"].get("query", "")
            mdc_content += f"**Pattern Type**: {pattern_type}  \n"
            mdc_content += f"**Pattern Query**: {pattern_query}  \n\n"
        
        # Handle message if it exists
        if "message" in rule:
            mdc_content += f"**Message**: {rule['message']}\n\n"
    
    return mdc_content

def main():
    # Process all JSON files
    for json_file in [f for f in os.listdir(".") if f.endswith(".json")]:
        base_name = os.path.splitext(json_file)[0]
        mdc_content = convert_to_mdc(json_file)
        mdc_path = os.path.join("mdc", f"{base_name}.mdc")
        
        with open(mdc_path, "w") as f:
            f.write(mdc_content)
        
        print(f"Converted {json_file} to {mdc_path}")

if __name__ == "__main__":
    main() 